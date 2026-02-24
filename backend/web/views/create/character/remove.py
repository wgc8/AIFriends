from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character
from web.views.utils.photo import remove_photo

class RemoveCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            character_id = request.data['character_id']
            character = Character.objects.get(pk=character_id, author__user=request.user)
            if character:
                remove_photo(character.photo)
                remove_photo(character.background_image)
                character.delete()
                return Response({
                    'result': 'success',
                })
            else:
                return Response({
                    'result': '角色不存在或没有权限删除',
                })

        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
