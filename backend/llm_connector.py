import requests
from backend.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

def openrouter_chat(messages, model=OPENROUTER_MODEL, temperature=0.0):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    res = requests.post(url, headers=headers, json=payload, timeout=60)

    if res.status_code != 200:
        raise RuntimeError(res.text)

    return res.json()["choices"][0]["message"]["content"]
