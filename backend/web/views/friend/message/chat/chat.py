import json
from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from langchain_core.messages import HumanMessage

from web.views.friend.message.chat.graph import ChatGraph
from web.models.friend import Friend
from web.models.message import Message
from web.models.system_prompt import SystemPrompt

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
        
        #这里的event_stream是一个生成器函数，使用yield来逐步返回数据。pythoN对于含有yield的函数会将其转化为一个生成器函数，非普通函数
        #调用event_stream()时，并不会立即执行函数体，而是返回一个生成器对象。当使用for循环或next()函数来迭代这个生成器对象时，才会执行函数体。

        def event_stream():
            full_usage = {}
            full_output = ""
            for msg, metadata in app.stream(input_message, stream_mode="messages"):
                if isinstance(msg, BaseMessageChunk):
                    if msg.content:
                        full_output += msg.content
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n"  #yield类似于return, 但下次调用next()时会从yield的下一行作为函数入口继续执行
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                            full_usage = msg.usage_metadata
            yield 'data: [DONE]\n\n'
            #print("Full usage:", full_usage)
            #按json格式解析metadata中的token使用量，并保存到数据库
            input_tokens = full_usage.get('input_tokens', 0)
            output_tokens = full_usage.get('output_tokens', 0)
            total_tokens = full_usage.get('total_tokens', 0)
            Message.objects.create(
                friend=friend,
                user_message=user_message[:5000],
                input=json.dumps(
                    [m.model_dump() for m in input_message['messages']],
                    ensure_ascii=False,
                )[:10000],
                output=full_output[:5000],
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )


        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

            