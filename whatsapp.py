import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- NOVAS CONFIGURAÇÕES DO APP NOVO ---
WHATSAPP_TOKEN = "EAAO3IP1gsyMBSI0OJgps4pdKObH0wzoZCrhAr1lNdolFuT2x58qV5en26dRtf6VwLCXieym01hl41t021H0UFqWkZBTatKvm0JeWblcaMidMVWEHZCpvHcYlozCW7WEj8ovVFliRakYdxAcry6ZAcXz1wvZBcI9EkZBoKFw6wZBI2rVPv9LWV5jPIuJx9qNVn58W5zMCDUkZCNEcMFlE0S2THwsvMAa3D9iUCUTAvyyTAt9ENfJtuZBc0lTInPPvbQCET9gIt5hP3VQRfBfZAe67F2SuLO"
PHONE_NUMBER_ID = "1270754979453091"
VERIFY_TOKEN = "suprabot_novo_2026"

# --- FUNÇÃO PARA ENVIAR MENSAGEM ---
def enviar_mensagem_whatsapp(telefone_destino, texto):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone_destino,
        "type": "text",
        "text": {"body": texto}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status do Envio: {response.status_code} - {response.text}")

# --- ROTA DO WEBHOOK ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. Validação da Meta (GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Webhook verificado com sucesso pela Meta!")
            return challenge, 200
        else:
            return "Erro de Validação", 403

    # 2. Recebimento de Mensagens (POST)
    if request.method == 'POST':
        data = request.get_json()
        
        if data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        mensagem_info = value["messages"][0]
                        telefone_remetente = mensagem_info["from"]
                        texto_recebido = mensagem_info.get("text", {}).get("body", "").lower()
                        
                        print(f"📩 Nova mensagem de {telefone_remetente}: {texto_recebido}")
                        
                        # Resposta automática do bot
                        resposta = f"Olá Tiago! Recebi sua mensagem: '{texto_recebido}'. O SupraBot está online e limpinho!"
                        enviar_mensagem_whatsapp(telefone_remetente, resposta)
                        
        return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    print("🚀 Servidor Webhook rodando na porta 5000...")
    app.run(port=5000, debug=True)