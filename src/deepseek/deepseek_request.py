import requests
from config import DEEPSEEK_API

def request_deep(data):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [{"role": "user", "content":data}]
    }

    return requests.post(url, headers=headers, json=data)