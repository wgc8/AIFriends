import os

import requests
from django.conf import settings

def delete_voice(voice_id):
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "delete_voice",
            "voice_id": voice_id,
        }
    }
    response = requests.post(os.getenv('VOICE_CUSTOMIZATION_URL'), headers=headers, json=data)
    return response.json()

def delete_local_audio(audio_file):
    full_path = os.path.join(settings.MEDIA_ROOT, audio_file.name)
    if os.path.exists(full_path):
        os.remove(full_path)