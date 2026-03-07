import json
from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from langchain_core.messages import HumanMessage

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph
from web.models.message import Message

class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, media_type=None, renderer_context=None):
        return data
class MessageView(APIView):
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

        #这里的event_stream是一个生成器函数，使用yield来逐步返回数据。pythoN对于含有yield的函数会将其转化为一个生成器函数，非普通函数
        #调用event_stream()时，并不会立即执行函数体，而是返回一个生成器对象。当使用for循环或next()函数来迭代这个生成器对象时，才会执行函数体。

        def event_stream():
            full_usage = {}
            for msg, metadata in app.stream(input_message, stream_mode="messages"):
                if isinstance(msg, BaseMessageChunk):
                    if msg.content:
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n"  #yield类似于return, 但下次调用next()时会从yield的下一行作为函数入口继续执行
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                            full_usage = msg.usage_metadata
            yield 'data: [DONE]\n\n'
            print("Full usage:", full_usage)

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

            