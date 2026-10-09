import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

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
    
    .side-card-banco {
        min-height: 170px; /* Ajuste este valor em pixels */
        max-height: 170px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .side-card-previsto {
        min-height: 170px; /* Ajuste este valor em pixels */
        max-height: 170px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* Container com sombra garantida */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# --- CARD DE MÉTRICA COM BADGE DESTACADO NO DELTA ---
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
    try:
        res_acc = requests.get(f"{API_URL}/accounts/")
        if res_acc.status_code == 200:
            contas = res_acc.json()

        res_cat = requests.get(f"{API_URL}/categories/")
        if res_cat.status_code == 200:
            for cat in res_cat.json():
                categorias[cat["id"]] = cat

        res_exp = requests.get(f"{API_URL}/expenses/?limit=100")
        if res_exp.status_code == 200:
            despesas = res_exp.json()
    except Exception as e:
        st.error(f"Erro de comunicação com a API: {e}")

    return contas, categorias, despesas

contas, categorias, despesas = buscar_dados_completos()

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ==============================================================================
# SEÇÃO 1: SAUDAÇÕES E SELEÇÃO DE MÊS (~10% Altura)
# ==============================================================================
col_saudacao, _, col_mes = st.columns([5, 2, 3], vertical_alignment="center")

with col_saudacao:
    st.markdown("### Olá Jessica!\nAqui está um overview das suas finanças pessoais")

with col_mes:
    meses_opcoes = ["Outubro/2026", "Setembro/2026", "Agosto/2026", "Julho/2026"]
    mes_selecionado = st.selectbox("Mês", options=meses_opcoes, index=0)

st.write("")


# ==============================================================================
# SEÇÃO 2: BALANCE, RECEITA, DESPESAS E INVESTIMENTOS (~25% Altura, Proporção 2:1:1:1)
# ==============================================================================
total_balance = sum(float(c.get("balance", 0.0)) for c in contas)
total_despesas = sum(float(exp.get("amount", 0.0)) for exp in despesas)
total_receita = 12500.00
total_investimentos = 3000.00

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
        valor=formatar_moeda(total_despesas),
        delta="▼ -2.1% vs ant.",
        bg_color="#FFFFFF",
        text_color="#0F172A",
        delta_text_color="#B91C1C",
        delta_bg_color="#FEE2E2",
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
# SEÇÃO 3: OVERVIEW, GASTOS POR BANCO E PREVISTOS (Com Sombra e Hierarquia de Categoria)
# ==============================================================================
col_overview, col_laterais = st.columns([7, 3], gap="medium")

# Função auxiliar para resolver a categoria pai
def resolver_categoria_pai(cat_id: str) -> str:
    if not cat_id or cat_id not in categorias:
        return "Outros"
    cat = categorias[cat_id]
    parent_id = cat.get("parent_id")
    # Se tiver pai cadastrado, busca o nome do pai
    if parent_id and parent_id in categorias:
        return categorias[parent_id].get("name", "Outros")
    return cat.get("name", "Outros")


# --- 70%: Caixa de Overview ---
with col_overview:
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-bottom: 2px;'>Overview: Gastos por Categoria</p>", unsafe_allow_html=True)
        
        if despesas:
            dados_cat = []
            for d in despesas:
                nome_categoria_pai = resolver_categoria_pai(d.get("category_id"))
                dados_cat.append({"categoria": nome_categoria_pai, "valor": float(d.get("amount", 0.0))})

            df_cat = pd.DataFrame(dados_cat).groupby("categoria", as_index=False)["valor"].sum()
            soma_total_despesas = df_cat["valor"].sum() or 1.0

            def formatar_rotulo_legenda(row):
                pct = (row["valor"] / soma_total_despesas) * 100
                val_fmt = formatar_moeda(row["valor"])
                
                # 1. Defina as larguras fixas de cada coluna (em número de caracteres)
                LARGURA_NOME = 16   # ex: "Supermercado    "
                LARGURA_VALOR = 14  # ex: "  R$ 1.250,00 "
                
                # Trunca se o nome for gigante ou completa com &nbsp; à direita (alinhado à esquerda)
                nome = str(row["categoria"])[:LARGURA_NOME]
                espacos_nome = "&nbsp;" * max(1, (LARGURA_NOME - len(nome)))
                col_nome = f"{nome}{espacos_nome}"
                
                # Completa com &nbsp; à esquerda do valor (para alinhar os números à direita)
                espacos_valor = "&nbsp;" * max(1, (LARGURA_VALOR - len(val_fmt)))
                col_valor = f"{espacos_valor}{val_fmt}"
                
                # Formata a porcentagem com largura fixa (ex: "  34.5%")
                pct_str = f"{pct:5.1f}%"
                espacos_pct = "&nbsp;" * max(1, (7 - len(pct_str)))
                col_pct = f"{espacos_pct}{pct_str}"
                
                # Linha divisória sutil em cinza claro com caracteres de traço contínuo
                divisor = "<br><span style='color: #E2E8F0; font-size: 7px;'>─────────────────────────────────────────────</span>"
                
                # 2. Envolve tudo numa fonte monoespaçada para garantir que cada &nbsp; tenha o mesmo tamanho
                texto_linha = (
                    f"<span style='font-family: monospace; font-size: 11px; color: #334155;'>"
                    f"<b>{col_nome}</b>{col_valor}&nbsp;&nbsp;<b>{col_pct}</b>"
                    f"</span>"
                )
                
                return f"{texto_linha}{divisor}"

            df_cat["label_completo"] = df_cat.apply(formatar_rotulo_legenda, axis=1)

            fig = px.pie(
                df_cat,
                names="label_completo",
                values="valor",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            # Altura do gráfico controlando a altura total da caixa esquerda
            fig.update_layout(
                margin=dict(t=5, b=5, l=10, r=10),
                height=330,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=11),
                    itemwidth=30,
                    tracegroupgap=10  # Respiro entre os itens
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

# --- 30%: Caixas Laterais com Altura Customizável ---
with col_laterais:
    # 🏦 Caixa 1: Gastos por Banco
    with st.container(border=True):
        # Altura configurável via CSS inline no wrapper interno (ex: 145px)
        st.markdown("<p style='font-size: 0.90rem; font-weight: 600; margin-bottom: 4px;'>🏦 Gastos por Banco</p>", unsafe_allow_html=True)
        
        # Área rolável caso haja muitos bancos, mantendo a altura cravada
        st.markdown("<div style='height: 37px; overflow-y: auto; padding-right: 4px;'>", unsafe_allow_html=True)
        if despesas and contas:
            mapa_contas_info = {c["id"]: c["name"] for c in contas}
            dados_bancos = []
            for d in despesas:
                banco_nome = mapa_contas_info.get(d.get("account_id"), "Outros")
                dados_bancos.append({"banco": banco_nome, "valor": float(d.get("amount", 0.0))})

            df_bancos = pd.DataFrame(dados_bancos).groupby("banco", as_index=False)["valor"].sum()
            for _, r in df_bancos.iterrows():
                cb_nome, cb_val = st.columns([3, 2])
                cb_nome.caption(f"**{r['banco']}**")
                cb_val.caption(f"**{formatar_moeda(r['valor'])}**")
        else:
            st.caption("Sem lançamentos por instituição.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 📅 Caixa 2: Gastos Previstos
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.90rem; font-weight: 600; margin-bottom: 4px;'>📅 Gastos Previstos</p>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 40px; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
        hoje = datetime.now().date()
        gastos_futuros = [
            float(d.get("amount", 0.0)) for d in despesas 
            if datetime.strptime(d.get("expense_date"), "%Y-%m-%d").date() > hoje
        ]
        total_futuro = sum(gastos_futuros)
        
        st.caption("Parcelas Futuras Contratadas:")
        st.markdown(f"#### {formatar_moeda(total_futuro)}")
        st.caption("Faturas em aberto nos cartões: **R$ 0,00**")
        st.markdown("</div>", unsafe_allow_html=True)

st.write("")


# ==============================================================================
# SEÇÃO 4: TRANSAÇÕES RECENTES (Largura Total)
# ==============================================================================
st.markdown("<p style='font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;'>💳 Transações Recentes</p>", unsafe_allow_html=True)

if not despesas:
    st.info("Nenhuma despesa recente encontrada.")
else:
    mapa_contas = {c["id"]: c for c in contas}

    linhas_tabela = []
    for exp in despesas[:15]:
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