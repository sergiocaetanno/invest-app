import streamlit as st
import pandas as pd

from calculator import processar_dados

# Configuração da Página
st.set_page_config(page_title="Calculadora de Preço Médio e IR", layout="wide")

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