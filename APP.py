import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="🔧 Painel de Montagens", layout="wide")
st.title("📌 Pedidos com Quantidade a Produzir > 0")

# URLs das planilhas no GitHub
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos/raw/main/PEDIDOS.xlsx"

# Palavras-chave para ignorar na descrição
PALAVRAS_DESC_IGNORAR = ["BONÉ", "CAMISETA", "CHAVEIRO", "CORTA VENTO", "CORTE"]
TP_DOC_IGNORAR = ["PCONS", "PEF"]

# Carregar pedidos
df_pedidos = pd.read_excel(URL_PEDIDOS)
df_pedidos.columns = df_pedidos.columns.str.strip()

# Calcular Quantidade_Produzir com fórmula correta
df_pedidos["Quantidade_Produzir"] = (
    df_pedidos["Qtde. Abe"].fillna(0) - (df_pedidos["Qtde. Separ"].fillna(0) - df_pedidos["Qtde.Ate"].fillna(0))
)

# Aplicar filtros
df_pedidos["Tp.Doc"] = df_pedidos["Tp.Doc"].astype(str).str.strip()
df_pedidos["Descricao"] = df_pedidos["Descricao"].astype(str).str.upper()

filtro_qtd = df_pedidos["Quantidade_Produzir"] > 0
filtro_doc = ~df_pedidos["Tp.Doc"].isin(TP_DOC_IGNORAR)
filtro_desc = ~df_pedidos["Descricao"].str.contains("|".join(PALAVRAS_DESC_IGNORAR), case=False, na=False)

df_filtrado = df_pedidos[filtro_qtd & filtro_doc & filtro_desc].copy()

# Selecionar colunas para mostrar
colunas_exibir = ["Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Qtde. Abe", "Quantidade_Produzir"]
df_resultado = df_filtrado[colunas_exibir]

# Exibir no painel
st.dataframe(df_resultado, use_container_width=True)

# Gerar Excel para download
buffer = io.BytesIO()
df_resultado.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Baixar Pedidos com Qtde. a Produzir > 0",
    data=buffer,
    file_name="Pedidos_a_Produzir.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
