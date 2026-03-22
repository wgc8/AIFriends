import asyncio
import base64
import json
import os
import threading
import uuid
from queue import Queue

import websockets

from pprint import pprint
from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from langchain_core.messages import HumanMessage

from web.models.friend import Friend
from web.models.message import Message
from web.models.system_prompt import SystemPrompt

from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, media_type=None, renderer_context=None):
        return data
    
def add_system_prompt(state, friend):
    msgs = state['messages']
    system_prompts = SystemPrompt.objects.filter(title='回复').order_by('order_number')
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompt
    prompt += f'\n【角色性格】\n{friend.character.profile}\n'
    prompt += f'【长期记忆】\n{friend.memory}\n'
    return {'messages': [SystemMessage(prompt)] + msgs}


def add_recent_messages(state, friend):
    msgs = state['messages']
    message_raw = list(Message.objects.filter(friend=friend).order_by('-id')[:10])
    message_raw.reverse()
    messages = []
    for m in message_raw:
        messages.append(HumanMessage(m.user_message))
        messages.append(AIMessage(m.output))
    #前10论对话加在系统提示词和用户输入之间
    return {'messages': msgs[:1] + messages + msgs[-1:]}

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer]

    def post(self, request):
        friend_id = request.data.get('friend_id')
        user_message = request.data.get('message').strip()
        if not user_message:
            return Response({
                "result": "消息不能为空"
            })
        
        friends = Friend.objects.filter(id=friend_id, me__user=request.user).select_related('character')
        if not friends.exists():
            return Response({
                "result": "好友不存在"
            })
        friend = friends.first()
        app = ChatGraph.create_app()

        input_message = {
            "messages": [HumanMessage(content=user_message)]
        }

        input_message = add_system_prompt(input_message, friend)
        input_message = add_recent_messages(input_message, friend)
        # pprint(input_message)
        response = StreamingHttpResponse(
            self.event_stream(app, input_message, friend, user_message), 
            content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response
    
    # 语音合成发送协程
    async def tts_sender(self, app, inputs, mq, ws, task_id):
        async for msg, metadata in app.astream(inputs, stream_mode="messages"):
            if isinstance(msg, BaseMessageChunk):
                if msg.content:
                    await ws.send(json.dumps({
                                                "header": {
                            "action": "continue-task",
                            "task_id": task_id,  # 随机uuid
                            "streaming": "duplex"
                        },
                        "payload": {
                            "input": {
                                "text": msg.content,
                            }
                        }
                    }))
                    mq.put_nowait({'content': msg.content})
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    mq.put_nowait({'usage': msg.usage_metadata})


    # 语音合成接收协程
    async def tts_receiver(self, mq, ws):
        async for msg in ws:
            if isinstance(msg, bytes):
                audio_base64 = base64.b64encode(msg).decode('utf-8')
                mq.put_nowait({'audio': audio_base64})
            else:
                data = json.loads(msg)
                event = data['header']['event']
                if event in ['task_finished', 'task_failed']:
                    break

    #子线程
    async def run_tts_tasks(self, app, inputs, mq):
        task_id = uuid.uuid4().hex
        api_key = os.getenv('OPENAI_API_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            'Authorization': f'Bearer {api_key}',
        }
        async with websockets.connect(wss_url, additional_headers=headers) as ws:
            await ws.send(json.dumps({
                "header": {
                    "action": "run-task",
                    "task_id": task_id,  # 随机uuid
                    "streaming": "duplex"
                },
                "payload": {
                    "task_group": "audio",
                    "task": "tts",
                    "function": "SpeechSynthesizer",
                    "model": "cosyvoice-v3-flash",
                    "parameters": {
                        "text_type": "PlainText",
                        "voice": "longanyang",  # 音色
                        "format": "mp3",  # 音频格式
                        "sample_rate": 22050,  # 采样率
                        "volume": 50,  # 音量
                        "rate": 1.25,  # 语速
                        "pitch": 1  # 音调
                    },
                    "input": {  # input不能省去，不然会报错
                    }
                }
            }))

            async for msg in ws:
                if (json.loads(msg)['header']['event'] == 'task_started'):
                    break

            await asyncio.gather(
                self.tts_sender(app, inputs, mq, ws, task_id),
                self.tts_receiver(mq, ws)
            )
    
    # 工作线程
    def work(self,app, imputs, mq):
        try:
            asyncio.run(self.run_tts_tasks(app, imputs, mq))
        finally:
            mq.put_nowait(None)  # 发送结束信号

    
    #这里的event_stream是一个同步生成器函数，使用yield来逐步返回数据。pythoN对于含有yield的函数会将其转化为一个生成器函数，非普通函数
    #调用event_stream()时，并不会立即执行函数体，而是返回一个生成器对象。当使用for循环或next()函数来迭代这个生成器对象时，才会执行函数体。
    def event_stream(self, app, inputs, friend, message):
        mq = Queue()
        thread = threading.Thread(target=self.work, args=(app, inputs, mq))
        thread.start()

        full_usage = {}
        full_output = ""

        while True:
            msg = mq.get()  # 阻塞式获取，从队列中获取消息
            if msg is None:  # 接收到结束信号，退出循环
                break
            if msg.get('content', None):
                full_output += msg['content']
                yield f"data: {json.dumps({'content': msg['content']}, ensure_ascii=False)}\n\n"
            if msg.get('audio', None):
                yield f"data: {json.dumps({'audio': msg['audio']}, ensure_ascii=False)}\n\n"
            if msg.get('usage', None):
                full_usage = msg['usage']
        yield 'data: [DONE]\n\n'
        #print("Full usage:", full_usage)
        #按json格式解析metadata中的token使用量，并保存到数据库
        input_tokens = full_usage.get('input_tokens', 0)
        output_tokens = full_usage.get('output_tokens', 0)
        total_tokens = full_usage.get('total_tokens', 0)
        Message.objects.create(
            friend=friend,
            user_message=message[:5000],
            input=json.dumps(
                [m.model_dump() for m in inputs['messages']],
                ensure_ascii=False,
            )[:10000],
            output=full_output[:5000],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
        if Message.objects.filter(friend=friend).count() % 10 == 0:  #每10条消息记录更新一次记忆
            update_memory(friend)
