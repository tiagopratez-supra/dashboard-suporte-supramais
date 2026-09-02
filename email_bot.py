import pyodbc
import pandas as pd
import smtplib
import warnings
import os
import time
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

SMTP_SERVER = "smtp.office365.com" 
SMTP_PORT   = 587
EMAIL_REMETENTE = "tiago.prates@suprasoft.net"
SENHA_REMETENTE = st.secrets["email"]["senha"]

EMAIL_TESTE_GESTOR = "tiago.prates@suprasoft.net"
MODO_TESTE = False

EMAILS_GESTAO = [
    "tiago.prates@suprasoft.net",
    "sonia.silva@suprasoft.net",
    "tatiane.fernandes@suprasoft.net"
]

def get_db_connection():
    cfg = st.secrets["database"]
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['server']};DATABASE={cfg['database']};UID={cfg['username']};PWD={cfg['password']};"
    return pyodbc.connect(conn_str)

def anexar_imagem(msg_root, caminho_arquivo, content_id):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', f'<{content_id}>')
            img.add_header('Content-Disposition', 'inline')
            msg_root.attach(img)

def formatar_nome_curto(nome_completo):
    """Extrai apenas o Primeiro Nome e Sobrenome para evitar homônimos."""
    if not nome_completo or pd.isna(nome_completo):
        return "—"
    partes = str(nome_completo).split()
    if len(partes) > 1:
        return f"{partes[0]} {partes[1]}".title()
    elif partes:
        return partes[0].title()
    return "—"

def formatar_lista_top(df_agrupado, limite=5):
    html = ""
    for idx, row in df_agrupado.head(limite).iterrows():
        nome = str(row.iloc[0]).title()
        qtd = row.iloc[1]
        html += f"<li><strong>{qtd}</strong> - {nome}</li>"
    if html == "":
        return "<li>Nenhum registro</li>"
    return html

def formatar_tabela_clientes(df_clientes, limite=5):
    html = ""
    total = len(df_clientes.head(limite))
    for i, (idx, row) in enumerate(df_clientes.head(limite).iterrows()):
        nome_cliente = str(row.iloc[0]).title()
        if len(nome_cliente) > 25:
            nome_cliente = nome_cliente[:25] + "..."
        qtd = row.iloc[1]
        border = "border-bottom: 1px dashed #CBD5E1;" if i < (total - 1) else ""
        html += f"""
        <tr>
            <td style="padding: 8px 0; color: #475569; font-size: 12px; {border}">{nome_cliente}</td>
            <td align="right" style="padding: 8px 0; color: #0F172A; font-size: 13px; font-weight: 700; {border}">{qtd}</td>
        </tr>
        """
    if html == "":
        return '<tr><td style="padding: 8px 0; color: #475569; font-size: 12px;">Nenhum cliente registrado</td></tr>'
    return html

def enviar_relatorios_individuais():
    fuso_br = ZoneInfo("America/Sao_Paulo")
    hoje = datetime.now(fuso_br)
    
    data_alvo = hoje - timedelta(days=1)
    data_str_sql = data_alvo.strftime('%Y%m%d')
    data_formatada = data_alvo.strftime('%d/%m/%Y')
    mes_atual = data_alvo.month
    ano_atual = data_alvo.year
    
    print(f"Buscando informacoes do dia {data_formatada} e acumulado do mes...")
    
    try:
        conn = get_db_connection()
        query_dia = f"""
        SELECT Sac, Atendente, Email, Origem, Modulo, Cliente, Motivo, Assunto, Situacao, Finalizado_Mesmo_Dia
        FROM sgrp_atendimentos_geral
        WHERE CONVERT(DATE, Data_abertura) = '{data_str_sql}'
        """
        df_dia = pd.read_sql(query_dia, conn)
        
        query_mes = f"""
        SELECT Atendente, COUNT(Sac) as Total_Mes
        FROM sgrp_atendimentos_geral
        WHERE MONTH(Data_abertura) = {mes_atual} AND YEAR(Data_abertura) = {ano_atual}
        GROUP BY Atendente
        """
        df_mes = pd.read_sql(query_mes, conn)
        conn.close()
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")
        return

    total_global_dia = len(df_dia)
    total_global_mes = df_mes['Total_Mes'].sum() if not df_mes.empty else 0

    if total_global_dia == 0:
        print(f"Nenhum chamado em {data_formatada}.")
        return

    motivos_regex = 'erro|erro de versão|erro de versao|correçao|correção'
    situacoes_fechadas = ['solucionada', 'fechado', 'encerrado', 'cancelado', 'resolvido', 'concluído', 'concluido']
    
    mask_erro = df_dia['Motivo'].str.lower().str.contains(motivos_regex, regex=True, na=False)
    mask_aberto = ~df_dia['Situacao'].str.lower().str.strip().isin(situacoes_fechadas)
    
    df_erros_dia = df_dia[mask_erro & mask_aberto].sort_values(by='Sac')
    
    html_erros = ""
    if not df_erros_dia.empty:
        linhas_erros = ""
        for _, err in df_erros_dia.iterrows():
            sac = err['Sac']
            cli = str(err['Cliente']).title()[:20]
            
            # Assunto Completo sem truncar
            assunto = str(err['Assunto'])
                
            atend = formatar_nome_curto(err['Atendente'])
            sit = str(err['Situacao']).title()
            linhas_erros += f"""
            <tr>
                <td style="padding: 8px 5px; border-bottom: 1px dashed #FCA5A5; color: #1E293B; font-size: 12px; font-weight: 600;">{sac}</td>
                <td style="padding: 8px 5px; border-bottom: 1px dashed #FCA5A5; color: #475569; font-size: 12px;">{cli}</td>
                <td style="padding: 8px 5px; border-bottom: 1px dashed #FCA5A5; color: #475569; font-size: 12px;">{assunto}</td>
                <td style="padding: 8px 5px; border-bottom: 1px dashed #FCA5A5; color: #475569; font-size: 12px;">{atend}</td>
                <td style="padding: 8px 5px; border-bottom: 1px dashed #FCA5A5; color: #475569; font-size: 12px;">{sit}</td>
            </tr>
            """
            
        html_erros = f"""
        <tr><td style="padding: 0 30px;"><div style="height: 1px; background-color: #E2E8F0; width: 100%; margin-top: 10px;"></div></td></tr>
        <tr>
            <td style="padding: 30px;">
                <h3 style="color: #DC2626; margin: 0 0 10px 0; font-size: 16px; text-transform: uppercase;">🚨 Erros Registrados Ontem ({len(df_erros_dia)})</h3>
                <p style="color: #475569; font-size: 13px; line-height: 1.5; margin: 0 0 15px 0;">Estes são os chamados de erro classificados no expediente de ontem que seguem pendentes. Caso recebam relatos parecidos hoje, agrupem as demandas.</p>
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="text-align: left; border-collapse: collapse; background-color: #FEF2F2; border-radius: 8px; overflow: hidden; border: 1px solid #FECACA;">
                    <thead>
                        <tr>
                            <th style="padding: 8px 5px; background-color: #FEE2E2; color: #991B1B; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #FCA5A5;">SAC</th>
                            <th style="padding: 8px 5px; background-color: #FEE2E2; color: #991B1B; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #FCA5A5;">Cliente</th>
                            <th style="padding: 8px 5px; background-color: #FEE2E2; color: #991B1B; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #FCA5A5;">Assunto</th>
                            <th style="padding: 8px 5px; background-color: #FEE2E2; color: #991B1B; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #FCA5A5;">Atendente</th>
                            <th style="padding: 8px 5px; background-color: #FEE2E2; color: #991B1B; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #FCA5A5;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {linhas_erros}
                    </tbody>
                </table>
            </td>
        </tr>
        """
    else:
        html_erros = f"""
        <tr><td style="padding: 0 30px;"><div style="height: 1px; background-color: #E2E8F0; width: 100%; margin-top: 10px;"></div></td></tr>
        <tr>
            <td style="padding: 30px;">
                <h3 style="color: #10B981; margin: 0 0 8px 0; font-size: 16px; text-transform: uppercase;">✅ Erros Registrados Ontem</h3>
                <p style="color: #475569; font-size: 13px; margin: 0;">Excelente notícia! Não tivemos nenhum chamado classificado como erro ou correção pendente registrado no expediente de ontem.</p>
            </td>
        </tr>
        """

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_REMETENTE)
    except Exception as e:
        print(f"Erro SMTP: {e}")
        return

    atendentes_dia = df_dia['Atendente'].dropna().unique()
    print(f"Preparando a Daily para {len(atendentes_dia)} atendentes...\n")

    for atendente in atendentes_dia:
        df_agente_dia = df_dia[df_dia['Atendente'] == atendente]
        
        emails_atendente = df_agente_dia['Email'].dropna().unique()
        email_real_atendente = str(emails_atendente[0]).strip() if len(emails_atendente) > 0 else None
        
        email_destino = EMAIL_TESTE_GESTOR if MODO_TESTE else email_real_atendente
        
        if not email_destino:
            continue

        qtd_agente_dia = len(df_agente_dia)
        fcr_agente = (df_agente_dia['Finalizado_Mesmo_Dia'].sum() / qtd_agente_dia * 100) if qtd_agente_dia > 0 else 0
        participacao_dia = int((qtd_agente_dia / total_global_dia) * 100)
        
        try:
            qtd_agente_mes = int(df_mes[df_mes['Atendente'] == atendente]['Total_Mes'].sum())
        except:
            qtd_agente_mes = 0
            
        participacao_mes = int((qtd_agente_mes / total_global_mes) * 100) if total_global_mes > 0 else 0
        
        html_modulos = formatar_lista_top(df_agente_dia.groupby('Modulo').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False), 3)
        html_origem = formatar_lista_top(df_agente_dia.groupby('Origem').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False), 3)
        html_clientes = formatar_tabela_clientes(df_agente_dia.groupby('Cliente').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False), 5)

        nome_exibicao = formatar_nome_curto(atendente)

        corpo_html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head><meta charset="UTF-8"></head>
        <body style="margin: 0; padding: 30px 10px; background-color: #F4F7F6; font-family: 'Segoe UI', Arial, sans-serif;">
            <table align="center" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 650px; background-color: #FFFFFF; border-radius: 12px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden;">
                
                <tr>
                    <td style="background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td width="50%" align="left" style="padding: 25px 30px;">
                                    <img src="cid:logo_supra" height="35" alt="SupraMAIS" style="display: block;">
                                </td>
                                <td width="50%" align="right" style="padding: 25px 30px;">
                                    <p style="color: #64748B; margin: 0; font-size: 13px; font-weight: bold; text-transform: uppercase;">Fechamento Diário<br><span style="color: #94A3B8; font-size: 12px;">Ref. {data_formatada}</span></p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <tr>
                    <td style="padding: 40px 30px 20px 30px;">
                        <h2 style="color: #1E293B; margin: 0 0 10px 0; font-size: 24px;">Bom dia, {nome_exibicao}! ☀️</h2>
                        <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0;">
                            Segue a nossa <strong>Daily</strong> com o fechamento do dia {data_formatada}. Confira abaixo o panorama do seu desempenho operacional e o consolidado de chamados de erro que exigem nossa atenção no dia de hoje.
                        </p>
                    </td>
                </tr>

                <tr>
                    <td style="padding: 10px 30px 15px 30px;">
                        <h3 style="color: #0EA5E9; margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase;">📊 Resumo do Dia</h3>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td width="31%" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center;">
                                    <p style="color: #64748B; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Meus Chamados</p>
                                    <p style="color: #0F172A; margin: 0; font-size: 28px; font-weight: bold;">{qtd_agente_dia}</p>
                                </td>
                                <td width="3%"></td>
                                <td width="31%" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center;">
                                    <p style="color: #64748B; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Volume (Equipe)</p>
                                    <p style="color: #0F172A; margin: 0; font-size: 28px; font-weight: bold;">{participacao_dia}%</p>
                                </td>
                                <td width="3%"></td>
                                <td width="32%" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center;">
                                    <p style="color: #64748B; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Resolução Inicial</p>
                                    <p style="color: #0F172A; margin: 0; font-size: 28px; font-weight: bold;">{fcr_agente:.1f}%</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <tr>
                    <td style="padding: 0 30px 30px 30px;">
                        <h3 style="color: #8B5CF6; margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase;">📅 Acumulado do Mês</h3>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td width="48%" style="background-color: #F5F3FF; border: 1px solid #EDE9FE; border-radius: 12px; padding: 20px; text-align: center;">
                                    <p style="color: #6D28D9; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Meus Chamados (Mês)</p>
                                    <p style="color: #4C1D95; margin: 0; font-size: 28px; font-weight: bold;">{qtd_agente_mes}</p>
                                </td>
                                <td width="4%"></td>
                                <td width="48%" style="background-color: #F5F3FF; border: 1px solid #EDE9FE; border-radius: 12px; padding: 20px; text-align: center;">
                                    <p style="color: #6D28D9; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Volume (Equipe: {total_global_mes})</p>
                                    <p style="color: #4C1D95; margin: 0; font-size: 28px; font-weight: bold;">{participacao_mes}%</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <tr><td style="padding: 0 30px;"><div style="height: 1px; background-color: #E2E8F0; width: 100%;"></div></td></tr>

                <tr>
                    <td style="padding: 30px;">
                        <h3 style="color: #334155; margin: 0 0 20px 0; font-size: 18px;">🔍 Raio-X Detalhado do Dia (Ref. {data_formatada})</h3>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td width="48%" valign="top">
                                    <div style="margin-bottom: 25px;">
                                        <p style="color: #0EA5E9; font-size: 12px; font-weight: bold; text-transform: uppercase; margin: 0 0 10px 0;">Principais Módulos</p>
                                        <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 13px; line-height: 1.8;">{html_modulos}</ul>
                                    </div>
                                    <div>
                                        <p style="color: #0EA5E9; font-size: 12px; font-weight: bold; text-transform: uppercase; margin: 0 0 10px 0;">Canais (Origem)</p>
                                        <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 13px; line-height: 1.8;">{html_origem}</ul>
                                    </div>
                                </td>
                                <td width="4%"></td>
                                <td width="48%" valign="top" style="background-color: #F8FAFC; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0;">
                                    <p style="color: #8B5CF6; font-size: 12px; font-weight: bold; text-transform: uppercase; margin: 0 0 10px 0;">🏢 Principais Clientes</p>
                                    <table width="100%" cellpadding="0" cellspacing="0" border="0">{html_clientes}</table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                {html_erros}

                <tr>
                    <td style="background-color: #F1F5F9; padding: 25px 30px; text-align: center; border-top: 1px solid #E2E8F0;">
                        <p style="color: #64748B; font-size: 12px; margin: 0; line-height: 1.6;"><strong>Gestão de Suporte • SupraMAIS</strong></p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg_root = MIMEMultipart('related')
        msg_root['From'] = EMAIL_REMETENTE
        msg_root['To'] = email_destino
        msg_root['Subject'] = f"📆 Daily Suporte - {nome_exibicao} ({data_formatada})"
        
        msg_alt = MIMEMultipart('alternative')
        msg_root.attach(msg_alt)
        msg_html = MIMEText(corpo_html, 'html')
        msg_alt.attach(msg_html)
        anexar_imagem(msg_root, "logo_supra.png", "logo_supra")

        try:
            server.send_message(msg_root)
            print(f"Daily Individual enviada para: {atendente} -> {email_destino}")
            time.sleep(1)
        except Exception as e:
            print(f"Falha ao enviar para {atendente}: {e}")

    print("\nPreparando Daily Geral para a Gestao...")
    
    destinatarios_gestao = [EMAIL_TESTE_GESTOR] if MODO_TESTE else EMAILS_GESTAO
    
    fcr_equipe = (df_dia['Finalizado_Mesmo_Dia'].sum() / total_global_dia * 100) if total_global_dia > 0 else 0
    atendentes_ativos = df_dia['Atendente'].nunique()
    
    html_modulos_geral = formatar_lista_top(df_dia.groupby('Modulo').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False), 5)
    html_clientes_geral = formatar_tabela_clientes(df_dia.groupby('Cliente').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False), 5)
    
    df_rank = df_dia.groupby('Atendente').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False)
    linhas_rank_atendentes = ""
    for i, (_, row) in enumerate(df_rank.iterrows()):
        nome_atend = formatar_nome_curto(row['Atendente'])
        qtd = row['Qtd']
        border = "border-bottom: 1px dashed #CBD5E1;" if i < (len(df_rank) - 1) else ""
        linhas_rank_atendentes += f"""
        <tr>
            <td style="padding: 8px 0; color: #475569; font-size: 12px; {border}">👤 {nome_atend}</td>
            <td align="right" style="padding: 8px 0; color: #0F172A; font-size: 13px; font-weight: 700; {border}">{qtd}</td>
        </tr>
        """
    if not linhas_rank_atendentes:
        linhas_rank_atendentes = '<tr><td style="padding: 8px 0; color: #475569; font-size: 12px;">Nenhum registro</td></tr>'

    corpo_html_gestao = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"></head>
    <body style="margin: 0; padding: 30px 10px; background-color: #F4F7F6; font-family: 'Segoe UI', Arial, sans-serif;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 650px; background-color: #FFFFFF; border-radius: 12px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden;">
            
            <tr>
                <td style="background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td width="50%" align="left" style="padding: 25px 30px;">
                                <img src="cid:logo_supra" height="35" alt="SupraMAIS" style="display: block;">
                            </td>
                            <td width="50%" align="right" style="padding: 25px 30px;">
                                <p style="color: #64748B; margin: 0; font-size: 13px; font-weight: bold; text-transform: uppercase;">Visão Gestão<br><span style="color: #94A3B8; font-size: 12px;">Ref. {data_formatada}</span></p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td style="padding: 40px 30px 20px 30px;">
                    <h2 style="color: #1E293B; margin: 0 0 10px 0; font-size: 24px;">Bom dia! ☀️</h2>
                    <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0;">
                        Segue a <strong>Daily</strong> consolidada da equipe referente ao dia {data_formatada}. Confira o volume total de entregas, o ranking de produtividade e os erros pendentes no sistema.
                    </p>
                </td>
            </tr>

            <tr>
                <td style="padding: 10px 30px 15px 30px;">
                    <h3 style="color: #0EA5E9; margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase;">📊 Resumo da Equipe (Dia)</h3>
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td width="31%" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center;">
                                <p style="color: #64748B; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Total de Chamados</p>
                                <p style="color: #0F172A; margin: 0; font-size: 28px; font-weight: bold;">{total_global_dia}</p>
                            </td>
                            <td width="3%"></td>
                            <td width="31%" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center;">
                                <p style="color: #64748B; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Atendentes Ativos</p>
                                <p style="color: #0F172A; margin: 0; font-size: 28px; font-weight: bold;">{atendentes_ativos}</p>
                            </td>
                            <td width="3%"></td>
                            <td width="32%" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center;">
                                <p style="color: #64748B; margin: 0 0 5px 0; font-size: 11px; font-weight: bold; text-transform: uppercase;">Resolução Inicial (FCR)</p>
                                <p style="color: #0F172A; margin: 0; font-size: 28px; font-weight: bold;">{fcr_equipe:.1f}%</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td style="padding: 30px;">
                    <h3 style="color: #334155; margin: 0 0 20px 0; font-size: 18px;">🔍 Raio-X Consolidado</h3>
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td width="48%" valign="top" style="background-color: #F8FAFC; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0;">
                                <p style="color: #8B5CF6; font-size: 12px; font-weight: bold; text-transform: uppercase; margin: 0 0 10px 0;">🏆 Ranking da Equipe</p>
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">{linhas_rank_atendentes}</table>
                            </td>
                            <td width="4%"></td>
                            <td width="48%" valign="top">
                                <div style="margin-bottom: 20px; background-color: #F8FAFC; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0;">
                                    <p style="color: #0EA5E9; font-size: 12px; font-weight: bold; text-transform: uppercase; margin: 0 0 10px 0;">🏢 Principais Clientes</p>
                                    <table width="100%" cellpadding="0" cellspacing="0" border="0">{html_clientes_geral}</table>
                                </div>
                                <div style="background-color: #F8FAFC; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0;">
                                    <p style="color: #0EA5E9; font-size: 12px; font-weight: bold; text-transform: uppercase; margin: 0 0 10px 0;">⚙️ Principais Módulos</p>
                                    <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 13px; line-height: 1.8;">{html_modulos_geral}</ul>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            {html_erros}

            <tr>
                <td style="background-color: #F1F5F9; padding: 25px 30px; text-align: center; border-top: 1px solid #E2E8F0;">
                    <p style="color: #64748B; font-size: 12px; margin: 0; line-height: 1.6;"><strong>Gestão de Suporte • SupraMAIS</strong></p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    for email_gestor in destinatarios_gestao:
        msg_root = MIMEMultipart('related')
        msg_root['From'] = EMAIL_REMETENTE
        msg_root['To'] = email_gestor
        msg_root['Subject'] = f"📈 Daily GESTÃO - Resumo da Equipe ({data_formatada})"
        
        msg_alt = MIMEMultipart('alternative')
        msg_root.attach(msg_alt)
        msg_html = MIMEText(corpo_html_gestao, 'html')
        msg_alt.attach(msg_html)
        anexar_imagem(msg_root, "logo_supra.png", "logo_supra")

        try:
            server.send_message(msg_root)
            print(f"Daily GESTAO enviada para: {email_gestor}")
            time.sleep(1)
        except Exception as e:
            print(f"Falha ao enviar Gestao para {email_gestor}: {e}")

    server.quit()
    print("Rotina de Dailys finalizada com sucesso!")

if __name__ == "__main__":
    enviar_relatorios_individuais()