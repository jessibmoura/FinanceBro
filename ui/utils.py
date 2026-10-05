import uuid
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta


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
            num = int(num_parcela)
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
                for i in range(num + 1, total + 1):
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