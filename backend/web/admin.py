from django.contrib import admin
from web.models.user import UserProfile
from web.models.character import Character
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    # list_display = ('user', 'profile', 'create_time', 'update_time')
    # search_fields = ('user__username', 'profile')
    # list_filter = ('create_time', 'update_time')

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
    # list_display = ('author', 'name', 'profile', 'create_time', 'update_time')
    # search_fields = ('author__user__username', 'name', 'profile')
    # list_filter = ('create_time', 'update_time')
