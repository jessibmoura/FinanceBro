import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import utils as utl

from config import API_URL

st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="📊",
    layout="wide"
)

# --- ESTILIZAÇÃO GLOBAL (CSS) ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    .metric-card-container {
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 120px;
    }
    /* Sombra nos containers do Streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #EEF2F6 !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# --- CARD DE MÉTRICA ---
def metric_card(
    titulo: str, 
    valor: str, 
    delta: str, 
    bg_color: str = "#FFFFFF", 
    text_color: str = "#1E222D", 
    delta_text_color: str = "#00875A", 
    delta_bg_color: str = "#E3FCEF",
    border_color: str = "#E2E8F0",
    is_highlight: bool = False
):
    font_size_val = "1.85rem" if is_highlight else "1.55rem"
    title_color = "#8F9CA9" if is_highlight else "#64748B"
    
    html_card = f"""
    <div class="metric-card-container" style="background-color: {bg_color}; border: 1px solid {border_color};">
        <span style="font-size: 0.80rem; font-weight: 600; color: {title_color}; text-transform: uppercase; letter-spacing: 0.6px;">
            {titulo}
        </span>
        <span style="font-size: {font_size_val}; font-weight: 700; color: {text_color}; margin: 4px 0;">
            {valor}
        </span>
        <div>
            <span style="
                display: inline-block;
                background-color: {delta_bg_color};
                color: {delta_text_color};
                font-size: 0.78rem;
                font-weight: 600;
                padding: 3px 8px;
                border-radius: 6px;
                letter-spacing: 0.2px;
            ">
                {delta}
            </span>
        </div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)


# --- BUSCA DE DADOS NA API ---
@st.cache_data(ttl=15)
def buscar_dados_completos():
    contas = []
    despesas = []
    categorias = {}
    recorrentes = []
    try:
        res_acc = requests.get(f"{API_URL}/accounts/")
        if res_acc.status_code == 200:
            contas = res_acc.json()

        res_cat = requests.get(f"{API_URL}/categories/")
        if res_cat.status_code == 200:
            for cat in res_cat.json():
                categorias[cat["id"]] = cat

        res_exp = requests.get(f"{API_URL}/expenses/?limit=200")
        if res_exp.status_code == 200:
            despesas = res_exp.json()

        # Busca despesas recorrentes cadastradas
        res_rec = requests.get(f"{API_URL}/recurring-bills/")
        if res_rec.status_code == 200:
            recorrentes = res_rec.json()
    except Exception as e:
        st.error(f"Erro de comunicação com a API: {e}")

    return contas, categorias, despesas, recorrentes

contas, categorias, despesas, recorrentes = buscar_dados_completos()

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ==============================================================================
# SEÇÃO 1: SAUDAÇÕES E SELEÇÃO DE MÊS (~10% Altura)
# ==============================================================================
opcoes_meses = utl.gerar_opcoes_meses(12)
labels_meses = [m["label"] for m in opcoes_meses]

col_saudacao, _, col_mes = st.columns([5, 2, 3], vertical_alignment="center")

with col_saudacao:
    st.markdown("### Olá Jessica!\nAqui está um overview das suas finanças pessoais:")

with col_mes:
    mes_selecionado_label = st.selectbox("Mês", options=labels_meses, index=0)

# Identifica o mês atual e o mês anterior selecionados
info_mes_atual = next(m for m in opcoes_meses if m["label"] == mes_selecionado_label)
ano_sel, mes_sel = info_mes_atual["ano"], info_mes_atual["mes"]

data_referencia = date(ano_sel, mes_sel, 1)
data_mes_anterior = data_referencia - relativedelta(months=1)
ano_ant, mes_ant = data_mes_anterior.year, data_mes_anterior.month

# Despesas filtradas para o mês atual e anterior
despesas_mes_atual = utl.filtrar_despesas_por_mes(despesas, ano_sel, mes_sel)
despesas_mes_anterior = utl.filtrar_despesas_por_mes(despesas, ano_ant, mes_ant)

st.html("<hr style='border: 0; border-top: 1px solid #E2E8F0; margin: 16px 0 24px 0;'>")

# ==============================================================================
# SEÇÃO 2: BALANCE, RECEITA, DESPESAS E INVESTIMENTOS (Proporção 2:1:1:1)
# ==============================================================================
total_balance, total_receita, total_investimentos = utl.gerar_resumo_contas(contas)
total_despesas_atual = sum(float(d.get("amount", 0.0)) for d in despesas_mes_atual)
total_despesas_anterior = sum(float(d.get("amount", 0.0)) for d in despesas_mes_anterior)

delta_txt_desp, delta_cor_txt_desp, delta_cor_bg_desp = utl.calcular_delta_percentual(
    total_despesas_atual, total_despesas_anterior
)

# Inverte o sentido da cor para Despesas: gastar menos é bom (verde), gastar mais é alerta (vermelho)
if total_despesas_anterior > 0:
    var_desp = ((total_despesas_atual - total_despesas_anterior) / total_despesas_anterior) * 100
    if var_desp > 0:
        delta_cor_txt_desp, delta_cor_bg_desp = "#B91C1C", "#FEE2E2"
    elif var_desp < 0:
        delta_cor_txt_desp, delta_cor_bg_desp = "#00875A", "#E3FCEF"

col_bal, col_rec, col_desp, col_inv = st.columns([2, 1, 1, 1], gap="medium")

with col_bal:
    metric_card(
        titulo="Balance Total",
        valor=formatar_moeda(total_balance),
        delta="▲ +4.2% vs mês ant.",
        bg_color="#131722",
        text_color="#FFFFFF",
        delta_text_color="#00D09C",
        delta_bg_color="rgba(0, 208, 156, 0.15)",
        border_color="rgba(255, 255, 255, 0.1)",
        is_highlight=True
    )

with col_rec:
    metric_card(
        titulo="Receita",
        valor=formatar_moeda(total_receita),
        delta="▲ +1.5% vs ant.",
        bg_color="#FFFFFF",
        text_color="#0F172A",
        delta_text_color="#0F766E",
        delta_bg_color="#CCFBF1",
        border_color="#E2E8F0"
    )

with col_desp:
    metric_card(
        titulo="Despesas",
        valor=formatar_moeda(total_despesas_atual),
        delta=delta_txt_desp,
        bg_color="#FFFFFF",
        text_color="#0F172A",
        delta_text_color=delta_cor_txt_desp,
        delta_bg_color=delta_cor_bg_desp,
        border_color="#E2E8F0"
    )

with col_inv:
    metric_card(
        titulo="Investimentos",
        valor=formatar_moeda(total_investimentos),
        delta="▲ +8.0% vs ant.",
        bg_color="#FFFFFF",
        text_color="#0F172A",
        delta_text_color="#1D4ED8",
        delta_bg_color="#DBEAFE",
        border_color="#E2E8F0"
    )

st.write("")


# ==============================================================================
# SEÇÃO 3: OVERVIEW (60%) | GASTOS PREVISTOS (30%) | COLUNA LATERAL (10%)
# ==============================================================================
col_overview, col_previstos, col_laterais = st.columns([6, 2.5, 1.5], gap="medium")

def resolver_categoria_pai(cat_id: str) -> str:
    if not cat_id or cat_id not in categorias:
        return "Outros"
    cat = categorias[cat_id]
    parent_id = cat.get("parent_id")
    if parent_id and parent_id in categorias:
        return categorias[parent_id].get("name", "Outros")
    return cat.get("name", "Outros")


# --- 1. OVERVIEW: GASTOS POR CATEGORIA (60%) ---
with col_overview:
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-bottom: 2px;'>Overview: Gastos por Categoria</p>", unsafe_allow_html=True)
        
        if despesas_mes_atual:
            dados_cat = []
            for d in despesas_mes_atual:
                nome_categoria_pai = resolver_categoria_pai(d.get("category_id"))
                dados_cat.append({"categoria": nome_categoria_pai, "valor": float(d.get("amount", 0.0))})

            df_cat = pd.DataFrame(dados_cat).groupby("categoria", as_index=False)["valor"].sum()
            soma_total_despesas = df_cat["valor"].sum() or 1.0

            # Formatação alinhada monoespaçada com divisória cinza sutil
            def formatar_rotulo_legenda(row):
                pct = (row["valor"] / soma_total_despesas) * 100
                val_fmt = formatar_moeda(row["valor"])
                
                LARGURA_NOME = 15
                LARGURA_VALOR = 13
                
                nome = str(row["categoria"])[:LARGURA_NOME]
                espacos_nome = "&nbsp;" * max(1, (LARGURA_NOME - len(nome)))
                col_nome = f"{nome}{espacos_nome}"
                
                espacos_valor = "&nbsp;" * max(1, (LARGURA_VALOR - len(val_fmt)))
                col_valor = f"{espacos_valor}{val_fmt}"
                
                pct_str = f"{pct:4.1f}%"
                espacos_pct = "&nbsp;" * max(1, (6 - len(pct_str)))
                col_pct = f"{espacos_pct}{pct_str}"
                
                divisor = "<br><span style='color: #E2E8F0; font-size: 7px;'>─────────────────────────────────────────</span>"
                
                linha_mono = (
                    f"<span style='font-family: monospace; font-size: 11px; color: #334155;'>"
                    f"<b>{col_nome}</b>{col_valor}&nbsp;&nbsp;<b>{col_pct}</b>"
                    f"</span>"
                )
                return f"{linha_mono}{divisor}"

            df_cat["label_completo"] = df_cat.apply(formatar_rotulo_legenda, axis=1)

            fig = px.pie(
                df_cat,
                names="label_completo",
                values="valor",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig.update_layout(
                margin=dict(t=5, b=5, l=10, r=10),
                height=360,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=11)
                )
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                hoverinfo="label+value+percent"
            )

            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Nenhuma despesa registrada para exibir o gráfico.")


# --- 2. GASTOS PREVISTOS (30% - RECURRING BILLS) ---
with col_previstos:
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;'> Gastos Previstos</p>", unsafe_allow_html=True)
        
        descricoes_despesas = [str(d.get("description", "")).lower() for d in recorrentes]

        itens_recorrentes = recorrentes if recorrentes else [
            {"name": "Aluguel", "amount": 2200.00},
            {"name": "Condomínio", "amount": 650.00},
            {"name": "Energia", "amount": 280.00},
            {"name": "Internet", "amount": 120.00},
            {"name": "Spotify", "amount": 34.90},
            {"name": "Academia", "amount": 150.00},
            {"name": "Plano Celular", "amount": 89.90},
            {"name": "Seguro Auto", "amount": 210.00}
        ]

        # 1. Cabeçalho fixo no topo (sem espaços no início das linhas)
        header_html = (
            '<div style="display: grid; grid-template-columns: 4fr 3fr 1.5fr; font-size: 0.75rem; font-weight: 600; color: #64748B; padding-bottom: 6px; border-bottom: 1px solid #E2E8F0; margin-bottom: 6px;">'
            '<span>NOME</span>'
            '<span style="text-align: right;">VALOR</span>'
            '<span style="text-align: center;">STATUS</span>'
            '</div>'
        )

        # 2. Monta as linhas de dados em linha única (evita qualquer interpretação de tab/espaço como código)
        linhas_html = []
        for bill in itens_recorrentes:
            nome_bill = bill.get("name") or bill.get("description", "Gasto")
            valor_bill = float(bill.get("amount", 0.0))
            ja_pago = any(nome_bill.lower() in d_desc for d_desc in descricoes_despesas)
            
            badge = "✅" if ja_pago else "⏳"
            
            linha = (
                '<div style="display: grid; grid-template-columns: 4fr 3fr 1.5fr; align-items: center; font-size: 0.83rem; padding: 7px 0; border-bottom: 1px solid #F8FAFC;">'
                f'<span style="font-weight: 500; color: #1E293B; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{nome_bill}">{nome_bill}</span>'
                f'<span style="color: #475569; text-align: right; font-family: monospace; font-size: 0.80rem;">{formatar_moeda(valor_bill)}</span>'
                f'<span style="text-align: center; font-size: 0.85rem;" title="{"Pago" if ja_pago else "Pendente"}">{badge}</span>'
                '</div>'
            )
            linhas_html.append(linha)

        conteudo_linhas = "".join(linhas_html)

        # 3. Envolve no container de scroll fixo (255px de altura)
        scroll_container_html = (
            '<div style="height: 320px; max-height: 320px; overflow-y: auto; padding-right: 6px;">'
            f'{conteudo_linhas}'
            '</div>'
        )

        # Renderiza o HTML completo
        st.html(header_html + scroll_container_html)


# --- 3. COLUNA LATERAL EMPILHADA (10%) ---
with col_laterais:
    # 🏦 Caixa 1: Gastos por Banco
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;'>Gastos por Banco</p>", unsafe_allow_html=True)
        st.markdown("<div style='height: 10px; overflow-y: auto;'>", unsafe_allow_html=True)
        if despesas_mes_atual and contas:
            mapa_contas_info = {c["id"]: c["name"] for c in contas}
            dados_bancos = []
            for d in despesas_mes_atual:
                banco_nome = mapa_contas_info.get(d.get("account_id"), "Outros")
                dados_bancos.append({"banco": banco_nome, "valor": float(d.get("amount", 0.0))})

            df_bancos = pd.DataFrame(dados_bancos).groupby("banco", as_index=False)["valor"].sum()
            for _, r in df_bancos.iterrows():
                st.caption(f"**{r['banco']}**")
                st.markdown(f"<span style='font-size: 0.80rem; font-weight: 600;'>{formatar_moeda(r['valor'])}</span>", unsafe_allow_html=True)
        else:
            st.caption("Sem dados.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 🛍️ Caixa 2: Compras Parceladas (Renomeado)
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;'>Compras Parceladas</p>", unsafe_allow_html=True)
        
        # Calcula parcelas projetadas especificamente para o próximo mês
        hoje = datetime.now().date()
        mes_seguinte_inicio = (hoje.replace(day=1) + relativedelta(months=1))
        mes_seguinte_fim = (hoje.replace(day=1) + relativedelta(months=2))
        
        parcelas_mes_seguinte = [
            float(d.get("amount", 0.0)) for d in despesas_mes_atual 
            if d.get("installment_number") is not None
            and mes_seguinte_inicio <= datetime.strptime(d.get("expense_date"), "%Y-%m-%d").date() < mes_seguinte_fim
        ]
        total_parcelas_prox_mes = sum(parcelas_mes_seguinte)

        st.markdown("<div style='height: 5px; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
        st.caption("Próximo mês:")
        st.markdown(f"**{formatar_moeda(total_parcelas_prox_mes)}**")
        st.caption("Comprometido")
        st.markdown("</div>", unsafe_allow_html=True)

st.write("")


# ==============================================================================
# SEÇÃO 4: TRANSAÇÕES RECENTES (Largura Total)
# ==============================================================================
st.markdown("<p style='font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;'>💳 Transações Recentes</p>", unsafe_allow_html=True)

if not despesas_mes_atual:
    st.info("Nenhuma despesa recente encontrada.")
else:
    mapa_contas = {c["id"]: c for c in contas}

    linhas_tabela = []
    for exp in despesas_mes_atual[:5]:
        conta_info = mapa_contas.get(exp.get("account_id"), {})
        cat_info = categorias.get(exp.get("category_id"), {})

        icone_conta = conta_info.get("icon")
        logo_url = f"{API_URL}/imgs/{icone_conta}" if icone_conta else None

        num_p = exp.get("installment_number")
        tot_p = exp.get("total_installments")
        parcela_str = f"{num_p}/{tot_p}" if num_p and tot_p else "À vista"

        linhas_tabela.append({
            "logo": logo_url,
            "conta": conta_info.get("name", "Outra"),
            "data": exp.get("expense_date"),
            "descricao": exp.get("description"),
            "categoria": cat_info.get("name", "Sem Categoria"),
            "parcela": parcela_str,
            "valor": float(exp.get("amount", 0.0))
        })

    df_ultimas = pd.DataFrame(linhas_tabela)

    st.dataframe(
        df_ultimas,
        width='stretch',
        hide_index=True,
        column_config={
            "logo": st.column_config.ImageColumn("Conta", width="small"),
            "conta": st.column_config.TextColumn("Instituição"),
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "parcela": st.column_config.TextColumn("Parcela"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")
        }
    )

st.divider()
if st.button("🔄 Atualizar Indicadores"):
    st.cache_data.clear()
    st.rerun()