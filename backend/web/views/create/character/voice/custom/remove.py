from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.voice import Voice
from web.views.create.character.voice.scripts.delete_voice import delete_voice, delete_local_audio
class RemoveCustomVoiceView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            voice_id = request.data.get('voice_id')
            if not voice_id:
                return Response({
                    'result': '请提供声音ID'
                })
            voice = Voice.objects.get(id=voice_id)
            if not voice:
                return Response({
                    'result': '声音不存在或没有权限删除'
                })
            # 删除阿里云上创建的声音
            ret = delete_voice(voice.voice_id)
            if not ret or ret.get('code') != 0:
                return Response({
                    'result': '删除声音失败'
                })

            # 删除本地文件和数据库记录
            delete_local_audio(voice.local_file)

            voice.delete()  # 删除数据库记录
            return Response({
                'result': 'success'
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })