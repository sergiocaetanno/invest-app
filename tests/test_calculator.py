import pandas as pd

from calculator import lucro_da_venda, normalizar_ticker, processar_dados


def test_normalizar_ticker_remove_sufixo_fracionario():
    assert normalizar_ticker("klbn4f") == "KLBN4"
    assert normalizar_ticker("PETR4") == "PETR4"
    assert normalizar_ticker("VALE3F") == "VALE3"


def test_preco_medio_ponderado_apos_compras():
    df = pd.DataFrame([
        _linha("01/01/2026", "Compra", "PETR4", 10, 20.0),
        _linha("02/01/2026", "Compra", "PETR4", 10, 30.0),
    ])

    resultado, erro = processar_dados(df)

    assert erro is None
    ultima = resultado.iloc[-1]
    assert ultima["Preço Médio (Pós)"] == 25.0
    assert ultima["Saldo Qtd"] == 20
    assert ultima["Saldo Investido"] == 500.0


def test_lucro_na_venda_usa_preco_medio():
    df = pd.DataFrame([
        _linha("01/01/2026", "Compra", "PETR4F", 10, 20.0),
        _linha("03/01/2026", "Venda", "PETR4", 4, 25.0),
    ])

    resultado, erro = processar_dados(df)

    assert erro is None
    venda = resultado.iloc[-1]
    assert venda["Ticker"] == "PETR4"
    assert venda["Lucro/Prejuízo (Venda)"] == lucro_da_venda(25.0, 20.0, 4)
    assert venda["Lucro/Prejuízo (Venda)"] == 20.0
    assert venda["Preço Médio (Pós)"] == 20.0
    assert venda["Saldo Qtd"] == 6


def test_venda_que_zera_posicao_reseta_preco_medio():
    df = pd.DataFrame([
        _linha("01/01/2026", "Compra", "VALE3", 5, 10.0),
        _linha("02/01/2026", "Venda", "VALE3", 5, 12.0),
    ])

    resultado, erro = processar_dados(df)

    assert erro is None
    venda = resultado.iloc[-1]
    assert venda["Lucro/Prejuízo (Venda)"] == 10.0
    assert venda["Saldo Qtd"] == 0
    assert venda["Preço Médio (Pós)"] == 0


def test_arquivo_sem_colunas_obrigatorias():
    df = pd.DataFrame([{"Ativo": "PETR4", "Qtd": 1}])

    resultado, erro = processar_dados(df)

    assert resultado is None
    assert erro is not None
    assert "Código de Negociação" in erro


def _linha(data, tipo, ticker, quantidade, preco):
    return {
        "Data do Negócio": data,
        "Tipo de Movimentação": tipo,
        "Código de Negociação": ticker,
        "Quantidade": quantidade,
        "Preço": preco,
    }
