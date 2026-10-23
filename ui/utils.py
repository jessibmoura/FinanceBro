import uuid
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- 1. GERADOR DE OPÇÕES DE MESES ---
def gerar_opcoes_meses(qtd_meses: int = 12):
    hoje = datetime.now().date()
    nomes_meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    opcoes = []
    for i in range(qtd_meses):
        d = hoje - relativedelta(months=i)
        nome_formatado = f"{nomes_meses[d.month - 1]}/{d.year}"
        opcoes.append({
            "label": nome_formatado,
            "ano": d.year,
            "mes": d.month
        })
    return opcoes

# --- 2. FILTRAR DESPESAS POR MÊS E ANO ---
def filtrar_despesas_por_mes(despesas: list, ano: int, mes: int):
    resultado = []
    for d in despesas:
        data_str = d.get("expense_date")
        if not data_str:
            continue
        try:
            dt = datetime.strptime(str(data_str)[:10], "%Y-%m-%d").date()
            if dt.year == ano and dt.month == mes:
                resultado.append(d)
        except ValueError:
            continue
    return resultado

# --- 3. CÁLCULO DE DELTA PERCENTUAL VS MÊS ANTERIOR ---
def calcular_delta_percentual(valor_atual: float, valor_anterior: float) -> tuple[str, str, str]:
    """Retorna (badge_texto, cor_texto, cor_fundo)"""
    if valor_anterior == 0:
        if valor_atual > 0:
            return ("▲ +100%", "#00875A", "#E3FCEF")
        return ("0.0%", "#64748B", "#F1F5F9")
    
    variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
    if variacao > 0:
        return (f"▲ +{variacao:.1f}% vs ant.", "#00875A", "#E3FCEF")
    elif variacao < 0:
        return (f"▼ {variacao:.1f}% vs ant.", "#B91C1C", "#FEE2E2")
    else:
        return ("0.0% vs ant.", "#64748B", "#F1F5F9")


def gerar_resumo_contas(contas: list) -> tuple[float, float]:
    """
    Retorna (total_armazenado, total_credito)
    total_armazenado: soma das contas que não são do tipo CORRENTE ou CONTA_SALARIO
    total_credito: soma das contas do tipo CORRENTE ou CONTA_SALARIO
    """
    contas_armazenadas = [c for c in contas if str(c.get("account_type", "")).upper() != "CORRENTE" and str(c.get("account_type", "")).upper() != "CONTA_SALARIO"]
    total_balance = sum(float(c.get("balance", 0.0)) for c in contas_armazenadas)

    # Contas do tipo CREDIT entram como Saldo Disponível (Limite de Crédito)
    contas_credito = [c for c in contas if str(c.get("account_type", "")).upper() == "CORRENTE" or str(c.get("account_type", "")).upper() == "CONTA_SALARIO"]
    total_receita = sum(float(c.get("balance", 0.0)) for c in contas_credito)

    contas_investimento = [c for c in contas if str(c.get("account_type", "")).upper() == "INVESTIMENTO"]
    total_investimentos = sum(float(c.get("balance", 0.0)) for c in contas_investimento)

    return total_balance, total_receita, total_investimentos

def expand_installments(df: pd.DataFrame, generate_past: bool = False) -> pd.DataFrame:
    """
    Trata compras parceladas novas ou em andamento.
    Assume que a coluna 'data' representa a data da 1ª parcela (data da compra original).
    
    - Corrige a data da linha atual para refletir seu mês correto: data_base + (Num_parcela - 1) meses.
    - Gera as parcelas futuras: de (Num_parcela + 1) até Total_parcelas.
    - Se generate_past=True: gera também as parcelas retroativas anteriores que ficaram de fora.
    """
    novas_linhas = []
    df = df.copy()

    if "Num_parcela" not in df.columns:
        df["Num_parcela"] = None
    if "Total_parcelas" not in df.columns:
        df["Total_parcelas"] = None
    if "installment_group_id" not in df.columns:
        df["installment_group_id"] = None

    for idx, row in df.iterrows():
        num_parcela = row.get("Num_parcela")
        total_parcelas = row.get("Total_parcelas")

        # Verifica se é uma transação parcelada válida
        is_parcelada = (
            pd.notna(num_parcela)
            and pd.notna(total_parcelas)
            and int(total_parcelas) > 1
        )

        if is_parcelada:
            num = int(num_parcela) # 9
            total = int(total_parcelas)
            group_id = str(uuid.uuid4())

            # Converte a data_base (considerada como a data da 1ª parcela)
            data_base = row["Data"]
            if isinstance(data_base, str):
                data_base = datetime.strptime(data_base, "%Y-%m-%d").date()
            elif isinstance(data_base, pd.Timestamp):
                data_base = data_base.date()

            # 1. Atualiza a linha atual no DataFrame
            # Corrige a data dela para o mês correspondente ao seu número de parcela
            data_parcela_atual = data_base + relativedelta(months=(num - 1))
            df.at[idx, "Data"] = data_parcela_atual
            df.at[idx, "installment_group_id"] = group_id
            df.at[idx, "Num_parcela"] = num
            df.at[idx, "Total_parcelas"] = total

            # 2. (Opcional) Gerar parcelas passadas (de 1 até num - 1)
            # Útil apenas se você quiser preencher o histórico que ficou para trás
            if generate_past and num > 1:
                for i in range(1, num):
                    linha_passada = row.copy()
                    linha_passada["Data"] = data_base + relativedelta(months=(i - 1))
                    linha_passada["Num_parcela"] = i
                    linha_passada["Total_parcelas"] = total
                    linha_passada["installment_group_id"] = group_id
                    novas_linhas.append(linha_passada)

            # 3. Gerar as parcelas FUTURAS (de num + 1 até total)
            if num < total:
                for i in range(num + 1, total + 1): # 10, 13
                    linha_futura = row.copy()
                    linha_futura["Data"] = data_base + relativedelta(months=(i - 1))
                    linha_futura["Num_parcela"] = i
                    linha_futura["Total_parcelas"] = total
                    linha_futura["installment_group_id"] = group_id
                    novas_linhas.append(linha_futura)

    if novas_linhas:
        df_novas = pd.DataFrame(novas_linhas)
        df_final = pd.concat([df, df_novas], ignore_index=True)
    else:
        df_final = df

    return df_final.sort_values(by="Data").reset_index(drop=True)