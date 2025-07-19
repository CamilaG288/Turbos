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
df_pedidos.columns = df_pedidos.columns.str.strip()  # tira espaços

# Exibir nomes das colunas para debug
st.write("🧪 Colunas encontradas na planilha PEDIDOS:")
st.write(df_pedidos.columns.tolist())

# Verificar se a coluna esperada existe
col_qtd = None
for col in df_pedidos.columns:
    if "QUANTIDADE" in col.upper() and "REAL" in col.upper():
        col_qtd = col
        break

if col_qtd is None:
    st.error("❌ Coluna de quantidade real não encontrada.")
    st.stop()

# Aplicar filtros
df_pedidos['Tp.Doc'] = df_pedidos['Tp.Doc'].astype(str).str.strip()
df_pedidos['Descricao'] = df_pedidos['Descricao'].astype(str).str.upper()

filtro_doc = ~df_pedidos['Tp.Doc'].isin(TP_DOC_IGNORAR)
filtro_desc = ~df_pedidos['Descricao'].str.contains('|'.join(PALAVRAS_DESC_IGNORAR), case=False, na=False)
filtro_qtd = df_pedidos[col_qtd] > 0

df_filtrado = df_pedidos[filtro_doc & filtro_desc & filtro_qtd].copy()

# Renomear para padrão
df_filtrado.rename(columns={col_qtd: "Quantidade_Produzir"}, inplace=True)

# Selecionar colunas para exibir
colunas_exibir = ["Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Qtde. Abe", "Quantidade_Produzir"]
df_resultado = df_filtrado.loc[:, [col for col in colunas_exibir if col in df_filtrado.columns]]

st.dataframe(df_resultado, use_container_width=True)

# Botão para baixar Excel
buffer = io.BytesIO()
df_resultado.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Baixar Pedidos com Qtde. a Produzir > 0",
    data=buffer,
    file_name="Pedidos_a_Produzir.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
