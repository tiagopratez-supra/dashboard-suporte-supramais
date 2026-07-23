import telebot
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Configurações de Credenciais
CHAVE_TELEGRAM = "8922477706:AAFpgSxQyz8YR_S3ZAaX0_tMlrebq9SWspk"
MEU_ID = 739554583

bot = telebot.TeleBot(CHAVE_TELEGRAM)

# Função auxiliar para buscar os dados do dia
def buscar_dados_hoje():
    try:
        cfg = st.secrets["database"]
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['server']};DATABASE={cfg['database']};UID={cfg['username']};PWD={cfg['password']};"
        
        hoje_brasil = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')
        
        sql_query = f"""
        SELECT 
            Atendente, 
            Situacao,
            Cliente,
            Modulo 
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

# Função central que monta o menu com as explicações
def enviar_menu_com_explicacao(chat_id, nome_usuario):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("📊 Volume por Atendente", callback_data="btn_resumo"),
        InlineKeyboardButton("🏢 Top Clientes", callback_data="btn_clientes"),
        InlineKeyboardButton("⚙️ Chamados por Módulo", callback_data="btn_modulos")
    )
    
    texto = f"👋 Olá, **{nome_usuario}**! Bem-vindo ao assistente de gestão da Suprasoft.\n\n"
    texto += "Escolha abaixo o relatório que deseja visualizar:\n\n"
    texto += "📊 **Volume por Atendente:** Exibe o total de chamados do dia e quantos cada atendente realizou.\n"
    texto += "🏢 **Top Clientes:** Mostra o ranking das empresas que mais acionaram o suporte hoje.\n"
    texto += "⚙️ **Chamados por Módulo:** Lista quais módulos ou rotinas do ERP SupraMAIS geraram mais suporte.\n"
    
    bot.send_message(chat_id, texto, reply_markup=markup, parse_mode="Markdown")

# 1. Comandos tradicionais (/start ou /resumo)
@bot.message_handler(commands=['resumo', 'start'])
def comando_inicial(mensagem):
    if mensagem.chat.id != MEU_ID:
        bot.reply_to(mensagem, "⛔ Acesso Negado.")
        return
    nome_usuario = mensagem.from_user.first_name or "Gestor"
    enviar_menu_com_explicacao(mensagem.chat.id, nome_usuario)

# 2. Responde a QUALQUER texto enviado (oi, ola, bom dia, etc.)
@bot.message_handler(func=lambda mensagem: True)
def responder_texto_livre(mensagem):
    if mensagem.chat.id != MEU_ID:
        bot.reply_to(mensagem, "⛔ Acesso Negado.")
        return
    nome_usuario = mensagem.from_user.first_name or "Gestor"
    enviar_menu_com_explicacao(mensagem.chat.id, nome_usuario)

# Tratamento do clique nos botões interativos
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message.chat.id != MEU_ID:
        return
    
    bot.answer_callback_query(call.id, "Consultando dados...")
    df, data_hoje = buscar_dados_hoje()
    
    if df is None or df.empty:
        bot.send_message(call.message.chat.id, "❌ Nenhum dado encontrado para hoje ou erro na conexão.")
        return

    if call.data == "btn_resumo":
        total_atendimentos = len(df)
        resumo_atendentes = df.groupby('Atendente').size().reset_index(name='Quantidade')
        resumo_atendentes = resumo_atendentes.sort_values(by='Quantidade', ascending=False)
        
        texto_resposta = f"📊 *Resumo da Operação - SupraMAIS*\n📅 Data: {data_hoje}\n\n"
        texto_resposta += f"📈 *TOTAL DE CHAMADOS HOJE: {total_atendimentos}*\n\n👥 *Volume por Atendente:*\n"
        
        for _, row in resumo_atendentes.iterrows():
            nome = str(row['Atendente']).title() 
            qtd = row['Quantidade']
            texto_resposta += f"👤 {nome}: {qtd} chamado(s)\n"
            
        bot.send_message(call.message.chat.id, texto_resposta, parse_mode="Markdown")

    elif call.data == "btn_clientes":
        resumo_clientes = df.groupby('Cliente').size().reset_index(name='Quantidade')
        resumo_clientes = resumo_clientes.sort_values(by='Quantidade', ascending=False).head(10)
        
        texto_resposta = f"🏢 *Top Clientes com Chamados Hoje*\n📅 Data: {data_hoje}\n\n"
        for _, row in resumo_clientes.iterrows():
            cliente = str(row['Cliente']).title()
            qtd = row['Quantidade']
            texto_resposta += f"🔹 {cliente}: *{qtd}* chamado(s)\n"
            
        bot.send_message(call.message.chat.id, texto_resposta, parse_mode="Markdown")

    elif call.data == "btn_modulos":
        resumo_modulos = df.groupby('Modulo').size().reset_index(name='Quantidade')
        resumo_modulos = resumo_modulos.sort_values(by='Quantidade', ascending=False)
        
        texto_resposta = f"⚙️ *Chamados por Módulo / Rotina*\n📅 Data: {data_hoje}\n\n"
        for _, row in resumo_modulos.iterrows():
            modulo = str(row['Modulo']).strip().title()
            qtd = row['Quantidade']
            texto_resposta += f"🔹 {modulo}: *{qtd}* chamado(s)\n"
            
        bot.send_message(call.message.chat.id, texto_resposta, parse_mode="Markdown")

print("Robô inteligente pronto e rodando localmente...")
bot.infinity_polling()