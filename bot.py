import telebot

# Cole o seu Token real dentro das aspas abaixo
CHAVE_TELEGRAM = "8922477706:AAFpgSxQyz8YR_S3ZAaX0_tMlrebq9SWspk"

# O seu ID de segurança exclusivo
MEU_ID = 739554583

bot = telebot.TeleBot(CHAVE_TELEGRAM)

@bot.message_handler(commands=['resumo', 'start'])
def enviar_resumo(mensagem):
    # Trava de Segurança: Ignora qualquer pessoa que não seja você
    if mensagem.chat.id != MEU_ID:
        bot.reply_to(mensagem, "⛔ Acesso Negado: Área restrita à gestão da Suprasoft.")
        return
    
    # Mensagem de sucesso (Em breve substituiremos isso pelo resultado do banco de dados)
    resposta = (
        "📊 *Resumo da Operação - SupraMAIS*\n\n"
        "Olá, Tiago! A sua conexão segura foi estabelecida com sucesso.\n"
        "O robô já está pronto para receber os comandos em SQL e monitorar os chamados da equipe!"
    )
    
    bot.reply_to(mensagem, resposta, parse_mode="Markdown")

bot.polling()