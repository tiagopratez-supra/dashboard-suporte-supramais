import requests

WHATSAPP_TOKEN = "EAATNc6FAXicBSJkPsG2LfI5d98pj2KrlZAJ6MJjZAJ83oeTRizN6fzlJymBF3LPdZCgCLHJ5Ort91d2ZB7aJyCl7L7eQTCCY2ZAsUrHVx5jhW8fbmsavHkM9qBcLOfzUuLg8TehC9yMzTjrA49GWZCIZAQgGfzB4gawkXnVZCl2ajaZBe58jtZBwD1GEeFieeVgesFtRLtqtwoktRxDfZBPRKQGAZBbZCEZAu1DLh4kF4YFPybZCKebvdhlfWr8LAD1bXUu29W4iY7W56dhAFRbSTMVtP58rtYq"
PHONE_NUMBER_ID = "1270754979453091"
MEU_CELULAR = "5531975328729"

url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "messaging_product": "whatsapp",
    "to": MEU_CELULAR,
    "type": "template",
    "template": {
        "name": "jaspers_market_order_confirmation_v1",
        "language": {"code": "en_US"},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "Tiago"},
                    {"type": "text", "text": "SupraBot"},
                    {"type": "text", "text": "Hoje"}
                ]
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status HTTP: {response.status_code}")
print(f"Resposta da Meta: {response.text}")