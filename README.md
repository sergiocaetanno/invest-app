# 📊 Calculadora de Preço Médio e IR

Aplicação web para calcular o preço médio de investimentos e apurar lucro/prejuízo em vendas para auxílio no Imposto de Renda.

## 🚀 Como Rodar

### 1. Instalar Dependências

```bash
pip install streamlit pandas openpyxl
```

### 2. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

## 📦 Dependências

- **streamlit** - Framework web para interface
- **pandas** - Processamento de dados
- **openpyxl** - Leitura de arquivos Excel

## 📝 Sobre o App

A ferramenta processa o extrato de negociação da B3 (CSV ou Excel) e:

- ✅ Calcula o **preço médio ponderado** de cada ativo
- ✅ Apura **lucro/prejuízo** em operações de venda
- ✅ Gera extrato detalhado de todas as operações
- ✅ Permite filtrar por ativo específico

### Formato do Arquivo

O arquivo deve conter as seguintes colunas:
- `Data do Negócio`
- `Tipo de Movimentação` (Compra/Venda)
- `Código de Negociação` (ticker)
- `Quantidade`
- `Preço`
