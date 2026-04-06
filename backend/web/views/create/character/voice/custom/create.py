from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.voice import Voice
from web.views.create.character.voice.scripts.create_voice import create_voice
class CreateCustomVoiceView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            # 前端传参：voice_id(声音名)、audio_file(音频文件)
            voice_name = request.data.get('name')
            audio_file = request.data.get('audio_file')
            if not voice_name:
                return Response({
                    'result': '请提供声音名称'
                })
            if not audio_file:
                return Response({
                    'result': '请提供音频文件'
                })
            # 1. 保存音频到本地（Django会自动处理存储）
            voice = Voice.objects.create(
                name=voice_name,
                local_file=audio_file  # 直接传文件对象，Django自动处理存储
            )

            voice_public_url = request.build_absolute_uri(voice.local_file.url)

            # 3. ✅ 调用阿里云接口，传递公网URL
            ali_result = create_voice(
                voice_url=voice_public_url,
                prefix=voice_name
            )
            # 4. ✅ 阿里云返回结果后，更新数据库中的voice_id
            if ali_result.get('code') == 0:
                voice.voice_id = ali_result['data']['voice_id']
                voice.save()
            else:
                # 阿里云接口调用失败，删除本地文件和数据库记录
                voice.local_file.delete(save=False)  # 删除文件但不保存模型
                voice.delete()  # 删除数据库记录
                return Response({
                    'result': '阿里云接口调用失败，请稍后重试'
                })
            # 5. 返回结果
            return Response({
                'result': 'success',
                'voice_id': voice.id,
                'audio_url': voice_public_url,  # 公网完整地址
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })