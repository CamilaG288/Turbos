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

# Carregando os dados
df_pedidos = pd.read_excel(URL_PEDIDOS)

# Normalização
df_pedidos.columns = df_pedidos.columns.str.strip()
df_pedidos['Tp.Doc'] = df_pedidos['Tp.Doc'].astype(str).str.strip()
df_pedidos['Descricao'] = df_pedidos['Descricao'].astype(str).str.upper()

# Filtros
filtro_doc = ~df_pedidos['Tp.Doc'].isin(TP_DOC_IGNORAR)
filtro_desc = ~df_pedidos['Descricao'].str.contains('|'.join(PALAVRAS_DESC_IGNORAR), case=False, na=False)
filtro_qtd = df_pedidos['QUANTIDADE_REAL'] > 0

df_filtrado = df_pedidos[filtro_doc & filtro_desc & filtro_qtd].copy()

# Renomear coluna
df_filtrado.rename(columns={"QUANTIDADE_REAL": "Quantidade_Produzir"}, inplace=True)

# Selecionar e reordenar colunas
colunas_exibir = ["Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Qtde. Abe", "Quantidade_Produzir"]
df_resultado = df_filtrado.loc[:, colunas_exibir]

# Exibir no Streamlit
st.dataframe(df_resultado, use_container_width=True)

# Botão de download em Excel
buffer = io.BytesIO()
df_resultado.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Baixar Pedidos com Qtde. a Produzir > 0",
    data=buffer,
    file_name="Pedidos_a_Produzir.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
