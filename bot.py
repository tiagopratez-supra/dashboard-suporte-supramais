import telebot
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from flask import Flask
import threading
import os

# 1. Configurações de Credenciais
CHAVE_TELEGRAM = "8922477706:AAFpgSxQyz8YR_S3ZAaX0_tMlrebq9SWspk"
MEU_ID = 739554583

bot = telebot.TeleBot(CHAVE_TELEGRAM)
app = Flask(__name__)

# Rota web simples para o Render manter o serviço acordado
@app.route('/')
def home():
    return "🤖 Assistente SupraMAIS Telegram está online e operando!"

# 2. Função de Consulta ao Banco de Dados
def buscar_dados_hoje():
    try:
        # Puxa as credenciais diretamente das variáveis de ambiente do Render ou do Streamlit local
        server = os.environ.get("DB_SERVER") or st.secrets["database"]["server"]
        database = os.environ.get("DB_NAME") or st.secrets["database"]["database"]
        username = os.environ.get("DB_USER") or st.secrets["database"]["username"]
        password = os.environ.get("DB_PASS") or st.secrets["database"]["password"]
        
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
        
        hoje_brasil = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')
        
        sql_query = f"""
        SELECT 
            Atendente, 
            Situacao 
        FROM 
            sgrp_atendimentos_geral 
        WHERE 
            CONVERT(VARCHAR(10), Data_abertura, 103) = '{hoje_brasil}'
        """
        
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql(sql_query, conn)
        conn.close()
        
        return df, hoje_brasil
    
    except Exception as e:
        print(f"Erro na conexão com o banco: {e}")
        return None, None

# 3. Comando /resumo
@bot.message_handler(commands=['resumo', 'start'])
def enviar_resumo(mensagem):
    if mensagem.chat.id != MEU_ID:
        bot.reply_to(mensagem, "⛔ Acesso Negado: Área restrita à gestão da Suprasoft.")
        return
    
    msg_espera = bot.reply_to(mensagem, "⏳ Consultando os chamados do dia no SupraMAIS...")
    
    df, data_hoje = buscar_dados_hoje()
    
    if df is None:
        bot.edit_message_text("❌ Erro ao conectar com o banco de dados.", chat_id=mensagem.chat.id, message_id=msg_espera.message_id)
        return
    
    if df.empty:
        bot.edit_message_text(f"📊 *Resumo do dia {data_hoje}*\n\nNenhum atendimento registrado pela equipe até o momento.", chat_id=mensagem.chat.id, message_id=msg_espera.message_id, parse_mode="Markdown")
        return

    total_atendimentos = len(df)
    resumo_atendentes = df.groupby('Atendente').size().reset_index(name='Quantidade')
    resumo_atendentes = resumo_atendentes.sort_values(by='Quantidade', ascending=False)
    
    texto_resposta = f"📊 *Resumo da Operação - SupraMAIS*\n"
    texto_resposta += f"📅 Data: {data_hoje}\n\n"
    texto_resposta += f"📈 *TOTAL DE CHAMADOS HOJE: {total_atendimentos}*\n\n"
    texto_resposta += "👥 *Volume por Atendente:*\n"
    
    for index, row in resumo_atendentes.iterrows():
        nome = str(row['Atendente']).title() 
        qtd = row['Quantidade']
        texto_resposta += f"👤 {nome}: {qtd} chamado(s)\n"
    
    bot.edit_message_text(texto_resposta, chat_id=mensagem.chat.id, message_id=msg_espera.message_id, parse_mode="Markdown")

# Função para rodar o robô em segundo plano junto com o site
def rodar_telegram():
    print("Iniciando o loop do Telegram...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Inicia o Telegram em uma linha paralela (thread)
    t = threading.Thread(target=rodar_telegram)
    t.daemon = True
    t.start()
    
    # Inicia o servidor web Flask na porta exigida pelo Render
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)