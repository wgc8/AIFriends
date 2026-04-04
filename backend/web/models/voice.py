import uuid
from django.db import models
from django.utils.timezone import now, localtime
from web.models.user import UserProfile

def voice_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'voices/{instance.author.user_id}_{filename}'

class Voice(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # 阿里云文档中需要的定义
    voice_id = models.CharField(max_length=100, unique=True)
    local_file = models.FileField(upload_to=voice_upload_to, null=True)
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.name} - {self.voice_id} - {localtime(self.create_time).strftime("%Y-%m-%d %H:%M:%S")}'