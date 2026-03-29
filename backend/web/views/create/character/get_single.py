from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character
from web.models.voice import Voice

class GetSingleCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            character_id = request.query_params.get('character_id')
            character = Character.objects.get(id=character_id, author__user=request.user)
            voices_raw = Voice.objects.order_by('id')
            voice_list = []
            for voice in voices_raw:
                voice_list.append({
                    'id': voice.id,
                    'name': voice.name,
                })
            if character:
              return Response({
                  'result': 'success',
                  'character': {
                      'id': character.id,
                      'name': character.name,
                      'profile': character.profile,
                      'photo': character.photo.url,
                      'background_image': character.background_image.url,
                      'voice_id': character.voice.id,
                  },
                  'voices': voice_list,
              })
            else:
              return Response({
                  'result': '角色不存在或无权限访问',
              })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
