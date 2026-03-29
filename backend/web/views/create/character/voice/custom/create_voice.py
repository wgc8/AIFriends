import os

import requests


def create_voice(voice_url, prefix):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    #cosyvoice-v3-flash需要和tts用同一个模型
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            "target_model": "cosyvoice-v3-flash",
            "prefix": prefix,
            "url": voice_url,
        }
    }
    response = requests.post(os.getenv('VOICE_CUSTOMIZATION_URL'), headers=headers, json=data)
    return response.json()
