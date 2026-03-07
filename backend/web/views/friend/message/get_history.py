from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.message import Message


class GetHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            last_message_id = int(request.query_params.get('last_message_id'))
            friend_id = request.query_params.get('friend_id')
            queryset = Message.objects.filter(friend_id=friend_id, friend__me__user=request.user)
            if last_message_id > 0:
                #如果last_message_id大于0，说明需要分页加载历史消息，则在查询集中添加过滤条件，获取id小于last_message_id的消息记录
                queryset = queryset.filter(pk__lt=last_message_id)
            messages_raw = queryset.order_by('-id')[:10]
            messages = []
            for m in messages_raw:
                messages.append({
                    'id': m.id,
                    'user_message': m.user_message,
                    'output': m.output,
                })
            return Response({
                'result': 'success',
                'messages': messages,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
