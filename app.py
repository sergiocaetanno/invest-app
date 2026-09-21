import streamlit as st
import pandas as pd
import io
import re

# Configuração da Página
st.set_page_config(page_title="Calculadora de Preço Médio e IR", layout="wide")

def normalizar_ticker(ticker):
    """
    Normaliza o ticker para usar apenas as 4 letras iniciais e o número que vem depois.
    Exemplos: KLBN4F -> KLBN4, KLBN4 -> KLBN4, PETR4F -> PETR4
    """
    ticker = ticker.strip().upper()
    # Extrai as primeiras 4 letras e o número que vem depois
    match = re.match(r'^([A-Z]{4})(\d+)', ticker)
    if match:
        return match.group(1) + match.group(2)
    # Se não encontrar o padrão, retorna o ticker original
    return ticker

def processar_dados(df):
    # Padronização dos nomes das colunas (remove espaços extras)
    df.columns = df.columns.str.strip()
    
    # Mapeamento de colunas baseado no seu arquivo
    col_data = 'Data do Negócio'
    col_tipo = 'Tipo de Movimentação'
    col_ticker = 'Código de Negociação'
    col_qtd = 'Quantidade'
    col_preco = 'Preço'
    
    # Verificação básica
    required_cols = [col_data, col_tipo, col_ticker, col_qtd, col_preco]
    if not all(col in df.columns for col in required_cols):
        return None, f"Erro: O arquivo deve conter as colunas: {', '.join(required_cols)}"

    # Tratamento de Tipos de Dados
    # Converter data para datetime (DD/MM/YYYY)
    df[col_data] = pd.to_datetime(df[col_data], dayfirst=True, errors='coerce')
    
    # Ordenar cronologicamente (essencial para o cálculo do PM)
    df = df.sort_values(by=col_data).reset_index(drop=True)

    # Dicionário para armazenar o estado atual de cada ativo
    # Estrutura: { 'TICKER': { 'qtd': 0, 'pm': 0, 'custo_total': 0 } }
    carteira = {}
    
    historico_operacoes = []

    for index, row in df.iterrows():
        ticker = row[col_ticker].strip().upper()
        tipo = row[col_tipo].strip()
        qtd = float(row[col_qtd])
        preco = float(row[col_preco])
        data = row[col_data]

        # Normalizar ticker: extrai apenas as 4 letras iniciais e o número (ignora letras no final)
        ticker_base = normalizar_ticker(ticker) 

        if ticker_base not in carteira:
            carteira[ticker_base] = {'qtd': 0.0, 'pm': 0.0, 'custo_total': 0.0}

        posicao = carteira[ticker_base]
        
        lucro_prejuizo = 0.0
        
        # Lógica de Compra (Altera PM)
        if 'Compra' in tipo:
            custo_operacao = qtd * preco
            posicao['custo_total'] += custo_operacao
            posicao['qtd'] += qtd
            
            if posicao['qtd'] > 0:
                posicao['pm'] = posicao['custo_total'] / posicao['qtd']
            else:
                posicao['pm'] = 0 # Zerou ou ficou negativo (short)

        # Lógica de Venda (Não altera PM, gera Lucro/Prejuízo)
        elif 'Venda' in tipo:
            # Lucro é calculado sobre a diferença entre Preço de Venda e o PM ATUAL
            lucro_prejuizo = (preco - posicao['pm']) * qtd
            
            posicao['qtd'] -= qtd
            
            # Atualiza o custo total proporcionalmente à saída
            # O PM se mantém, então Custo Total = PM * Nova Qtd
            posicao['custo_total'] = posicao['qtd'] * posicao['pm']
            
            # Se zerou a posição, reseta variáveis para evitar erros de arredondamento
            if posicao['qtd'] <= 0:
                posicao['qtd'] = 0
                posicao['custo_total'] = 0
                posicao['pm'] = 0

        # Registrar a linha processada
        historico_operacoes.append({
            'Data': data.strftime('%d/%m/%Y'),
            'Ticker': ticker_base,
            'Operação': tipo,
            'Qtd Operada': qtd,
            'Preço Execução': preco,
            'Valor Total Op': qtd * preco,
            'Preço Médio (Pós)': posicao['pm'],
            'Saldo Qtd': posicao['qtd'],
            'Saldo Investido': posicao['custo_total'],
            'Lucro/Prejuízo (Venda)': lucro_prejuizo if 'Venda' in tipo else None
        })

    df_resultado = pd.DataFrame(historico_operacoes)
    return df_resultado, None

# --- Interface Visual ---

st.title("📊 Calculadora de Investimentos & IR")
st.markdown("""
Esta ferramenta processa seu extrato de negociação da B3 (formato CSV/Excel), calcula o **Preço Médio** ponderado 
e apura o **Lucro ou Prejuízo** em vendas para auxílio no Imposto de Renda.
""")

uploaded_file = st.file_uploader("Arraste sua planilha aqui (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            # Tenta ler CSV (assumindo separador virgula conforme seu snippet, se falhar tenta ponto e virgula)
            try:
                df_raw = pd.read_csv(uploaded_file)
            except:
                uploaded_file.seek(0)
                df_raw = pd.read_csv(uploaded_file, sep=';')
        else:
            df_raw = pd.read_excel(uploaded_file)

        st.success("Arquivo carregado com sucesso! Processando...")
        
        df_processado, erro = processar_dados(df_raw)
        
        if erro:
            st.error(erro)
        else:
            # Formatação Visual
            st.subheader("Extrato Detalhado de Operações")
            
            # Formatar colunas numéricas para exibição
            df_display = df_processado.copy()
            cols_moeda = ['Preço Execução', 'Valor Total Op', 'Preço Médio (Pós)', 'Saldo Investido', 'Lucro/Prejuízo (Venda)']
            
            for col in cols_moeda:
                df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "-")
            
            df_display['Qtd Operada'] = df_display['Qtd Operada'].astype(int)
            df_display['Saldo Qtd'] = df_display['Saldo Qtd'].astype(int)

            # Filtros Interativos
            ticker_filter = st.multiselect("Filtrar por Ativo:", options=df_processado['Ticker'].unique())
            if ticker_filter:
                df_display = df_display[df_display['Ticker'].isin(ticker_filter)]

            st.dataframe(df_display, use_container_width=True, height=500)

    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {e}")