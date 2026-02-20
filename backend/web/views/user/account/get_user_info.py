from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.user import UserProfile

class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # 强制必须登录才能访问

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return Response({
                'result': 'success',
                'user_id': request.user.id,
                'username': request.user.username,
                'photo': user_profile.photo.url,  # 必须加url！！！
                'profile': user_profile.profile,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })