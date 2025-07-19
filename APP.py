import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔧 Análise de Pedidos", layout="wide")
st.title("📌 Pedidos com Quantidade a Produzir > 0")

# URLs dos arquivos no novo repositório Turbos
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos/raw/main/PEDIDOS.xlsx"

# Função para carregar os pedidos e calcular quantidade real
@st.cache_data
def carregar_pedidos():
    df = pd.read_excel(URL_PEDIDOS)
    df.columns = df.columns.astype(str)

    # Cálculo da Quantidade_Produzir = Qtde. Abe - (Qtde. Separ - Qtde.Ate)
    df["Quantidade_Produzir"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])

    # Filtros adicionais:
    # - Descrição (coluna 8) não pode conter palavras indesejadas
    descricoes_invalidas = ["BONÉ", "CAMISETA", "CHAVEIRO", "CORTA VENTO", "CORTE"]
    doc_invalidos = ["PCONS", "PEF"]

    df_filtrado = df[
        (df["Quantidade_Produzir"] > 0) &
        (~df.iloc[:, 5].isin(doc_invalidos)) &
        (~df.iloc[:, 8].str.upper().str.contains("|".join(descricoes_invalidas)))
    ]

    # Reorganiza as colunas para exibição
    df_resultado = df_filtrado.loc[:, [
        df.columns[1],   # Cliente
        df.columns[2],   # Nome
        df.columns[5],   # Tp.Doc
        df.columns[6],   # Pedido
        df.columns[11],  # Produto
        df.columns[8],   # Descrição
        df.columns[15],  # Qtde. Abe
        "Quantidade_Produzir"
    ]]

    return df_resultado

# Carregar e exibir
df_pedidos = carregar_pedidos()

st.dataframe(df_pedidos, use_container_width=True)

# Botão de download
st.download_button(
    label="📥 Baixar Pedidos com Qtde. a Produzir > 0",
    data=df_pedidos.to_csv(index=False).encode('utf-8-sig'),
    file_name="pedidos_quantidade_produzir.csv",
    mime="text/csv"
)
