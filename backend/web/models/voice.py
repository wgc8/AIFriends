from django.db import models
from django.utils.timezone import now, localtime

class Voice(models.Model):
    name = models.CharField(max_length=100)
    # 阿里云文档中需要的定义
    voice_id = models.CharField(max_length=100, unique=True)
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.name} - {self.voice_id} - {localtime(self.create_time).strftime("%Y-%m-%d %H:%M:%S")}'