from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character


class GetSingleCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            character_id = request.query_params.get('character_id')
            character = Character.objects.get(id=character_id, author__user=request.user)
            if character:
              return Response({
                  'result': 'success',
                  'character': {
                      'id': character.id,
                      'name': character.name,
                      'profile': character.profile,
                      'photo': character.photo.url,
                      'background_image': character.background_image.url,
                  }
              })
            else:
              return Response({
                  'result': '角色不存在或无权限访问',
              })
        except:
            return Response({
                'reuslt': '系统异常，请稍后重试'
            })
