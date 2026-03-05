from django.db import models
from django.utils.timezone import now, localtime
from web.models.friend import Friend

class Message(models.Model):
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)
    user_message = models.TextField(default="", max_length=500)
    input = models.TextField(default="", max_length=500)
    output = models.TextField(default="", max_length=500)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.friend.character.name} - {self.friend.me.user.username} - {self.user_message[:50]} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"