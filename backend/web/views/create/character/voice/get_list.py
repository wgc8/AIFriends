from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.voice import Voice

class GetVoiceListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            voices_raw = Voice.objects.order_by('id')
            voice_list = []
            for voice in voices_raw:
                voice_list.append({
                    'id': voice.id,
                    'name': voice.name,
                })
            return Response({
                'result': 'success',
                'voice_list': voice_list,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })