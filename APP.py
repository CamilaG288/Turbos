import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Quantidade a Produzir")

# --- Carregar pedidos ---
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df_pedidos = pd.read_excel(URL_PEDIDOS)

# --- Cálculo: Quantidade a Produzir ---
df_pedidos["Quantidade_Produzir"] = df_pedidos.iloc[:, 15] - (df_pedidos.iloc[:, 16] - df_pedidos.iloc[:, 13])

# --- Filtros de exclusão ---
desc_excluir = ["BONÉ", "CAMISETA", "CHAVEIRO", "CORTA VENTO", "CORTE"]
tpdoc_excluir = ["PCONS", "PEF"]

# Padronização
df_pedidos["Descricao"] = df_pedidos["Descricao"].astype(str).str.upper()
df_pedidos["Tp.Doc"] = df_pedidos["Tp.Doc"].astype(str).str.strip().str.upper()

# Aplicar filtros
df_pedidos_filtrados = df_pedidos[
    (df_pedidos["Quantidade_Produzir"] > 0) &
    (~df_pedidos["Descricao"].str.contains("|".join(desc_excluir))) &
    (~df_pedidos["Tp.Doc"].isin(tpdoc_excluir))
].copy()

# Diagnóstico
st.write("📥 Total de pedidos lidos:", df_pedidos.shape)
st.write("📋 Após filtros aplicados:", df_pedidos_filtrados.shape)
st.dataframe(df_pedidos_filtrados[["Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Quantidade_Produzir"]].head(50))
