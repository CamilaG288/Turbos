import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔧 Painel de Montagem", layout="wide")
st.title("📌 Pedidos com Quantidade a Produzir > 0")

# URLs atualizados do novo repositório "Turbos"
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos/raw/main/PEDIDOS.xlsx"

# Leitura dos pedidos
df = pd.read_excel(URL_PEDIDOS)

# Renomear colunas pelo índice para facilitar
df.columns = df.columns.str.strip()  # Remove espaços
df["Quantidade_Produzir"] = df.iloc[:, 15] - (df.iloc[:, 16] - df.iloc[:, 13])  # Qtde. Abe - (Qtde. Separ - Qtde. Ate)

# Filtros de exclusão
desc_excluir = ["BONÉ", "CAMISETA", "CHAVEIRO", "CORTA VENTO", "CORTE"]
tipos_doc_excluir = ["PCONS", "PEF"]

# Aplicar filtros
df_filtrado = df[
    (df["Quantidade_Produzir"] > 0) &
    (~df.iloc[:, 8].str.upper().str.contains("|".join(desc_excluir))) &  # Coluna I - Descrição
    (~df.iloc[:, 5].isin(tipos_doc_excluir))  # Coluna F - Tp.Doc
].copy()

# Selecionar e renomear colunas
df_resultado = df_filtrado.loc[:, [
    "Cliente",  # col 1
    "Nome",     # col 2
    "Tp.Doc",   # col 5
    "Pedido",   # col 6
    "Produto",  # col 11
    "Descricao",  # col 8
    "Qtde. Abe",  # col 15
