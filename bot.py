import telebot
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# 1. Configurações de Credenciais
CHAVE_TELEGRAM = "8922477706:AAFpgSxQyz8YR_S3ZAaX0_tMlrebq9SWspk"
MEU_ID = 739554583

bot = telebot.TeleBot(CHAVE_TELEGRAM)

# 2. Função de Consulta ao Banco de Dados (Via Cofre Local e pyodbc)
def buscar_dados_hoje():
    try:
        # Puxa as credenciais diretamente do cofre local (.streamlit/secrets.toml)
        cfg = st.secrets["database"]
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['server']};DATABASE={cfg['database']};UID={cfg['username']};PWD={cfg['password']};"
        
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
        bot.edit_message_text("❌ Erro ao conectar com o banco de dados local.", chat_id=mensagem.chat.id, message_id=msg_espera.message_id)
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

print("Robô local conectado e ouvindo o Telegram...")
bot.infinity_polling()