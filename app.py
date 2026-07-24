# =============================================================================
# Central de Suporte — SupraMAIS  |  Command Center
# Stack: Streamlit + pyodbc + pandas + plotly
# SQL : INALTERADO — lê direto da view sgrp_atendimentos_geral
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
    page_title="Central de Suporte · SupraMAIS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)
components.html('<script>setTimeout(()=>window.parent.location.reload(),1800000)</script>', height=0)

# ── PALETA (tema escuro) ───────────────────────────────────────────────────────
BG      = "#0D1B2A"
CARD    = "#112240"
CARD2   = "#1A3258"
BRAND   = "#CC2020"
TEAL    = "#00CEC9"
GREEN   = "#00B894"
ORANGE  = "#E17055"
GOLD    = "#FDCB6E"
PURPLE  = "#A29BFE"
WHITE   = "#E8F4FD"
MUTED   = "#8BA3BF"
BORDER  = "#1E3A5F"
DANGER  = "#E63946"

CORES = [BRAND, TEAL, ORANGE, GOLD, GREEN, PURPLE, "#FD79A8", "#74B9FF", "#55EFC4", "#A29BFE"]

# ── CSS GLOBAL (dark theme) ────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif !important; box-sizing: border-box; }}

/* ── Fundo principal ── */
.stApp {{ background: {BG} !important; color: {WHITE} !important; }}
.block-container {{ padding: 0.6rem 1.6rem 2rem !important; max-width: 100% !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}

/* ── Sidebar colapsada ── */
section[data-testid="stSidebar"] {{
  background: {CARD} !important;
  border-right: 1px solid {BORDER} !important;
}}

/* ── Textos globais ── */
h1,h2,h3,h4,h5,h6,p,label,span,div {{ color: {WHITE} !important; }}
.stMarkdown p {{ color: {MUTED} !important; }}

/* ── Inputs ── */
input, textarea, select {{
  background: {CARD2} !important;
  color: {WHITE} !important;
  border: 1px solid {BORDER} !important;
  border-radius: 8px !important;
}}
.stDateInput input {{ color: {WHITE} !important; }}
[data-baseweb="select"] {{ background: {CARD2} !important; border: 1px solid {BORDER} !important; }}
[data-baseweb="select"] * {{ color: {WHITE} !important; }}
[data-baseweb="popover"] {{ background: {CARD2} !important; border: 1px solid {BORDER} !important; }}
[data-baseweb="menu"] {{ background: {CARD2} !important; }}
[data-baseweb="option"] {{ background: {CARD2} !important; color: {WHITE} !important; }}
[data-baseweb="option"]:hover {{ background: {CARD} !important; }}
[data-baseweb="tag"] {{ background: {BRAND} !important; }}

/* ── Botão ── */
.stButton button {{
  background: {BRAND} !important; color: {WHITE} !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 600 !important; padding: 6px 16px !important;
  transition: opacity 0.2s !important;
}}
.stButton button:hover {{ opacity: 0.85 !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: {CARD} !important;
  border-bottom: 1px solid {BORDER} !important;
  padding: 0 4px !important; gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important; border: none !important;
  color: {MUTED} !important; font-weight: 500 !important;
  font-size: 0.84rem !important; padding: 10px 20px !important;
  border-bottom: 3px solid transparent !important;
}}
.stTabs [aria-selected="true"] {{
  color: {TEAL} !important; font-weight: 700 !important;
  border-bottom: 3px solid {TEAL} !important;
  background: transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
  color: {WHITE} !important;
}}

/* ── Selectbox label ── */
.stMultiSelect label, .stSelectbox label, .stDateInput label {{
  color: {MUTED} !important; font-size: 0.76rem !important; font-weight: 600 !important;
  text-transform: uppercase; letter-spacing: 0.4px;
}}

/* ── KPI cards ── */
.kpi-card {{
  background: {CARD};
  border: 1px solid {BORDER};
  border-radius: 14px;
  padding: 16px 18px 14px;
  position: relative; overflow: hidden;
  min-height: 110px;
}}
.kpi-glow {{
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  border-radius: 14px 14px 0 0;
}}
.kpi-icon {{
  position: absolute; right: 14px; top: 12px;
  font-size: 1.8rem; opacity: 0.08;
}}
.kpi-label {{
  font-size: 0.67rem; font-weight: 700; letter-spacing: 0.7px;
  text-transform: uppercase; color: {MUTED} !important;
  margin-bottom: 7px;
}}
.kpi-val {{
  font-size: 1.95rem; font-weight: 800;
  color: {WHITE} !important; line-height: 1;
}}
.kpi-sub {{
  font-size: 0.68rem; color: {MUTED} !important; margin-top: 5px;
}}
.kpi-badge {{
  display: inline-block; padding: 2px 8px; border-radius: 20px;
  font-size: 0.64rem; font-weight: 700; margin-top: 4px;
}}
.b-green  {{ background: rgba(0,184,148,0.2); color: {GREEN}; }}
.b-red    {{ background: rgba(230,57,70,0.2);  color: {DANGER}; }}
.b-orange {{ background: rgba(225,112,85,0.2); color: {ORANGE}; }}
.b-gold   {{ background: rgba(253,203,110,0.2);color: {GOLD}; }}
.b-muted  {{ background: rgba(139,163,191,0.15);color: {MUTED}; }}
.b-teal   {{ background: rgba(0,206,201,0.2);  color: {TEAL}; }}

/* ── Chart card ── */
.chart-card {{
  background: {CARD}; border: 1px solid {BORDER};
  border-radius: 14px; padding: 16px 16px 8px; margin-bottom: 14px;
}}
.chart-title {{
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.5px; color: {MUTED} !important;
  border-bottom: 1px solid {BORDER}; padding-bottom: 8px; margin-bottom: 10px;
}}

/* ── Seção title ── */
.sec-t {{
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.8px; color: {MUTED} !important;
  border-left: 3px solid {TEAL}; padding-left: 9px;
  margin: 18px 0 12px; display: block;
}}

/* ── Tooltip ── */
.tip {{
  position: relative; display: inline-block;
  cursor: help; border-bottom: 1px dashed {MUTED};
}}
.tip::after {{
  content: attr(data-tip);
  position: absolute; bottom: 120%; left: 50%;
  transform: translateX(-50%);
  background: {CARD2}; color: {WHITE};
  border: 1px solid {BORDER};
  padding: 7px 10px; border-radius: 8px;
  font-size: 0.71rem; font-weight: 400;
  white-space: normal; width: 230px;
  opacity: 0; pointer-events: none;
  transition: opacity 0.2s; z-index: 999;
  line-height: 1.4;
}}
.tip:hover::after {{ opacity: 1; }}

/* ── Filtro bar ── */
.filter-bar {{
  background: {CARD}; border: 1px solid {BORDER};
  border-radius: 12px; padding: 12px 18px;
  margin-bottom: 16px;
  display: flex; align-items: flex-end; gap: 14px; flex-wrap: wrap;
}}
.filter-label {{
  font-size: 0.65rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px;
  color: {MUTED} !important; margin-bottom: 4px;
}}

/* ── Alerta cards ── */
.alert-card {{
  background: rgba(230,57,70,0.08);
  border: 1px solid rgba(230,57,70,0.3);
  border-left: 4px solid {DANGER};
  border-radius: 10px; padding: 11px 14px;
  margin-bottom: 8px;
}}
.alert-warn {{
  background: rgba(253,203,110,0.08);
  border: 1px solid rgba(253,203,110,0.25);
  border-left: 4px solid {GOLD};
}}
.alert-info {{
  background: rgba(0,206,201,0.08);
  border: 1px solid rgba(0,206,201,0.2);
  border-left: 4px solid {TEAL};
}}
.alert-title {{
  font-size: 0.8rem; font-weight: 700; color: {WHITE} !important;
}}
.alert-sub {{
  font-size: 0.72rem; color: {MUTED} !important; margin-top: 2px;
}}

/* ── Ranking ── */
.rank-row {{
  display: flex; align-items: center; gap: 10px;
  padding: 7px 0; border-bottom: 1px solid {BORDER};
}}
.rank-pos {{ font-size: 0.75rem; font-weight: 700; color: {MUTED} !important; width: 22px; text-align: center; }}
.rank-name {{ font-size: 0.82rem; color: {WHITE} !important; flex: 1; font-weight: 500;
              white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.rank-bg {{ flex: 2; height: 5px; background: {CARD2}; border-radius: 4px; overflow: hidden; }}
.rank-fill {{ height: 5px; border-radius: 4px; }}
.rank-val {{ font-size: 0.82rem; font-weight: 700; min-width: 38px; text-align: right; }}

/* ── Tabela de atendentes ── */
.att-table {{ width: 100%; border-collapse: collapse; }}
.att-table th {{
  font-size: 0.67rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.5px; color: {MUTED} !important;
  padding: 8px 12px; border-bottom: 1px solid {BORDER};
  text-align: left;
}}
.att-table td {{
  font-size: 0.82rem; color: {WHITE} !important;
  padding: 9px 12px; border-bottom: 1px solid {BORDER};
}}
.att-table tr:hover td {{ background: {CARD2}; }}
.bar-cell {{ display: flex; align-items: center; gap: 7px; }}
.bar-bg {{ flex: 1; height: 6px; background: {CARD2}; border-radius: 3px; overflow: hidden; }}
.bar-fill {{ height: 6px; border-radius: 3px; }}
.badge-val {{
  padding: 2px 7px; border-radius: 5px; font-size: 0.72rem; font-weight: 700;
}}

/* ── Pulse ── */
@keyframes pulse {{
  0%   {{ box-shadow: 0 0 0 0 rgba(0,206,201,.6); }}
  70%  {{ box-shadow: 0 0 0 7px rgba(0,206,201,0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(0,206,201,0); }}
}}
.dot-live {{
  display: inline-block; width: 7px; height: 7px;
  background: {GREEN}; border-radius: 50%;
  animation: pulse 2s infinite;
  margin-right: 6px; vertical-align: middle;
}}

/* ── DataFrames ── */
.stDataFrame {{ border: 1px solid {BORDER} !important; border-radius: 10px; }}
[data-testid="stDataFrameResizable"] {{ background: {CARD} !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}

/* ── hr ── */
hr {{ border-color: {BORDER} !important; margin: 10px 0 !important; }}

/* ── info box ── */
.stAlert {{ background: {CARD2} !important; border: 1px solid {BORDER} !important; border-radius: 10px !important; }}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ────────────────────────────────────────────────────────────────────
def pb(height=300, **kw):
    """Plotly base layout para tema escuro."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=12, b=8, l=8, r=8),
        height=height,
        font=dict(family="Inter, sans-serif", color=MUTED, size=11),
        **kw
    )

def chart_open(title=""):
    t = f'<div class="chart-title">{title}</div>' if title else ""
    return f'<div class="chart-card">{t}'

def chart_close():
    return '</div>'

def tip(term, desc):
    """Retorna span com tooltip."""
    return f'<span class="tip" data-tip="{desc}">{term}</span>'

def kpi(label, val, sub="", icon="📊", color=TEAL, badge="", bcls="b-muted", tip_text=""):
    tip_html = f' <span class="tip" data-tip="{tip_text}" style="font-size:0.7rem;opacity:0.6">ⓘ</span>' if tip_text else ""
    badge_html = f'<span class="kpi-badge {bcls}">{badge}</span>' if badge else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-glow" style="background:{color}"></div>
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}{tip_html}</div>
      <div class="kpi-val">{val}</div>
      <div class="kpi-sub">{sub} {badge_html}</div>
    </div>"""

def ranking_html(df_r, col_n, col_v, color=TEAL):
    medals = ["🥇", "🥈", "🥉"]
    top = df_r[col_v].max() if not df_r.empty else 1
    rows = ""
    for i, row in enumerate(df_r.itertuples(), 1):
        pct = int(getattr(row, col_v) / top * 100) if top > 0 else 0
        pos = medals[i-1] if i <= 3 else f'<span class="rank-pos">{i}</span>'
        rows += f"""
        <div class="rank-row">
          <span style="font-size:1rem">{pos}</span>
          <span class="rank-name">{getattr(row, col_n)}</span>
          <div class="rank-bg"><div class="rank-fill" style="width:{pct}%;background:{color}"></div></div>
          <span class="rank-val" style="color:{color}">{getattr(row, col_v):,}</span>
        </div>"""
    return rows


# ── SQL & CACHE (QUERY INALTERADA) ────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner="Carregando dados do banco…")
def carregar_dados() -> pd.DataFrame:
    cfg = st.secrets["database"]
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={cfg['server']};DATABASE={cfg['database']};"
        f"UID={cfg['username']};PWD={cfg['password']};",
        timeout=30,
    )
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
    # Tempo médio de resolução em horas
    df["TMR_h"] = (df["Data_Solucao"] - df["Data_abertura"]).dt.total_seconds() / 3600
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 1 — RESUMO GERAL
# ══════════════════════════════════════════════════════════════════════════════
def aba_resumo(df, df_raw, hoje):
    # ── Volume diário + média móvel ──────────────────────────────────────────
    col_v, col_sit = st.columns([3, 2])

    with col_v:
        st.markdown(chart_open("📊 Volume Diário de Chamados + Média Móvel 7 Dias"), unsafe_allow_html=True)
        df_d = df.groupby(df["Data_abertura"].dt.date).size().reset_index(name="Qtd")
        df_d.columns = ["Data", "Qtd"]
        df_d = df_d.sort_values("Data")
        df_d["MM7"] = df_d["Qtd"].rolling(7, min_periods=1).mean().round(1)

        fig = go.Figure()
        fig.add_bar(x=df_d["Data"], y=df_d["Qtd"], name="Chamados",
                    marker_color=BRAND, opacity=0.7)
        fig.add_scatter(x=df_d["Data"], y=df_d["MM7"], mode="lines",
                        name="Média 7 dias", line=dict(color=TEAL, width=2.5))
        fig.update_layout(**pb(260,
            xaxis=dict(showgrid=False, color=MUTED),
            yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=WHITE)),
            bargap=0.25))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_sit:
        st.markdown(chart_open("🔵 Situação Atual dos Chamados"), unsafe_allow_html=True)
        df_sit = df.groupby("Situacao").size().reset_index(name="Qtd")
        fig_sit = px.pie(df_sit, names="Situacao", values="Qtd", hole=0.55,
                          color_discrete_sequence=CORES)
        fig_sit.update_traces(textposition="outside", textinfo="label+percent",
                               textfont=dict(size=11, color=WHITE),
                               marker=dict(line=dict(color=BG, width=2)))
        fig_sit.update_layout(**pb(260, showlegend=False))
        st.plotly_chart(fig_sit, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # ── Principais motivos + canais ──────────────────────────────────────────
    col_mot, col_orig = st.columns([3, 2])

    with col_mot:
        st.markdown(chart_open("🎯 Principais Motivos de Contato (Treemap)"), unsafe_allow_html=True)
        df_mot = df.groupby("Motivo").size().reset_index(name="Qtd").nlargest(20, "Qtd")
        fig_mot = px.treemap(df_mot, path=["Motivo"], values="Qtd",
                              color="Qtd",
                              color_continuous_scale=[[0, CARD2],[0.5, BRAND],[1, "#FF6B6B"]])
        fig_mot.update_coloraxes(showscale=False)
        fig_mot.update_traces(
            textfont=dict(size=12, color=WHITE),
            marker=dict(line=dict(width=1.5, color=BG)),
        )
        fig_mot.update_layout(**pb(300))
        st.plotly_chart(fig_mot, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_orig:
        st.markdown(chart_open("📡 Canal de Entrada (Origem)"), unsafe_allow_html=True)
        df_or = df.groupby("Origem").size().reset_index(name="Qtd").sort_values("Qtd")
        fig_or = px.bar(df_or, y="Origem", x="Qtd", orientation="h",
                         text="Qtd", color="Qtd",
                         color_continuous_scale=[[0, CARD2],[1, TEAL]])
        fig_or.update_traces(textposition="outside", cliponaxis=False,
                              textfont=dict(color=WHITE))
        fig_or.update_coloraxes(showscale=False)
        fig_or.update_layout(**pb(300,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
            yaxis_title="", xaxis_title=""))
        st.plotly_chart(fig_or, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # ── Tendência mensal ─────────────────────────────────────────────────────
    st.markdown(chart_open("📈 Tendência de Volume — Mensal (Chamados Abertos vs Resolvidos)"), unsafe_allow_html=True)
    df_men = df.copy()
    df_men["MesAno"] = df_men["Data_abertura"].dt.to_period("M").astype(str)
    abertos_m  = df_men.groupby("MesAno").size().reset_index(name="Abertos")
    resolvidos_m = df_men[df_men["Data_Solucao"].notna()].groupby("MesAno").size().reset_index(name="Resolvidos")
    df_trend = abertos_m.merge(resolvidos_m, on="MesAno", how="left").fillna(0).sort_values("MesAno")

    fig_t = go.Figure()
    fig_t.add_scatter(x=df_trend["MesAno"], y=df_trend["Abertos"], mode="lines+markers",
                      name="Abertos", line=dict(color=BRAND, width=2.5), marker=dict(size=5))
    fig_t.add_scatter(x=df_trend["MesAno"], y=df_trend["Resolvidos"], mode="lines+markers",
                      name="Resolvidos", line=dict(color=GREEN, width=2.5), marker=dict(size=5))
    fig_t.add_traces([go.Scatter(
        x=df_trend["MesAno"].tolist() + df_trend["MesAno"].tolist()[::-1],
        y=df_trend["Abertos"].tolist() + df_trend["Resolvidos"].tolist()[::-1],
        fill="toself", fillcolor="rgba(0,184,148,0.07)",
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    )])
    fig_t.update_layout(**pb(230,
        xaxis=dict(showgrid=False, color=MUTED),
        yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(color=WHITE))))
    st.plotly_chart(fig_t, use_container_width=True)
    st.markdown(chart_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 2 — CLIENTES
# ══════════════════════════════════════════════════════════════════════════════
def aba_clientes(df):
    col_tree, col_rank = st.columns([3, 2])

    with col_tree:
        st.markdown(chart_open("📦 Volume de Chamados por Cliente (Treemap)"), unsafe_allow_html=True)
        df_cli = df.groupby("Cliente").size().reset_index(name="Qtd").nlargest(30, "Qtd")
        fig_tree = px.treemap(df_cli, path=["Cliente"], values="Qtd",
                               color="Qtd",
                               color_continuous_scale=[[0, CARD2],[0.4, BRAND],[1, "#FF6B6B"]])
        fig_tree.update_coloraxes(showscale=False)
        fig_tree.update_traces(
            textfont=dict(size=11, color=WHITE),
            marker=dict(line=dict(width=1.5, color=BG))
        )
        fig_tree.update_layout(**pb(340))
        st.plotly_chart(fig_tree, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_rank:
        st.markdown(chart_open("🏆 Top 15 Clientes"), unsafe_allow_html=True)
        df_rc = df.groupby("Cliente").size().reset_index(name="Total").sort_values("Total", ascending=False).head(15)
        st.markdown(ranking_html(df_rc, "Cliente", "Total", TEAL), unsafe_allow_html=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # Sunburst Cliente → Módulo → Situação
    col_sun, col_cont = st.columns([3, 2])
    with col_sun:
        st.markdown(chart_open("🌐 Hierarquia: Cliente → Módulo → Situação (Top 10 Clientes)"), unsafe_allow_html=True)
        top10 = df.groupby("Cliente").size().nlargest(10).index
        df_s = df[df["Cliente"].isin(top10)].copy()
        top5m = df_s["Modulo"].value_counts().nlargest(5).index
        df_s["Modulo_s"] = df_s["Modulo"].apply(lambda x: x if x in top5m else "Outros")
        df_sg = df_s.groupby(["Cliente","Modulo_s","Situacao"]).size().reset_index(name="Qtd")
        fig_sun = px.sunburst(df_sg, path=["Cliente","Modulo_s","Situacao"],
                               values="Qtd", color_discrete_sequence=CORES)
        fig_sun.update_layout(**pb(380))
        fig_sun.update_traces(textfont=dict(size=10, color=WHITE))
        st.plotly_chart(fig_sun, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_cont:
        st.markdown(chart_open("🗣️ Top 15 Contatos que Mais Acionaram o Suporte"), unsafe_allow_html=True)
        df_rc2 = df.groupby("Contato").size().reset_index(name="Total").sort_values("Total", ascending=False).head(15)
        st.markdown(ranking_html(df_rc2, "Contato", "Total", GOLD), unsafe_allow_html=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # Raio-X do cliente
    st.markdown('<span class="sec-t">🔍 Raio-X do Cliente</span>', unsafe_allow_html=True)
    st.markdown(chart_open(""), unsafe_allow_html=True)
    clientes = sorted(df["Cliente"].dropna().unique())
    cli_sel = st.selectbox("Selecione o Cliente:", clientes, label_visibility="collapsed")
    if cli_sel:
        df_ce = df[df["Cliente"] == cli_sel]
        tot_ce  = len(df_ce)
        ab_ce   = df_ce["Data_Solucao"].isna().sum()
        fcr_ce  = df_ce["Finalizado_Mesmo_Dia"].sum() / tot_ce * 100 if tot_ce > 0 else 0
        tmr_ce  = df_ce[df_ce["TMR_h"] > 0]["TMR_h"].mean()
        tmr_str = f"{tmr_ce:.1f}h" if (not pd.isna(tmr_ce) and tmr_ce < 72) else (f"{tmr_ce/24:.1f} dias" if not pd.isna(tmr_ce) else "N/D")

        st.markdown(f"""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px">
          {kpi("Total de Chamados", f"{tot_ce:,}", "", "📋", TEAL)}
          {kpi("Em Aberto", f"{ab_ce:,}", "", "📌", ORANGE)}
          {kpi("FCR", f"{fcr_ce:.1f}%", "1º contato", "⚡", GOLD,
               tip_text="Resolução no Primeiro Contato: % de chamados finalizados sem retorno.")}
          {kpi("Tempo Médio Resolução", tmr_str, "", "⏱️", GREEN,
               tip_text="Tempo médio entre abertura e fechamento do chamado.")}
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Top Contatos**")
            df_ct = df_ce.groupby("Contato").size().reset_index(name="Qtd").nlargest(8,"Qtd").sort_values("Qtd")
            fig_ct = px.bar(df_ct, y="Contato", x="Qtd", orientation="h", text="Qtd",
                             color="Qtd", color_continuous_scale=[[0,CARD2],[1,TEAL]])
            fig_ct.update_coloraxes(showscale=False)
            fig_ct.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=WHITE))
            fig_ct.update_layout(**pb(240, yaxis_title="", xaxis_title="",
                                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)))
            st.plotly_chart(fig_ct, use_container_width=True)
        with c2:
            st.markdown("**Módulos Demandados**")
            df_mc = df_ce.groupby("Modulo").size().reset_index(name="Qtd").nlargest(8,"Qtd").sort_values("Qtd")
            fig_mc = px.bar(df_mc, y="Modulo", x="Qtd", orientation="h", text="Qtd",
                             color="Qtd", color_continuous_scale=[[0,CARD2],[1,BRAND]])
            fig_mc.update_coloraxes(showscale=False)
            fig_mc.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=WHITE))
            fig_mc.update_layout(**pb(240, yaxis_title="", xaxis_title="",
                                       xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)))
            st.plotly_chart(fig_mc, use_container_width=True)
        with c3:
            st.markdown("**Origem dos Contatos**")
            df_oc = df_ce.groupby("Origem").size().reset_index(name="Qtd")
            fig_oc = px.pie(df_oc, names="Origem", values="Qtd", hole=0.52,
                             color_discrete_sequence=CORES)
            fig_oc.update_traces(textposition="inside", textinfo="percent+label",
                                  textfont=dict(size=10, color=WHITE))
            fig_oc.update_layout(**pb(240, showlegend=False))
            st.plotly_chart(fig_oc, use_container_width=True)
    st.markdown(chart_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 3 — ATENDENTES
# ══════════════════════════════════════════════════════════════════════════════
def aba_atendentes(df):
    df_at = df.groupby("Atendente").agg(
        Total=("Sac","count"),
        Resolvidos=("Data_Solucao", lambda x: x.notna().sum()),
        Em_Aberto=("Data_Solucao", lambda x: x.isna().sum()),
        FCR=("Finalizado_Mesmo_Dia","sum"),
        TMR_medio=("TMR_h", lambda x: x[x>0].mean()),
    ).reset_index()
    df_at["FCR_pct"] = (df_at["FCR"] / df_at["Total"] * 100).round(1)
    df_at["Enc_pct"] = (df_at["Resolvidos"] / df_at["Total"] * 100).round(1)
    df_at["TMR_str"] = df_at["TMR_medio"].apply(
        lambda x: f"{x:.0f}h" if (not pd.isna(x) and x < 72) else (f"{x/24:.1f}d" if not pd.isna(x) else "N/D")
    )
    df_at = df_at.sort_values("Total", ascending=False)

    # Tabela de performance
    st.markdown('<span class="sec-t">📋 Tabela de Performance por Atendente</span>', unsafe_allow_html=True)
    st.markdown(chart_open(""), unsafe_allow_html=True)

    max_fcr = df_at["FCR_pct"].max() or 1
    max_enc = df_at["Enc_pct"].max() or 1
    max_tot = df_at["Total"].max() or 1

    rows_html = ""
    for _, r in df_at.iterrows():
        fcr_cor  = GREEN  if r["FCR_pct"] >= 70 else (GOLD if r["FCR_pct"] >= 50 else DANGER)
        enc_cor  = GREEN  if r["Enc_pct"] >= 80 else (GOLD if r["Enc_pct"] >= 60 else ORANGE)
        fcr_pct  = int(r["FCR_pct"] / max_fcr * 100)
        enc_pct  = int(r["Enc_pct"] / max_enc * 100)
        tot_pct  = int(r["Total"]   / max_tot * 100)
        rows_html += f"""
        <tr>
          <td><b>{r['Atendente']}</b></td>
          <td>
            <div class="bar-cell">
              <div class="bar-bg"><div class="bar-fill" style="width:{tot_pct}%;background:{TEAL}"></div></div>
              <span style="min-width:30px;font-weight:700;color:{TEAL}">{r['Total']:,}</span>
            </div>
          </td>
          <td style="color:{GREEN}">{r['Resolvidos']:,}</td>
          <td style="color:{ORANGE}">{r['Em_Aberto']:,}</td>
          <td>
            <div class="bar-cell">
              <div class="bar-bg"><div class="bar-fill" style="width:{fcr_pct}%;background:{fcr_cor}"></div></div>
              <span class="badge-val" style="background:rgba(0,0,0,0.2);color:{fcr_cor}">{r['FCR_pct']:.0f}%</span>
            </div>
          </td>
          <td>
            <div class="bar-cell">
              <div class="bar-bg"><div class="bar-fill" style="width:{enc_pct}%;background:{enc_cor}"></div></div>
              <span class="badge-val" style="background:rgba(0,0,0,0.2);color:{enc_cor}">{r['Enc_pct']:.0f}%</span>
            </div>
          </td>
          <td style="color:{MUTED}">{r['TMR_str']}</td>
        </tr>"""

    fcr_tip = tip("FCR%", "Resolução no 1º Contato: % de chamados finalizados sem retorno do cliente. Meta recomendada: 70%")
    enc_tip = tip("Enc.%", "Taxa de Encerramento: % de chamados resolvidos em relação ao total atribuído ao atendente no período")
    tmr_tip = tip("TMR", "Tempo Médio de Resolução: tempo médio entre abertura e fechamento do chamado")

    st.markdown(f"""
    <table class="att-table">
      <thead>
        <tr>
          <th>Atendente</th>
          <th>Total Chamados</th>
          <th>Resolvidos</th>
          <th>Em Aberto</th>
          <th>{fcr_tip}</th>
          <th>{enc_tip}</th>
          <th>{tmr_tip}</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown(chart_close(), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quadrante eficiência + heatmap
    col_q, col_hm = st.columns([3, 2])

    with col_q:
        st.markdown(chart_open(f"🎯 Quadrante de Eficiência — Volume vs {tip('FCR%', 'Porcentagem de chamados resolvidos no primeiro contato')}"), unsafe_allow_html=True)
        med_t = df_at["Total"].median()
        med_f = df_at["FCR_pct"].median()
        max_t = df_at["Total"].max() * 1.25

        fig_q = go.Figure()
        for rect, color in [
            ((med_t, max_t, med_f, 102), f"rgba(0,184,148,0.06)"),
            ((0, med_t, med_f, 102),     f"rgba(0,180,216,0.06)"),
            ((med_t, max_t, 0, med_f),   f"rgba(225,112,85,0.06)"),
            ((0, med_t, 0, med_f),       f"rgba(230,57,70,0.06)"),
        ]:
            fig_q.add_shape(type="rect", x0=rect[0], x1=rect[1], y0=rect[2], y1=rect[3],
                             fillcolor=color, line_width=0)
        fig_q.add_vline(x=med_t, line_color=BORDER, line_dash="dot", line_width=1.5)
        fig_q.add_hline(y=med_f, line_color=BORDER, line_dash="dot", line_width=1.5)
        fig_q.add_scatter(
            x=df_at["Total"], y=df_at["FCR_pct"],
            mode="markers+text", text=df_at["Atendente"],
            textposition="top center",
            textfont=dict(size=10, color=WHITE),
            marker=dict(size=df_at["Total"]**0.55*2.5, color=TEAL, opacity=0.75,
                        line=dict(color=BG, width=1.5)),
            hovertemplate="<b>%{text}</b><br>Chamados: %{x}<br>FCR: %{y:.1f}%<extra></extra>",
        )
        fig_q.add_annotation(x=max_t*0.97, y=100, text="⭐ Alta Eficiência",
                              showarrow=False, font=dict(size=9, color=GREEN), xanchor="right")
        fig_q.add_annotation(x=max_t*0.03, y=100, text="🧘 Baixo Volume / Boa FCR",
                              showarrow=False, font=dict(size=9, color=TEAL), xanchor="left")
        fig_q.add_annotation(x=max_t*0.97, y=med_f*0.15, text="🔥 Alto Volume / FCR Baixa",
                              showarrow=False, font=dict(size=9, color=ORANGE), xanchor="right")
        fig_q.add_annotation(x=max_t*0.03, y=med_f*0.15, text="⚠️ Atenção",
                              showarrow=False, font=dict(size=9, color=DANGER), xanchor="left")
        fig_q.update_layout(**pb(320,
            xaxis=dict(title="Total de Chamados", showgrid=False, color=MUTED),
            yaxis=dict(title="FCR %", showgrid=False, color=MUTED, range=[0, 108]),
        ))
        st.plotly_chart(fig_q, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_hm:
        st.markdown(chart_open("🧩 Mapa de Calor — Atendente × Módulo"), unsafe_allow_html=True)
        top6m = df["Modulo"].value_counts().nlargest(6).index
        df_hm = df.copy()
        df_hm["Mod_x"] = df_hm["Modulo"].apply(lambda x: x if x in top6m else "Outros")
        piv = df_hm.groupby(["Atendente","Mod_x"]).size().reset_index(name="Qtd") \
                   .pivot(index="Atendente", columns="Mod_x", values="Qtd").fillna(0)
        fig_hm = px.imshow(piv, text_auto=True, aspect="auto",
                            color_continuous_scale=[[0,CARD2],[0.5,CARD],[1,BRAND]])
        fig_hm.update_coloraxes(showscale=False)
        fig_hm.update_layout(**pb(max(300, piv.shape[0]*38), xaxis_title="", yaxis_title=""))
        fig_hm.update_traces(textfont=dict(color=WHITE))
        st.plotly_chart(fig_hm, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # Gauges de FCR
    st.markdown('<span class="sec-t">⚡ Resolução no Primeiro Contato (FCR) — por Atendente</span>', unsafe_allow_html=True)
    df_fcr_g = df_at.sort_values("FCR_pct", ascending=False)
    n = min(len(df_fcr_g), 6)
    cols_g = st.columns(n)
    for i, (_, row) in enumerate(df_fcr_g.head(n).iterrows()):
        cor = GREEN if row["FCR_pct"] >= 70 else (GOLD if row["FCR_pct"] >= 50 else DANGER)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row["FCR_pct"],
            number=dict(suffix="%", font=dict(size=18, color=cor)),
            title=dict(text=row["Atendente"].split()[0], font=dict(size=10, color=MUTED)),
            gauge=dict(
                axis=dict(range=[0,100], tickwidth=0, tickcolor="transparent"),
                bar=dict(color=cor, thickness=0.22),
                bgcolor=CARD2, borderwidth=0,
                steps=[dict(range=[0,70], color=CARD2), dict(range=[70,100], color="rgba(0,184,148,0.15)")],
                threshold=dict(line=dict(color=GREEN, width=2), thickness=0.75, value=70),
            ),
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=5, l=10, r=10), height=160)
        cols_g[i].plotly_chart(fig_g, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 4 — SITUAÇÃO DOS CHAMADOS
# ══════════════════════════════════════════════════════════════════════════════
def aba_situacao(df):
    col_f, col_tipo, col_mot = st.columns([1, 1, 2])

    with col_f:
        st.markdown(chart_open("🔀 Funil — Situações"), unsafe_allow_html=True)
        df_sit = df.groupby("Situacao").size().reset_index(name="Qtd").sort_values("Qtd", ascending=False)
        fig_f = go.Figure(go.Funnel(
            y=df_sit["Situacao"], x=df_sit["Qtd"],
            textposition="inside", textinfo="value+percent initial",
            marker=dict(color=CORES[:len(df_sit)]),
        ))
        fig_f.update_layout(**pb(300))
        st.plotly_chart(fig_f, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_tipo:
        st.markdown(chart_open("📁 Tipo de Chamado"), unsafe_allow_html=True)
        df_tp = df.groupby("Tipo").size().reset_index(name="Qtd")
        fig_tp = px.pie(df_tp, names="Tipo", values="Qtd", hole=0.55,
                         color_discrete_sequence=CORES)
        fig_tp.update_traces(textposition="inside", textinfo="percent+label",
                              textfont=dict(size=11, color=WHITE))
        fig_tp.update_layout(**pb(300, showlegend=False))
        st.plotly_chart(fig_tp, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_mot:
        st.markdown(chart_open("📈 Tendência de Situações — Mensal"), unsafe_allow_html=True)
        df_ts = df.copy()
        df_ts["MesAno"] = df_ts["Data_abertura"].dt.to_period("M").astype(str)
        top_s = df_ts["Situacao"].value_counts().nlargest(5).index
        df_ts["Sit_f"] = df_ts["Situacao"].apply(lambda x: x if x in top_s else "Outras")
        df_tsg = df_ts.groupby(["MesAno","Sit_f"]).size().reset_index(name="Qtd").sort_values("MesAno")
        fig_ts = px.area(df_tsg, x="MesAno", y="Qtd", color="Sit_f",
                          color_discrete_sequence=CORES)
        fig_ts.update_layout(**pb(300, xaxis_title="", yaxis_title="",
                                   xaxis=dict(showgrid=False, color=MUTED),
                                   yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED),
                                   legend=dict(orientation="h", y=1.12, x=0, title="",
                                               font=dict(color=WHITE))))
        st.plotly_chart(fig_ts, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # Backlog aging
    df_bl = df[df["Data_Solucao"].isna()].copy()
    if not df_bl.empty:
        hoje = date.today()
        df_bl["Dias"] = (pd.Timestamp(hoje) - df_bl["Data_abertura"]).dt.days.clip(lower=0)
        df_bl["Faixa"] = pd.cut(df_bl["Dias"],
                                  bins=[-1, 3, 7, 15, 30, 60, 9999],
                                  labels=["0–3 dias","4–7 dias","8–15 dias","16–30 dias","31–60 dias","60+ dias"])
        df_ag = df_bl.groupby("Faixa", observed=True).size().reset_index(name="Qtd")

        col_ag, col_at_sit = st.columns([2, 3])
        with col_ag:
            st.markdown(chart_open(f"⏳ {tip('Backlog', 'Fila de pendências: chamados ainda sem solução')} — Tempo em Aberto (Faixas)"), unsafe_allow_html=True)
            cores_ag = [GREEN, TEAL, GOLD, ORANGE, DANGER, "#8E1010"]
            fig_ag = px.bar(df_ag, x="Faixa", y="Qtd", text="Qtd",
                             color="Faixa", color_discrete_sequence=cores_ag)
            fig_ag.update_traces(textposition="outside", cliponaxis=False,
                                  textfont=dict(color=WHITE), showlegend=False)
            fig_ag.update_layout(**pb(260, xaxis_title="", yaxis_title="",
                                       xaxis=dict(showgrid=False, color=MUTED),
                                       yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED)))
            st.plotly_chart(fig_ag, use_container_width=True)
            st.markdown(chart_close(), unsafe_allow_html=True)

        with col_at_sit:
            st.markdown(chart_open("✅ Resolvidos vs 📌 Em Aberto — por Atendente"), unsafe_allow_html=True)
            df_ra = df.copy()
            df_ra["Status"] = df_ra["Data_Solucao"].apply(lambda x: "Resolvido" if pd.notna(x) else "Em Aberto")
            df_rag = df_ra.groupby(["Atendente","Status"]).size().reset_index(name="Qtd")
            n_at = df["Atendente"].nunique()
            fig_ra = px.bar(df_rag, y="Atendente", x="Qtd", color="Status",
                             orientation="h", barmode="stack", text="Qtd",
                             color_discrete_map={"Resolvido": GREEN, "Em Aberto": DANGER})
            fig_ra.update_traces(textposition="inside", textfont=dict(size=9, color=WHITE),
                                  cliponaxis=False)
            fig_ra.update_layout(**pb(max(260, n_at*34),
                yaxis_title="", xaxis_title="",
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                legend=dict(orientation="h", y=1.1, x=0, title="", font=dict(color=WHITE))))
            st.plotly_chart(fig_ra, use_container_width=True)
            st.markdown(chart_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 5 — SLA & KPIs
# ══════════════════════════════════════════════════════════════════════════════
def aba_sla(df):
    st.markdown(f"""
    <div class="chart-card" style="margin-bottom:14px">
      <div class="chart-title">
        ℹ️ Sobre os indicadores desta aba
      </div>
      <div style="font-size:0.8rem;color:{MUTED};line-height:1.7">
        <b style="color:{WHITE}">• {tip('FCR', 'First Contact Resolution — Resolução no Primeiro Contato')}</b>: % de chamados finalizados sem retorno do cliente. <b>Meta recomendada: ≥ 70%</b><br>
        <b style="color:{WHITE}">• {tip('TMR', 'Tempo Médio de Resolução')}</b>: tempo médio entre abertura e fechamento. Quanto menor, melhor.<br>
        <b style="color:{WHITE}">• {tip('SLA', 'Service Level Agreement — Acordo de Nível de Serviço')}</b>: compromisso de prazo entre empresa e cliente para resolução dos chamados.<br>
        <b style="color:{WHITE}">• Taxa de Encerramento</b>: % de chamados resolvidos no período filtrado.<br>
        <b style="color:{WHITE}">• Sazonalidade</b>: variação do volume por módulo ao longo dos meses do ano.
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_fcr_m, col_tmr_at = st.columns(2)

    with col_fcr_m:
        st.markdown(chart_open(f"⚡ Evolução Mensal do {tip('FCR%', 'Resolução no Primeiro Contato — meta: 70%')}"), unsafe_allow_html=True)
        df_fm = df.copy()
        df_fm["MesAno"] = df_fm["Data_abertura"].dt.to_period("M").astype(str)
        df_fm = df_fm.groupby("MesAno").agg(Total=("Sac","count"), FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
        df_fm["FCR_pct"] = (df_fm["FCR"] / df_fm["Total"] * 100).round(1)
        df_fm = df_fm.sort_values("MesAno")

        fig_fm = go.Figure()
        fig_fm.add_bar(x=df_fm["MesAno"], y=df_fm["Total"],
                        marker_color=CARD2, name="Total Chamados", yaxis="y")
        fig_fm.add_scatter(x=df_fm["MesAno"], y=df_fm["FCR_pct"],
                            mode="lines+markers+text", name="FCR %",
                            line=dict(color=GOLD, width=2.5), marker=dict(size=6),
                            text=df_fm["FCR_pct"].astype(str)+"%",
                            textposition="top center", textfont=dict(size=9, color=GOLD),
                            yaxis="y2")
        fig_fm.add_hline(y=70, line_dash="dash", line_color=GREEN, opacity=0.5,
                          annotation_text="Meta 70%", annotation_font_color=GREEN,
                          yref="y2")
        fig_fm.update_layout(**pb(260,
            xaxis=dict(showgrid=False, color=MUTED),
            yaxis=dict(title="Chamados", showgrid=True, gridcolor=BORDER, color=MUTED),
            yaxis2=dict(title="FCR %", overlaying="y", side="right",
                        range=[0,110], showgrid=False, color=MUTED, ticksuffix="%"),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=WHITE))))
        st.plotly_chart(fig_fm, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_tmr_at:
        st.markdown(chart_open(f"⏱️ {tip('TMR', 'Tempo Médio de Resolução — calculado a partir da data de abertura até a data de solução')} por Atendente"), unsafe_allow_html=True)
        df_tmr = df[df["TMR_h"] > 0].groupby("Atendente")["TMR_h"].mean().reset_index()
        df_tmr.columns = ["Atendente", "TMR_h"]
        df_tmr["TMR_dias"] = (df_tmr["TMR_h"] / 24).round(2)
        df_tmr = df_tmr.sort_values("TMR_dias")
        df_tmr["cor"] = df_tmr["TMR_dias"].apply(lambda x: GREEN if x <= 2 else (GOLD if x <= 5 else DANGER))

        fig_tmr = go.Figure()
        for _, r in df_tmr.iterrows():
            fig_tmr.add_bar(x=[r["TMR_dias"]], y=[r["Atendente"]],
                             orientation="h", marker_color=r["cor"],
                             showlegend=False,
                             text=[f"{r['TMR_dias']:.1f}d"], textposition="outside",
                             textfont=dict(color=WHITE))
        fig_tmr.update_layout(**pb(max(260, len(df_tmr)*34),
            xaxis=dict(title="Dias", showgrid=False, color=MUTED),
            yaxis=dict(showgrid=False, color=MUTED),
            yaxis_title="", bargap=0.3))
        st.plotly_chart(fig_tmr, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    # Sazonalidade
    st.markdown(chart_open(f"🌡️ Sazonalidade — {tip('Módulo', 'Módulo do ERP ao qual o chamado está associado')} × Mês do Ano"), unsafe_allow_html=True)
    meses_pt = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    df_saz = df.copy()
    df_saz["MesN"] = df_saz["Data_abertura"].dt.month
    df_saz["Mes"] = df_saz["MesN"].map(meses_pt)
    top8m = df_saz["Modulo"].value_counts().nlargest(8).index
    df_saz = df_saz[df_saz["Modulo"].isin(top8m)]
    piv_s = df_saz.groupby(["Modulo","Mes"]).size().reset_index(name="Qtd") \
                   .pivot(index="Modulo", columns="Mes", values="Qtd").fillna(0)
    col_ord = [m for m in list(meses_pt.values()) if m in piv_s.columns]
    piv_s = piv_s[col_ord]
    fig_saz = px.imshow(piv_s, text_auto=True, aspect="auto",
                         color_continuous_scale=[[0, CARD2],[0.5, ORANGE],[1, BRAND]])
    fig_saz.update_coloraxes(showscale=False)
    fig_saz.update_traces(textfont=dict(color=WHITE))
    fig_saz.update_layout(**pb(max(280, len(top8m)*40), xaxis_title="", yaxis_title=""))
    st.plotly_chart(fig_saz, use_container_width=True)
    st.markdown(chart_close(), unsafe_allow_html=True)

    # Comparativo ano a ano
    col_ya, col_yf = st.columns(2)
    df_ano = df.copy()
    df_ano["Ano"] = df_ano["Ano_abertura"].astype(str)
    df_ano_g = df_ano.groupby("Ano").agg(Total=("Sac","count"), FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
    df_ano_g["FCR_pct"] = (df_ano_g["FCR"] / df_ano_g["Total"] * 100).round(1)

    with col_ya:
        st.markdown(chart_open("📆 Total de Chamados por Ano"), unsafe_allow_html=True)
        fig_ya = px.bar(df_ano_g, x="Ano", y="Total", text="Total",
                         color="Total", color_continuous_scale=[[0,CARD2],[1,TEAL]])
        fig_ya.update_coloraxes(showscale=False)
        fig_ya.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=WHITE))
        fig_ya.update_layout(**pb(240, xaxis_title="", yaxis_title="",
                                   xaxis=dict(showgrid=False, color=MUTED),
                                   yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED)))
        st.plotly_chart(fig_ya, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

    with col_yf:
        st.markdown(chart_open(f"⚡ {tip('FCR%', 'Resolução no Primeiro Contato')} por Ano"), unsafe_allow_html=True)
        fig_yf = go.Figure()
        fig_yf.add_bar(x=df_ano_g["Ano"], y=df_ano_g["FCR_pct"],
                        marker_color=[GREEN if v>=70 else ORANGE for v in df_ano_g["FCR_pct"]],
                        text=df_ano_g["FCR_pct"].astype(str)+"%", textposition="outside",
                        textfont=dict(color=WHITE))
        fig_yf.add_hline(y=70, line_dash="dash", line_color=GREEN, opacity=0.5,
                          annotation_text="Meta 70%", annotation_font_color=GREEN)
        fig_yf.update_layout(**pb(240, xaxis_title="", yaxis_title="FCR %",
                                   yaxis_range=[0,110],
                                   xaxis=dict(showgrid=False, color=MUTED),
                                   yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED)))
        st.plotly_chart(fig_yf, use_container_width=True)
        st.markdown(chart_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 6 — ALERTAS & GESTÃO
# ══════════════════════════════════════════════════════════════════════════════
def aba_alertas(df, df_raw):
    hoje = date.today()

    # Chamados críticos em aberto
    df_bl = df_raw[df_raw["Data_Solucao"].isna()].copy()
    df_bl["Dias_Aberto"] = (pd.Timestamp(hoje) - df_bl["Data_abertura"]).dt.days.clip(lower=0)

    criticos  = df_bl[df_bl["Dias_Aberto"] >= 30].sort_values("Dias_Aberto", ascending=False)
    urgentes  = df_bl[(df_bl["Dias_Aberto"] >= 7) & (df_bl["Dias_Aberto"] < 30)].sort_values("Dias_Aberto", ascending=False)
    recentes  = df_bl[df_bl["Dias_Aberto"] < 7]

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.markdown(f"""
    <div class="kpi-card" style="border-left:4px solid {DANGER}">
      <div class="kpi-label">🔴 Críticos (+30 dias)</div>
      <div class="kpi-val" style="color:{DANGER}">{len(criticos):,}</div>
      <div class="kpi-sub">chamados sem solução</div>
    </div>""", unsafe_allow_html=True)
    col_m2.markdown(f"""
    <div class="kpi-card" style="border-left:4px solid {ORANGE}">
      <div class="kpi-label">🟠 Urgentes (7–29 dias)</div>
      <div class="kpi-val" style="color:{ORANGE}">{len(urgentes):,}</div>
      <div class="kpi-sub">requerem atenção</div>
    </div>""", unsafe_allow_html=True)
    col_m3.markdown(f"""
    <div class="kpi-card" style="border-left:4px solid {GOLD}">
      <div class="kpi-label">🟡 Recentes (&lt;7 dias)</div>
      <div class="kpi-val" style="color:{GOLD}">{len(recentes):,}</div>
      <div class="kpi-sub">em acompanhamento</div>
    </div>""", unsafe_allow_html=True)
    col_m4.markdown(f"""
    <div class="kpi-card" style="border-left:4px solid {TEAL}">
      <div class="kpi-label">📋 Total em Aberto</div>
      <div class="kpi-val" style="color:{TEAL}">{len(df_bl):,}</div>
      <div class="kpi-sub">chamados pendentes</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<span class="sec-t">🔴 Chamados Críticos — Em Aberto há 30+ Dias</span>', unsafe_allow_html=True)
        if not criticos.empty:
            for _, r in criticos.head(10).iterrows():
                dias = int(r["Dias_Aberto"])
                cor_cls = "alert-card"
                st.markdown(f"""
                <div class="{cor_cls}">
                  <div class="alert-title">
                    🔴 #{r['Sac']} — {r['Cliente']}
                    <span style="float:right;font-size:0.72rem;color:{DANGER};font-weight:700">{dias} dias em aberto</span>
                  </div>
                  <div class="alert-sub">
                    👤 {r['Atendente']} &nbsp;·&nbsp; 📋 {r['Assunto']} &nbsp;·&nbsp; 🧩 {r['Modulo']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-card alert-info"><div class="alert-title">✅ Nenhum chamado crítico no momento!</div></div>', unsafe_allow_html=True)

        st.markdown('<span class="sec-t">🟠 Chamados Urgentes — 7 a 29 Dias</span>', unsafe_allow_html=True)
        if not urgentes.empty:
            for _, r in urgentes.head(8).iterrows():
                dias = int(r["Dias_Aberto"])
                st.markdown(f"""
                <div class="alert-card alert-warn">
                  <div class="alert-title">
                    🟠 #{r['Sac']} — {r['Cliente']}
                    <span style="float:right;font-size:0.72rem;color:{GOLD};font-weight:700">{dias} dias</span>
                  </div>
                  <div class="alert-sub">
                    👤 {r['Atendente']} &nbsp;·&nbsp; 📋 {r['Assunto']} &nbsp;·&nbsp; 🧩 {r['Modulo']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    with col_b:
        st.markdown('<span class="sec-t">📊 Clientes com Maior Backlog</span>', unsafe_allow_html=True)
        st.markdown(chart_open(""), unsafe_allow_html=True)
        df_cli_bl = df_bl.groupby("Cliente").size().reset_index(name="Total").sort_values("Total", ascending=False).head(12)
        st.markdown(ranking_html(df_cli_bl, "Cliente", "Total", DANGER), unsafe_allow_html=True)
        st.markdown(chart_close(), unsafe_allow_html=True)

        st.markdown('<span class="sec-t">⚠️ Atendentes com FCR Abaixo da Meta</span>', unsafe_allow_html=True)
        df_fcr_al = df.groupby("Atendente").agg(Total=("Sac","count"), FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
        df_fcr_al["FCR_pct"] = (df_fcr_al["FCR"] / df_fcr_al["Total"] * 100).round(1)
        df_fcr_al = df_fcr_al[(df_fcr_al["FCR_pct"] < 70) & (df_fcr_al["Total"] > 5)].sort_values("FCR_pct")

        if not df_fcr_al.empty:
            for _, r in df_fcr_al.iterrows():
                cor_b = DANGER if r["FCR_pct"] < 50 else ORANGE
                st.markdown(f"""
                <div class="alert-card alert-warn">
                  <div class="alert-title">
                    👤 {r['Atendente']}
                    <span style="float:right;color:{cor_b};font-weight:700">{r['FCR_pct']:.0f}%</span>
                  </div>
                  <div class="alert-sub">{r['Total']:,} chamados · Meta: 70%</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-card alert-info"><div class="alert-title">✅ Todos acima da meta!</div></div>', unsafe_allow_html=True)

    # Sankey origem → módulo → situação
    st.markdown('<span class="sec-t">🔀 Fluxo dos Chamados — Origem → Módulo → Situação</span>', unsafe_allow_html=True)
    st.markdown(chart_open(""), unsafe_allow_html=True)
    try:
        top5o = df["Origem"].value_counts().nlargest(5).index.tolist()
        top5m = df["Modulo"].value_counts().nlargest(5).index.tolist()
        top4s = df["Situacao"].value_counts().nlargest(4).index.tolist()
        df_sk = df[df["Origem"].isin(top5o) & df["Modulo"].isin(top5m) & df["Situacao"].isin(top4s)]
        all_nodes = top5o + top5m + top4s
        nidx = {n: i for i, n in enumerate(all_nodes)}
        src, tgt, val = [], [], []
        for _, r in df_sk.groupby(["Origem","Modulo"]).size().reset_index(name="v").iterrows():
            if r["Origem"] in nidx and r["Modulo"] in nidx:
                src.append(nidx[r["Origem"]]); tgt.append(nidx[r["Modulo"]]); val.append(r["v"])
        for _, r in df_sk.groupby(["Modulo","Situacao"]).size().reset_index(name="v").iterrows():
            if r["Modulo"] in nidx and r["Situacao"] in nidx:
                src.append(nidx[r["Modulo"]]); tgt.append(nidx[r["Situacao"]]); val.append(r["v"])
        ncors = [TEAL]*len(top5o) + [BRAND]*len(top5m) + [GREEN]*len(top4s)
        fig_sk = go.Figure(go.Sankey(
            node=dict(pad=18, thickness=18, label=all_nodes, color=ncors,
                      line=dict(color=BG, width=0.5)),
            link=dict(source=src, target=tgt, value=val, color=f"rgba(139,163,191,0.2)"),
        ))
        fig_sk.update_layout(**pb(320))
        st.plotly_chart(fig_sk, use_container_width=True)
    except Exception as e:
        st.caption(f"Diagrama de fluxo indisponível: {e}")
    st.markdown(chart_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    hoje = date.today()

    # ── HEADER ────────────────────────────────────────────────────────────────
    col_l1, col_tt, col_l2 = st.columns([1, 5, 1], vertical_alignment="center")
    with col_l1:
        if os.path.exists("logo_supra.png"):
            st.image("logo_supra.png", width=110)
    with col_tt:
        st.markdown(f"""
        <div style="text-align:center;padding:4px 0">
          <div style="font-size:1.22rem;font-weight:800;color:{WHITE};letter-spacing:-0.3px">
            Central de Suporte Técnico — SupraMAIS
          </div>
          <div style="font-size:0.73rem;color:{MUTED};margin-top:3px">
            <span class="dot-live"></span>
            Dados em tempo real &nbsp;·&nbsp; Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_l2:
        if os.path.exists("logo_supramais.png"):
            st.image("logo_supramais.png", width=60)

    st.markdown(f"<hr>", unsafe_allow_html=True)

    # ── CARREGAR DADOS ────────────────────────────────────────────────────────
    try:
        df_raw = carregar_dados()
    except Exception as e:
        st.error(f"❌ **Erro ao conectar ao banco.** Detalhe: `{e}`")
        st.stop()
    if df_raw.empty:
        st.warning("⚠️ Nenhum registro retornado.")
        st.stop()

    # ── FILTROS VISÍVEIS ──────────────────────────────────────────────────────
    st.markdown(f'<div class="chart-card" style="margin-bottom:14px">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">🔍 Filtros Globais — aplicados em todas as abas</div>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([1.2, 1.2, 1.8, 1.8, 1.8, 0.8])

    data_min = df_raw["Data_abertura"].dropna().min().date()
    data_max = max(df_raw["Data_abertura"].dropna().max().date(), hoje)

    with fc1:
        di = st.date_input("Data Inicial", value=hoje - timedelta(days=30),
                            min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
    with fc2:
        df_ = st.date_input("Data Final", value=hoje,
                             min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
    with fc3:
        atendentes = sorted(df_raw["Atendente"].dropna().unique())
        sel_at = st.multiselect("Atendente", atendentes, placeholder="Todos")
    with fc4:
        situacoes = sorted(df_raw["Situacao"].dropna().unique())
        sel_sit = st.multiselect("Situação", situacoes, placeholder="Todas")
    with fc5:
        origens = sorted(df_raw["Origem"].dropna().unique())
        sel_or = st.multiselect("Origem / Canal", origens, placeholder="Todas")
    with fc6:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()

    # Aplicar filtros
    df = df_raw.copy()
    if di <= df_:
        df = df[(df["Data_abertura"].dt.date >= di) & (df["Data_abertura"].dt.date <= df_)]
    if sel_at:  df = df[df["Atendente"].isin(sel_at)]
    if sel_sit: df = df[df["Situacao"].isin(sel_sit)]
    if sel_or:  df = df[df["Origem"].isin(sel_or)]

    st.markdown(f"""
    <div style="font-size:0.7rem;color:{MUTED};margin-top:6px">
      📋 <b style="color:{WHITE}">{len(df):,}</b> chamados no período filtrado
      &nbsp;·&nbsp; de <b style="color:{WHITE}">{di.strftime('%d/%m/%Y')}</b>
      até <b style="color:{WHITE}">{df_.strftime('%d/%m/%Y')}</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── KPI STRIP ─────────────────────────────────────────────────────────────
    mes_a, ano_a = hoje.month, hoje.year
    df_mes = df_raw[(df_raw["Mes_abertura"]==mes_a) & (df_raw["Ano_abertura"]==ano_a)]
    df_mes_ant = df_raw[
        (df_raw["Mes_abertura"]==(mes_a-1 or 12)) &
        (df_raw["Ano_abertura"]==(ano_a if mes_a>1 else ano_a-1))
    ]

    hoje_q   = df_raw[df_raw["Data_abertura"].dt.date == hoje].shape[0]
    sol_h    = df_raw[df_raw["Data_Solucao"].dt.date == hoje].shape[0]
    backlog  = df_raw[df_raw["Data_Solucao"].isna()].shape[0]
    tot_mes  = len(df_mes)
    tot_ant  = len(df_mes_ant)
    fcr_mes  = (df_mes["Finalizado_Mesmo_Dia"].sum() / tot_mes * 100) if tot_mes > 0 else 0

    df_res = df_raw[df_raw["TMR_h"] > 0]
    tmr_h  = df_res["TMR_h"].mean() if not df_res.empty else 0
    tmr_str = f"{tmr_h:.0f}h" if tmr_h < 72 else f"{tmr_h/24:.1f} dias"

    tot_fil   = len(df)
    res_fil   = df["Data_Solucao"].notna().sum()
    enc_pct   = res_fil / tot_fil * 100 if tot_fil > 0 else 0

    delta_m  = tot_mes - tot_ant
    d_cls    = "b-red" if delta_m > 0 else "b-green"
    d_str    = f"{'↑' if delta_m>0 else '↓'} {abs(delta_m)} vs mês ant."
    fcr_cls  = "b-green" if fcr_mes >= 70 else ("b-gold" if fcr_mes >= 50 else "b-red")

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:16px">
      {kpi("Abertos Hoje",    f"{hoje_q:,}",   "novos chamados",     "📥", BRAND,  "",      "b-muted")}
      {kpi("Resolvidos Hoje", f"{sol_h:,}",    "encerrados hoje",    "✅", GREEN,  "",      "b-muted")}
      {kpi("Mês Atual",       f"{tot_mes:,}",  f"{hoje.strftime('%b/%Y')}", "📅", TEAL, d_str, d_cls)}
      {kpi("FCR do Mês",      f"{fcr_mes:.1f}%", "1º contato",      "⚡", GOLD,  "Meta: 70%", fcr_cls,
           tip_text="Resolução no Primeiro Contato: % de chamados resolvidos sem necessidade de retorno do cliente.")}
      {kpi("TMR Geral",       tmr_str,         "tempo médio resolução","⏱️", PURPLE, "",   "b-muted",
           tip_text="Tempo Médio de Resolução: calculado entre Data de Abertura e Data de Solução dos chamados fechados.")}
      {kpi("Backlog Total",   f"{backlog:,}",  "sem solução",        "🗂️", ORANGE if backlog>30 else GREEN, "", "b-muted",
           tip_text="Fila de Pendências: chamados abertos que ainda não receberam solução.")}
    </div>
    """, unsafe_allow_html=True)

    # ── ABAS ─────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Resumo Geral",
        "🏢 Clientes",
        "👥 Atendentes",
        "🎫 Situação dos Chamados",
        "📈 SLA & KPIs",
        "🚨 Alertas & Gestão",
    ])

    with tabs[0]: aba_resumo(df, df_raw, hoje)
    with tabs[1]: aba_clientes(df)
    with tabs[2]: aba_atendentes(df)
    with tabs[3]: aba_situacao(df)
    with tabs[4]: aba_sla(df)
    with tabs[5]: aba_alertas(df, df_raw)


if __name__ == "__main__":
    main()
