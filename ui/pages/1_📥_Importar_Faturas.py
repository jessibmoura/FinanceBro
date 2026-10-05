import streamlit as st
import pandas as pd
from datetime import datetime
from personal_rules import process_xp_sheet, categorize
from utils import expand_installments
import requests

from config import API_URL

st.set_page_config(
    page_title="Importador de Faturas",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Importação de Faturas e Extratos")
st.markdown("Submeta o arquivo `.csv`, revise as transações na tabela interativa e selecione o que deseja importar.")

@st.cache_data(ttl=30)
def carregar_metadados():
    contas = {}
    categorias = {}
    try:
        res_acc = requests.get(f"{API_URL}/accounts/")
        if res_acc.status_code == 200:
            for acc in res_acc.json():
                contas[acc["name"]] = acc["id"]

        res_cat = requests.get(f"{API_URL}/categories/")
        if res_cat.status_code == 200:
            for cat in res_cat.json():
                categorias[cat["name"]] = cat["id"]
    except Exception as e:
        st.warning(f"Não foi possível conectar à API: {e}")

    return contas, categorias

mapa_contas, mapa_categorias = carregar_metadados()
nomes_bancos = list(mapa_contas.keys()) if mapa_contas else ["Nubank", "XP"]
nomes_categorias = list(mapa_categorias.keys()) if mapa_categorias else ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Outros"]

# 1. Seleção da Instituição Financeira
banco = st.radio(
    "Selecione o Banco / Cartão:",
    options=["Nubank", "XP"],
    index=0,
    horizontal=True,
    help="Escolha o banco emissor do arquivo para aplicar o padrão correto de colunas."
)

ICONES_BANCO = {
    "Nubank": f"{API_URL}/imgs/nubank.png",
    "XP": f"{API_URL}/imgs/xp.png"
}

def normalize_dataframe(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
    if bank_name == "XP":
        df_result = process_xp_sheet(df)
    df_result["icone"] = ICONES_BANCO.get(bank_name, None)
    df_result.insert(0, "importar", True)
    return df_result

# 2. Upload do arquivo
uploaded_file = st.file_uploader(
    f"Faça o upload da fatura/extrato ({banco}) em formato CSV",
    type=["csv"]
)

# Inicializa ou reseta o DataFrame no session_state ao enviar novo arquivo
if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}_{banco}"
    if st.session_state.get("current_file_id") != file_id:
        st.session_state["df_transacoes"] = normalize_dataframe(uploaded_file, banco)
        st.session_state["current_file_id"] = file_id
        st.session_state["classificado"] = False

# Se temos dados carregados no session_state
if "df_transacoes" in st.session_state:
    st.subheader("📋 Revisão e Categorização")

    # Barra de Ações com botões
    col_btn1, col_btn2 = st.columns([1, 4])
    
    with col_btn1:
        if st.button("🪄 Classificar Categorias", type="secondary", help="Executa o modelo/regras nas descrições atuais"):
            # Pega as descrições (mesmo que você já tenha alterado na tabela) e classifica
            with st.spinner("Classificando transações..."):
                st.session_state["df_transacoes"]["Categoria"] = st.session_state["df_transacoes"]["Descricao"].apply(categorize)
                st.session_state["classificado"] = True
            st.toast("Categorias sugeridas com sucesso!", icon="✨")
            st.rerun()

    # --- 6. TABELA INTERATIVA COM ST.DATA_EDITOR ---
    edited_df = st.data_editor(
        st.session_state["df_transacoes"],
        width='stretch',
        hide_index=True,
        key="data_editor_faturas",
        column_config={
                "importar": st.column_config.CheckboxColumn(
                    "Importar?",
                    help="Desmarque caso não queira registrar esta despesa no banco.",
                    default=True,
                ),
                "icone": st.column_config.ImageColumn("Conta", width="small"),
                "Data": st.column_config.DateColumn(
                    "Data",
                    format="DD/MM/YYYY"
                ),
                "Estabelecimento": st.column_config.TextColumn(
                    "Estabelecimento",
                    help="Descrição original do estabelecimento.",
                    required=True
                ),
                "Descricao": st.column_config.TextColumn(
                    "Descrição",
                    help="Você pode renomear a descrição para algo mais amigável.",
                    required=True
                ),
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    help="Categoria atribuída pela classificação. Você pode alterar manualmente aqui se quiser.",
                    options=nomes_categorias,
                    required=True
                ),
                "Valor": st.column_config.NumberColumn(
                    "Valor (R$)",
                    format="R$ %.2f",
                    disabled=False
                ),
                "Num_parcela": st.column_config.TextColumn(
                    "N° Parcela",
                    disabled=False
                ),
                "Total_parcelas": st.column_config.TextColumn(
                    "Total de Parcelas",
                    disabled=False
                )
        }
    )

    # Sempre mantém o session_state sincronizado com as edições manuais feitas nas células
    st.session_state["df_transacoes"] = edited_df

    # --- 7. MÉTRICAS E RESUMO ---
    linhas_ativas = edited_df[edited_df["importar"] == True]
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Lançamentos selecionados", f"{len(linhas_ativas)} de {len(edited_df)}")
    col_m2.metric("Total a ser registrado", f"R$ {linhas_ativas['Valor'].sum():,.2f}")

    # --- 8. SUBMISSÃO FINAL ---
    st.divider()
    if st.button("💾 Confirmar e Submeter ao Banco", type="primary"):
        if linhas_ativas.empty:
            st.warning("Nenhuma transação selecionada para importação.")
        else:
            with st.spinner("Enviando transações para o banco de dados..."):
                account_id = mapa_contas.get(banco)
                linhas_ativas["Num_parcela"] = linhas_ativas["Num_parcela"].replace(["-", " - ", "", " "], None)
                linhas_ativas["Total_parcelas"] = linhas_ativas["Total_parcelas"].replace(["-", " - ", "", " "], None)
                df_processado = expand_installments(linhas_ativas, generate_past=True)

                # Monta a lista de despesas no formato esperado pelo ExpenseCreate
                payload = []
                for _, row in df_processado.iterrows():
                    cat_id = mapa_categorias.get(row["Categoria"])
                    expense_item = {
                        "description": str(row["Descricao"]),
                        "amount": float(row["Valor"]),
                        "expense_date": str(row["Data"]),
                        "payment_method": "CREDIT",
                        "account_id": account_id,
                        "category_id": cat_id,
                        "installment_number": int(row["Num_parcela"]) if pd.notna(row.get("Num_parcela")) else None,
                        "total_installments": int(row["Total_parcelas"]) if pd.notna(row.get("Total_parcelas")) else None,
                        "installment_group_id": row.get("installment_group_id") if pd.notna(row.get("installment_group_id")) else None
                    }
                    payload.append(expense_item)
                
                try:
                    res = requests.post(f"{API_URL}/expenses/add_expenses", json=payload)
                    if res.status_code == 201:
                        st.balloons()
                        st.success(f"🎉 Sucesso! {len(res.json())} despesas foram salvas com sucesso no banco de dados.")

                        with st.expander("👀 Ver dados enviados para a API:"):
                            final_df = pd.DataFrame(payload).fillna("").astype(str)
                            st.dataframe(final_df, width='stretch')

                        del st.session_state["df_transacoes"]
                        del st.session_state["current_file_id"]
                        st.cache_data.clear()
                    else:
                        st.error(f"Erro ao salvar na API ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Falha de comunicação com a API: {e}")