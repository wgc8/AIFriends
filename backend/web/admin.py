from django.contrib import admin
from web.models.user import UserProfile
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('user', 'profile', 'create_time', 'update_time')
    search_fields = ('user__username', 'profile')
    list_filter = ('create_time', 'update_time')