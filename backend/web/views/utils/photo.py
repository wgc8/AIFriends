import os
from django.conf import settings

def remove_photo(photo):
    if photo and photo.name != 'user/photos/default.png':
        full_path = os.path.join(settings.MEDIA_ROOT, photo.name)
        if os.path.exists(full_path):
            os.remove(full_path)