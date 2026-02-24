from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character


class GetSingleCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            
            # 1. 获取并打印 character_id
            character_id = request.query_params.get('character_id')
            # 2. 获取当前请求用户的关键信息（id 和 username 更易识别）
            current_user_id = request.user.id
            current_user_name = request.user.username
            
            # 3. 打印需要的四个核心值（清晰标注便于排查）
            print("===== 角色查询参数 =====")
            print(f"character_id: {character_id}")
            print(f"request.user.id: {current_user_id}")
            print(f"request.user.username: {current_user_name}")
            print(f"查询条件 author__user: {request.user}")  # 等价于 author__user=request.user

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
