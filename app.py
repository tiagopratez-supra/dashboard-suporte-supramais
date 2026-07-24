# =============================================================================
# BI Suporte SupraMAIS — Edição Avançada 2.0
# Stack: Streamlit + pyodbc + pandas + plotly
# SQL: INALTERADO — lê direto da view sgrp_atendimentos_geral
# =============================================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pyodbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import os, warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BI Suporte · SupraMAIS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
components.html('<script>setTimeout(()=>window.parent.location.reload(),1800000)</script>', height=0)

# ── PALETA ─────────────────────────────────────────────────────────────────────
RED    = "#CC2020"
DARK   = "#1A1A2E"
WHITE  = "#FFFFFF"
BG     = "#F0F2F6"
GREEN  = "#00B894"
ORANGE = "#E17055"
BLUE   = "#0984E3"
GOLD   = "#FDCB6E"
PURPLE = "#6C5CE7"
TEAL   = "#00CEC9"
GRAY1  = "#636E72"
GRAY2  = "#B2BEC3"
GRAY3  = "#DFE6E9"
CORES  = [RED, DARK, ORANGE, BLUE, GOLD, GREEN, PURPLE, TEAL, "#FD79A8", "#A29BFE"]

# ── CSS GLOBAL ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  * {{ font-family: 'Inter', sans-serif !important; }}
  .stApp {{ background: {BG} !important; }}
  .block-container {{ padding: 0.8rem 1.8rem 2rem !important; max-width: 100% !important; }}
  header[data-testid="stHeader"] {{ background: transparent !important; }}

  /* ── Sidebar escura ── */
  section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {DARK} 0%, #16213E 100%) !important;
    border-right: none !important;
  }}
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span {{
    color: {WHITE} !important;
  }}
  section[data-testid="stSidebar"] .stDateInput input {{
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: {WHITE} !important;
    border-radius: 8px !important;
  }}
  section[data-testid="stSidebar"] [data-baseweb="select"] {{
    background: rgba(255,255,255,0.1) !important;
  }}
  section[data-testid="stSidebar"] [data-baseweb="select"] * {{
    color: {WHITE} !important;
  }}
  section[data-testid="stSidebar"] .stButton button {{
    background: rgba(204,32,32,0.75) !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
  }}
  section[data-testid="stSidebar"] .stButton button:hover {{
    background: {RED} !important;
  }}
  div.row-widget.stRadio > div {{
    flex-direction: column; gap: 3px !important; background: transparent !important;
  }}
  div.row-widget.stRadio > div > label {{
    background: rgba(255,255,255,0.06) !important;
    border-radius: 10px !important; padding: 9px 14px !important;
    margin: 0 !important; font-size: 0.86rem !important;
    color: rgba(255,255,255,0.8) !important; border: 1px solid rgba(255,255,255,0.08) !important;
    transition: all 0.15s;
  }}
  div.row-widget.stRadio > div > label:hover {{
    background: rgba(204,32,32,0.2) !important;
  }}
  div.row-widget.stRadio > div > label[data-testid="stMarkdownContainer"],
  div.row-widget.stRadio [aria-checked="true"] > div > label {{
    background: rgba(204,32,32,0.35) !important;
    border-color: rgba(204,32,32,0.5) !important;
    color: {WHITE} !important;
  }}

  /* ── KPI Cards ── */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 18px; }}
  .kpi-card {{
    background: {WHITE}; border-radius: 14px; padding: 15px 16px 13px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07); border: 1px solid {GRAY3};
    position: relative; overflow: hidden; min-height: 105px;
  }}
  .kpi-top-bar {{
    position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 14px 14px 0 0;
  }}
  .kpi-icon {{ position: absolute; right: 13px; top: 13px; font-size: 1.6rem; opacity: 0.1; }}
  .kpi-label {{ font-size: 0.67rem; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; color: {GRAY1}; margin-bottom: 6px; }}
  .kpi-val {{ font-size: 1.9rem; font-weight: 800; color: {DARK}; line-height: 1; }}
  .kpi-sub {{ font-size: 0.68rem; color: {GRAY2}; margin-top: 5px; }}
  .kpi-badge {{
    display: inline-block; padding: 2px 7px; border-radius: 20px;
    font-size: 0.64rem; font-weight: 700; margin-top: 4px;
  }}
  .b-green {{ background: #D4F1EB; color: #00875A; }}
  .b-red   {{ background: #FDECEA; color: #C0392B; }}
  .b-gray  {{ background: {GRAY3}; color: {GRAY1}; }}
  .b-blue  {{ background: #E8F4FD; color: #0984E3; }}
  .b-gold  {{ background: #FEF9E7; color: #C8960C; }}

  /* ── Chart Wrapper ── */
  .chart-card {{
    background: {WHITE}; border-radius: 14px; padding: 16px 16px 8px;
    border: 1px solid {GRAY3}; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 14px;
  }}
  .chart-card-title {{
    font-size: 0.72rem; font-weight: 700; color: {GRAY1};
    text-transform: uppercase; letter-spacing: 0.5px;
    border-bottom: 1px solid {GRAY3}; padding-bottom: 8px; margin-bottom: 10px;
  }}

  /* ── Section title ── */
  .sec-title {{
    font-size: 0.72rem; font-weight: 700; color: {GRAY1};
    text-transform: uppercase; letter-spacing: 0.8px;
    border-left: 3px solid {RED}; padding-left: 9px;
    margin: 18px 0 12px; display: block;
  }}

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {{
    background: {GRAY3} !important; border-radius: 10px !important;
    padding: 3px !important; gap: 0 !important; border: none !important;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent !important; border: none !important;
    border-radius: 8px !important; color: {GRAY1} !important;
    font-weight: 500 !important; font-size: 0.82rem !important;
    padding: 5px 18px !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: {WHITE} !important; color: {RED} !important;
    font-weight: 700 !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
  }}

  /* ── Quadrant scatter ── */
  .quad-label {{
    font-size: 0.68rem; font-weight: 700; padding: 4px 9px;
    border-radius: 6px; position: absolute;
  }}

  /* ── Ranking ── */
  .rank-row {{
    display: flex; align-items: center; gap: 10px;
    padding: 7px 0; border-bottom: 1px solid {GRAY3};
  }}
  .rank-pos {{ font-size: 0.75rem; font-weight: 700; color: {GRAY2}; width: 22px; text-align: center; }}
  .rank-name {{ font-size: 0.82rem; color: {DARK}; flex: 1; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .rank-bar-bg {{ flex: 2; height: 5px; background: {GRAY3}; border-radius: 4px; overflow: hidden; }}
  .rank-bar-fill {{ height: 5px; border-radius: 4px; }}
  .rank-val {{ font-size: 0.82rem; font-weight: 700; min-width: 35px; text-align: right; }}
  .medal {{ font-size: 1rem; }}

  /* ── Pulse animation ── */
  @keyframes pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(0,184,148,.6); }}
    70%  {{ box-shadow: 0 0 0 7px rgba(0,184,148,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(0,184,148,0); }}
  }}
  .dot-live {{
    display: inline-block; width: 7px; height: 7px;
    background: {GREEN}; border-radius: 50%;
    animation: pulse 2s infinite; margin-right: 5px; vertical-align: middle;
  }}

  ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
  ::-webkit-scrollbar-thumb {{ background: {GRAY2}; border-radius: 4px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ────────────────────────────────────────────────────────────────────
def plotly_base(height=300, **kw):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=12, b=8, l=8, r=8), height=height,
        font=dict(family="Inter, sans-serif", color=GRAY1, size=11),
        **kw
    )

def card_open(title=""):
    t = f'<div class="chart-card-title">{title}</div>' if title else ""
    return f'<div class="chart-card">{t}'

def card_close():
    return '</div>'

def kpi_card(label, val, sub="", icon="📊", color=RED, badge="", badge_cls="b-gray"):
    badge_html = f'<span class="kpi-badge {badge_cls}">{badge}</span>' if badge else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-top-bar" style="background:{color}"></div>
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}</div>
      <div class="kpi-val">{val}</div>
      <div class="kpi-sub">{sub} {badge_html}</div>
    </div>"""

def ranking_html(df_rank, col_name, col_val, color=RED, max_val=None):
    medals = ["🥇", "🥈", "🥉"]
    rows = ""
    top = max_val or (df_rank[col_val].max() if not df_rank.empty else 1)
    for i, row in enumerate(df_rank.itertuples(), 1):
        pct = int(getattr(row, col_val) / top * 100) if top > 0 else 0
        medal = medals[i-1] if i <= 3 else f'<span class="rank-pos">{i}</span>'
        rows += f"""
        <div class="rank-row">
          <span class="medal">{medal}</span>
          <span class="rank-name">{getattr(row, col_name)}</span>
          <div class="rank-bar-bg"><div class="rank-bar-fill" style="width:{pct}%;background:{color}"></div></div>
          <span class="rank-val" style="color:{color}">{getattr(row, col_val):,}</span>
        </div>"""
    return rows


# ── SQL & CACHE (QUERY INALTERADA) ────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner="Carregando dados do banco…")
def carregar_dados() -> pd.DataFrame:
    cfg = st.secrets["database"]
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={cfg['server']};DATABASE={cfg['database']};"
        f"UID={cfg['username']};PWD={cfg['password']};"
    )
    conn = pyodbc.connect(conn_str, timeout=30)
    SQL_QUERY = """
    SELECT
        Sac, CONVERT(VARCHAR(10), Data_abertura, 103) AS Data_abertura,
        Dia_abertura, Mes_abertura, Ano_abertura,
        CONVERT(VARCHAR(10), [Data Solucao], 103) AS Data_Solucao,
        [Cliente Codigo] AS Cliente_Codigo, Cliente, Contato,
        Assunto, Motivo, Motivocodigo, Modulo, Situacao, Atendente, Origem,
        Finalizado_Mesmo_Dia, Tipo
    FROM sgrp_atendimentos_geral
    WHERE Ano_abertura >= 2020;
    """
    df = pd.read_sql(SQL_QUERY, conn)
    conn.close()
    for col in ["Data_abertura", "Data_Solucao"]:
        df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — PAINEL EXECUTIVO
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_executivo(df, df_raw, hoje):
    st.markdown('<span class="sec-title">📅 Análise Temporal</span>', unsafe_allow_html=True)
    tab_dia, tab_mes, tab_ano = st.tabs(["Visão Diária", "Visão Mensal", "Visão Anual"])

    # ── Tab: DIÁRIA ──────────────────────────────────────────────────────────
    with tab_dia:
        col_a, col_b = st.columns([2, 1])

        with col_a:
            st.markdown(card_open("📊 Volume Diário + Média Móvel 7 Dias"), unsafe_allow_html=True)
            df_dia = df.groupby(df["Data_abertura"].dt.date).size().reset_index(name="Qtd")
            df_dia.columns = ["Data", "Qtd"]
            df_dia = df_dia.sort_values("Data")
            df_dia["MM7"] = df_dia["Qtd"].rolling(7, min_periods=1).mean().round(1)

            fig = go.Figure()
            fig.add_bar(x=df_dia["Data"], y=df_dia["Qtd"], name="Chamados",
                        marker_color=RED, opacity=0.75, yaxis="y")
            fig.add_scatter(x=df_dia["Data"], y=df_dia["MM7"], mode="lines",
                            name="Média 7d", line=dict(color=BLUE, width=2.5), yaxis="y")
            fig.update_layout(**plotly_base(260, xaxis_title="", yaxis_title="",
                                            legend=dict(orientation="h", y=1.12, x=0),
                                            bargap=0.25))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        with col_b:
            st.markdown(card_open("🗓️ Distribuição Dia da Semana"), unsafe_allow_html=True)
            dias_pt = {0:"Seg",1:"Ter",2:"Qua",3:"Qui",4:"Sex",5:"Sáb",6:"Dom"}
            df["DiaSem"] = df["Data_abertura"].dt.dayofweek.map(dias_pt)
            ordem = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
            df_sem = df.groupby("DiaSem").size().reset_index(name="Qtd")
            df_sem["ord"] = df_sem["DiaSem"].map({d:i for i,d in enumerate(ordem)})
            df_sem = df_sem.sort_values("ord")

            fig2 = px.bar(df_sem, x="DiaSem", y="Qtd", text="Qtd",
                          color="Qtd", color_continuous_scale=[[0, GRAY3],[1, RED]])
            fig2.update_traces(textposition="outside", cliponaxis=False)
            fig2.update_coloraxes(showscale=False)
            fig2.update_layout(**plotly_base(260, xaxis_title="", yaxis_title="", xaxis=dict(categoryorder="array", categoryarray=ordem)))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        # Heatmap Calendário (GitHub-style)
        st.markdown(card_open("🔥 Mapa de Calor — Densidade de Chamados por Data"), unsafe_allow_html=True)
        df_cal = df.copy()
        df_cal = df_cal.dropna(subset=["Data_abertura"])
        df_cal["date"] = df_cal["Data_abertura"].dt.date
        df_cal["dow"] = df_cal["Data_abertura"].dt.dayofweek
        df_cal["week"] = df_cal["Data_abertura"].dt.isocalendar().week.astype(int)
        df_cal["year"] = df_cal["Data_abertura"].dt.year
        df_cal["yw"] = df_cal["year"].astype(str) + "-W" + df_cal["week"].astype(str).str.zfill(2)

        if not df_cal.empty:
            contagem_cal = df_cal.groupby(["yw", "dow"]).size().reset_index(name="Qtd")
            pivot_cal = contagem_cal.pivot(index="dow", columns="yw", values="Qtd").fillna(0)
            dias_labels = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
            pivot_cal.index = [dias_labels[i] if i < len(dias_labels) else i for i in pivot_cal.index]

            # Mostrar apenas últimas 26 semanas para não sobrecarregar
            colunas = sorted(pivot_cal.columns)[-26:]
            pivot_cal = pivot_cal[colunas]

            fig_cal = px.imshow(
                pivot_cal, aspect="auto",
                color_continuous_scale=[[0,"#F0F2F6"],[0.3,"#FFB3B3"],[1, RED]],
                labels=dict(color="Chamados"),
            )
            fig_cal.update_layout(**plotly_base(160,
                xaxis=dict(showticklabels=True, tickangle=-45, tickfont_size=9),
                yaxis=dict(showticklabels=True),
                coloraxis_showscale=False,
            ))
            fig_cal.update_traces(hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Chamados: %{z}<extra></extra>")
            st.plotly_chart(fig_cal, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    # ── Tab: MENSAL ──────────────────────────────────────────────────────────
    with tab_mes:
        df_men = df.copy()
        df_men["MesAno"] = df_men["Data_abertura"].dt.to_period("M").astype(str)
        df_men["AnoN"] = df_men["Data_abertura"].dt.year.astype(str)
        df_men["MesN"] = df_men["Data_abertura"].dt.month

        col_m1, col_m2 = st.columns([3, 2])
        with col_m1:
            st.markdown(card_open("📈 Evolução Mensal (Linha + Barras)"), unsafe_allow_html=True)
            cnt_men = df_men.groupby("MesAno").size().reset_index(name="Qtd").sort_values("MesAno")
            cnt_men["Delta"] = cnt_men["Qtd"].diff()
            cnt_men["Cor"] = cnt_men["Delta"].apply(lambda x: GREEN if (x is None or x <= 0) else RED)

            fig_m = go.Figure()
            fig_m.add_bar(x=cnt_men["MesAno"], y=cnt_men["Qtd"],
                          marker_color=[RED if d > 0 else GREEN for d in cnt_men["Delta"].fillna(0)],
                          name="Volume", opacity=0.7)
            fig_m.add_scatter(x=cnt_men["MesAno"], y=cnt_men["Qtd"], mode="lines+markers",
                              line=dict(color=DARK, width=2), marker=dict(size=5), name="Tendência")
            fig_m.update_layout(**plotly_base(260, xaxis_title="", yaxis_title="",
                                              legend=dict(orientation="h", y=1.12, x=0)))
            st.plotly_chart(fig_m, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        with col_m2:
            st.markdown(card_open("📊 Comparativo Ano a Ano por Mês"), unsafe_allow_html=True)
            meses_pt = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                        7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
            cnt_ym = df_men.groupby(["AnoN","MesN"]).size().reset_index(name="Qtd")
            cnt_ym["Mes_Label"] = cnt_ym["MesN"].map(meses_pt)
            cnt_ym = cnt_ym.sort_values(["AnoN","MesN"])

            fig_ym = px.line(cnt_ym, x="Mes_Label", y="Qtd", color="AnoN", markers=True,
                             color_discrete_sequence=CORES,
                             category_orders={"Mes_Label": list(meses_pt.values())})
            fig_ym.update_layout(**plotly_base(260, xaxis_title="", yaxis_title="",
                                               legend=dict(orientation="h", y=1.12, x=0, title="")))
            st.plotly_chart(fig_ym, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        # FCR mensal
        st.markdown(card_open("⚡ FCR (Finalizado Mesmo Dia) — Evolução Mensal"), unsafe_allow_html=True)
        df_fcr_men = df_men.groupby("MesAno").agg(Total=("Sac","count"), FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
        df_fcr_men["FCR_Pct"] = (df_fcr_men["FCR"] / df_fcr_men["Total"] * 100).round(1)
        df_fcr_men = df_fcr_men.sort_values("MesAno")

        fig_fcr_men = go.Figure()
        fig_fcr_men.add_bar(x=df_fcr_men["MesAno"], y=df_fcr_men["Total"],
                             name="Total Chamados", marker_color=GRAY3, yaxis="y")
        fig_fcr_men.add_scatter(x=df_fcr_men["MesAno"], y=df_fcr_men["FCR_Pct"],
                                mode="lines+markers+text", name="FCR %",
                                line=dict(color=GOLD, width=2.5), marker=dict(size=6),
                                text=df_fcr_men["FCR_Pct"].astype(str)+"%",
                                textposition="top center", textfont=dict(size=9, color=GOLD),
                                yaxis="y2")
        fig_fcr_men.add_hline(y=70, line_dash="dash", line_color=GREEN, opacity=0.5,
                               annotation_text="Meta 70%", annotation_position="top right",
                               yref="y2")
        fig_fcr_men.update_layout(**plotly_base(220,
            xaxis_title="", yaxis=dict(title="Chamados", showgrid=False),
            yaxis2=dict(title="FCR %", overlaying="y", side="right", range=[0,110],
                        showgrid=False, ticksuffix="%"),
            legend=dict(orientation="h", y=1.15, x=0),
        ))
        st.plotly_chart(fig_fcr_men, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    # ── Tab: ANUAL ───────────────────────────────────────────────────────────
    with tab_ano:
        col_a1, col_a2 = st.columns([1, 1])
        df_ano_g = df.groupby("Ano_abertura").agg(Total=("Sac","count"), FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
        df_ano_g["FCR_Pct"] = (df_ano_g["FCR"] / df_ano_g["Total"] * 100).round(1)
        df_ano_g["Ano_abertura"] = df_ano_g["Ano_abertura"].astype(str)

        with col_a1:
            st.markdown(card_open("📆 Total de Chamados por Ano"), unsafe_allow_html=True)
            fig_ya = px.bar(df_ano_g, x="Ano_abertura", y="Total", text="Total",
                            color="Total", color_continuous_scale=[[0,GRAY3],[1,RED]])
            fig_ya.update_traces(textposition="outside", cliponaxis=False)
            fig_ya.update_coloraxes(showscale=False)
            fig_ya.update_layout(**plotly_base(270, xaxis_title="", yaxis_title=""))
            st.plotly_chart(fig_ya, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        with col_a2:
            st.markdown(card_open("⚡ FCR % por Ano"), unsafe_allow_html=True)
            fig_yf = go.Figure()
            fig_yf.add_bar(x=df_ano_g["Ano_abertura"], y=df_ano_g["FCR_Pct"],
                           marker_color=[GREEN if v >= 70 else ORANGE for v in df_ano_g["FCR_Pct"]],
                           text=df_ano_g["FCR_Pct"].astype(str)+"%", textposition="outside")
            fig_yf.add_hline(y=70, line_dash="dash", line_color=RED, opacity=0.6,
                              annotation_text="Meta 70%")
            fig_yf.update_layout(**plotly_base(270, xaxis_title="", yaxis_title="FCR %",
                                               yaxis_range=[0, 110]))
            st.plotly_chart(fig_yf, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        # Sunburst geral Ano > Mês > Situação
        st.markdown(card_open("🌐 Hierarquia: Ano → Situação → Módulo (Top 5)"), unsafe_allow_html=True)
        df_sun = df.copy()
        df_sun["Ano_str"] = df_sun["Ano_abertura"].astype(str)
        top5_mod = df_sun["Modulo"].value_counts().nlargest(5).index
        df_sun["Modulo_s"] = df_sun["Modulo"].apply(lambda x: x if x in top5_mod else "Outros")
        df_sun_g = df_sun.groupby(["Ano_str", "Situacao", "Modulo_s"]).size().reset_index(name="Qtd")

        fig_sun = px.sunburst(df_sun_g, path=["Ano_str","Situacao","Modulo_s"], values="Qtd",
                              color_discrete_sequence=CORES)
        fig_sun.update_layout(**plotly_base(360))
        fig_sun.update_traces(textfont_size=11)
        st.plotly_chart(fig_sun, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — TIME DE SUPORTE
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_time(df):
    st.markdown('<span class="sec-title">👥 Desempenho Individual da Equipe</span>', unsafe_allow_html=True)

    # Quadrante de Eficiência
    col_q, col_rank = st.columns([3, 2])

    df_at = df.groupby("Atendente").agg(
        Total=("Sac","count"),
        FCR=("Finalizado_Mesmo_Dia","sum"),
        Abertos=("Data_Solucao", lambda x: x.isna().sum()),
    ).reset_index()
    df_at["FCR_Pct"] = (df_at["FCR"] / df_at["Total"] * 100).round(1)
    df_at = df_at[df_at["Total"] > 0]

    with col_q:
        st.markdown(card_open("🎯 Quadrante de Eficiência — Volume vs FCR%"), unsafe_allow_html=True)
        med_total = df_at["Total"].median()
        med_fcr   = df_at["FCR_Pct"].median()

        fig_q = go.Figure()
        # Quadrant fill areas
        max_total = df_at["Total"].max() * 1.2
        fig_q.add_shape(type="rect", x0=med_total, x1=max_total, y0=med_fcr, y1=110,
                        fillcolor="rgba(0,184,148,0.06)", line_width=0)
        fig_q.add_shape(type="rect", x0=0, x1=med_total, y0=med_fcr, y1=110,
                        fillcolor="rgba(9,132,227,0.06)", line_width=0)
        fig_q.add_shape(type="rect", x0=med_total, x1=max_total, y0=0, y1=med_fcr,
                        fillcolor="rgba(253,203,110,0.1)", line_width=0)
        fig_q.add_shape(type="rect", x0=0, x1=med_total, y0=0, y1=med_fcr,
                        fillcolor="rgba(225,112,85,0.07)", line_width=0)
        # Crosshair
        fig_q.add_vline(x=med_total, line_color=GRAY2, line_dash="dot", line_width=1.5)
        fig_q.add_hline(y=med_fcr,   line_color=GRAY2, line_dash="dot", line_width=1.5)

        fig_q.add_scatter(
            x=df_at["Total"], y=df_at["FCR_Pct"],
            mode="markers+text",
            text=df_at["Atendente"],
            textposition="top center",
            textfont=dict(size=10, color=DARK),
            marker=dict(size=df_at["Total"]**0.55 * 2.5, color=RED,
                        opacity=0.75, line=dict(color=WHITE, width=1.5)),
            hovertemplate="<b>%{text}</b><br>Chamados: %{x}<br>FCR: %{y:.1f}%<extra></extra>",
        )
        # Quadrant labels
        fig_q.add_annotation(x=max_total*0.97, y=107, text="⭐ Alta Eficiência",
                              showarrow=False, font=dict(size=9, color=GREEN), xanchor="right")
        fig_q.add_annotation(x=max_total*0.03, y=107, text="🧘 Baixo Volume / Boa FCR",
                              showarrow=False, font=dict(size=9, color=BLUE), xanchor="left")
        fig_q.add_annotation(x=max_total*0.97, y=med_fcr*0.15, text="🔥 Volume Alto / FCR Baixa",
                              showarrow=False, font=dict(size=9, color=ORANGE), xanchor="right")
        fig_q.add_annotation(x=max_total*0.03, y=med_fcr*0.15, text="⚠️ Atenção",
                              showarrow=False, font=dict(size=9, color=RED), xanchor="left")

        fig_q.update_layout(**plotly_base(320,
            xaxis=dict(title="Total de Chamados", zeroline=False, showgrid=False),
            yaxis=dict(title="FCR %", zeroline=False, showgrid=False, range=[0,110]),
        ))
        st.plotly_chart(fig_q, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_rank:
        st.markdown(card_open("🏆 Ranking de Chamados por Atendente"), unsafe_allow_html=True)
        df_rank = df_at.sort_values("Total", ascending=False).head(15)
        html_rank = ranking_html(df_rank, "Atendente", "Total", RED)
        st.markdown(html_rank, unsafe_allow_html=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    st.markdown('<span class="sec-title">📊 Análise Detalhada</span>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown(card_open("✅ Resolvidos vs 📌 Em Aberto — por Atendente"), unsafe_allow_html=True)
        df_sit_at = df.copy()
        df_sit_at["Status"] = df_sit_at["Data_Solucao"].apply(lambda x: "Resolvido" if pd.notna(x) else "Em Aberto")
        df_grp = df_sit_at.groupby(["Atendente","Status"]).size().reset_index(name="Qtd")
        df_grp = df_grp.sort_values("Qtd", ascending=False)

        qtd_at = df["Atendente"].nunique()
        fig_st = px.bar(df_grp, y="Atendente", x="Qtd", color="Status", orientation="h",
                        barmode="stack", text="Qtd",
                        color_discrete_map={"Resolvido": GREEN, "Em Aberto": RED},
                        category_orders={"Atendente": df_at.sort_values("Total", ascending=False)["Atendente"].tolist()})
        fig_st.update_traces(textposition="inside", textfont_size=9, cliponaxis=False)
        fig_st.update_layout(**plotly_base(max(280, qtd_at*34),
                                           yaxis_title="", xaxis_title="",
                                           legend=dict(orientation="h", y=1.1, x=0, title="")))
        st.plotly_chart(fig_st, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_s2:
        st.markdown(card_open("📡 Canal de Entrada (Origem) — por Atendente"), unsafe_allow_html=True)
        df_orig_at = df.groupby(["Atendente","Origem"]).size().reset_index(name="Qtd")
        fig_orig = px.bar(df_orig_at, y="Atendente", x="Qtd", color="Origem", orientation="h",
                          barmode="stack", text="Qtd", color_discrete_sequence=CORES,
                          category_orders={"Atendente": df_at.sort_values("Total", ascending=False)["Atendente"].tolist()})
        fig_orig.update_traces(textposition="inside", textfont_size=9, cliponaxis=False)
        fig_orig.update_layout(**plotly_base(max(280, qtd_at*34),
                                              yaxis_title="", xaxis_title="",
                                              legend=dict(orientation="h", y=1.1, x=0, title="")))
        st.plotly_chart(fig_orig, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    # Heatmap atendente × módulo
    st.markdown(card_open("🧩 Mapa de Calor — Atendente × Módulo"), unsafe_allow_html=True)
    top5_mod = df["Modulo"].value_counts().nlargest(6).index
    df_hm = df.copy()
    df_hm["Modulo_x"] = df_hm["Modulo"].apply(lambda x: x if x in top5_mod else "Outros")
    df_hm_g = df_hm.groupby(["Atendente","Modulo_x"]).size().reset_index(name="Qtd")
    df_piv = df_hm_g.pivot(index="Atendente", columns="Modulo_x", values="Qtd").fillna(0)

    fig_hm = px.imshow(df_piv, text_auto=True, aspect="auto",
                       color_continuous_scale=[[0, GRAY3],[0.5, "#FFB3B3"],[1, RED]])
    fig_hm.update_coloraxes(showscale=False)
    fig_hm.update_layout(**plotly_base(max(300, df_piv.shape[0]*40),
                                        xaxis_title="", yaxis_title=""))
    st.plotly_chart(fig_hm, use_container_width=True)
    st.markdown(card_close(), unsafe_allow_html=True)

    # FCR gauge por atendente
    st.markdown('<span class="sec-title">⚡ FCR — Finalização no Mesmo Dia</span>', unsafe_allow_html=True)
    st.markdown(card_open(""), unsafe_allow_html=True)
    df_fcr_at = df_at[["Atendente","FCR_Pct","Total"]].sort_values("FCR_Pct", ascending=False)
    n_at = len(df_fcr_at)
    colunas_gauge = st.columns(min(n_at, 5))
    for i, (_, row) in enumerate(df_fcr_at.iterrows()):
        if i >= 5: break
        cor = GREEN if row["FCR_Pct"] >= 70 else (ORANGE if row["FCR_Pct"] >= 50 else RED)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row["FCR_Pct"],
            number=dict(suffix="%", font=dict(size=18, color=cor)),
            title=dict(text=row["Atendente"].split()[0], font=dict(size=10, color=GRAY1)),
            gauge=dict(
                axis=dict(range=[0,100], tickwidth=0, tickcolor="transparent"),
                bar=dict(color=cor, thickness=0.22),
                bgcolor=GRAY3, borderwidth=0,
                steps=[dict(range=[0,70], color=GRAY3), dict(range=[70,100], color="#D4F1EB")],
                threshold=dict(line=dict(color=GREEN, width=2), thickness=0.75, value=70),
            ),
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10, l=10, r=10), height=160)
        colunas_gauge[i].plotly_chart(fig_g, use_container_width=True)
    st.markdown(card_close(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — SITUAÇÃO DOS CHAMADOS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_situacao(df):
    st.markdown('<span class="sec-title">🎫 Pipeline e Situação dos Chamados</span>', unsafe_allow_html=True)

    col_f, col_tipo, col_mot = st.columns([1, 1, 2])

    with col_f:
        st.markdown(card_open("📊 Funil — Situações"), unsafe_allow_html=True)
        df_sit = df.groupby("Situacao").size().reset_index(name="Qtd").sort_values("Qtd", ascending=False)
        fig_fun = go.Figure(go.Funnel(
            y=df_sit["Situacao"], x=df_sit["Qtd"],
            textposition="inside", textinfo="value+percent initial",
            marker=dict(color=CORES[:len(df_sit)]),
        ))
        fig_fun.update_layout(**plotly_base(320))
        st.plotly_chart(fig_fun, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_tipo:
        st.markdown(card_open("📁 Tipo de Chamado"), unsafe_allow_html=True)
        df_tipo = df.groupby("Tipo").size().reset_index(name="Qtd")
        fig_tipo = px.pie(df_tipo, names="Tipo", values="Qtd", hole=0.52,
                          color_discrete_sequence=CORES)
        fig_tipo.update_traces(textposition="inside", textinfo="percent+label",
                                textfont_size=11)
        fig_tipo.update_layout(**plotly_base(320, showlegend=False))
        st.plotly_chart(fig_tipo, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_mot:
        st.markdown(card_open("🎯 Treemap — Motivos por Volume"), unsafe_allow_html=True)
        df_mot = df.groupby("Motivo").size().reset_index(name="Qtd").nlargest(20, "Qtd")
        fig_tree_mot = px.treemap(df_mot, path=["Motivo"], values="Qtd",
                                   color="Qtd",
                                   color_continuous_scale=[[0, GRAY3],[0.5,"#FFB3B3"],[1, RED]])
        fig_tree_mot.update_coloraxes(showscale=False)
        fig_tree_mot.update_traces(textfont_size=12)
        fig_tree_mot.update_layout(**plotly_base(320))
        st.plotly_chart(fig_tree_mot, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    # Tendência de situações ao longo do tempo
    st.markdown(card_open("📈 Tendência de Situações — Mensal"), unsafe_allow_html=True)
    df_tend_sit = df.copy()
    df_tend_sit["MesAno"] = df_tend_sit["Data_abertura"].dt.to_period("M").astype(str)
    top_sits = df_tend_sit["Situacao"].value_counts().nlargest(5).index
    df_tend_sit["Situacao_f"] = df_tend_sit["Situacao"].apply(lambda x: x if x in top_sits else "Outras")
    df_ts = df_tend_sit.groupby(["MesAno","Situacao_f"]).size().reset_index(name="Qtd").sort_values("MesAno")
    fig_ts = px.area(df_ts, x="MesAno", y="Qtd", color="Situacao_f",
                     color_discrete_sequence=CORES, markers=False)
    fig_ts.update_layout(**plotly_base(250, xaxis_title="", yaxis_title="",
                                        legend=dict(orientation="h", y=1.12, x=0, title="")))
    st.plotly_chart(fig_ts, use_container_width=True)
    st.markdown(card_close(), unsafe_allow_html=True)

    # Backlog aging: estimativa de chamados abertos por tempo
    df_backlog = df[df["Data_Solucao"].isna()].copy()
    if not df_backlog.empty:
        hoje = date.today()
        df_backlog["Dias_Aberto"] = (pd.Timestamp(hoje) - df_backlog["Data_abertura"]).dt.days.clip(lower=0)
        df_backlog["Faixa"] = pd.cut(df_backlog["Dias_Aberto"],
                                      bins=[-1, 3, 7, 15, 30, 60, 9999],
                                      labels=["0-3d","4-7d","8-15d","16-30d","31-60d","60d+"])
        df_aging = df_backlog.groupby("Faixa", observed=True).size().reset_index(name="Qtd")

        st.markdown(card_open("⏳ Backlog Aging — Chamados Em Aberto por Faixa de Tempo"), unsafe_allow_html=True)
        cores_aging = [GREEN, GOLD, ORANGE, RED, "#8E1010", "#5D0000"]
        fig_aging = px.bar(df_aging, x="Faixa", y="Qtd", text="Qtd",
                            color="Faixa",
                            color_discrete_sequence=cores_aging)
        fig_aging.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
        fig_aging.update_layout(**plotly_base(230, xaxis_title="Tempo em aberto", yaxis_title="Qtd"))
        st.plotly_chart(fig_aging, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — CLIENTES & CONTATOS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_clientes(df):
    st.markdown('<span class="sec-title">🏢 Análise de Clientes</span>', unsafe_allow_html=True)

    tab_top, col_raiox = st.tabs(["🏆 Top Clientes", "🔍 Raio-X do Cliente"])

    with tab_top:
        col_t1, col_t2 = st.columns([3, 2])

        with col_t1:
            st.markdown(card_open("📦 Treemap — Top Clientes por Volume"), unsafe_allow_html=True)
            df_cli = df.groupby("Cliente").size().reset_index(name="Qtd").nlargest(25, "Qtd")
            fig_tree = px.treemap(df_cli, path=["Cliente"], values="Qtd",
                                   color="Qtd",
                                   color_continuous_scale=[[0, GRAY3],[0.4,"#FFB3B3"],[1, RED]])
            fig_tree.update_coloraxes(showscale=False)
            fig_tree.update_traces(textfont_size=11)
            fig_tree.update_layout(**plotly_base(340))
            st.plotly_chart(fig_tree, use_container_width=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        with col_t2:
            st.markdown(card_open("🏆 Ranking Top 15 Clientes"), unsafe_allow_html=True)
            df_rank_cli = df.groupby("Cliente").size().reset_index(name="Total").sort_values("Total", ascending=False).head(15)
            html_r = ranking_html(df_rank_cli, "Cliente", "Total", RED)
            st.markdown(html_r, unsafe_allow_html=True)
            st.markdown(card_close(), unsafe_allow_html=True)

        st.markdown(card_open("🌐 Sunburst — Cliente → Módulo → Situação (Top 10 Clientes)"), unsafe_allow_html=True)
        top10_cli = df.groupby("Cliente").size().nlargest(10).index
        df_sun_cli = df[df["Cliente"].isin(top10_cli)].copy()
        top5_mod = df_sun_cli["Modulo"].value_counts().nlargest(5).index
        df_sun_cli["Modulo_s"] = df_sun_cli["Modulo"].apply(lambda x: x if x in top5_mod else "Outros")
        df_sun_g = df_sun_cli.groupby(["Cliente","Modulo_s","Situacao"]).size().reset_index(name="Qtd")

        fig_sun_cli = px.sunburst(df_sun_g, path=["Cliente","Modulo_s","Situacao"],
                                   values="Qtd", color_discrete_sequence=CORES)
        fig_sun_cli.update_layout(**plotly_base(400))
        fig_sun_cli.update_traces(textfont_size=10)
        st.plotly_chart(fig_sun_cli, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_raiox:
        st.markdown(card_open("🔍 Raio-X do Cliente"), unsafe_allow_html=True)
        clientes_lista = sorted(df["Cliente"].dropna().unique())
        cliente_sel = st.selectbox("Selecione o Cliente:", clientes_lista,
                                    index=0 if clientes_lista else None,
                                    label_visibility="collapsed")
        if cliente_sel:
            df_ce = df[df["Cliente"] == cliente_sel]
            total_ce = len(df_ce)
            fcr_ce = df_ce["Finalizado_Mesmo_Dia"].sum() / total_ce * 100 if total_ce > 0 else 0
            abertos_ce = df_ce["Data_Solucao"].isna().sum()

            st.markdown(f"""
            <div style="display:flex;gap:12px;margin-bottom:12px">
              <div class="kpi-card" style="flex:1">
                <div class="kpi-top-bar" style="background:{RED}"></div>
                <div class="kpi-label">Total Chamados</div>
                <div class="kpi-val">{total_ce:,}</div>
              </div>
              <div class="kpi-card" style="flex:1">
                <div class="kpi-top-bar" style="background:{GOLD}"></div>
                <div class="kpi-label">FCR %</div>
                <div class="kpi-val">{fcr_ce:.1f}%</div>
              </div>
              <div class="kpi-card" style="flex:1">
                <div class="kpi-top-bar" style="background:{ORANGE}"></div>
                <div class="kpi-label">Em Aberto</div>
                <div class="kpi-val">{abertos_ce:,}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("**Top Contatos**")
                df_cont = df_ce.groupby("Contato").size().reset_index(name="Qtd").nlargest(10,"Qtd").sort_values("Qtd")
                fig_cont = px.bar(df_cont, y="Contato", x="Qtd", orientation="h", text="Qtd")
                fig_cont.update_traces(marker_color=DARK, textposition="outside", cliponaxis=False)
                fig_cont.update_layout(**plotly_base(260, xaxis_title="", yaxis_title=""))
                st.plotly_chart(fig_cont, use_container_width=True)

            with col_r2:
                st.markdown("**Módulos Demandados**")
                df_mod_ce = df_ce.groupby("Modulo").size().reset_index(name="Qtd").nlargest(10,"Qtd").sort_values("Qtd")
                fig_mod_ce = px.bar(df_mod_ce, y="Modulo", x="Qtd", orientation="h", text="Qtd")
                fig_mod_ce.update_traces(marker_color=RED, textposition="outside", cliponaxis=False)
                fig_mod_ce.update_layout(**plotly_base(260, xaxis_title="", yaxis_title=""))
                st.plotly_chart(fig_mod_ce, use_container_width=True)

            st.markdown("**Origem dos Contatos**")
            df_orig_ce = df_ce.groupby("Origem").size().reset_index(name="Qtd")
            fig_orig_ce = px.pie(df_orig_ce, names="Origem", values="Qtd", hole=0.5,
                                  color_discrete_sequence=CORES)
            fig_orig_ce.update_traces(textposition="inside", textinfo="percent+label")
            fig_orig_ce.update_layout(**plotly_base(200, showlegend=False))
            st.plotly_chart(fig_orig_ce, use_container_width=True)

        st.markdown(card_close(), unsafe_allow_html=True)

    # Top contatos globais
    st.markdown('<span class="sec-title">🗣️ Top Contatos Globais</span>', unsafe_allow_html=True)
    col_cont1, col_cont2 = st.columns([2, 3])
    with col_cont1:
        st.markdown(card_open("🏆 Top 15 Contatos que Mais Acionaram o Suporte"), unsafe_allow_html=True)
        df_rank_cont = df.groupby("Contato").size().reset_index(name="Total").sort_values("Total", ascending=False).head(15)
        html_rc = ranking_html(df_rank_cont, "Contato", "Total", BLUE)
        st.markdown(html_rc, unsafe_allow_html=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_cont2:
        st.markdown(card_open("🔥 Treemap — Contatos por Volume de Chamados"), unsafe_allow_html=True)
        df_cont_tree = df.groupby(["Cliente","Contato"]).size().reset_index(name="Qtd").nlargest(30, "Qtd")
        fig_cont_tree = px.treemap(df_cont_tree, path=["Cliente","Contato"], values="Qtd",
                                    color="Qtd",
                                    color_continuous_scale=[[0, GRAY3],[0.4,"#B3D4FF"],[1, BLUE]])
        fig_cont_tree.update_coloraxes(showscale=False)
        fig_cont_tree.update_traces(textfont_size=10)
        fig_cont_tree.update_layout(**plotly_base(340))
        st.plotly_chart(fig_cont_tree, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 5 — MÓDULOS & ORIGENS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_modulos(df):
    st.markdown('<span class="sec-title">🧩 Módulos & Canais de Entrada</span>', unsafe_allow_html=True)

    col_tree, col_orig = st.columns([3, 2])

    with col_tree:
        st.markdown(card_open("🧩 Treemap — Módulos por Demanda"), unsafe_allow_html=True)
        df_mod = df.groupby("Modulo").size().reset_index(name="Qtd").sort_values("Qtd", ascending=False)
        fig_tree_m = px.treemap(df_mod, path=["Modulo"], values="Qtd",
                                 color="Qtd",
                                 color_continuous_scale=[[0, GRAY3],[0.4,"#FFB3B3"],[1, RED]])
        fig_tree_m.update_coloraxes(showscale=False)
        fig_tree_m.update_traces(textfont_size=11)
        fig_tree_m.update_layout(**plotly_base(340))
        st.plotly_chart(fig_tree_m, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    with col_orig:
        st.markdown(card_open("📡 Origem dos Contatos"), unsafe_allow_html=True)
        df_or = df.groupby("Origem").size().reset_index(name="Qtd").sort_values("Qtd", ascending=False)
        fig_or = px.pie(df_or, names="Origem", values="Qtd", hole=0.55,
                         color_discrete_sequence=CORES)
        fig_or.update_traces(textposition="outside", textinfo="label+percent",
                              textfont_size=11, pull=[0.05]*len(df_or))
        fig_or.update_layout(**plotly_base(340, showlegend=False))
        st.plotly_chart(fig_or, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

    # Sankey: Origem → Módulo → Situação
    st.markdown(card_open("🔀 Fluxo Sankey — Origem → Módulo → Situação"), unsafe_allow_html=True)
    try:
        top5_orig = df["Origem"].value_counts().nlargest(5).index.tolist()
        top5_mod  = df["Modulo"].value_counts().nlargest(5).index.tolist()
        top5_sit  = df["Situacao"].value_counts().nlargest(4).index.tolist()

        df_sk = df[
            df["Origem"].isin(top5_orig) &
            df["Modulo"].isin(top5_mod) &
            df["Situacao"].isin(top5_sit)
        ].copy()

        all_nodes = top5_orig + top5_mod + top5_sit
        node_idx  = {n: i for i, n in enumerate(all_nodes)}

        links_om = df_sk.groupby(["Origem","Modulo"]).size().reset_index(name="v")
        links_ms = df_sk.groupby(["Modulo","Situacao"]).size().reset_index(name="v")

        src, tgt, val = [], [], []
        for _, r in links_om.iterrows():
            if r["Origem"] in node_idx and r["Modulo"] in node_idx:
                src.append(node_idx[r["Origem"]])
                tgt.append(node_idx[r["Modulo"]])
                val.append(r["v"])
        for _, r in links_ms.iterrows():
            if r["Modulo"] in node_idx and r["Situacao"] in node_idx:
                src.append(node_idx[r["Modulo"]])
                tgt.append(node_idx[r["Situacao"]])
                val.append(r["v"])

        node_colors = (
            [BLUE]*len(top5_orig) +
            [RED]*len(top5_mod) +
            [GREEN]*len(top5_sit)
        )

        fig_sk = go.Figure(go.Sankey(
            node=dict(
                pad=18, thickness=18,
                line=dict(color=WHITE, width=0.5),
                label=all_nodes, color=node_colors,
            ),
            link=dict(source=src, target=tgt, value=val, color="rgba(180,180,180,0.3)"),
        ))
        fig_sk.update_layout(**plotly_base(360))
        st.plotly_chart(fig_sk, use_container_width=True)
    except Exception as e:
        st.caption(f"Sankey indisponível: {e}")
    st.markdown(card_close(), unsafe_allow_html=True)

    # Heatmap Módulo × Mês (Sazonalidade)
    st.markdown(card_open("🌡️ Sazonalidade — Módulo × Mês do Ano"), unsafe_allow_html=True)
    meses_pt = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    df_saz = df.copy()
    df_saz["MesN"] = df_saz["Data_abertura"].dt.month
    df_saz["Mes_label"] = df_saz["MesN"].map(meses_pt)
    top8_mod = df_saz["Modulo"].value_counts().nlargest(8).index
    df_saz_f = df_saz[df_saz["Modulo"].isin(top8_mod)]
    df_saz_g = df_saz_f.groupby(["Modulo","Mes_label"]).size().reset_index(name="Qtd")
    df_piv_saz = df_saz_g.pivot(index="Modulo", columns="Mes_label", values="Qtd").fillna(0)
    col_order = [m for m in list(meses_pt.values()) if m in df_piv_saz.columns]
    df_piv_saz = df_piv_saz[col_order]

    fig_saz = px.imshow(df_piv_saz, text_auto=True, aspect="auto",
                         color_continuous_scale=[[0, GRAY3],[0.5,"#FFD3B3"],[1, ORANGE]])
    fig_saz.update_coloraxes(showscale=False)
    fig_saz.update_layout(**plotly_base(max(280, len(top8_mod)*40),
                                         xaxis_title="", yaxis_title=""))
    st.plotly_chart(fig_saz, use_container_width=True)
    st.markdown(card_close(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    hoje = date.today()

    # ── HEADER ────────────────────────────────────────────────────────────────
    col_logo1, col_title, col_logo2 = st.columns([1, 5, 1], vertical_alignment="center")
    with col_logo1:
        if os.path.exists("logo_supra.png"):
            st.image("logo_supra.png", width=110)
    with col_title:
        st.markdown(f"""
        <div style="text-align:center;padding:6px 0">
          <div style="font-size:1.25rem;font-weight:800;color:{DARK};letter-spacing:-0.3px">
            Central de Inteligência de Suporte — SupraMAIS
          </div>
          <div style="font-size:0.74rem;color:{GRAY1};margin-top:3px">
            <span class="dot-live"></span>
            Dados em tempo real &nbsp;·&nbsp; Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_logo2:
        if os.path.exists("logo_supramais.png"):
            st.image("logo_supramais.png", width=60)

    st.markdown(f"<hr style='margin:8px 0 14px;border:none;border-top:1px solid {GRAY3}'>",
                unsafe_allow_html=True)

    # ── CARREGAR DADOS ────────────────────────────────────────────────────────
    try:
        df_raw = carregar_dados()
    except Exception as e:
        st.error(f"❌ **Erro ao conectar ao banco.** Detalhe: `{e}`")
        st.stop()

    if df_raw.empty:
        st.warning("⚠️ Nenhum registro retornado.")
        st.stop()

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"<div style='padding:8px 0 16px'><span style='font-size:1.1rem;font-weight:700'>🎯 BI Suporte</span></div>",
                    unsafe_allow_html=True)
        pagina = st.radio("Navegação", [
            "📊 Painel Executivo",
            "👥 Time de Suporte",
            "🎫 Situação dos Chamados",
            "🏢 Clientes & Contatos",
            "🧩 Módulos & Origens",
        ], label_visibility="collapsed")

        st.markdown(f"<hr style='border-color:rgba(255,255,255,0.12);margin:12px 0'>",
                    unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem;font-weight:700;opacity:0.7'>🔍 FILTROS</span>",
                    unsafe_allow_html=True)

        data_min = df_raw["Data_abertura"].dropna().min().date()
        data_max = max(df_raw["Data_abertura"].dropna().max().date(), hoje)

        col_d1, col_d2 = st.columns(2)
        di = col_d1.date_input("De", value=hoje-timedelta(days=30),
                                min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
        df_ = col_d2.date_input("Até", value=hoje,
                                  min_value=data_min, max_value=data_max, format="DD/MM/YYYY")

        atendentes = sorted(df_raw["Atendente"].dropna().unique())
        sel_at = st.multiselect("Atendente", atendentes, placeholder="Todos os atendentes")

        situacoes = sorted(df_raw["Situacao"].dropna().unique())
        sel_sit = st.multiselect("Situação", situacoes, placeholder="Todas as situações")

        origens = sorted(df_raw["Origem"].dropna().unique())
        sel_or = st.multiselect("Origem", origens, placeholder="Todas as origens")

        st.markdown(f"<hr style='border-color:rgba(255,255,255,0.12);margin:12px 0'>",
                    unsafe_allow_html=True)
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        # Aplicar filtros
        df = df_raw.copy()
        if di <= df_:
            df = df[(df["Data_abertura"].dt.date >= di) & (df["Data_abertura"].dt.date <= df_)]
        else:
            st.error("Data inicial > data final")

        if sel_at:  df = df[df["Atendente"].isin(sel_at)]
        if sel_sit: df = df[df["Situacao"].isin(sel_sit)]
        if sel_or:  df = df[df["Origem"].isin(sel_or)]

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.08);border-radius:10px;padding:10px 14px;margin-top:6px">
          <div style="font-size:0.7rem;opacity:0.6;margin-bottom:2px">REGISTROS FILTRADOS</div>
          <div style="font-size:1.4rem;font-weight:800;color:{WHITE}">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPI STRIP ─────────────────────────────────────────────────────────────
    mes_atual, ano_atual = hoje.month, hoje.year
    df_mes  = df_raw[(df_raw["Mes_abertura"]==mes_atual)  & (df_raw["Ano_abertura"]==ano_atual)]
    df_ano  = df_raw[df_raw["Ano_abertura"]==ano_atual]
    df_m_ant_mes = mes_atual - 1 if mes_atual > 1 else 12
    df_m_ant_ano = ano_atual if mes_atual > 1 else ano_atual - 1
    df_mes_ant = df_raw[(df_raw["Mes_abertura"]==df_m_ant_mes) & (df_raw["Ano_abertura"]==df_m_ant_ano)]

    hoje_q     = df_raw[df_raw["Data_abertura"].dt.date == hoje].shape[0]
    sol_hoje   = df_raw[df_raw["Data_Solucao"].dt.date == hoje].shape[0]
    total_mes  = len(df_mes)
    total_ano  = len(df_ano)
    total_ant  = len(df_mes_ant)
    backlog    = df_raw[df_raw["Data_Solucao"].isna()].shape[0]
    fcr_mes    = (df_mes["Finalizado_Mesmo_Dia"].sum() / total_mes * 100) if total_mes > 0 else 0

    delta_m = total_mes - total_ant
    d_cls   = "b-red" if delta_m > 0 else "b-green"
    d_str   = f"{'↑' if delta_m > 0 else '↓'} {abs(delta_m)} vs mês ant."
    f_cls   = "b-green" if fcr_mes >= 70 else ("b-gold" if fcr_mes >= 50 else "b-red")

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_card("Abertos Hoje",    f"{hoje_q:,}",       "chamados abertos",    "📥", RED)}
      {kpi_card("Resolvidos Hoje", f"{sol_hoje:,}",     "chamados fechados",   "✅", GREEN)}
      {kpi_card("Mês Atual",       f"{total_mes:,}",    f"chamados em {hoje.strftime('%b/%Y')}", "📅", BLUE, d_str, d_cls)}
      {kpi_card(f"Ano {ano_atual}", f"{total_ano:,}",   "chamados no ano",     "🗓️", DARK)}
      {kpi_card("FCR — Mês",       f"{fcr_mes:.1f}%",  "resolução 1º contato","⚡", GOLD,   "Meta: 70%", f_cls)}
      {kpi_card("Backlog",         f"{backlog:,}",      "chamados em aberto",  "🗂️", ORANGE if backlog > 30 else GREEN)}
    </div>
    """, unsafe_allow_html=True)

    # ── ROTEAMENTO ────────────────────────────────────────────────────────────
    if pagina == "📊 Painel Executivo":
        pagina_executivo(df, df_raw, hoje)
    elif pagina == "👥 Time de Suporte":
        pagina_time(df)
    elif pagina == "🎫 Situação dos Chamados":
        pagina_situacao(df)
    elif pagina == "🏢 Clientes & Contatos":
        pagina_clientes(df)
    elif pagina == "🧩 Módulos & Origens":
        pagina_modulos(df)


if __name__ == "__main__":
    main()
