from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from langchain_core.messages import HumanMessage

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph
from web.models.message import Message

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

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

        res = app.invoke(input_message)
        print(res["messages"][-1].content)

        return Response({
            "result": "success",
        })