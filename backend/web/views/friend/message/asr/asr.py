import asyncio
import json
import os
import uuid
import websockets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ASRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 获取上传的音频数据
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({
                'result': '音频不存在'
            })
        pcm_data = audio_file.read()
        text = asyncio.run(self.run_asr_tasks(pcm_data))
        return Response({
            'result': 'success',
            'text': text
        })
    
    async def run_asr_tasks(self, pcm_data):
        # 生成task_id
        task_id = str(uuid.uuid4())
        # 读取环境变量
        api_key = os.getenv('OPENAI_API_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        # with语句自动管理websocket连接的生命周期
        # 跳出with语句时，会自动执行ws.close()
        async with websockets.connect(wss_url, additional_headers=headers) as ws:
            # 发送开始任务消息
            await ws.send(json.dumps({
                "header": {
                    "streaming": "duplex",
                    "task_id": task_id,
                    "action": "run-task"
                },
                "payload": {
                    "model": "gummy-realtime-v1",
                    "parameters": {
                        "sample_rate": 16000,
                        "format": "pcm",
                        "transcription_enabled": True,
                    },
                    "input": {},
                    "task": "asr",
                    "task_group": "audio",
                    "function": "recognition"
                }
            }))
            # 读取ws的响应，判断是否就绪
            async for msg in ws:
                if json.loads(msg)['header']['event'] == 'task_started':
                    break
            _, text = await asyncio.gather(
                    self.asr_sender(self, pcm_data, ws, task_id),
                    self.asr_receiver(self, ws)
                )
            return text

    async def asr_sender(self, pcm_data, ws, task_id):
        chunk_size = 3200  # 每次发送200ms的音频数据
        for i in range(0, len(pcm_data), chunk_size):
            chunk = pcm_data[i:i+chunk_size]
            await ws.send(chunk)
            await asyncio.sleep(0.01)
        # 发送结束消息
        await ws.send(json.dumps({
            "header": {
                "action": "finish-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}
            }
        }))

    
    async def asr_receiver(self, ws):
        text = ''
        async for msg in ws:
            data = json.loads(msg)
            event = data['header']['event']
            if event == 'result-generated':
                output = data['payload']['output']
                if output.get('transcription', None) and output['transcription']['sentence_end']:
                    text += output['transcription']['text']
            elif event in ['task_finished', 'task_failed']:
                break
        return text