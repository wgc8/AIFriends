from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.user import UserProfile
from web.models.character import Character
from web.models.friend import Friend

class GetOrCreateFriendView(APIView):
  permission_classes = [IsAuthenticated]
  def post(self, request):
    try:
      character_id = request.data.get('character_id')
      user = request.user
      user_profile = UserProfile.objects.get(user=user)
      friends = Friend.objects.filter(me=user_profile, character_id=character_id)
      if friends.exists():
        friend = friends.first()
      else:
        friend = Friend.objects.create(
          me=user_profile,
          character_id=character_id,
        )
      character = friend.character
      author = character.author
      return Response({
        'result': 'success',
        'friend': {
          'id': friend.id,
          'character': {
            'id': character.id,
            'name': character.name,
            'profile': character.profile,
            'photo': character.photo.url,
            'background_image': character.background_image.url,
            'author': {
              'user_id': author.user_id,
              'username': author.user.username,
              'photo': author.photo.url,
            }
          }
        }
      })
    except:
      return Response({
        'result': '系统异常，请稍后重试'
      })