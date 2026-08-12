import telebot
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Configurações de Credenciais
CHAVE_TELEGRAM = "8922477706:AAFpgSxQyz8YR_S3ZAaX0_tMlrebq9SWspk"

bot = telebot.TeleBot(CHAVE_TELEGRAM)

# Senha de liberação automática para novos usuários
SENHA_LIBERACAO = "Suprabot1762"

# Lista inicial de IDs autorizados
IDS_AUTORIZADOS = [739554583] 

# Dicionários de controle de estado e tempo
estado_usuarios = {}
ultima_interacao = {}
TEMPO_LIMITE_INATIVIDADE = 300 # 5 minutos

# ----------------- CONTROLE DE ALERTAS DIÁRIOS -----------------
chamados_notificados_hoje = set()
data_notificacao_atual = (datetime.utcnow() - timedelta(hours=3)).date()

# ----------------- MONITORAMENTO PROATIVO DE INATIVIDADE -----------------
def monitorar_inatividade():
    """Roda em segundo plano checando a cada 30 segundos se alguém excedeu os 5 minutos de inatividade"""
    while True:
        time.sleep(30)
        tempo_atual = datetime.now().timestamp()
        usuarios_inativos = []
        
        for chat_id, ultima_vez in list(ultima_interacao.items()):
            if (tempo_atual - ultima_vez) > TEMPO_LIMITE_INATIVIDADE:
                usuarios_inativos.append(chat_id)
                
        for chat_id in usuarios_inativos:
            estado_usuarios.pop(chat_id, None)
            ultima_interacao.pop(chat_id, None)
            try:
                bot.send_message(chat_id, "⏳ Sessão encerrada por inatividade.\n\nObrigado por usar o SuporteBOT, espero te ver novamente em breve.")
            except Exception as e:
                print(f"Erro ao enviar timeout para {chat_id}: {e}")

thread_timeout = threading.Thread(target=monitorar_inatividade, daemon=True)
thread_timeout.start()

# ----------------- FUNÇÕES DE BANCO DE DADOS -----------------
def get_db_connection():
    cfg = st.secrets["database"]
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['server']};DATABASE={cfg['database']};UID={cfg['username']};PWD={cfg['password']};"
    return pyodbc.connect(conn_str)

def buscar_erros_hoje():
    """Busca os chamados abertos hoje com os motivos críticos e que ainda não foram concluídos"""
    try:
        hoje_brasil = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')
        
        # Conversão 103 utilizada para garantir a formatação da data no padrão Brasil e exclusão dos finalizados
        sql_query = f"""
        SELECT Sac, Cliente, Atendente, Motivo, Assunto, Situacao,
               CONVERT(VARCHAR(10), Data_abertura, 103) AS Data_abertura_br
        FROM sgrp_atendimentos_status
        WHERE CONVERT(VARCHAR(10), Data_abertura, 103) = '{hoje_brasil}'
          AND (
               LOWER(Motivo) LIKE '%erro%' 
            OR LOWER(Motivo) LIKE '%erro de versão%'
            OR LOWER(Motivo) LIKE '%erro de versao%'
            OR LOWER(Motivo) LIKE '%correçao%'
            OR LOWER(Motivo) LIKE '%correção%'
          )
          AND LOWER(RTRIM(LTRIM(Situacao))) NOT IN ('solucionada', 'fechado', 'encerrado', 'cancelado', 'resolvido', 'concluído', 'concluido')
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return []
            
        colunas = [column[0] for column in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in rows]
        
        conn.close()
        return resultados
    except Exception as e:
        print(f"Erro BD (Monitoramento de Erros): {e}")
        return []

def buscar_dados_hoje():
    try:
        hoje_brasil = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')
        sql_query = f"""
        SELECT Atendente, Situacao, Cliente, Modulo 
        FROM sgrp_atendimentos_geral 
        WHERE CONVERT(VARCHAR(10), Data_abertura, 103) = '{hoje_brasil}'
        """
        conn = get_db_connection()
        df = pd.read_sql(sql_query, conn)
        conn.close()
        return df, hoje_brasil
    except Exception as e:
        print(f"Erro BD: {e}")
        return None, None

def buscar_chamado_especifico(coluna_busca, valor):
    try:
        if coluna_busca not in ['Sac', 'Card']: return None
        sql_query = f"""
        SELECT TOP 1 
            Sac, Card, CONVERT(VARCHAR(10), Data_abertura, 103) AS Data_abertura, 
            Cliente, Contato, Assunto, Situacao, Atendente, Origem, Status, Responsavel_atual,
            [Ultima Atualizacao], CONVERT(VARCHAR(10), [Data Ultima Atualizacao], 103) AS [Data Ultima Atualizacao]
        FROM sgrp_atendimentos_status 
        WHERE {coluna_busca} = ?
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query, (valor,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
            
        colunas = [column[0] for column in cursor.description]
        dados = dict(zip(colunas, row))
        conn.close()
        return dados
    except Exception as e:
        print(f"Erro BD: {e}")
        return None

def buscar_clientes_por_termo(termo):
    try:
        termo_numeros = ''.join(filter(str.isdigit, termo))
        
        sql_query = """
        SELECT DISTINCT [Cliente Codigo], Cliente 
        FROM sgrp_atendimentos_status 
        WHERE Cliente LIKE ? 
           OR REPLACE(REPLACE(REPLACE(CNPJ, '.', ''), '/', ''), '-', '') = ?
        """
        termo_nome = f"%{termo}%"
        termo_cnpj = termo_numeros 
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query, (termo_nome, termo_cnpj))
        rows = cursor.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({"Codigo": row[0], "Cliente": row[1]})
            
        conn.close()
        return resultados
    except Exception as e:
        print(f"Erro BD: {e}")
        return None

def buscar_ultimos_chamados_cliente(codigo_cliente):
    try:
        sql_query = """
        SELECT TOP 20 
            Sac, Card, CONVERT(VARCHAR(10), Data_abertura, 103) AS Data_abertura_br, 
            Assunto, Situacao, Atendente, Cliente, Contato
        FROM sgrp_atendimentos_status 
        WHERE [Cliente Codigo] = ? AND Situacao NOT LIKE '%Removido%'
        ORDER BY 
            CASE 
                WHEN LOWER(Situacao) IN ('solucionada', 'fechado', 'encerrado', 'cancelado', 'resolvido') THEN 1 
                ELSE 0 
            END ASC,
            Data_abertura DESC
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query, (codigo_cliente,))
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return []
            
        colunas = [column[0] for column in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in rows]
        conn.close()
        return resultados
    except Exception as e:
        print(f"Erro BD: {e}")
        return None


# ----------------- THREAD DE MONITORAMENTO DE ERROS -----------------
def monitorar_erros_diarios():
    """Roda em segundo plano checando chamados críticos abertos a cada 2 horas entre 10h e 19h"""
    global chamados_notificados_hoje, data_notificacao_atual
    
    while True:
        agora_brasil = datetime.utcnow() - timedelta(hours=3)
        
        if agora_brasil.date() != data_notificacao_atual:
            chamados_notificados_hoje.clear()
            data_notificacao_atual = agora_brasil.date()

        if 10 <= agora_brasil.hour < 19:
            erros = buscar_erros_hoje()
            novos_erros = [e for e in erros if e['Sac'] not in chamados_notificados_hoje]

            if novos_erros:
                for erro in novos_erros:
                    cliente = str(erro.get('Cliente', 'Não informado')).title()
                    atendente = str(erro.get('Atendente', 'Não atribuído')).title()
                    motivo = erro.get('Motivo', 'Não especificado')
                    assunto = erro.get('Assunto', 'Não informado')
                    situacao = erro.get('Situacao', 'Em aberto')
                    data_br = erro.get('Data_abertura_br', 'Sem data')
                    
                    mensagem_alerta = (
                        f"🚨 *ALERTA DE SISTEMA: Novo Chamado Crítico Pendente*\n\n"
                        f"📌 *SAC:* `{erro['Sac']}`\n"
                        f"🏢 *Cliente:* {cliente}\n"
                        f"💬 *Assunto:* {assunto}\n"
                        f"🛠 *Motivo:* {motivo}\n"
                        f"📍 *Situação:* {situacao}\n"
                        f"👤 *Atendente:* {atendente}\n"
                        f"📅 *Data:* {data_br}"
                    )
                    
                    for chat_id in IDS_AUTORIZADOS:
                        try:
                            bot.send_message(chat_id, mensagem_alerta, parse_mode="Markdown")
                        except Exception as e:
                            print(f"Erro ao enviar alerta para {chat_id}: {e}")
                    
                    chamados_notificados_hoje.add(erro['Sac'])
            
            # Aguarda 2 horas
            time.sleep(7200)
        else:
            # Fora do horário, aguarda 15 minutos para tentar de novo
            time.sleep(900)

thread_erros = threading.Thread(target=monitorar_erros_diarios, daemon=True)
thread_erros.start()


# ----------------- FUNÇÕES DO TELEGRAM -----------------

def enviar_menu_com_explicacao(chat_id, nome_usuario):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("📊 Volume por Atendente", callback_data="btn_resumo"),
        InlineKeyboardButton("🏢 Top Clientes", callback_data="btn_clientes"),
        InlineKeyboardButton("⚙️ Chamados por Módulo", callback_data="btn_modulos"),
        InlineKeyboardButton("🔍 Consultar Chamado (SAC / Card)", callback_data="btn_consultar"),
        InlineKeyboardButton("🔎 Buscar por Cliente (Nome/CNPJ)", callback_data="btn_buscar_cliente"),
        InlineKeyboardButton("❌ Encerrar Atendimento", callback_data="btn_encerrar")
    )
    
    texto = f"👋 Olá, **{nome_usuario}**! Bem-vindo ao assistente de gestão.\n\n"
    texto += "Escolha abaixo a opção desejada:\n"
    
    bot.send_message(chat_id, texto, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda mensagem: True)
def gerenciar_mensagens(mensagem):
    chat_id = mensagem.chat.id
    texto = mensagem.text.strip().lower()
    tempo_atual = datetime.now().timestamp()
    nome_usuario = mensagem.from_user.first_name or "Gestor"

    if chat_id in IDS_AUTORIZADOS:
        ultima_interacao[chat_id] = tempo_atual

        if texto in ['sair', 'encerrar', 'fim']:
            estado_usuarios.pop(chat_id, None)
            ultima_interacao.pop(chat_id, None)
            bot.send_message(chat_id, "Obrigado por usar o SuporteBOT, espero te ver novamente em breve.")
            return
        
        if texto in ['/start', '/resumo', '/menu', 'oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']:
            estado_usuarios.pop(chat_id, None)
            enviar_menu_com_explicacao(chat_id, nome_usuario)
            return

        estado_atual = estado_usuarios.get(chat_id)
        if estado_atual in ["aguardando_sac", "aguardando_card"]:
            processar_consulta_chamado(mensagem)
        elif estado_atual == "aguardando_cliente":
            processar_busca_cliente(mensagem)
        else:
            enviar_menu_com_explicacao(chat_id, nome_usuario)
        return

    if mensagem.text.strip() == SENHA_LIBERACAO:
        IDS_AUTORIZADOS.append(chat_id)
        ultima_interacao[chat_id] = tempo_atual
        bot.reply_to(mensagem, "✅ **Senha aceita com sucesso!** Acesso liberado à gestão.")
        enviar_menu_com_explicacao(chat_id, nome_usuario)
        return

    bot.reply_to(mensagem, "🔒 **Acesso Restrito.**\n\nEste é um assistente exclusivo da gestão. Digite a **senha de acesso**:")

def processar_consulta_chamado(mensagem):
    chat_id = mensagem.chat.id
    estado = estado_usuarios.get(chat_id)
    texto_digitado = mensagem.text.strip()
    
    if not texto_digitado.isdigit():
        bot.reply_to(mensagem, "❌ Por favor, digite apenas números válidos ou envie /menu para voltar.")
        return
        
    coluna = "Sac" if estado == "aguardando_sac" else "Card"
    dados = buscar_chamado_especifico(coluna, int(texto_digitado))
    
    if not dados:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 Voltar ao Menu Principal", callback_data="btn_voltar_menu"))
        bot.send_message(chat_id, f"🔍 Nenhum chamado encontrado com o {coluna} **{texto_digitado}**.\n\n✍️ Digite outro número para tentar novamente ou volte ao menu:", reply_markup=markup, parse_mode="Markdown")
        return
        
    estado_usuarios.pop(chat_id, None)
    
    resp = f"📋 *Detalhes do Chamado*\n\n"
    resp += f"📌 **SAC:** {dados.get('Sac')} | 💳 **Card:** {dados.get('Card') or 'Não informado'}\n"
    resp += f"📅 **Abertura:** {dados.get('Data_abertura')}\n"
    resp += f"🏢 **Cliente:** {str(dados.get('Cliente')).title()}\n"
    resp += f"🗣 **Solicitante:** {str(dados.get('Contato')).title() if dados.get('Contato') else 'Não informado'}\n"
    resp += f"💬 **Assunto:** {dados.get('Assunto')}\n"
    resp += f"📌 **Situação:** {dados.get('Situacao')} | ⚡ **Status:** {dados.get('Status')}\n"
    resp += f"👤 **Atendente:** {str(dados.get('Atendente')).title()}\n"
    resp += f"🌐 **Origem:** {dados.get('Origem')}\n"
    resp += f"ref: **Resp. Atual:** {str(dados.get('Responsavel_atual')).title() if dados.get('Responsavel_atual') else 'Nenhum'}\n\n"
    resp += f"📝 **Última Atualização:** {dados.get('Ultima Atualizacao') or 'Nenhum registro'}\n"
    resp += f"📅 **Data Última Atualização:** {dados.get('Data Ultima Atualizacao') or 'Não informada'}\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔍 Nova Consulta", callback_data="btn_consultar"),
        InlineKeyboardButton("🏠 Menu Principal", callback_data="btn_voltar_menu")
    )
    bot.send_message(chat_id, resp, reply_markup=markup, parse_mode="Markdown")

def processar_busca_cliente(mensagem):
    chat_id = mensagem.chat.id
    termo = mensagem.text.strip()
    
    clientes = buscar_clientes_por_termo(termo)
    
    if clientes is None:
        bot.reply_to(mensagem, "❌ Ocorreu um erro ao consultar o banco de dados.")
        return
        
    if len(clientes) == 0:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏠 Voltar ao Menu Principal", callback_data="btn_voltar_menu"))
        bot.send_message(chat_id, f"🔍 Nenhum cliente encontrado para **'{termo}'**.\n\n✍️ Digite outro nome/CNPJ ou volte ao menu:", reply_markup=markup, parse_mode="Markdown")
        return
        
    if len(clientes) == 1:
        estado_usuarios.pop(chat_id, None)
        enviar_chamados_cliente(chat_id, clientes[0]['Codigo'])
        return
        
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for c in clientes[:10]:
        markup.add(InlineKeyboardButton(f"{str(c['Cliente']).title()}", callback_data=f"cli_{c['Codigo']}"))
    
    markup.add(InlineKeyboardButton("🏠 Voltar ao Menu Principal", callback_data="btn_voltar_menu"))
    
    texto = f"Encontramos {len(clientes)} clientes correspondentes." if len(clientes) <= 10 else f"Muitos clientes encontrados. Mostrando os 10 primeiros."
    bot.send_message(chat_id, f"🏢 {texto} Por favor, selecione o correto abaixo:", reply_markup=markup)

def enviar_chamados_cliente(chat_id, codigo_cliente):
    chamados = buscar_ultimos_chamados_cliente(codigo_cliente)
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔎 Nova Busca Cliente", callback_data="btn_buscar_cliente"),
        InlineKeyboardButton("🏠 Menu Principal", callback_data="btn_voltar_menu")
    )
    
    if chamados is None:
        bot.send_message(chat_id, "❌ Erro ao buscar chamados.", reply_markup=markup)
        return
        
    if len(chamados) == 0:
        bot.send_message(chat_id, "ℹ️ Este cliente não possui chamados recentes.", reply_markup=markup)
        return
        
    nome_cliente = str(chamados[0]['Cliente']).title()
    
    abertos = []
    fechados = []
    situacoes_fechadas = ['solucionada', 'fechado', 'encerrado', 'cancelado', 'resolvido']
    
    for c in chamados:
        if str(c['Situacao']).lower().strip() in situacoes_fechadas:
            fechados.append(c)
        else:
            abertos.append(c)
            
    resp = f"🏢 *Últimos Chamados: {nome_cliente}*\n\n"
    
    if abertos:
        resp += "🟢 *EM ABERTO*\n"
        for c in abertos:
            contato = str(c['Contato']).title() if c['Contato'] else "Não informado"
            resp += f"📌 SAC: `{c['Sac']}` | 📅 {c['Data_abertura_br']}\n🗣 Solicitante: {contato}\n💬 {c['Assunto']}\n👤 {str(c['Atendente']).title()} | 📍 {c['Situacao']}\n\n"
            
    if fechados:
        resp += "🔴 *FECHADOS (Recentes)*\n"
        for c in fechados:
            contato = str(c['Contato']).title() if c['Contato'] else "Não informado"
            resp += f"📌 SAC: `{c['Sac']}` | 📅 {c['Data_abertura_br']}\n🗣 Solicitante: {contato}\n💬 {c['Assunto']}\n👤 {str(c['Atendente']).title()} | 📍 {c['Situacao']}\n\n"
            
    if len(resp) > 4000:
        bot.send_message(chat_id, resp[:4000] + "...\n(Limitado pelo tamanho)", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, resp, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in IDS_AUTORIZADOS:
        bot.answer_callback_query(call.id, "Acesso não autorizado.")
        return
        
    ultima_interacao[chat_id] = datetime.now().timestamp()

    if call.data == "btn_encerrar":
        estado_usuarios.pop(chat_id, None)
        ultima_interacao.pop(chat_id, None)
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Obrigado por usar o SuporteBOT, espero te ver novamente em breve.")
        return

    if call.data == "btn_voltar_menu":
        estado_usuarios.pop(chat_id, None)
        bot.answer_callback_query(call.id)
        enviar_menu_com_explicacao(chat_id, call.from_user.first_name or "Gestor")
        return
        
    if call.data.startswith("cli_"):
        estado_usuarios.pop(chat_id, None) 
        codigo_cliente = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "Buscando chamados do cliente...")
        enviar_chamados_cliente(chat_id, codigo_cliente)
        return

    if call.data == "btn_buscar_cliente":
        estado_usuarios[chat_id] = "aguardando_cliente"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔎 *Buscar Cliente*\n\n✍️ Por favor, digite o **Nome** (parcial ou completo) ou apenas os números do **CNPJ**:")
        return

    if call.data == "btn_consultar":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔢 Buscar por SAC", callback_data="tipo_sac"),
            InlineKeyboardButton("💳 Buscar por Card", callback_data="tipo_card")
        )
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔍 Como você deseja localizar o chamado?", reply_markup=markup)
        return

    elif call.data == "tipo_sac":
        estado_usuarios[chat_id] = "aguardando_sac"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "✍️ Por favor, digite o **número do SAC**:")
        return

    elif call.data == "tipo_card":
        estado_usuarios[chat_id] = "aguardando_card"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "✍️ Por favor, digite o **número do Card**:")
        return

    bot.answer_callback_query(call.id, "Consultando dados...")
    df, data_hoje = buscar_dados_hoje()
    
    if df is None or df.empty:
        bot.send_message(chat_id, "❌ Nenhum dado encontrado para hoje ou erro na conexão.")
        return

    markup_voltar = InlineKeyboardMarkup()
    markup_voltar.add(InlineKeyboardButton("🏠 Voltar ao Menu Principal", callback_data="btn_voltar_menu"))

    if call.data == "btn_resumo":
        total_atendimentos = len(df)
        resumo_atendentes = df.groupby('Atendente').size().reset_index(name='Quantidade').sort_values(by='Quantidade', ascending=False)
        texto_resposta = f"📊 *Resumo da Operação*\n📅 Data: {data_hoje}\n\n📈 *TOTAL DE CHAMADOS HOJE: {total_atendimentos}*\n\n👥 *Volume por Atendente:*\n"
        for _, row in resumo_atendentes.iterrows(): texto_resposta += f"👤 {str(row['Atendente']).title()}: {row['Quantidade']} chamado(s)\n"
        bot.send_message(chat_id, texto_resposta, reply_markup=markup_voltar, parse_mode="Markdown")

    elif call.data == "btn_clientes":
        resumo_clientes = df.groupby('Cliente').size().reset_index(name='Quantidade').sort_values(by='Quantidade', ascending=False).head(10)
        texto_resposta = f"🏢 *Top Clientes com Chamados Hoje*\n📅 Data: {data_hoje}\n\n"
        for _, row in resumo_clientes.iterrows(): texto_resposta += f"🔹 {str(row['Cliente']).title()}: *{row['Quantidade']}* chamado(s)\n"
        bot.send_message(chat_id, texto_resposta, reply_markup=markup_voltar, parse_mode="Markdown")

    elif call.data == "btn_modulos":
        resumo_modulos = df.groupby('Modulo').size().reset_index(name='Quantidade').sort_values(by='Quantidade', ascending=False)
        texto_resposta = f"⚙️ *Chamados por Módulo / Rotina*\n📅 Data: {data_hoje}\n\n"
        for _, row in resumo_modulos.iterrows(): texto_resposta += f"🔹 {str(row['Modulo']).strip().title()}: *{row['Quantidade']}* chamado(s)\n"
        bot.send_message(chat_id, texto_resposta, reply_markup=markup_voltar, parse_mode="Markdown")

print("Robô ativo e monitorando.")
bot.infinity_polling()