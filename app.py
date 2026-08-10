# =============================================================================
# Central de Suporte — SupraMAIS  |  Command Center
# Stack: Streamlit + pymssql + pandas + plotly
# =============================================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pymssql
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import os, warnings
import calendar

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Central de Suporte · SupraMAIS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)
components.html('<script>setTimeout(()=>window.parent.location.reload(),1800000)</script>', height=0)

# ── PALETA ─────────────────────────────────────────────────────────────────────
BG     = "#0F172A"
CARD   = "#1E293B"
CARD2  = "#334155"
BRAND  = "#CC2020"
TEAL   = "#00CEC9"
GREEN  = "#00B894"
ORANGE = "#E17055"
GOLD   = "#FDCB6E"
PURPLE = "#A29BFE"
WHITE  = "#F8FAFC"
MUTED  = "#94A3B8"
BORDER = "#334155"
DANGER = "#E63946"
CORES  = [BRAND, TEAL, ORANGE, GOLD, GREEN, PURPLE, "#FD79A8", "#74B9FF", "#55EFC4", "#DFE6E9"]

# ── CSS LIMPO (Apenas Componentes Customizados) ────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{ font-family:'Inter',sans-serif !important; box-sizing:border-box; }}
.block-container {{ padding:0.4rem 1.2rem 1rem !important; max-width:100% !important; }}
header[data-testid="stHeader"] {{ background:transparent !important; }}

/* ── KPI grid (Compacto) ── */
.kpi-grid {{
  display:grid;
  grid-template-columns:repeat(7,1fr);
  gap:8px; margin-bottom:8px;
}}
@media(max-width:1200px) {{ .kpi-grid {{ grid-template-columns:repeat(4,1fr); }} }}
@media(max-width:900px)  {{ .kpi-grid {{ grid-template-columns:repeat(3,1fr); }} }}
@media(max-width:600px)  {{ .kpi-grid {{ grid-template-columns:repeat(2,1fr); }} }}
@media(max-width:380px)  {{ .kpi-grid {{ grid-template-columns:1fr; }} }}

.kpi-card {{
  background:{CARD}; border:1px solid {BORDER};
  border-radius:10px; padding:8px 12px 6px;
  position:relative; overflow:hidden; min-height:74px;
}}
.kpi-glow {{ position:absolute; top:0; left:0; right:0; height:3px; border-radius:10px 10px 0 0; }}
.kpi-icon {{ position:absolute; right:8px; top:8px; font-size:1.3rem; opacity:0.08; }}
.kpi-label {{
  font-size:0.58rem; font-weight:700; letter-spacing:0.4px;
  text-transform:uppercase; color:{MUTED} !important; margin-bottom:2px;
}}
.kpi-val {{ font-size:1.4rem; font-weight:800; color:{WHITE} !important; line-height:1; }}
.kpi-sub {{ font-size:0.60rem; color:{MUTED} !important; margin-top:2px; }}
.kpi-badge {{
  display:inline-block; padding:1px 6px; border-radius:20px;
  font-size:0.55rem; font-weight:700; margin-top:2px;
}}
.b-green  {{ background:rgba(0,184,148,.18);  color:{GREEN};  }}
.b-red    {{ background:rgba(230,57,70,.18);   color:{DANGER}; }}
.b-orange {{ background:rgba(225,112,85,.18);  color:{ORANGE}; }}
.b-gold   {{ background:rgba(253,203,110,.18); color:{GOLD};   }}
.b-muted  {{ background:rgba(148,163,184,.12); color:{MUTED};  }}
.b-teal   {{ background:rgba(0,206,201,.18);   color:{TEAL};   }}

/* ── Chart card (Compacto) ── */
.chart-card {{
  background:{CARD}; border:1px solid {BORDER};
  border-radius:10px; padding:10px 12px 6px; margin-bottom:8px;
}}
.chart-title {{
  font-size:0.65rem; font-weight:700; text-transform:uppercase;
  letter-spacing:0.5px; color:{MUTED} !important;
  border-bottom:1px solid {BORDER}; padding-bottom:4px; margin-bottom:6px;
}}

/* ── Section title ── */
.sec-t {{
  font-size:0.68rem; font-weight:700; text-transform:uppercase;
  letter-spacing:0.8px; color:{MUTED} !important;
  border-left:3px solid {TEAL}; padding-left:8px;
  margin:10px 0 6px; display:block;
}}

/* ── Tooltip ── */
.tip {{ position:relative; display:inline-block; cursor:help; border-bottom:1px dashed {MUTED}; }}
.tip::after {{
  content:attr(data-tip);
  position:absolute; bottom:120%; left:50%; transform:translateX(-50%);
  background:{CARD2}; color:{WHITE}; border:1px solid {BORDER};
  padding:6px 10px; border-radius:8px; font-size:0.7rem; font-weight:400;
  white-space:normal; width:220px; opacity:0; pointer-events:none;
  transition:opacity .2s; z-index:9999; line-height:1.4;
}}
.tip:hover::after {{ opacity:1; }}

/* ── Filtro bar ── */
.filter-bar-title {{
  font-size:0.62rem; font-weight:700; text-transform:uppercase;
  letter-spacing:0.6px; color:{TEAL} !important;
  display:flex; align-items:center; gap:6px; margin-bottom:4px;
}}

/* ── Alerta cards ── */
.alert-card {{
  background:rgba(230,57,70,.08); border:1px solid rgba(230,57,70,.25);
  border-left:4px solid {DANGER}; border-radius:10px;
  padding:8px 12px; margin-bottom:6px;
}}
.alert-warn {{
  background:rgba(253,203,110,.07); border:1px solid rgba(253,203,110,.2);
  border-left-color:{GOLD};
}}
.alert-info {{
  background:rgba(0,206,201,.07); border:1px solid rgba(0,206,201,.18);
  border-left-color:{TEAL};
}}
.alert-title {{ font-size:0.75rem; font-weight:700; color:{WHITE} !important; }}
.alert-sub   {{ font-size:0.68rem; color:{MUTED} !important; margin-top:2px; line-height:1.4; }}

/* ── Ranking ── */
.rank-row {{
  display:flex; align-items:center; gap:8px;
  padding:4px 0; border-bottom:1px solid {BORDER};
}}
.rank-name {{ font-size:0.75rem; color:{WHITE} !important; flex:1; font-weight:500;
              white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.rank-bg   {{ flex:2; height:5px; background:{CARD2}; border-radius:3px; overflow:hidden; }}
.rank-fill {{ height:5px; border-radius:3px; }}
.rank-val  {{ font-size:0.75rem; font-weight:700; min-width:32px; text-align:right; }}

/* ── Tabela atendentes ── */
.att-table {{ width:100%; border-collapse:collapse; font-size:0.75rem; }}
.att-table th {{
  font-size:0.60rem; font-weight:700; text-transform:uppercase;
  letter-spacing:0.5px; color:{MUTED} !important;
  padding:6px 8px; border-bottom:1px solid {BORDER}; text-align:left;
}}
.att-table td {{ color:{WHITE} !important; padding:6px 8px; border-bottom:1px solid {BORDER}; }}
.att-table tr:hover td {{ background:{CARD2}; }}
.barcell {{ display:flex; align-items:center; gap:6px; }}
.bbar-bg {{ flex:1; height:5px; background:{CARD2}; border-radius:3px; overflow:hidden; }}
.bbar    {{ height:5px; border-radius:3px; }}

/* ── Pulse ── */
@keyframes pulse {{
  0%   {{ box-shadow:0 0 0 0 rgba(0,206,201,.6); }}
  70%  {{ box-shadow:0 0 0 6px rgba(0,206,201,0); }}
  100% {{ box-shadow:0 0 0 0 rgba(0,206,201,0); }}
}}
.dot-live {{
  display:inline-block; width:6px; height:6px;
  background:{GREEN}; border-radius:50%;
  animation:pulse 2s infinite; margin-right:5px; vertical-align:middle;
}}

/* ── hr ── */
hr {{ border-color:{BORDER} !important; margin:4px 0 8px !important; }}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ────────────────────────────────────────────────────────────────────
def pb(h=300, **kw):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=8, b=8, l=6, r=6), height=h,
        font=dict(family="Inter,sans-serif", color=MUTED, size=11),
        **kw,
    )

def co(title=""):
    t = f'<div class="chart-title">{title}</div>' if title else ""
    return f'<div class="chart-card">{t}'

def cc():
    return '</div>'

def tip(term, desc):
    safe = desc.replace('"', '&quot;')
    return f'<span class="tip" data-tip="{safe}">{term}</span>'

def kpi(label, val, sub="", icon="📊", color=TEAL, badge="", bcls="b-muted", tip_text=""):
    safe_tip = tip_text.replace('"', '&quot;')
    ti = f' <span class="tip" data-tip="{safe_tip}" style="font-size:.65rem;opacity:.5">ⓘ</span>' if tip_text else ""
    ba = f'<span class="kpi-badge {bcls}">{badge}</span>' if badge else ""
    return f"""<div class="kpi-card">
  <div class="kpi-glow" style="background:{color}"></div>
  <span class="kpi-icon">{icon}</span>
  <div class="kpi-label">{label}{ti}</div>
  <div class="kpi-val">{val}</div>
  <div class="kpi-sub">{sub} {ba}</div>
</div>"""

def rank_html(df_r, cn, cv, color=TEAL):
    medals = ["🥇","🥈","🥉"]
    top = df_r[cv].max() if not df_r.empty and df_r[cv].max() > 0 else 1
    rows = ""
    for i, row in enumerate(df_r.itertuples(), 1):
        pct = int(getattr(row, cv) / top * 100)
        pos = medals[i-1] if i <= 3 else f'<span style="font-size:.70rem;color:{MUTED};width:22px;text-align:center">{i}</span>'
        rows += f"""<div class="rank-row">
  <span style="font-size:.90rem">{pos}</span>
  <span class="rank-name">{getattr(row, cn)}</span>
  <div class="rank-bg"><div class="rank-fill" style="width:{pct}%;background:{color}"></div></div>
  <span class="rank-val" style="color:{color}">{getattr(row, cv):,}</span>
</div>"""
    return rows

def safe_pct(num, den):
    return round(num / den * 100, 1) if den and den > 0 else 0.0

def tmr_fmt(h):
    if pd.isna(h) or h < 0:
        return "N/D"
    if h < 24:
        return f"{h:.1f}h"
    return f"{h/24:.1f} dias"


# ── QUERY & CACHE (SQL ATUALIZADO COM HORAS E FORMATO BR) ────────────────────
@st.cache_data(ttl=1800, show_spinner="Carregando dados…")
def carregar_dados() -> pd.DataFrame:
    cfg = st.secrets["database"]
    srv = cfg["server"]
    if "," in srv:
        host, port = srv.split(",", 1)
        port = int(port)
    else:
        host, port = srv, 1433
    conn = pymssql.connect(
        server=host, port=port,
        database=cfg["database"],
        user=cfg["username"],
        password=cfg["password"],
        login_timeout=30,
    )
    SQL_QUERY = """
    SELECT
        Sac, 
        CONVERT(VARCHAR(10), Data_abertura, 103) + ' ' + CONVERT(VARCHAR(8), Data_abertura, 108) AS Data_abertura,
        Dia_abertura, Mes_abertura, Ano_abertura,
        CONVERT(VARCHAR(10), [Data Solucao], 103) + ' ' + CONVERT(VARCHAR(8), [Data Solucao], 108) AS Data_Solucao,
        [Cliente Codigo] AS Cliente_Codigo, Cliente, Contato,
        Assunto, Motivo, Motivocodigo, Modulo, Situacao, Atendente, Origem,
        Finalizado_Mesmo_Dia, Tipo
    FROM sgrp_atendimentos_geral
    WHERE Ano_abertura >= 2020;
    """
    df = pd.read_sql(SQL_QUERY, conn)
    conn.close()
    
    # Conversão incluindo as horas
    for col in ["Data_abertura", "Data_Solucao"]:
        df[col] = pd.to_datetime(df[col], format="%d/%m/%Y %H:%M:%S", errors="coerce")
        
    df["TMR_h"] = (df["Data_Solucao"] - df["Data_abertura"]).dt.total_seconds() / 3600
    return df

@st.cache_data(ttl=3600, show_spinner="Carregando contratos vigentes…")
def carregar_contratos() -> pd.DataFrame:
    cfg = st.secrets["database"]
    srv = cfg["server"]
    if "," in srv:
        host, port = srv.split(",", 1)
        port = int(port)
    else:
        host, port = srv, 1433
    conn = pymssql.connect(
        server=host, port=port,
        database=cfg["database"],
        user=cfg["username"],
        password=cfg["password"],
        login_timeout=30,
    )
    SQL_QUERY = """
    SELECT 
        ct.fk_cliente_fornecedor AS CLIENTE_codigo, 
        cf.nome AS RAZAO, 
        cf.cnpj AS CNPJ,
        CASE ct.id_situacao 
            WHEN 1 THEN 'VIGENTE' 
            WHEN 2 THEN 'FINALIZADO' 
            WHEN 3 THEN 'RESCINDIDO' 
            WHEN 4 THEN 'SUSPENSO'
        END AS SITUACAO,
        fl.clifor_codigo AS cod_matrix
    FROM sgc.dbo.contrato ct
    JOIN sgc.dbo.cliente_fornecedor cf ON cf.codigo = ct.fk_cliente_fornecedor
    JOIN sgc.dbo.cidade c ON c.codigo = cf.cid_codigo
    JOIN sgc.dbo.tipo_contrato tc ON tc.codigo = ct.fk_tipo_contrato
    LEFT JOIN sgc.dbo.filial fl ON fl.clifor_codigo_filial = cf.codigo
    WHERE ct.id_situacao = 1
    ORDER BY cf.nome
    """
    df = pd.read_sql(SQL_QUERY, conn)
    conn.close()
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 0 — HOJE
# ══════════════════════════════════════════════════════════════════════════════
def aba_hoje(df_raw, hoje):
    df_h = df_raw[df_raw["Data_abertura"].dt.date == hoje].copy()
    df_sol_h = df_raw[df_raw["Data_Solucao"].dt.date == hoje]

    ab_h   = len(df_h)
    sol_h  = len(df_sol_h)
    backlog = df_raw[df_raw["Data_Solucao"].isna()].shape[0]
    fcr_h  = safe_pct(df_h["Finalizado_Mesmo_Dia"].sum(), ab_h)
    
    # >= 0 em vez de > 0
    tmr_h_v = df_sol_h[df_sol_h["TMR_h"] >= 0]["TMR_h"].mean()
    
    # Contagem de clientes diferentes atendidos hoje
    clientes_hj = df_h["Cliente"].nunique()

    # KPIs do dia
    st.markdown(f"""
    <div class="kpi-grid">
      {kpi("Abertos Hoje",      f"{ab_h}",       "novos chamados hoje",      "📥", BRAND)}
      {kpi("Resolvidos Hoje",   f"{sol_h}",      "fechamentos hoje",         "✅", GREEN)}
      {kpi("FCR do Dia", f"{fcr_h:.1f}%",        "1º contato",               "⚡", GOLD,
           "Meta: 70%", "b-green" if fcr_h>=70 else "b-red",
           tip_text="Resolução no Primeiro Contato: % dos chamados de hoje finalizados sem retorno.")}
      {kpi("TMR do Dia", tmr_fmt(tmr_h_v),       "tempo médio resolução",    "⏱️", PURPLE,
           tip_text="Tempo Médio de Resolução: calculado entre abertura e solução dos chamados encerrados hoje.")}
      {kpi("Backlog Total",     f"{backlog:,}",  "ainda sem solução",        "🗂️", ORANGE if backlog>50 else GREEN,
           tip_text="Fila de pendências: total de chamados abertos sem data de solução, independente do período.")}
      {kpi("Ativos Hoje",       str(df_h["Atendente"].nunique()), "atendentes com chamados", "👥", TEAL)}
      {kpi("Clientes Hoje",     f"{clientes_hj}", "atendidos hoje",         "🏢", PURPLE,
           tip_text="Quantidade de clientes distintos que abriram chamados na data de hoje.")}
    </div>
    """, unsafe_allow_html=True)

    if df_h.empty:
        st.markdown(f"""
        <div style="text-align:center;padding:40px;color:{MUTED}">
          <div style="font-size:2rem">🌅</div>
          <div style="font-size:1rem;margin-top:8px">Nenhum chamado aberto hoje ainda.</div>
        </div>""", unsafe_allow_html=True)
        return

    # Preparar base unificada de total por atendente
    tot_ag = df_h.groupby("Atendente").size()

    # Linha 1: Gráficos de Atendentes
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        try:
            st.markdown(co("📊 Atendimentos Hoje: Atendente × Canal"), unsafe_allow_html=True)
            df_at_or = df_h.groupby(["Atendente", "Origem"]).size().reset_index(name="Qtd")
            
            df_at_or["Atendente_Lbl"] = df_at_or["Atendente"].apply(lambda x: f"{x} [{tot_ag[x]}]")
            ordem_lbl = [f"{x} [{tot_ag[x]}]" for x in tot_ag.sort_values().index.tolist()]
            
            fig = px.bar(df_at_or, y="Atendente_Lbl", x="Qtd", color="Origem", orientation="h", text="Qtd",
                         category_orders={"Atendente_Lbl": ordem_lbl},
                         color_discrete_sequence=CORES, barmode="stack")
            
            fig.update_traces(textposition="inside", textfont=dict(size=11, color=WHITE), insidetextanchor="middle")
            fig.update_layout(**pb(max(240, len(ordem_lbl)*35),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                yaxis_title="", xaxis_title="",
                legend=dict(orientation="v", title="", font=dict(color=WHITE, size=10))
            ))
            fig.update_layout(margin=dict(t=25, b=6, l=6, r=6)) 
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with r1c2:
        try:
            st.markdown(co("🧩 Mapa de Calor Hoje: Atendente × Módulo"), unsafe_allow_html=True)
            top_mod_h = df_h["Modulo"].value_counts().nlargest(5).index
            df_hm = df_h.copy()
            df_hm["Mod_x"] = df_hm["Modulo"].apply(lambda x: x if x in top_mod_h else "Outros")
            
            df_hm["Atendente_Lbl"] = df_hm["Atendente"].apply(lambda x: f"{x} [{tot_ag[x]}]")
            
            piv_h = df_hm.groupby(["Atendente_Lbl", "Mod_x"]).size().reset_index(name="Qtd")\
                      .pivot(index="Atendente_Lbl", columns="Mod_x", values="Qtd").fillna(0)
            
            piv_h = piv_h.reindex(ordem_lbl).fillna(0)
            
            fig_mod = px.imshow(piv_h, text_auto=True, aspect="auto",
                                color_continuous_scale=[[0,CARD2],[0.5,CARD],[1,PURPLE]])
            fig_mod.update_coloraxes(showscale=False)
            fig_mod.update_traces(textfont=dict(color=WHITE))
            fig_mod.update_layout(**pb(max(240, len(ordem_lbl)*35),
                xaxis_title="", yaxis_title="",
                xaxis=dict(side="top") 
            ))
            fig_mod.update_layout(margin=dict(t=25, b=6, l=6, r=6))
            
            st.plotly_chart(fig_mod, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    # Linha 2: Top Clientes, Motivos, Origem e Situação
    r2c1, r2c2, r2c3 = st.columns([1.5, 1.5, 1])

    with r2c1:
        st.markdown(co("🏆 Top 10 Clientes — Hoje"), unsafe_allow_html=True)
        dr_h = df_h.groupby("Cliente").size().reset_index(name="Total").sort_values("Total", ascending=False).head(10)
        if not dr_h.empty:
            st.markdown(rank_html(dr_h, "Cliente", "Total", TEAL), unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding:20px;color:#8BA3BF'>Nenhum cliente ainda.</div>", unsafe_allow_html=True)
        st.markdown(cc(), unsafe_allow_html=True)

    with r2c2:
        try:
            st.markdown(co("🎯 Principais Motivos — Hoje"), unsafe_allow_html=True)
            df_mot_h = df_h.groupby("Motivo").size().reset_index(name="Qtd").nlargest(8,"Qtd").sort_values("Qtd")
            fig2 = px.bar(df_mot_h, y="Motivo", x="Qtd", orientation="h", text="Qtd",
                           color="Qtd", color_continuous_scale=[[0,CARD2],[1,BRAND]])
            fig2.update_coloraxes(showscale=False)
            fig2.update_traces(textposition="outside", cliponaxis=False,
                                textfont=dict(color=WHITE))
            fig2.update_layout(**pb(max(180, len(df_mot_h)*28),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                yaxis_title="", xaxis_title=""))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with r2c3:
        try:
            st.markdown(co("📡 Origem — Hoje"), unsafe_allow_html=True)
            df_or_h = df_h.groupby("Origem").size().reset_index(name="Qtd")
            fig3 = px.pie(df_or_h, names="Origem", values="Qtd", hole=0.5,
                           color_discrete_sequence=CORES)
            fig3.update_traces(textposition="inside", textinfo="percent+label",
                                textfont=dict(size=10, color=WHITE))
            fig3.update_layout(**pb(180, showlegend=False))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

        try:
            st.markdown(co("🔵 Situação — Hoje"), unsafe_allow_html=True)
            df_sit_h = df_h.groupby("Situacao").size().reset_index(name="Qtd")
            fig4 = px.pie(df_sit_h, names="Situacao", values="Qtd", hole=0.5,
                           color_discrete_sequence=CORES)
            fig4.update_traces(textposition="outside", textinfo="label+percent",
                                textfont=dict(size=10, color=WHITE))
            fig4.update_layout(**pb(180, showlegend=False))
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    # ===== AUDITORIA DE DADOS =====
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 Auditoria e Depuração (Comparar com Excel)", expanded=False):
        st.markdown("**1. Query SQL Executada no Banco:**")
        st.code("""
SELECT
    Sac, 
    CONVERT(VARCHAR(10), Data_abertura, 103) + ' ' + CONVERT(VARCHAR(8), Data_abertura, 108) AS Data_abertura,
    Dia_abertura, Mes_abertura, Ano_abertura,
    CONVERT(VARCHAR(10), [Data Solucao], 103) + ' ' + CONVERT(VARCHAR(8), [Data Solucao], 108) AS Data_Solucao,
    [Cliente Codigo] AS Cliente_Codigo, Cliente, Contato,
    Assunto, Motivo, Motivocodigo, Modulo, Situacao, Atendente, Origem,
    Finalizado_Mesmo_Dia, Tipo
FROM sgrp_atendimentos_geral
WHERE Ano_abertura >= 2020;
        """, language="sql")
        
        st.markdown("**2. Dados Brutos (Somente chamados ABERTOS hoje):**")
        st.dataframe(df_h.reset_index(drop=True), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
#  NOVA ABA — POR HORA
# ══════════════════════════════════════════════════════════════════════════════
def aba_por_hora(df_base, hoje):
    st.markdown('<span class="sec-t">📅 Filtro de Data (Exclusivo para esta análise)</span>', unsafe_allow_html=True)
    
    c_filt, _ = st.columns([2, 8])
    with c_filt:
        data_filtro = st.date_input("Escolha o dia para analisar o fluxo", value=hoje, format="DD/MM/YYYY", key="filtro_hora")
    
    df_dia = df_base[df_base["Data_abertura"].dt.date == data_filtro].copy()
    
    if df_dia.empty:
        st.markdown(f"""
        <div style="text-align:center;padding:40px;color:{MUTED}">
          <div style="font-size:2rem">📭</div>
          <div style="font-size:1rem;margin-top:8px">Nenhum chamado aberto em {data_filtro.strftime('%d/%m/%Y')} com os filtros selecionados.</div>
        </div>""", unsafe_allow_html=True)
        return

    df_dia["Hora_Int"] = df_dia["Data_abertura"].dt.hour
    df_dia["Hora"] = df_dia["Hora_Int"].apply(lambda x: f"{x:02d}:00")
    
    df_hora = df_dia.groupby("Hora").size().reset_index(name="Qtd")
    pico_hora = df_hora.iloc[df_hora['Qtd'].idxmax()]['Hora'] if not df_hora.empty else "N/A"
    pico_qtd = df_hora['Qtd'].max() if not df_hora.empty else 0
    
    horas_ativas = df_dia["Hora"].nunique()
    media_hora = len(df_dia) / horas_ativas if horas_ativas > 0 else 0
    
    st.markdown(f"""<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:12px">
      {kpi("Total no Dia", f"{len(df_dia):,}", "com os filtros aplicados", "📋", TEAL)}
      {kpi("Atendentes", f"{df_dia['Atendente'].nunique()}", "com chamados registrados", "👥", BRAND)}
      {kpi("Clientes", f"{df_dia['Cliente'].nunique()}", "atendidos na data", "🏢", PURPLE)}
      {kpi("Média por Hora", f"{media_hora:.1f}", "chamados por hora ativa", "⏱️", GREEN)}
      {kpi("Pico de Volume", f"{pico_hora}", f"com {pico_qtd} chamados neste horário", "🔥", ORANGE)}
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        try:
            st.markdown(co(f"📊 Fluxo de Chamados por Hora × Atendente"), unsafe_allow_html=True)
            dh_at = df_dia.groupby(["Hora", "Atendente"]).size().reset_index(name="Qtd")
            fig1 = px.bar(dh_at, x="Hora", y="Qtd", color="Atendente", text="Qtd",
                          color_discrete_sequence=CORES)
            fig1.update_traces(textposition="inside", textfont=dict(size=10, color=WHITE))
            fig1.update_layout(**pb(320, xaxis_title="", yaxis_title="Volume de Chamados",
                                legend=dict(orientation="v", title="", font=dict(color=WHITE, size=9))))
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            
    with c2:
        try:
            st.markdown(co("🧩 Fluxo de Chamados por Hora × Módulo (Top 5)"), unsafe_allow_html=True)
            top5m = df_dia["Modulo"].value_counts().nlargest(5).index
            df_hm = df_dia.copy()
            df_hm["Mod_x"] = df_hm["Modulo"].apply(lambda x: x if x in top5m else "Outros")
            dh_mod = df_hm.groupby(["Hora", "Mod_x"]).size().reset_index(name="Qtd")
            fig2 = px.bar(dh_mod, x="Hora", y="Qtd", color="Mod_x", text="Qtd",
                          color_discrete_sequence=CORES)
            fig2.update_traces(textposition="inside", textfont=dict(size=10, color=WHITE))
            fig2.update_layout(**pb(320, xaxis_title="", yaxis_title="Volume de Chamados",
                                legend=dict(orientation="v", title="", font=dict(color=WHITE, size=9))))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)

    st.markdown('<span class="sec-t">📋 Detalhamento Cronológico dos Chamados</span>', unsafe_allow_html=True)
    
    col_f, _ = st.columns([3, 7])
    with col_f:
        busca = st.text_input("🔍 Filtrar na tabela abaixo:", placeholder="Busque por SAC, Cliente, Assunto...", key="busca_hora")
    
    cols_disp = ["Hora", "Sac", "Atendente", "Cliente", "Modulo", "Situacao", "Origem", "Assunto"]
    valid_cols = [c for c in cols_disp if c in df_dia.columns]
    
    df_show = df_dia.sort_values(["Hora_Int", "Sac"])[valid_cols].reset_index(drop=True)
    
    if busca:
        busca_lower = busca.lower()
        mask = df_show.astype(str).apply(lambda x: x.str.lower().str.contains(busca_lower)).any(axis=1)
        df_show = df_show[mask]
        
    st.dataframe(df_show, width="stretch", height=300)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 1 — RESUMO GERAL
# ══════════════════════════════════════════════════════════════════════════════
def aba_resumo(df):
    c1, c2 = st.columns([3, 2])

    with c1:
        try:
            st.markdown(co("📊 Volume Diário + Média Móvel 7 Dias"), unsafe_allow_html=True)
            dd = df.groupby(df["Data_abertura"].dt.date).size().reset_index(name="Qtd")
            dd.columns = ["Data","Qtd"]
            dd = dd.sort_values("Data")
            dd["MM7"] = dd["Qtd"].rolling(7, min_periods=1).mean().round(1)
            fig = go.Figure()
            fig.add_bar(x=dd["Data"], y=dd["Qtd"], name="Chamados",
                         marker_color=BRAND, opacity=0.7)
            fig.add_scatter(x=dd["Data"], y=dd["MM7"], mode="lines", name="Média 7d",
                             line=dict(color=TEAL, width=2.5))
            fig.update_layout(**pb(250,
                xaxis=dict(showgrid=False, color=MUTED),
                yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED),
                legend=dict(orientation="h", y=1.12, x=0, font=dict(color=WHITE)),
                bargap=0.25))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with c2:
        try:
            st.markdown(co("🔵 Situação Atual"), unsafe_allow_html=True)
            ds = df.groupby("Situacao").size().reset_index(name="Qtd")
            fig2 = px.pie(ds, names="Situacao", values="Qtd", hole=0.52,
                           color_discrete_sequence=CORES)
            fig2.update_traces(textposition="outside", textinfo="label+percent",
                                textfont=dict(size=10, color=WHITE),
                                marker=dict(line=dict(color=BG, width=1.5)))
            fig2.update_layout(**pb(250, showlegend=False))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    c3, c4 = st.columns([3, 2])
    with c3:
        try:
            st.markdown(co("🎯 Principais Motivos de Contato (Treemap)"), unsafe_allow_html=True)
            dm = df.groupby("Motivo").size().reset_index(name="Qtd").nlargest(20,"Qtd")
            fig3 = px.treemap(dm, path=["Motivo"], values="Qtd",
                               color="Qtd",
                               color_continuous_scale=[[0,CARD2],[0.5,BRAND],[1,DANGER]])
            fig3.update_coloraxes(showscale=False)
            fig3.update_traces(textfont=dict(size=11, color=WHITE),
                                marker=dict(line=dict(width=1.5, color=BG)))
            fig3.update_layout(**pb(300))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with c4:
        try:
            st.markdown(co("📡 Canais de Entrada (Origem)"), unsafe_allow_html=True)
            dor = df.groupby("Origem").size().reset_index(name="Qtd").sort_values("Qtd")
            fig4 = px.bar(dor, y="Origem", x="Qtd", orientation="h", text="Qtd",
                           color="Qtd", color_continuous_scale=[[0,CARD2],[1,TEAL]])
            fig4.update_coloraxes(showscale=False)
            fig4.update_traces(textposition="outside", cliponaxis=False,
                                textfont=dict(color=WHITE))
            fig4.update_layout(**pb(300, xaxis=dict(showgrid=False),
                                     yaxis=dict(showgrid=False),
                                     yaxis_title="", xaxis_title=""))
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    try:
        st.markdown(co("📈 Tendência Mensal — Abertos vs Resolvidos"), unsafe_allow_html=True)
        dm2 = df.copy()
        dm2["MesAno"] = dm2["Data_abertura"].dt.to_period("M").astype(str)
        ab_m = dm2.groupby("MesAno").size().reset_index(name="Abertos")
        re_m = dm2[dm2["Data_Solucao"].notna()].groupby("MesAno").size().reset_index(name="Resolvidos")
        tr = ab_m.merge(re_m, on="MesAno", how="left").fillna(0).sort_values("MesAno")
        fig5 = go.Figure()
        fig5.add_scatter(x=tr["MesAno"], y=tr["Abertos"], mode="lines+markers",
                          name="Abertos", line=dict(color=BRAND, width=2.5), marker=dict(size=5))
        fig5.add_scatter(x=tr["MesAno"], y=tr["Resolvidos"], mode="lines+markers",
                          name="Resolvidos", line=dict(color=GREEN, width=2.5), marker=dict(size=5))
        fig5.update_layout(**pb(220,
            xaxis=dict(showgrid=False, color=MUTED),
            yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=WHITE))))
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown(cc(), unsafe_allow_html=True)
    except Exception as e:
        st.markdown(cc(), unsafe_allow_html=True)
        st.warning(f"Gráfico indisponível: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 2 — CLIENTES
# ══════════════════════════════════════════════════════════════════════════════
def aba_clientes(df):
    c1, c2 = st.columns([3, 2])
    with c1:
        try:
            st.markdown(co("📦 Volume de Chamados por Cliente (Treemap)"), unsafe_allow_html=True)
            dc = df.groupby("Cliente").size().reset_index(name="Qtd").nlargest(30,"Qtd")
            fig = px.treemap(dc, path=["Cliente"], values="Qtd",
                              color="Qtd",
                              color_continuous_scale=[[0,CARD2],[0.4,BRAND],[1,DANGER]])
            fig.update_coloraxes(showscale=False)
            fig.update_traces(textfont=dict(size=11,color=WHITE),
                               marker=dict(line=dict(width=1.5,color=BG)))
            fig.update_layout(**pb(340))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with c2:
        st.markdown(co("🏆 Top 15 Clientes"), unsafe_allow_html=True)
        dr = df.groupby("Cliente").size().reset_index(name="Total").sort_values("Total",ascending=False).head(15)
        st.markdown(rank_html(dr,"Cliente","Total",TEAL), unsafe_allow_html=True)
        st.markdown(cc(), unsafe_allow_html=True)

    c3, c4 = st.columns([3, 2])
    with c3:
        try:
            st.markdown(co("🌐 Hierarquia: Cliente → Módulo → Situação (Top 10)"), unsafe_allow_html=True)
            top10 = df.groupby("Cliente").size().nlargest(10).index
            ds = df[df["Cliente"].isin(top10)].copy()
            top5m = ds["Modulo"].value_counts().nlargest(5).index
            ds["Mod_s"] = ds["Modulo"].apply(lambda x: x if x in top5m else "Outros")
            dsg = ds.groupby(["Cliente","Mod_s","Situacao"]).size().reset_index(name="Qtd")
            fig2 = px.sunburst(dsg, path=["Cliente","Mod_s","Situacao"],
                                values="Qtd", color_discrete_sequence=CORES)
            fig2.update_traces(textfont=dict(size=10,color=WHITE))
            fig2.update_layout(**pb(360))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with c4:
        st.markdown(co("🗣️ Top 15 Contatos"), unsafe_allow_html=True)
        dc2 = df.groupby("Contato").size().reset_index(name="Total").sort_values("Total",ascending=False).head(15)
        st.markdown(rank_html(dc2,"Contato","Total",GOLD), unsafe_allow_html=True)
        st.markdown(cc(), unsafe_allow_html=True)

    st.markdown('<span class="sec-t">🔍 Raio-X do Cliente</span>', unsafe_allow_html=True)
    st.markdown(co(""), unsafe_allow_html=True)
    clientes = sorted(df["Cliente"].dropna().unique())
    cli = st.selectbox("Cliente:", clientes, label_visibility="collapsed")
    if cli:
        dce = df[df["Cliente"]==cli]
        tot = len(dce); ab = dce["Data_Solucao"].isna().sum()
        fcr = safe_pct(dce["Finalizado_Mesmo_Dia"].sum(), tot)
        
        # >= 0 em vez de > 0
        tmr = dce[dce["TMR_h"]>=0]["TMR_h"].mean()
        
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px">
          {kpi("Total Chamados", f"{tot:,}", "", "📋", TEAL)}
          {kpi("Em Aberto", f"{ab:,}", "", "📌", ORANGE)}
          {kpi("FCR", f"{fcr:.1f}%", "1º contato", "⚡", GOLD,
               tip_text="Resolução no Primeiro Contato")}
          {kpi("TMR", tmr_fmt(tmr), "tempo médio", "⏱️", GREEN,
               tip_text="Tempo Médio de Resolução")}
        </div>""", unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        for col, campo, tit, cor in [(r1,"Contato","Top Contatos",TEAL),
                                      (r2,"Modulo","Módulos",BRAND),
                                      (r3,"Origem","Origem",ORANGE)]:
            with col:
                try:
                    dg = dce.groupby(campo).size().reset_index(name="Qtd").nlargest(8,"Qtd").sort_values("Qtd")
                    if campo == "Origem":
                        fig_r = px.pie(dg, names=campo, values="Qtd", hole=0.5,
                                        color_discrete_sequence=CORES)
                        fig_r.update_traces(textposition="inside",textinfo="percent+label",
                                             textfont=dict(size=10,color=WHITE))
                        fig_r.update_layout(**pb(220,showlegend=False))
                    else:
                        fig_r = px.bar(dg, y=campo, x="Qtd", orientation="h", text="Qtd",
                                        color="Qtd",
                                        color_continuous_scale=[[0,CARD2],[1,cor]])
                        fig_r.update_coloraxes(showscale=False)
                        fig_r.update_traces(textposition="outside",cliponaxis=False,
                                             textfont=dict(color=WHITE))
                        fig_r.update_layout(**pb(max(200,len(dg)*30),
                            xaxis=dict(showgrid=False),yaxis=dict(showgrid=False),
                            yaxis_title="",xaxis_title=""))
                    st.caption(tit)
                    st.plotly_chart(fig_r, use_container_width=True)
                except Exception as e:
                    st.warning(f"Gráfico indisponível: {e}")
    st.markdown(cc(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 3 — ATENDENTES
# ══════════════════════════════════════════════════════════════════════════════
def aba_atendentes(df):
    df_at = df.groupby("Atendente").agg(
        Total=("Sac","count"),
        Resolvidos=("Data_Solucao", lambda x: x.notna().sum()),
        Em_Aberto=("Data_Solucao", lambda x: x.isna().sum()),
        FCR_raw=("Finalizado_Mesmo_Dia","sum"),
        
        # >= 0 em vez de > 0
        TMR_raw=("TMR_h", lambda x: x[x>=0].mean() if (x>=0).any() else float("nan")),
        
    ).reset_index()
    df_at["FCR_pct"] = df_at.apply(lambda r: safe_pct(r["FCR_raw"], r["Total"]), axis=1)
    df_at["Enc_pct"] = df_at.apply(lambda r: safe_pct(r["Resolvidos"], r["Total"]), axis=1)
    df_at = df_at[df_at["Total"] > 0].sort_values("Total", ascending=False)

    st.markdown('<span class="sec-t">📋 Performance por Atendente</span>', unsafe_allow_html=True)
    st.markdown(co(""), unsafe_allow_html=True)
    max_fcr = df_at["FCR_pct"].max() or 1
    max_enc = df_at["Enc_pct"].max() or 1
    max_tot = df_at["Total"].max() or 1
    rows = ""
    for _, r in df_at.iterrows():
        fc = GREEN if r["FCR_pct"]>=70 else (GOLD if r["FCR_pct"]>=50 else DANGER)
        ec = GREEN if r["Enc_pct"]>=80 else (GOLD if r["Enc_pct"]>=60 else ORANGE)
        fp = int(r["FCR_pct"]/max_fcr*100)
        ep = int(r["Enc_pct"]/max_enc*100)
        tp = int(r["Total"]/max_tot*100)
        rows += f"""<tr>
  <td><b>{r['Atendente']}</b></td>
  <td><div class="barcell">
    <div class="bbar-bg"><div class="bbar" style="width:{tp}%;background:{TEAL}"></div></div>
    <span style="color:{TEAL};font-weight:700;min-width:30px">{r['Total']:,}</span>
  </div></td>
  <td style="color:{GREEN}">{r['Resolvidos']:,}</td>
  <td style="color:{ORANGE}">{r['Em_Aberto']:,}</td>
  <td><div class="barcell">
    <div class="bbar-bg"><div class="bbar" style="width:{fp}%;background:{fc}"></div></div>
    <span style="color:{fc};font-weight:700">{r['FCR_pct']:.0f}%</span>
  </div></td>
  <td><div class="barcell">
    <div class="bbar-bg"><div class="bbar" style="width:{ep}%;background:{ec}"></div></div>
    <span style="color:{ec};font-weight:700">{r['Enc_pct']:.0f}%</span>
  </div></td>
  <td style="color:{MUTED}">{tmr_fmt(r['TMR_raw'])}</td>
</tr>"""

    h_fcr = tip("FCR%","Resolução no Primeiro Contato: % de chamados finalizados sem retorno. Meta ≥ 70%")
    h_enc = tip("Enc.%","Taxa de Encerramento: % de chamados resolvidos no período")
    h_tmr = tip("TMR","Tempo Médio de Resolução: média de dias/horas entre abertura e solução")
    st.markdown(f"""<table class="att-table"><thead><tr>
  <th>Atendente</th><th>Total</th><th>Resolvidos</th><th>Em Aberto</th>
  <th>{h_fcr}</th><th>{h_enc}</th><th>{h_tmr}</th>
</tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)
    st.markdown(cc(), unsafe_allow_html=True)

    cq, ch = st.columns([3,2])
    with cq:
        try:
            st.markdown(co(f"🎯 Quadrante de Eficiência — Volume vs {tip('FCR%','Resolução no Primeiro Contato')}"), unsafe_allow_html=True)
            med_t = df_at["Total"].median()
            med_f = df_at["FCR_pct"].median()
            maxt  = df_at["Total"].max() * 1.25
            fig_q = go.Figure()
            for (x0,x1,y0,y1),cor in [
                ((med_t,maxt,med_f,102),"rgba(0,184,148,.06)"),
                ((0,med_t,med_f,102),"rgba(0,206,201,.06)"),
                ((med_t,maxt,0,med_f),"rgba(225,112,85,.06)"),
                ((0,med_t,0,med_f),"rgba(230,57,70,.06)"),
            ]:
                fig_q.add_shape(type="rect",x0=x0,x1=x1,y0=y0,y1=y1,
                                 fillcolor=cor,line_width=0)
            fig_q.add_vline(x=med_t,line_color=BORDER,line_dash="dot",line_width=1.5)
            fig_q.add_hline(y=med_f,line_color=BORDER,line_dash="dot",line_width=1.5)
            fig_q.add_scatter(
                x=df_at["Total"], y=df_at["FCR_pct"],
                mode="markers+text", text=df_at["Atendente"],
                textposition="top center",
                textfont=dict(size=10,color=WHITE),
                marker=dict(size=df_at["Total"]**0.55*2.5, color=TEAL,
                             opacity=0.75, line=dict(color=BG,width=1.5)),
                hovertemplate="<b>%{text}</b><br>Chamados: %{x}<br>FCR: %{y:.1f}%<extra></extra>",
            )
            for txt,x,y,cor2 in [
                ("⭐ Alta Eficiência",maxt*.97,100,GREEN),
                ("🧘 Baixo Vol./FCR OK",maxt*.03,100,TEAL),
                ("🔥 Vol.Alto/FCR Baixa",maxt*.97,med_f*.12,ORANGE),
                ("⚠️ Atenção",maxt*.03,med_f*.12,DANGER),
            ]:
                fig_q.add_annotation(x=x,y=y,text=txt,showarrow=False,
                                      font=dict(size=9,color=cor2),
                                      xanchor="right" if x>maxt*.5 else "left")
            fig_q.update_layout(**pb(300,
                xaxis=dict(title="Total de Chamados",showgrid=False,color=MUTED),
                yaxis=dict(title="FCR %",showgrid=False,color=MUTED,range=[0,108])))
            st.plotly_chart(fig_q, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with ch:
        try:
            st.markdown(co("🧩 Mapa de Calor — Atendente × Módulo"), unsafe_allow_html=True)
            top6m = df["Modulo"].value_counts().nlargest(6).index
            dhm = df.copy()
            dhm["Mod_x"] = dhm["Modulo"].apply(lambda x: x if x in top6m else "Outros")
            piv = dhm.groupby(["Atendente","Mod_x"]).size().reset_index(name="Qtd")\
                      .pivot(index="Atendente",columns="Mod_x",values="Qtd").fillna(0)
            fig_hm = px.imshow(piv, text_auto=True, aspect="auto",
                                color_continuous_scale=[[0,CARD2],[0.5,CARD],[1,BRAND]])
            fig_hm.update_coloraxes(showscale=False)
            fig_hm.update_traces(textfont=dict(color=WHITE))
            fig_hm.update_layout(**pb(max(280,piv.shape[0]*36),xaxis_title="",yaxis_title=""))
            st.plotly_chart(fig_hm, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    st.markdown(f'<span class="sec-t">⚡ {tip("FCR","Resolução no Primeiro Contato — meta 70%")} por Atendente</span>', unsafe_allow_html=True)
    try:
        df_fg = df_at.sort_values("FCR_pct",ascending=False)
        if not df_fg.empty:
            n = min(len(df_fg), 6)
            cols_g = st.columns(max(n, 1))
            for i, (_, row) in enumerate(df_fg.head(n).iterrows()):
                try:
                    val = float(row["FCR_pct"]) if pd.notna(row["FCR_pct"]) else 0.0
                    cor = GREEN if val>=70 else (GOLD if val>=50 else DANGER)
                    nome = str(row["Atendente"]).split()[0] if pd.notna(row["Atendente"]) else "—"
                    fig_g = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=val,
                        number=dict(suffix="%", font=dict(size=16, color=cor, family="Inter")),
                        title=dict(text=nome, font=dict(size=10, color=MUTED, family="Inter")),
                        gauge=dict(
                            axis=dict(range=[0,100], tickwidth=0, tickcolor="transparent",
                                       tickfont=dict(color="transparent")),
                            bar=dict(color=cor, thickness=0.2),
                            bgcolor=CARD2, borderwidth=0,
                            steps=[
                                dict(range=[0,70], color=CARD2),
                                dict(range=[70,100], color="rgba(0,184,148,0.12)")
                            ],
                            threshold=dict(line=dict(color=GREEN,width=2),
                                            thickness=0.75, value=70),
                        ),
                    ))
                    fig_g.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=28,b=4,l=8,r=8),
                        height=150,
                        font=dict(family="Inter"),
                    )
                    cols_g[i].plotly_chart(fig_g, use_container_width=True)
                except Exception:
                    pass
    except Exception as e:
        st.warning(f"Gauges indisponíveis: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 4 — SITUAÇÃO DOS CHAMADOS
# ══════════════════════════════════════════════════════════════════════════════
def aba_situacao(df, df_raw):
    c1, c2, c3 = st.columns([1,1,2])

    with c1:
        try:
            st.markdown(co("📁 Tipo de Chamado"), unsafe_allow_html=True)
            dt = df.groupby("Tipo").size().reset_index(name="Qtd")
            if not dt.empty:
                fig = px.pie(dt, names="Tipo", values="Qtd", hole=0.52,
                              color_discrete_sequence=CORES)
                fig.update_traces(textposition="inside", textinfo="percent+label",
                                   textfont=dict(size=11,color=WHITE))
                fig.update_layout(**pb(280, showlegend=False))
                st.plotly_chart(fig, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with c2:
        try:
            st.markdown(co("🔵 Situação Atual"), unsafe_allow_html=True)
            ds = df.groupby("Situacao").size().reset_index(name="Qtd").sort_values("Qtd",ascending=False)
            if not ds.empty:
                fig2 = px.pie(ds, names="Situacao", values="Qtd", hole=0.52,
                               color_discrete_sequence=CORES)
                fig2.update_traces(textposition="outside", textinfo="label+percent",
                                    textfont=dict(size=10,color=WHITE))
                fig2.update_layout(**pb(280, showlegend=False))
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with c3:
        try:
            st.markdown(co("📈 Tendência de Situações — Mensal"), unsafe_allow_html=True)
            dts = df.copy()
            dts["MesAno"] = dts["Data_abertura"].dt.to_period("M").astype(str)
            if not dts.empty and "Situacao" in dts.columns:
                top_s = dts["Situacao"].value_counts().nlargest(5).index.tolist()
                dts["Sit_f"] = dts["Situacao"].apply(lambda x: x if x in top_s else "Outras")
                dtsg = dts.groupby(["MesAno","Sit_f"]).size().reset_index(name="Qtd").sort_values("MesAno")
                fig3 = px.area(dtsg, x="MesAno", y="Qtd", color="Sit_f",
                                color_discrete_sequence=CORES)
                fig3.update_layout(**pb(280,
                    xaxis=dict(showgrid=False,color=MUTED),
                    yaxis=dict(showgrid=True,gridcolor=BORDER,color=MUTED),
                    xaxis_title="", yaxis_title="",
                    legend=dict(orientation="h",y=1.12,x=0,title="",font=dict(color=WHITE))))
                st.plotly_chart(fig3, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    try:
        hoje = date.today()
        df_bl = df[df["Data_Solucao"].isna()].copy()
        if not df_bl.empty:
            df_bl["Dias"] = (pd.Timestamp(hoje) - df_bl["Data_abertura"]).dt.days.clip(lower=0)
            bins   = [-1, 3, 7, 15, 30, 60, 9999]
            labels = ["0–3 dias","4–7 dias","8–15 dias","16–30 dias","31–60 dias","60+ dias"]
            df_bl["Faixa"] = pd.cut(df_bl["Dias"], bins=bins, labels=labels)
            df_ag = df_bl.groupby("Faixa", observed=True).size().reset_index(name="Qtd")

            ca, cb = st.columns([2,3])
            with ca:
                try:
                    st.markdown(co(f"⏳ {tip('Backlog','Chamados sem solução')} — Tempo em Aberto"), unsafe_allow_html=True)
                    cores_ag = [GREEN,TEAL,GOLD,ORANGE,DANGER,"#8E1010"]
                    fig4 = px.bar(df_ag, x="Faixa", y="Qtd", text="Qtd",
                                   color="Faixa", color_discrete_sequence=cores_ag)
                    fig4.update_traces(textposition="outside", cliponaxis=False,
                                        textfont=dict(color=WHITE), showlegend=False)
                    fig4.update_layout(**pb(250,
                        xaxis=dict(showgrid=False,color=MUTED),
                        yaxis=dict(showgrid=True,gridcolor=BORDER,color=MUTED),
                        xaxis_title="", yaxis_title=""))
                    st.plotly_chart(fig4, use_container_width=True)
                    st.markdown(cc(), unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(cc(), unsafe_allow_html=True)
                    st.warning(f"Gráfico indisponível: {e}")

            with cb:
                try:
                    st.markdown(co("✅ Resolvidos vs 📌 Em Aberto — por Atendente"), unsafe_allow_html=True)
                    dra = df.copy()
                    dra["Status"] = dra["Data_Solucao"].apply(
                        lambda x: "Resolvido" if pd.notna(x) else "Em Aberto")
                    drag = dra.groupby(["Atendente","Status"]).size().reset_index(name="Qtd")
                    n_at = df["Atendente"].nunique()
                    fig5 = px.bar(drag, y="Atendente", x="Qtd", color="Status",
                                   orientation="h", barmode="stack", text="Qtd",
                                   color_discrete_map={"Resolvido":GREEN,"Em Aberto":DANGER})
                    fig5.update_traces(textposition="inside",
                                        textfont=dict(size=9,color=WHITE), cliponaxis=False)
                    fig5.update_layout(**pb(max(250,n_at*32),
                        yaxis_title="", xaxis_title="",
                        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                        legend=dict(orientation="h",y=1.1,x=0,title="",font=dict(color=WHITE))))
                    st.plotly_chart(fig5, use_container_width=True)
                    st.markdown(cc(), unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(cc(), unsafe_allow_html=True)
                    st.warning(f"Gráfico indisponível: {e}")
    except Exception as e:
        st.warning(f"Seção de backlog indisponível: {e}")

    # ================= NOVO: SEÇÃO DE FEEDBACKS =================
    st.markdown('<span class="sec-t">⭐ Feedbacks Acumulados por Atendente (Ignora Filtros)</span>', unsafe_allow_html=True)
    try:
        # Busca exclusiva no campo Situação do banco completo (df_raw)
        mask_fb = df_raw["Situacao"].astype(str).str.contains("feedback", case=False, na=False)
        df_fb = df_raw[mask_fb]
        
        if not df_fb.empty:
            st.markdown(co("🏆 Total Histórico de Feedbacks (Base Completa)"), unsafe_allow_html=True)
            df_fb_ag = df_fb.groupby("Atendente").size().reset_index(name="Qtd").sort_values("Qtd", ascending=True)
            
            fig_fb = px.bar(df_fb_ag, x="Qtd", y="Atendente", orientation="h", text="Qtd",
                           color="Qtd", color_continuous_scale=[[0, CARD2], [1, GOLD]])
            fig_fb.update_coloraxes(showscale=False)
            fig_fb.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=WHITE))
            fig_fb.update_layout(**pb(max(250, len(df_fb_ag)*32),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                xaxis_title="", yaxis_title=""))
            st.plotly_chart(fig_fb, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        else:
            st.info("Nenhum registro com a Situação 'Feedback' foi encontrado no banco de dados.")
    except Exception as e:
        st.warning(f"Erro ao gerar gráfico de Feedbacks: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 5 — SLA & KPIs
# ══════════════════════════════════════════════════════════════════════════════
def aba_sla(df):
    st.markdown(f"""<div class="chart-card" style="margin-bottom:12px">
  <div class="chart-title">ℹ️ Glossário dos Indicadores</div>
  <div style="font-size:0.78rem;color:{MUTED};line-height:1.8">
    <b style="color:{WHITE}">• {tip('FCR','First Contact Resolution')}</b>: % de chamados resolvidos no primeiro contato. Meta: ≥ 70%<br>
    <b style="color:{WHITE}">• {tip('TMR','Tempo Médio de Resolução')}</b>: média entre abertura e solução. Quanto menor, melhor.<br>
    <b style="color:{WHITE}">• {tip('SLA','Service Level Agreement — Acordo de Nível de Serviço')}</b>: compromisso de prazo de atendimento.<br>
    <b style="color:{WHITE}">• Taxa de Encerramento</b>: % de chamados resolvidos no período filtrado.<br>
    <b style="color:{WHITE}">• Sazonalidade</b>: variação do volume por módulo ao longo dos meses.
  </div>
</div>""", unsafe_allow_html=True)

    cf, ct = st.columns(2)

    with cf:
        try:
            st.markdown(co(f"⚡ Evolução Mensal — {tip('FCR%','Meta: ≥ 70%')}"), unsafe_allow_html=True)
            dfm = df.copy()
            dfm["MesAno"] = dfm["Data_abertura"].dt.to_period("M").astype(str)
            dfm = dfm.groupby("MesAno").agg(
                Total=("Sac","count"),
                FCR=("Finalizado_Mesmo_Dia","sum")
            ).reset_index()
            dfm["FCR_pct"] = dfm.apply(lambda r: safe_pct(r["FCR"],r["Total"]), axis=1)
            dfm = dfm.sort_values("MesAno")

            fig = go.Figure()
            fig.add_bar(x=dfm["MesAno"], y=dfm["Total"],
                         marker_color=CARD2, name="Total", yaxis="y",
                         opacity=0.8)
            fig.add_scatter(
                x=dfm["MesAno"], y=dfm["FCR_pct"],
                mode="lines+markers", name="FCR %", yaxis="y2",
                line=dict(color=GOLD, width=2.5), marker=dict(size=6),
            )
            fig.add_scatter(
                x=dfm["MesAno"],
                y=[70]*len(dfm),
                mode="lines", name="Meta 70%", yaxis="y2",
                line=dict(color=GREEN, width=1.5, dash="dash"),
            )
            fig.update_layout(**pb(260,
                xaxis=dict(showgrid=False,color=MUTED),
                yaxis=dict(title="Chamados",showgrid=True,gridcolor=BORDER,color=MUTED),
                yaxis2=dict(title="FCR %",overlaying="y",side="right",
                             range=[0,110],showgrid=False,color=MUTED,ticksuffix="%"),
                legend=dict(orientation="h",y=1.12,x=0,font=dict(color=WHITE)),
                barmode="overlay"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with ct:
        try:
            st.markdown(co(f"⏱️ {tip('TMR','Tempo Médio de Resolução')} por Atendente (dias)"), unsafe_allow_html=True)
            
            # >= 0 em vez de > 0
            dtmr = df[df["TMR_h"]>=0].groupby("Atendente")["TMR_h"].mean().reset_index()
            
            dtmr.columns = ["Atendente","TMR_h"]
            dtmr["TMR_dias"] = (dtmr["TMR_h"]/24).round(2)
            dtmr = dtmr.sort_values("TMR_dias")
            dtmr["cor"] = dtmr["TMR_dias"].apply(
                lambda x: GREEN if x<=2 else (GOLD if x<=5 else DANGER))
            if not dtmr.empty:
                fig2 = go.Figure()
                for _, r in dtmr.iterrows():
                    fig2.add_bar(
                        x=[float(r["TMR_dias"])], y=[r["Atendente"]],
                        orientation="h",
                        marker_color=r["cor"],
                        text=[f"{r['TMR_dias']:.1f}d"],
                        textposition="outside",
                        textfont=dict(color=WHITE),
                        showlegend=False,
                    )
                fig2.update_layout(**pb(max(240,len(dtmr)*32),
                    xaxis=dict(title="Dias",showgrid=False,color=MUTED),
                    yaxis=dict(showgrid=False,color=MUTED),
                    yaxis_title="", bargap=0.3))
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    try:
        st.markdown(co(f"🌡️ Sazonalidade — Módulo × Mês (identifica picos anuais)"), unsafe_allow_html=True)
        meses = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                 7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
        dsaz = df.copy()
        dsaz["MesN"] = dsaz["Data_abertura"].dt.month
        dsaz["Mes"]  = dsaz["MesN"].map(meses)
        top8m = dsaz["Modulo"].value_counts().nlargest(8).index
        dsaz = dsaz[dsaz["Modulo"].isin(top8m)]
        piv_s = dsaz.groupby(["Modulo","Mes"]).size().reset_index(name="Qtd")\
                     .pivot(index="Modulo",columns="Mes",values="Qtd").fillna(0)
        col_ord = [m for m in list(meses.values()) if m in piv_s.columns]
        piv_s = piv_s[col_ord]
        if not piv_s.empty:
            fig3 = px.imshow(piv_s, text_auto=True, aspect="auto",
                              color_continuous_scale=[[0,CARD2],[0.5,ORANGE],[1,BRAND]])
            fig3.update_coloraxes(showscale=False)
            fig3.update_traces(textfont=dict(color=WHITE))
            fig3.update_layout(**pb(max(260,len(top8m)*38),xaxis_title="",yaxis_title=""))
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown(cc(), unsafe_allow_html=True)
    except Exception as e:
        st.markdown(cc(), unsafe_allow_html=True)
        st.warning(f"Gráfico indisponível: {e}")

    ca, cb = st.columns(2)
    with ca:
        try:
            st.markdown(co("📆 Total de Chamados por Ano"), unsafe_allow_html=True)
            dya = df.groupby("Ano_abertura").size().reset_index(name="Total")
            dya["Ano"] = dya["Ano_abertura"].astype(str)
            fig4 = px.bar(dya, x="Ano", y="Total", text="Total",
                           color="Total",
                           color_continuous_scale=[[0,CARD2],[1,TEAL]])
            fig4.update_coloraxes(showscale=False)
            fig4.update_traces(textposition="outside",cliponaxis=False,
                                textfont=dict(color=WHITE))
            fig4.update_layout(**pb(230,
                xaxis=dict(showgrid=False,color=MUTED),
                yaxis=dict(showgrid=True,gridcolor=BORDER,color=MUTED),
                xaxis_title="",yaxis_title=""))
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")

    with cb:
        try:
            st.markdown(co(f"⚡ {tip('FCR%','Resolução no Primeiro Contato')} por Ano"), unsafe_allow_html=True)
            dyf = df.groupby("Ano_abertura").agg(
                Total=("Sac","count"), FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
            dyf["FCR_pct"] = dyf.apply(lambda r: safe_pct(r["FCR"],r["Total"]),axis=1)
            dyf["Ano"] = dyf["Ano_abertura"].astype(str)
            fig5 = px.bar(dyf, x="Ano", y="FCR_pct",
                           text=dyf["FCR_pct"].apply(lambda v: f"{v:.1f}%"),
                           color="FCR_pct",
                           color_continuous_scale=[[0,DANGER],[0.7,GOLD],[1,GREEN]])
            fig5.update_coloraxes(showscale=False)
            fig5.update_traces(textposition="outside",cliponaxis=False,
                                textfont=dict(color=WHITE))
            fig5.add_scatter(x=dyf["Ano"], y=[70]*len(dyf),
                              mode="lines", name="Meta 70%",
                              line=dict(color=GREEN,width=1.5,dash="dash"))
            fig5.update_layout(**pb(230,
                xaxis=dict(showgrid=False,color=MUTED),
                yaxis=dict(showgrid=True,gridcolor=BORDER,color=MUTED,range=[0,110]),
                xaxis_title="",yaxis_title="FCR %",
                showlegend=True,
                legend=dict(font=dict(color=WHITE))))
            st.plotly_chart(fig5, use_container_width=True)
            st.markdown(cc(), unsafe_allow_html=True)
        except Exception as e:
            st.markdown(cc(), unsafe_allow_html=True)
            st.warning(f"Gráfico indisponível: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 6 — ALERTAS & GESTÃO
# ══════════════════════════════════════════════════════════════════════════════
def aba_alertas(df, df_raw):
    try:
        hoje = date.today()
        df_bl = df_raw[df_raw["Data_Solucao"].isna()].copy()
        df_bl["Dias"] = (pd.Timestamp(hoje) - df_bl["Data_abertura"]).dt.days.clip(lower=0)

        criticos = df_bl[df_bl["Dias"] >= 30].sort_values("Dias", ascending=False)
        urgentes = df_bl[(df_bl["Dias"] >= 7) & (df_bl["Dias"] < 30)].sort_values("Dias", ascending=False)
        recentes = df_bl[df_bl["Dias"] < 7]

        st.markdown(f"""<div class="kpi-grid">
  <div class="kpi-card" style="border-left:4px solid {DANGER}">
    <div class="kpi-label">🔴 Críticos (+30 dias)</div>
    <div class="kpi-val" style="color:{DANGER}">{len(criticos):,}</div>
    <div class="kpi-sub">sem solução há 30+ dias</div>
  </div>
  <div class="kpi-card" style="border-left:4px solid {ORANGE}">
    <div class="kpi-label">🟠 Urgentes (7–29 dias)</div>
    <div class="kpi-val" style="color:{ORANGE}">{len(urgentes):,}</div>
    <div class="kpi-sub">requerem atenção</div>
  </div>
  <div class="kpi-card" style="border-left:4px solid {GOLD}">
    <div class="kpi-label">🟡 Recentes (&lt;7 dias)</div>
    <div class="kpi-val" style="color:{GOLD}">{len(recentes):,}</div>
    <div class="kpi-sub">em acompanhamento</div>
  </div>
  <div class="kpi-card" style="border-left:4px solid {TEAL}">
    <div class="kpi-label">📋 Total em Aberto</div>
    <div class="kpi-val" style="color:{TEAL}">{len(df_bl):,}</div>
    <div class="kpi-sub">backlog total</div>
  </div>
  <div class="kpi-card" style="border-left:4px solid {PURPLE}">
    <div class="kpi-label">👥 Clientes Afetados</div>
    <div class="kpi-val" style="color:{PURPLE}">{df_bl['Cliente'].nunique():,}</div>
    <div class="kpi-sub">com chamados abertos</div>
  </div>
  <div class="kpi-card" style="border-left:4px solid {GREEN}">
    <div class="kpi-label">✅ Resolvidos Hoje</div>
    <div class="kpi-val" style="color:{GREEN}">{df_raw[df_raw['Data_Solucao'].dt.date==hoje].shape[0]:,}</div>
    <div class="kpi-sub">fechamentos no dia</div>
  </div>
</div>""", unsafe_allow_html=True)

        ca, cb = st.columns([3,2])
        with ca:
            st.markdown('<span class="sec-t">🔴 Chamados Críticos — 30+ Dias em Aberto</span>', unsafe_allow_html=True)
            if not criticos.empty:
                for _, r in criticos.head(10).iterrows():
                    dias = int(r["Dias"])
                    cliente = str(r.get("Cliente","—"))
                    atend   = str(r.get("Atendente","—"))
                    assunto = str(r.get("Assunto","—"))[:60]
                    modulo  = str(r.get("Modulo","—"))
                    sac     = str(r.get("Sac","—"))
                    st.markdown(f"""<div class="alert-card">
  <div class="alert-title">🔴 #{sac} — {cliente}
    <span style="float:right;color:{DANGER};font-weight:700;font-size:.75rem">{dias} dias</span>
  </div>
  <div class="alert-sub">👤 {atend} &nbsp;·&nbsp; 🧩 {modulo} &nbsp;·&nbsp; 📋 {assunto}</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-card alert-info"><div class="alert-title">✅ Nenhum chamado crítico!</div></div>', unsafe_allow_html=True)

            st.markdown('<span class="sec-t">🟠 Chamados Urgentes — 7 a 29 Dias</span>', unsafe_allow_html=True)
            for _, r in urgentes.head(8).iterrows():
                dias = int(r["Dias"])
                st.markdown(f"""<div class="alert-card alert-warn">
  <div class="alert-title">🟠 #{r.get('Sac','—')} — {r.get('Cliente','—')}
    <span style="float:right;color:{GOLD};font-weight:700;font-size:.75rem">{dias} dias</span>
  </div>
  <div class="alert-sub">👤 {r.get('Atendente','—')} &nbsp;·&nbsp; 🧩 {r.get('Modulo','—')} &nbsp;·&nbsp; 📋 {str(r.get('Assunto','—'))[:55]}</div>
</div>""", unsafe_allow_html=True)

        with cb:
            st.markdown('<span class="sec-t">📊 Clientes com Maior Backlog</span>', unsafe_allow_html=True)
            st.markdown(co(""), unsafe_allow_html=True)
            dcb = df_bl.groupby("Cliente").size().reset_index(name="Total")\
                        .sort_values("Total",ascending=False).head(12)
            st.markdown(rank_html(dcb,"Cliente","Total",DANGER), unsafe_allow_html=True)
            st.markdown(cc(), unsafe_allow_html=True)

            st.markdown(f'<span class="sec-t">⚠️ {tip("FCR","Resolução no Primeiro Contato")} Abaixo da Meta (70%)</span>', unsafe_allow_html=True)
            dfa = df.groupby("Atendente").agg(
                Total=("Sac","count"),FCR=("Finalizado_Mesmo_Dia","sum")).reset_index()
            dfa["FCR_pct"] = dfa.apply(lambda r: safe_pct(r["FCR"],r["Total"]),axis=1)
            dfa = dfa[(dfa["FCR_pct"]<70) & (dfa["Total"]>5)].sort_values("FCR_pct")
            if not dfa.empty:
                for _, r in dfa.iterrows():
                    c2 = DANGER if r["FCR_pct"]<50 else ORANGE
                    st.markdown(f"""<div class="alert-card alert-warn">
  <div class="alert-title">👤 {r['Atendente']}
    <span style="float:right;color:{c2};font-weight:700">{r['FCR_pct']:.0f}%</span>
  </div>
  <div class="alert-sub">{r['Total']:,} chamados &nbsp;·&nbsp; Meta: 70%</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-card alert-info"><div class="alert-title">✅ Todos acima da meta!</div></div>', unsafe_allow_html=True)

        st.markdown('<span class="sec-t">🔀 Fluxo dos Chamados — Origem → Módulo → Situação</span>', unsafe_allow_html=True)
        st.markdown(co(""), unsafe_allow_html=True)
        try:
            top5o = df["Origem"].value_counts().nlargest(5).index.tolist()
            top5m = df["Modulo"].value_counts().nlargest(5).index.tolist()
            top4s = df["Situacao"].value_counts().nlargest(4).index.tolist()
            dsk   = df[df["Origem"].isin(top5o) & df["Modulo"].isin(top5m) & df["Situacao"].isin(top4s)]
            if not dsk.empty:
                all_n = top5o + top5m + top4s
                nidx  = {n:i for i,n in enumerate(all_n)}
                src,tgt,val = [],[],[]
                for _,r in dsk.groupby(["Origem","Modulo"]).size().reset_index(name="v").iterrows():
                    if r["Origem"] in nidx and r["Modulo"] in nidx:
                        src.append(nidx[r["Origem"]]); tgt.append(nidx[r["Modulo"]]); val.append(int(r["v"]))
                for _,r in dsk.groupby(["Modulo","Situacao"]).size().reset_index(name="v").iterrows():
                    if r["Modulo"] in nidx and r["Situacao"] in nidx:
                        src.append(nidx[r["Modulo"]]); tgt.append(nidx[r["Situacao"]]); val.append(int(r["v"]))
                ncors = [TEAL]*len(top5o) + [BRAND]*len(top5m) + [GREEN]*len(top4s)
                fig_sk = go.Figure(go.Sankey(
                    node=dict(pad=15,thickness=16,label=all_n,color=ncors,
                               line=dict(color=BG,width=0.5)),
                    link=dict(source=src,target=tgt,value=val,
                               color="rgba(139,163,191,0.18)"),
                ))
                fig_sk.update_layout(**pb(300))
                st.plotly_chart(fig_sk, use_container_width=True)
        except Exception as e:
            st.caption(f"Diagrama de fluxo indisponível: {e}")
        st.markdown(cc(), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro na aba de alertas: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 8 — CLIENTES INATIVOS (Radar)
# ══════════════════════════════════════════════════════════════════════════════
def aba_inativos(df_raw, df_contratos):
    st.markdown('<span class="sec-t">📡 Radar de Inatividade (Customer Success)</span>', unsafe_allow_html=True)
    
    # 1. Tratamento de IDs e criação da chave do Grupo (Matriz)
    df_c = df_contratos.copy()
    df_c['CLIENTE_codigo'] = df_c['CLIENTE_codigo'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_c['cod_matrix'] = df_c['cod_matrix'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', None)
    
    # Se tem cod_matrix, ele é o grupo. Se não, o próprio cliente é o grupo.
    df_c['ID_Grupo'] = df_c['cod_matrix'].combine_first(df_c['CLIENTE_codigo'])
    
    # 2. Mapear tickets para o Grupo
    map_grupo = df_c.set_index('CLIENTE_codigo')['ID_Grupo'].to_dict()
    df_t = df_raw.copy()
    df_t['Cliente_Codigo'] = df_t['Cliente_Codigo'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_t['ID_Grupo'] = df_t['Cliente_Codigo'].map(map_grupo).fillna(df_t['Cliente_Codigo'])
    
    # 3. Último contato geral do grupo
    ultimos = df_t.groupby('ID_Grupo')['Data_abertura'].max().reset_index()
    ultimos.rename(columns={'Data_abertura': 'Ultimo_Contato'}, inplace=True)
    
    # 4. Juntar as bases e calcular inatividade
    df_view = df_c.merge(ultimos, on='ID_Grupo', how='left')
    hoje = pd.Timestamp(date.today())
    df_view['Dias_Inativo'] = (hoje - df_view['Ultimo_Contato']).dt.days
    
    # Filtro Interativo na tela
    dias_filtro = st.slider("⚠️ Mostrar clientes vigentes sem contato há mais de (dias):", 
                            min_value=0, max_value=365, value=60, step=15)
    
    # Filtrar apenas o recorte selecionado
    df_view = df_view[df_view['Dias_Inativo'] >= dias_filtro].sort_values('Dias_Inativo', ascending=False)
    
    # 5. Formatar Data Padrão BR e exibir
    df_view['Último Contato'] = df_view['Ultimo_Contato'].dt.strftime('%d/%m/%Y').fillna('Sem registro histórico')
    df_view['Dias Inativo'] = df_view['Dias_Inativo'].fillna(9999).astype(int).astype(str).replace('9999', '∞')
    
    # KPIs da aba
    total_vigentes = len(df_c)
    total_inativos = len(df_view)
    taxa = (total_inativos / total_vigentes * 100) if total_vigentes > 0 else 0
    
    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr)">
      {kpi("Base Vigente", f"{total_vigentes:,}", "contratos ativos", "🏢", TEAL)}
      {kpi("Inativos", f"{total_inativos:,}", f"há +{dias_filtro} dias", "⚠️", ORANGE if taxa < 30 else DANGER)}
      {kpi("Taxa de Risco", f"{taxa:.1f}%", "da base sem contato", "📉", DANGER if taxa > 30 else GREEN)}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(co(f"📋 Contratos Vigentes — Sem contato há mais de {dias_filtro} dias"), unsafe_allow_html=True)
    cols = ['CLIENTE_codigo', 'RAZAO', 'CNPJ', 'SITUACAO', 'Último Contato', 'Dias Inativo']
    st.dataframe(df_view[cols].reset_index(drop=True), use_container_width=True, height=500)
    st.markdown(cc(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()

    c1, ct, c2 = st.columns([1,5,1], vertical_alignment="center")
    with c1:
        if os.path.exists("logo_supra.png"):
            st.image("logo_supra.png", width=100)
    with ct:
        st.markdown(f"""<div style="text-align:center;padding:2px 0">
  <div style="font-size:1.2rem;font-weight:800;color:{WHITE};letter-spacing:-.3px">
    Central de Suporte Técnico — SupraMAIS
  </div>
  <div style="font-size:0.72rem;color:{MUTED};margin-top:2px">
    <span class="dot-live"></span>
    Dados em tempo real &nbsp;·&nbsp; Atualizado em {datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y às %H:%M')}
  </div>
</div>""", unsafe_allow_html=True)
    with c2:
        if os.path.exists("logo_supramais.png"):
            st.image("logo_supramais.png", width=55)

    st.markdown(f"<hr>", unsafe_allow_html=True)

    try:
        df_raw = carregar_dados()
        df_contratos = carregar_contratos()
    except Exception as e:
        st.error(f"❌ Erro ao conectar: `{e}`")
        st.stop()
    if df_raw.empty:
        st.warning("⚠️ Nenhum registro retornado.")
        st.stop()

    with st.container():
        st.markdown(f"""<div class="filter-bar-title">
  <span style="display:inline-block;width:6px;height:6px;background:{TEAL};border-radius:50%"></span>
  FILTROS GLOBAIS — aplicados em todas as abas (Data é ignorada na aba "Hoje" e reconfigurada em "Por Hora")
</div>""", unsafe_allow_html=True)

        fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns([1.2, 1.2, 1.8, 1.8, 1.8, 1.8, 0.8])

        data_min = df_raw["Data_abertura"].dropna().min().date()
        data_max = max(df_raw["Data_abertura"].dropna().max().date(), hoje)

        with fc1:
            di = st.date_input("Data Inicial", value=hoje-timedelta(days=30),
                                min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
        with fc2:
            df_ = st.date_input("Data Final", value=hoje,
                                  min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
        with fc3:
            atendentes = sorted(df_raw["Atendente"].dropna().astype(str).unique())
            sel_at = st.multiselect("Atendente", atendentes,
                                     placeholder="Todos os atendentes")
        with fc4:
            situacoes = sorted(df_raw["Situacao"].dropna().astype(str).unique())
            sel_sit = st.multiselect("Situação", situacoes,
                                      placeholder="Todas as situações")
        with fc5:
            origens = sorted(df_raw["Origem"].dropna().astype(str).unique())
            sel_or = st.multiselect("Origem / Canal", origens,
                                     placeholder="Todas as origens")
        
        with fc6:
            modulos = sorted(df_raw["Modulo"].dropna().astype(str).unique())
            sel_mod = st.multiselect("Módulo", modulos,
                                     placeholder="Todos os módulos")
                                     
        with fc7:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            if st.button("🔄 Atualizar"):
                st.cache_data.clear()
                st.rerun()

    # Criação de um DF base que aplica todos os filtros EXCETO a data global.
    # Isso permite que a aba "Por Hora" obedeça as seleções acima, mas use sua própria data.
    df_base_no_date = df_raw.copy()
    if sel_at:  df_base_no_date = df_base_no_date[df_base_no_date["Atendente"].isin(sel_at)]
    if sel_sit: df_base_no_date = df_base_no_date[df_base_no_date["Situacao"].isin(sel_sit)]
    if sel_or:  df_base_no_date = df_base_no_date[df_base_no_date["Origem"].isin(sel_or)]
    if sel_mod: df_base_no_date = df_base_no_date[df_base_no_date["Modulo"].isin(sel_mod)]

    # Aplicação final do filtro de data para as demais abas de relatórios gerais
    df = df_base_no_date.copy()
    if di <= df_:
        df = df[(df["Data_abertura"].dt.date >= di) & (df["Data_abertura"].dt.date <= df_)]

    st.markdown(f"""<div style="font-size:0.68rem;color:{MUTED};margin:2px 0 10px">
  📋 <b style="color:{WHITE}">{len(df):,}</b> chamados no período
  &nbsp;·&nbsp; de <b style="color:{WHITE}">{di.strftime('%d/%m/%Y')}</b>
  até <b style="color:{WHITE}">{df_.strftime('%d/%m/%Y')}</b>
</div>""", unsafe_allow_html=True)

    # ── Lógica de MTD (Month-to-Date) por Dias Úteis ──
    start_curr = hoje.replace(day=1)
    bdays_curr = pd.bdate_range(start=start_curr, end=hoje).date
    qtd_dias_uteis = len(bdays_curr)

    mes_ant = 12 if hoje.month == 1 else hoje.month - 1
    ano_ant = hoje.year - 1 if hoje.month == 1 else hoje.year
    start_prev = date(ano_ant, mes_ant, 1)

    ult_dia_prev = calendar.monthrange(ano_ant, mes_ant)[1]
    end_prev = date(ano_ant, mes_ant, ult_dia_prev)

    bdays_prev = pd.bdate_range(start=start_prev, end=end_prev).date
    limite_idx = min(qtd_dias_uteis, len(bdays_prev)) - 1
    cutoff_prev = bdays_prev[limite_idx]

    df_mes = df_raw[(df_raw["Data_abertura"].dt.date >= start_curr) & (df_raw["Data_abertura"].dt.date <= hoje)]
    
    df_mant_parcial = df_raw[
        (df_raw["Data_abertura"].dt.date >= start_prev) &
        (df_raw["Data_abertura"].dt.date <= cutoff_prev)
    ]

    backlog = df_raw[df_raw["Data_Solucao"].isna()].shape[0]
    tot_mes = len(df_mes)
    tot_ant = len(df_mant_parcial) 
    fcr_mes = safe_pct(df_mes["Finalizado_Mesmo_Dia"].sum(), tot_mes)
    
    tmr_raw = df_raw[df_raw["TMR_h"]>=0]["TMR_h"].mean()
    
    tot_per = len(df)
    clientes_per = df["Cliente"].nunique()

    delta_m = tot_mes - tot_ant
    d_cls   = "b-red" if delta_m>0 else "b-green"
    d_str   = f"{'↑' if delta_m>0 else '↓'} {abs(delta_m)} vs {qtd_dias_uteis} dias úteis ant."
    f_cls   = "b-green" if fcr_mes>=70 else ("b-gold" if fcr_mes>=50 else "b-red")

    st.markdown(f"""<div class="kpi-grid">
  {kpi("Período Filtrado", f"{tot_per:,}",   "chamados no período",  "📋", TEAL)}
  {kpi("Clientes",         f"{clientes_per:,}","no período",          "🏢", PURPLE)}
  {kpi("Mês Atual",        f"{tot_mes:,}",   hoje.strftime('%b/%Y'), "📅", BRAND, d_str, d_cls)}
  {kpi("FCR do Mês",       f"{fcr_mes:.1f}%","1º contato",           "⚡", GOLD,"Meta: 70%",f_cls,
       tip_text="Resolução no Primeiro Contato: % de chamados finalizados sem retorno do cliente.")}
  {kpi("TMR Geral",        tmr_fmt(tmr_raw),"tempo médio resolução", "⏱️", ORANGE,"","b-muted",
       tip_text="Tempo Médio de Resolução: calculado entre data de abertura e data de solução.")}
  {kpi("Backlog",          f"{backlog:,}",  "sem solução",            "🗂️", DANGER if backlog>30 else GREEN,"","b-muted",
       tip_text="Fila de pendências: chamados abertos sem data de solução (todos os períodos).")}
</div>""", unsafe_allow_html=True)

    tabs = st.tabs([
        "🕐 Hoje",
        "⏱️ Por Hora",
        "📊 Resumo Geral",
        "🏢 Clientes",
        "👥 Atendentes",
        "🎫 Situação",
        "📈 SLA & KPIs",
        "🚨 Alertas & Gestão",
        "📡 Radar Inativos",
    ])

    with tabs[0]: aba_hoje(df_raw, hoje)
    with tabs[1]: aba_por_hora(df_base_no_date, hoje)
    with tabs[2]: aba_resumo(df)
    with tabs[3]: aba_clientes(df)
    with tabs[4]: aba_atendentes(df)
    with tabs[5]: aba_situacao(df, df_raw)
    with tabs[6]: aba_sla(df)
    with tabs[7]: aba_alertas(df, df_raw)
    with tabs[8]: aba_inativos(df_raw, df_contratos)


if __name__ == "__main__":
    main()