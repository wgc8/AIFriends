from django.contrib import admin
from web.models.friend import Friend
from web.models.user import UserProfile
from web.models.character import Character
from web.models.message import Message
from web.models.system_prompt import SystemPrompt
from web.models.voice import Voice
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    # list_display = ('user', 'profile', 'create_time', 'update_time')
    # search_fields = ('user__username', 'profile')
    # list_filter = ('create_time', 'update_time')

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'voice',)
    # list_display = ('author', 'name', 'profile', 'create_time', 'update_time')
    # search_fields = ('author__user__username', 'name', 'profile')
    # list_filter = ('create_time', 'update_time')

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    raw_id_fields = ('me', 'character',)
    # list_display = ('me', 'character', 'memory', 'create_time', 'update_time')
    # search_fields = ('me__user__username', 'character__name', 'memory')
    # list_filter = ('create_time', 'update_time')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('friend',)
    # list_display = ('friend', 'user_message', 'input', 'output', 'input_tokens', 'output_tokens', 'create_time')
    # search_fields = ('friend__me__user__username', 'friend__character__name', 'user_message', 'input', 'output')
    # list_filter = ('create_time',)

admin.site.register(SystemPrompt)

admin.site.register(Voice)