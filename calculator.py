import re

import pandas as pd

COL_DATA = "Data do Negócio"
COL_TIPO = "Tipo de Movimentação"
COL_TICKER = "Código de Negociação"
COL_QTD = "Quantidade"
COL_PRECO = "Preço"
REQUIRED_COLS = [COL_DATA, COL_TIPO, COL_TICKER, COL_QTD, COL_PRECO]


def normalizar_ticker(ticker: str) -> str:
    """Usa as 4 letras iniciais e o número seguinte. KLBN4F vira KLBN4."""
    ticker = ticker.strip().upper()
    match = re.match(r"^([A-Z]{4})(\d+)", ticker)
    if match:
        return match.group(1) + match.group(2)
    return ticker


def lucro_da_venda(preco: float, preco_medio: float, quantidade: float) -> float:
    """Lucro ou prejuízo da venda sobre o preço médio atual."""
    return (preco - preco_medio) * quantidade


def processar_dados(df: pd.DataFrame):
    df = df.copy()
    df.columns = df.columns.str.strip()

    if not all(col in df.columns for col in REQUIRED_COLS):
        return None, f"Erro: O arquivo deve conter as colunas: {', '.join(REQUIRED_COLS)}"

    df[COL_DATA] = pd.to_datetime(df[COL_DATA], dayfirst=True, errors="coerce")
    df = df.sort_values(by=COL_DATA).reset_index(drop=True)

    carteira = {}
    historico_operacoes = []

    for _, row in df.iterrows():
        ticker = str(row[COL_TICKER]).strip().upper()
        tipo = str(row[COL_TIPO]).strip()
        qtd = float(row[COL_QTD])
        preco = float(row[COL_PRECO])
        data = row[COL_DATA]
        ticker_base = normalizar_ticker(ticker)

        if ticker_base not in carteira:
            carteira[ticker_base] = {"qtd": 0.0, "pm": 0.0, "custo_total": 0.0}

        posicao = carteira[ticker_base]
        lucro_prejuizo = 0.0

        if "Compra" in tipo:
            posicao["custo_total"] += qtd * preco
            posicao["qtd"] += qtd
            posicao["pm"] = posicao["custo_total"] / posicao["qtd"] if posicao["qtd"] > 0 else 0
        elif "Venda" in tipo:
            lucro_prejuizo = lucro_da_venda(preco, posicao["pm"], qtd)
            posicao["qtd"] -= qtd
            posicao["custo_total"] = posicao["qtd"] * posicao["pm"]
            if posicao["qtd"] <= 0:
                posicao["qtd"] = 0
                posicao["custo_total"] = 0
                posicao["pm"] = 0

        historico_operacoes.append({
            "Data": data.strftime("%d/%m/%Y"),
            "Ticker": ticker_base,
            "Operação": tipo,
            "Qtd Operada": qtd,
            "Preço Execução": preco,
            "Valor Total Op": qtd * preco,
            "Preço Médio (Pós)": posicao["pm"],
            "Saldo Qtd": posicao["qtd"],
            "Saldo Investido": posicao["custo_total"],
            "Lucro/Prejuízo (Venda)": lucro_prejuizo if "Venda" in tipo else None,
        })

    return pd.DataFrame(historico_operacoes), None
