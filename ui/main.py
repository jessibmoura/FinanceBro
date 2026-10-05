import streamlit as st
import pandas as pd
import requests
from config import API_URL

st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Painel Financeiro")

# --- FUNÇÕES AUXILIARES DE BUSCA NA API ---
@st.cache_data(ttl=15)
def buscar_dados_dashboard():
    contas = []
    despesas = []
    categorias = {}

    try:
        # 1. Busca contas cadastradas
        res_acc = requests.get(f"{API_URL}/accounts/")
        if res_acc.status_code == 200:
            contas = res_acc.json()

        # 2. Busca categorias para resolução de nomes/ícones
        res_cat = requests.get(f"{API_URL}/categories/")
        if res_cat.status_code == 200:
            for cat in res_cat.json():
                categorias[cat["id"]] = {
                    "name": cat["name"],
                    "icon": cat.get("icon")
                }

        # 3. Busca últimas despesas cadastradas
        res_exp = requests.get(f"{API_URL}/expenses/?limit=50")
        if res_exp.status_code == 200:
            despesas = res_exp.json()

    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")

    return contas, categorias, despesas


# Carregando dados
contas, categorias, despesas = buscar_dados_dashboard()

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- 1. SEPARAÇÃO DOS MONTANTES POR TIPO DE CONTA ---
# Tudo que NÃO for CREDIT entra no Saldo Armazenado (Patrimônio/Liquidez)
contas_armazenadas = [c for c in contas if str(c.get("account_type", "")).upper() != "CORRENTE" and str(c.get("account_type", "")).upper() != "CONTA_SALARIO"]
total_armazenado = sum(float(c.get("balance", 0.0)) for c in contas_armazenadas)

# Contas do tipo CREDIT entram como Saldo Disponível (Limite de Crédito)
contas_credito = [c for c in contas if str(c.get("account_type", "")).upper() == "CORRENTE" or str(c.get("account_type", "")).upper() == "CONTA_SALARIO"]
total_credito = sum(float(c.get("balance", 0.0)) for c in contas_credito)

# Cards de resumo no topo
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Saldo Armazenado",
        value=formatar_moeda(total_armazenado),
        help="Soma de contas correntes, investimentos e poupança."
    )
    st.caption(f"{len(contas_armazenadas)} conta(s)")

with col2:
    st.metric(
        label="💳 Saldo Disponível (Crédito)",
        value=formatar_moeda(total_credito),
        help="Limite disponível nos cartões de crédito."
    )
    st.caption(f"{len(contas_credito)} cartão(ões)")

with col3:
    st.metric(
        label="🏦 Total de Contas",
        value=f"{len(contas)} ativas"
    )
    st.caption("Cadastradas no sistema")


# --- 2. DETALHAMENTO EXPANSÍVEL POR BANCO ---
with st.expander("🔍 Ver detalhamento por banco/conta", expanded=False):
    tab_armazenado, tab_credito = st.tabs(["💰 Saldo Armazenado", "💳 Cartões de Crédito"])

    def renderizar_lista_contas(lista_contas):
        if not lista_contas:
            st.info("Nenhuma conta registrada neste grupo.")
            return

        for acc in lista_contas:
            col_icon, col_nome, col_saldo = st.columns([1, 4, 3])
            
            # Ícone do Banco
            with col_icon:
                icone = acc.get("icon")
                if icone:
                    # Carrega a imagem da API estática
                    st.image(f"{API_URL}/imgs/{icone}", width=36)
                else:
                    st.markdown("🏦")

            # Nome e tipo da conta
            with col_nome:
                st.markdown(f"**{acc.get('name')}**")
                tipo = acc.get("account_type", "CONTA").capitalize()
                st.caption(f"Tipo: {tipo}")

            # Saldo formatado
            with col_saldo:
                saldo_val = float(acc.get("balance", 0.0))
                st.markdown(f"**{formatar_moeda(saldo_val)}**")

            st.divider()

    with tab_armazenado:
        renderizar_lista_contas(contas_armazenadas)

    with tab_credito:
        renderizar_lista_contas(contas_credito)

st.divider()

# --- 2. TABELA DE ÚLTIMAS DESPESAS ACRESCENTADAS ---
st.subheader("💳 Últimas Despesas Registradas")

if not despesas:
    st.info("Nenhuma despesa cadastrada até o momento. Acesse a aba **Importar Faturas** no menu lateral para registrar seus lançamentos!")
else:
    mapa_contas = {c["id"]: c for c in contas}

    linhas_tabela = []
    for exp in despesas:
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
        use_container_width=True,
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

if st.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()