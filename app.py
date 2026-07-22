# =============================================================================
# Dashboard de Chamados - ERP SupraMAIS
# Stack: Streamlit + pyodbc + pandas + plotly
# =============================================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pyodbc
import plotly.express as px
from datetime import date, datetime, timedelta
import os
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA E AUTO-REFRESH
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard SupraMAIS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

components.html(
    """
    <script>
        setTimeout(function() {
            window.parent.location.reload();
        }, 1800000);
    </script>
    """,
    height=0, width=0
)

# ── Paleta Supra ──
COR_SUPRA_VERMELHO = "#CC2020" 
COR_CINZA_ESCURO = "#3D3D3D"
COR_FUNDO_TELA = "#F8F9FA"
COR_BRANCA = "#FFFFFF"

st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }}
        .stApp {{ background-color: {COR_FUNDO_TELA}; }}
        header[data-testid="stHeader"] {{ background-color: transparent; }}
        section[data-testid="stSidebar"] {{ 
            background-color: {COR_BRANCA}; 
            border-right: 1px solid #EAEAEA;
        }}
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
            color: {COR_CINZA_ESCURO} !important;
        }}
        div.row-widget.stRadio > div {{
            background-color: #F1F1F1;
            padding: 10px;
            border-radius: 8px;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent;
            border-bottom: 1px solid #EAEAEA;
            gap: 20px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            border: none !important;
            padding-bottom: 10px !important;
            color: #888888 !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: transparent !important;
            color: {COR_SUPRA_VERMELHO} !important;
            border-bottom: 3px solid {COR_SUPRA_VERMELHO} !important;
            font-weight: bold !important;
        }}
        [data-testid="metric-container"] {{
            background: {COR_BRANCA};
            border-left: 4px solid {COR_SUPRA_VERMELHO};
            border-radius: 8px;
            padding: 10px 15px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #EAEAEA;
        }}
        [data-testid="stMetricValue"] {{ color: {COR_CINZA_ESCURO} !important; font-size: 1.8rem !important; }}
        h1, h2, h3, h4, p {{ color: {COR_CINZA_ESCURO} !important; margin-bottom: 0px; }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #CCCCCC; border-radius: 3px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DE CONEXÃO
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# QUERY SQL LENDO DIRETAMENTE DA VIEW
# ─────────────────────────────────────────────
SQL_QUERY = """
SELECT
    Sac,
    CONVERT(VARCHAR(10), Data_abertura, 103) AS Data_abertura,
    Dia_abertura,
    Mes_abertura,
    Ano_abertura,
    CONVERT(VARCHAR(10), [Data Solucao], 103) AS Data_Solucao,
    [Cliente Codigo] AS Cliente_Codigo,
    Cliente,
    Contato,
    Assunto,
    Motivo,
    Motivocodigo,
    Modulo,
    Situacao,
    Atendente,
    Origem,
    Finalizado_Mesmo_Dia,
    Tipo
FROM
    sgrp_atendimentos_geral
WHERE
    Ano_abertura >= 2020;
"""

@st.cache_data(ttl=1800, show_spinner="Carregando dados do banco…")
def carregar_dados() -> pd.DataFrame:
    # Agora as senhas virão do cofre seguro do Streamlit Cloud
    cfg = st.secrets["database"]
    
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['server']};DATABASE={cfg['database']};UID={cfg['username']};PWD={cfg['password']};"
    conn = pyodbc.connect(conn_str, timeout=30)
    
    SQL_QUERY = """
    SELECT
        Sac, CONVERT(VARCHAR(10), Data_abertura, 103) AS Data_abertura, Dia_abertura, Mes_abertura, Ano_abertura,
        CONVERT(VARCHAR(10), [Data Solucao], 103) AS Data_Solucao, [Cliente Codigo] AS Cliente_Codigo, Cliente, Contato,
        Assunto, Motivo, Motivocodigo, Modulo, Situacao, Atendente, Origem, Finalizado_Mesmo_Dia, Tipo
    FROM sgrp_atendimentos_geral
    WHERE Ano_abertura >= 2020;
    """
    
    df = pd.read_sql(SQL_QUERY, conn)
    conn.close()
    
    for col in ["Data_abertura", "Data_Solucao"]:
        df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")
    return df

# ─────────────────────────────────────────────
# PONTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────
def main():
    # ── Cabeçalho Principal ──
    col1, col2, col3 = st.columns([1, 4, 1], vertical_alignment="center")
    with col1:
        if os.path.exists("logo_supra.png"): st.image("logo_supra.png", width=110)
    with col2:
        st.markdown(
            f"<h3 style='text-align: center; margin-bottom: 0px;'>Dashboard de Chamados — SupraMAIS</h3>"
            f"<p style='text-align: center; font-size: 0.8em; color: gray;'>Última leitura do banco: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", 
            unsafe_allow_html=True
        )
    with col3:
        if os.path.exists("logo_supramais.png"): st.image("logo_supramais.png", width=60)
            
    st.markdown("<hr style='margin: 5px 0px 15px 0px;'>", unsafe_allow_html=True)

    try:
        df_raw = carregar_dados()
    except Exception as e:
        st.error(f"❌ **Erro ao conectar ao banco.** Detalhe: `{e}`")
        st.stop()

    if df_raw.empty:
        st.warning("⚠️ O banco de dados não retornou registros.")
        st.stop()

    # ── Menu de Navegação na Sidebar ──
    st.sidebar.markdown("## 🧭 Navegação")
    pagina_selecionada = st.sidebar.radio(
        "", 
        ["📊 Visão Geral", "🧑‍💻 Desempenho da Equipe", "🏢 Análise de Clientes"]
    )
    st.sidebar.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)

    # ── Filtros Laterais ──
    st.sidebar.markdown("## 🔍 Filtros")
    hoje = date.today()
    data_min = df_raw["Data_abertura"].min().date() if not df_raw.empty else hoje - timedelta(days=30)
    data_max = max(df_raw["Data_abertura"].max().date(), hoje)
    
    col_d1, col_d2 = st.sidebar.columns(2)
    data_inicial = col_d1.date_input("Data Inicial", value=hoje - timedelta(days=7), min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
    data_final = col_d2.date_input("Data Final", value=hoje, min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
    
    df = df_raw.copy()
    if data_inicial <= data_final:
        df = df[(df["Data_abertura"].dt.date >= data_inicial) & (df["Data_abertura"].dt.date <= data_final)]
    else:
        st.sidebar.error("⚠️ A data inicial não pode ser maior que a final.")

    atendentes = sorted(df["Atendente"].dropna().unique())
    sel_atendente = st.sidebar.multiselect("Atendente", atendentes, default=[], placeholder="Selecione...")
    if sel_atendente: df = df[df["Atendente"].isin(sel_atendente)]

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.info(f"🗄️ **{len(df):,}** registros filtrados")
    if st.sidebar.button("🔄 Atualizar banco de dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # ── KPIs Fixos no Topo ──
    mes_atual, ano_atual = hoje.month, hoje.year
    abertos_hoje = df_raw[df_raw["Data_abertura"].dt.date == hoje].shape[0]
    solucionados_hoje = df_raw[df_raw["Data_Solucao"].dt.date == hoje].shape[0]
    backlog = df_raw[df_raw["Data_Solucao"].isna()].shape[0]
    
    df_mes = df_raw[(df_raw["Mes_abertura"] == mes_atual) & (df_raw["Ano_abertura"] == ano_atual)]
    total_mes = len(df_mes)
    fcr = (df_mes["Finalizado_Mesmo_Dia"].sum() / total_mes * 100) if total_mes > 0 else 0

    cols = st.columns(5)
    cols[0].metric("📥 Abertos Hoje", abertos_hoje)
    cols[1].metric("✅ Solucionados Hoje", solucionados_hoje)
    cols[2].metric("⚡ FCR (Mês Atual)", f"{fcr:.1f}%")
    cols[3].metric("🗂️ Backlog (Em Aberto)", backlog)
    cols[4].metric("📊 Total Filtrado", len(df))
    
    st.markdown("<br>", unsafe_allow_html=True)

    cores_graficos = [COR_SUPRA_VERMELHO, COR_CINZA_ESCURO, "#E55050", "#777777", "#FF8888", "#444444", "#FFAAAA", "#222222", "#D3D3D3", "#999999"]

    # ─────────────────────────────────────────────
    # ROTEAMENTO DAS PÁGINAS
    # ─────────────────────────────────────────────
    
    # === PÁGINA 1: VISÃO GERAL ===
    if pagina_selecionada == "📊 Visão Geral":
        tab_geral, tab_tendencias = st.tabs(["Resumo de Volume", "📈 Tendências de Motivos"])
        
        with tab_geral:
            col_m, col_t, col_mod = st.columns(3)
            
            config_pizza = dict(
                height=320, 
                margin=dict(t=10, b=10, l=10, r=10), 
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            with col_m:
                st.markdown("##### 🎯 Top 5 Motivos")
                df_mot = df.groupby("Motivo").size().reset_index(name="Qtd").nlargest(5, "Qtd")
                if not df_mot.empty:
                    fig_mot = px.pie(df_mot, names="Motivo", values="Qtd", hole=0.45, color_discrete_sequence=cores_graficos)
                    fig_mot.update_layout(**config_pizza)
                    fig_mot.update_traces(textposition='inside', textinfo='percent', textfont_size=12)
                    st.plotly_chart(fig_mot, use_container_width=True)
                    
            with col_t:
                st.markdown("##### 📡 Top 5 Canais")
                df_orig = df.groupby("Origem").size().reset_index(name="Qtd").nlargest(5, "Qtd")
                if not df_orig.empty:
                    fig_orig = px.pie(df_orig, names="Origem", values="Qtd", hole=0.45, color_discrete_sequence=cores_graficos)
                    fig_orig.update_layout(**config_pizza)
                    fig_orig.update_traces(textposition='inside', textinfo='percent', textfont_size=12)
                    st.plotly_chart(fig_orig, use_container_width=True)
                    
            with col_mod:
                st.markdown("##### 🧩 Top 5 Módulos")
                df_mod = df.groupby("Modulo").size().reset_index(name="Qtd").nlargest(5, "Qtd")
                if not df_mod.empty:
                    fig_mod = px.pie(df_mod, names="Modulo", values="Qtd", hole=0.45, color_discrete_sequence=cores_graficos)
                    fig_mod.update_layout(**config_pizza)
                    fig_mod.update_traces(textposition='inside', textinfo='percent', textfont_size=12)
                    st.plotly_chart(fig_mod, use_container_width=True)

            st.markdown("<hr style='margin: 10px 0px 20px 0px;'>", unsafe_allow_html=True)

            st.markdown("##### 📅 Evolução Diária")
            df_dia = df.copy()
            df_dia["Data_Str"] = df_dia["Data_abertura"].dt.strftime("%d/%m/%Y") 
            contagem_dia = df_dia.groupby("Data_Str").size().reset_index(name="Quantidade")
            
            if not contagem_dia.empty:
                fig_dia = px.bar(contagem_dia, x="Data_Str", y="Quantidade", text="Quantidade")
                fig_dia.update_traces(marker_color=COR_SUPRA_VERMELHO, textposition="outside", cliponaxis=False)
                fig_dia.update_layout(
                    height=240, margin=dict(t=20, b=0, l=10, r=10), xaxis=dict(type='category', title=""), 
                    yaxis_title="Chamados", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_dia, use_container_width=True)

        with tab_tendencias:
            st.markdown("##### 📈 Tendência Mensal (Top 5 Motivos)")
            df_tend = df.copy()
            df_tend["MesAno"] = df_tend["Data_abertura"].dt.to_period("M").astype(str)
            df_tend = df_tend.dropna(subset=["Motivo", "MesAno"])
            
            top_motivos = df_tend.groupby("Motivo").size().nlargest(5).index.tolist()
            df_tend = df_tend[df_tend["Motivo"].isin(top_motivos)]
            contagem_tend = df_tend.groupby(["MesAno", "Motivo"]).size().reset_index(name="Qtd").sort_values("MesAno")
            
            if not contagem_tend.empty:
                fig_tend = px.line(contagem_tend, x="MesAno", y="Qtd", color="Motivo", markers=True, color_discrete_sequence=cores_graficos)
                fig_tend.update_layout(
                    height=400, xaxis_title="Mês/Ano", yaxis_title="Volume de Chamados",
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_tend, use_container_width=True)


    # === PÁGINA 2: DESEMPENHO DA EQUIPE ===
    elif pagina_selecionada == "🧑‍💻 Desempenho da Equipe":
        
        qtd_atendentes = df["Atendente"].nunique()
        altura_simples = max(300, qtd_atendentes * 35)
        altura_agrupada = max(400, qtd_atendentes * 50)

        # ── LINHA 1: SITUAÇÃO (FECHADOS VS ABERTOS) ──
        col_fechados, col_abertos = st.columns(2)
        
        with col_fechados:
            st.markdown("##### ✅ Chamados Resolvidos (Fechados)")
            df_fechados = df[df["Data_Solucao"].notna()].groupby("Atendente").size().reset_index(name="Qtd").sort_values("Qtd", ascending=True)
            if not df_fechados.empty:
                fig_fechados = px.bar(df_fechados, y="Atendente", x="Qtd", orientation="h", text="Qtd")
                fig_fechados.update_traces(marker_color=COR_SUPRA_VERMELHO, textposition="outside", cliponaxis=False)
                fig_fechados.update_layout(height=altura_simples, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="")
                st.plotly_chart(fig_fechados, use_container_width=True)

        with col_abertos:
            st.markdown("##### 📌 Chamados Pendentes (Em Aberto)")
            df_abertos = df[df["Data_Solucao"].isna()].groupby("Atendente").size().reset_index(name="Qtd").sort_values("Qtd", ascending=True)
            if not df_abertos.empty:
                fig_abertos = px.bar(df_abertos, y="Atendente", x="Qtd", orientation="h", text="Qtd")
                fig_abertos.update_traces(marker_color=COR_CINZA_ESCURO, textposition="outside", cliponaxis=False)
                fig_abertos.update_layout(height=altura_simples, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="")
                st.plotly_chart(fig_abertos, use_container_width=True)

        st.markdown("<hr style='margin: 15px 0px;'>", unsafe_allow_html=True)

        # ── LINHA 2: FCR E CANAL (GRUPADOS) ──
        col_fcr, col_canal = st.columns(2)
        
        with col_fcr:
            st.markdown("##### ⚡ FCR (Mesmo Dia) vs Outros Prazos")
            df_fcr = df.copy()
            df_fcr['Resolução'] = df_fcr['Finalizado_Mesmo_Dia'].apply(lambda x: 'Mesmo Dia' if x == 1 else 'Outros Prazos')
            df_fcr_grp = df_fcr.groupby(["Atendente", "Resolução"]).size().reset_index(name="Qtd")
            
            if not df_fcr_grp.empty:
                fig_fcr = px.bar(df_fcr_grp, y="Atendente", x="Qtd", color="Resolução", orientation="h", barmode="group",
                                 text="Qtd", color_discrete_map={'Mesmo Dia': COR_SUPRA_VERMELHO, 'Outros Prazos': COR_CINZA_ESCURO})
                fig_fcr.update_traces(textposition="outside", cliponaxis=False)
                fig_fcr.update_layout(height=altura_agrupada, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title=None, yaxis_title="")
                st.plotly_chart(fig_fcr, use_container_width=True)

        with col_canal:
            st.markdown("##### 📡 Canais de Atendimento (Origem)")
            df_canal = df.groupby(["Atendente", "Origem"]).size().reset_index(name="Qtd")
            
            if not df_canal.empty:
                fig_canal = px.bar(df_canal, y="Atendente", x="Qtd", color="Origem", orientation="h", barmode="group",
                                  text="Qtd", color_discrete_sequence=cores_graficos)
                fig_canal.update_traces(textposition="outside", cliponaxis=False)
                fig_canal.update_layout(height=altura_agrupada, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title=None, yaxis_title="")
                st.plotly_chart(fig_canal, use_container_width=True)

        st.markdown("<hr style='margin: 15px 0px;'>", unsafe_allow_html=True)

        # ── LINHA 3: MÓDULOS (MAPA DE CALOR) ──
        st.markdown("##### 🧩 Módulos Mais Acionados (Mapa de Calor)")
        top_5_modulos = df['Modulo'].value_counts().nlargest(5).index
        df_mod = df.copy()
        df_mod['Modulo_Ajustado'] = df_mod['Modulo'].apply(lambda x: x if x in top_5_modulos else 'Outros')
        df_mod_grp = df_mod.groupby(["Atendente", "Modulo_Ajustado"]).size().reset_index(name="Qtd")
        
        if not df_mod_grp.empty:
            df_matriz = df_mod_grp.pivot(index="Atendente", columns="Modulo_Ajustado", values="Qtd").fillna(0)
            fig_mod = px.imshow(
                df_matriz, text_auto=True, aspect="auto", 
                color_continuous_scale=[[0, "#EAEAEA"], [1, COR_SUPRA_VERMELHO]], labels=dict(color="Chamados")
            )
            fig_mod.update_layout(
                height=max(400, qtd_atendentes * 45), margin=dict(t=10, b=0, l=10, r=20), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title=""
            )
            fig_mod.update_coloraxes(showscale=False) 
            st.plotly_chart(fig_mod, use_container_width=True)

    # === PÁGINA 3: ANÁLISE DE CLIENTES ===
    elif pagina_selecionada == "🏢 Análise de Clientes":
        tab_top10, tab_raiox = st.tabs(["🏆 Top 10 Clientes Globais", "🔍 Raio-X do Cliente (Contatos)"])
        
        with tab_top10:
            df_top_clientes = df.groupby("Cliente").size().reset_index(name="Qtd").nlargest(10, "Qtd").sort_values("Qtd", ascending=True)
            top_10_lista = df_top_clientes["Cliente"].tolist()
            df_top_10_data = df[df["Cliente"].isin(top_10_lista)]
            
            # GRID 2x2 PARA REDUZIR A ROLAGEM VERTICAL
            col_vol, col_canal = st.columns(2)
            
            with col_vol:
                st.markdown("##### 🏆 Top 10 Volume Total")
                if not df_top_clientes.empty:
                    fig_cli = px.bar(df_top_clientes, y="Cliente", x="Qtd", orientation="h", text="Qtd")
                    fig_cli.update_traces(marker_color=COR_SUPRA_VERMELHO, textposition="outside", cliponaxis=False)
                    fig_cli.update_layout(height=320, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="", xaxis_title="")
                    st.plotly_chart(fig_cli, use_container_width=True)
                    
            with col_canal:
                st.markdown("##### 📡 Por Canal")
                df_cli_orig = df_top_10_data.groupby(["Cliente", "Origem"]).size().reset_index(name="Qtd")
                if not df_cli_orig.empty:
                    fig_cli_orig = px.bar(df_cli_orig, y="Cliente", x="Qtd", color="Origem", orientation="h", color_discrete_sequence=cores_graficos)
                    # Legenda movida para baixo para limpar o gráfico
                    fig_cli_orig.update_layout(height=320, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'}, yaxis_title="", xaxis_title="", legend_title="", legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_cli_orig, use_container_width=True)

            st.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)
            
            col_motivo, col_mod = st.columns(2)
            
            with col_motivo:
                st.markdown("##### 🎯 Por Motivo (Top 5)")
                # Limitar Motivos ao Top 5 para não estourar a legenda
                top_5_motivos = df_top_10_data['Motivo'].value_counts().nlargest(5).index
                df_mot_ajustado = df_top_10_data.copy()
                df_mot_ajustado['Motivo_Ajustado'] = df_mot_ajustado['Motivo'].apply(lambda x: x if x in top_5_motivos else 'Outros')
                df_cli_mot = df_mot_ajustado.groupby(["Cliente", "Motivo_Ajustado"]).size().reset_index(name="Qtd")
                
                if not df_cli_mot.empty:
                    fig_cli_mot = px.bar(df_cli_mot, y="Cliente", x="Qtd", color="Motivo_Ajustado", orientation="h", color_discrete_sequence=cores_graficos)
                    fig_cli_mot.update_layout(height=320, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'}, yaxis_title="", xaxis_title="", legend_title="", legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_cli_mot, use_container_width=True)

            with col_mod:
                st.markdown("##### 🧩 Por Módulo (Mapa de Calor Top 5)")
                # Substituído para Mapa de Calor focado no Top 5
                top_5_modulos = df_top_10_data['Modulo'].value_counts().nlargest(5).index
                df_mod_ajustado = df_top_10_data.copy()
                df_mod_ajustado['Modulo_Ajustado'] = df_mod_ajustado['Modulo'].apply(lambda x: x if x in top_5_modulos else 'Outros')
                df_cli_mod = df_mod_ajustado.groupby(["Cliente", "Modulo_Ajustado"]).size().reset_index(name="Qtd")
                
                if not df_cli_mod.empty:
                    df_matriz_cli = df_cli_mod.pivot(index="Cliente", columns="Modulo_Ajustado", values="Qtd").fillna(0)
                    ordem_clientes = df_top_clientes["Cliente"].tolist()
                    df_matriz_cli = df_matriz_cli.reindex(ordem_clientes)

                    fig_cli_mod = px.imshow(
                        df_matriz_cli, text_auto=True, aspect="auto", 
                        color_continuous_scale=[[0, "#EAEAEA"], [1, COR_SUPRA_VERMELHO]]
                    )
                    fig_cli_mod.update_layout(
                        height=320, margin=dict(t=10, b=0, l=10, r=20), 
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                        xaxis_title="", yaxis_title=""
                    )
                    fig_cli_mod.update_coloraxes(showscale=False) 
                    st.plotly_chart(fig_cli_mod, use_container_width=True)

        with tab_raiox:
            st.markdown("##### 🔍 Selecione um Cliente para Análise Detalhada")
            clientes_lista = sorted(df["Cliente"].dropna().unique())
            cliente_selecionado = st.selectbox("Selecione o Cliente:", clientes_lista, index=0 if clientes_lista else None)
            
            if cliente_selecionado:
                df_cli_esp = df[df["Cliente"] == cliente_selecionado]
                
                st.markdown(f"**Total de Chamados no período:** {len(df_cli_esp)}")
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    st.markdown("##### 🗣️ Top Contatos (Quem mais aciona o suporte)")
                    df_contatos = df_cli_esp.groupby("Contato").size().reset_index(name="Qtd").nlargest(10, "Qtd").sort_values("Qtd", ascending=True)
                    if not df_contatos.empty:
                        fig_cont = px.bar(df_contatos, y="Contato", x="Qtd", orientation="h", text="Qtd")
                        fig_cont.update_traces(marker_color=COR_CINZA_ESCURO, textposition="outside", cliponaxis=False)
                        fig_cont.update_layout(height=350, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="", xaxis_title="")
                        st.plotly_chart(fig_cont, use_container_width=True)
                        
                with col_c2:
                    st.markdown("##### 🧩 Módulos Mais Demandados")
                    df_mod_esp = df_cli_esp.groupby("Modulo").size().reset_index(name="Qtd").nlargest(10, "Qtd").sort_values("Qtd", ascending=True)
                    if not df_mod_esp.empty:
                        fig_mod_esp = px.bar(df_mod_esp, y="Modulo", x="Qtd", orientation="h", text="Qtd")
                        fig_mod_esp.update_traces(marker_color=COR_SUPRA_VERMELHO, textposition="outside", cliponaxis=False)
                        fig_mod_esp.update_layout(height=350, margin=dict(t=10, b=0, l=10, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="", xaxis_title="")
                        st.plotly_chart(fig_mod_esp, use_container_width=True)

if __name__ == "__main__":
    main()