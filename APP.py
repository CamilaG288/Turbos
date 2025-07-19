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
st.subheader("📊 Cálculo Total de Componentes por Estrutura")

# URL da estrutura
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA, header=0)

# 🧽 Lista de palavras para ignorar na descrição dos componentes
DESCR_IGNORAR = [
    "SACO PLASTICO", "CAIXA", "PLAQUETA", "REBITE", "ETIQUETA", "CERTIFICADO", "CINTA PLASTICA"
]

# 🏷️ Renomear colunas por índice
df_estrutura = df_estrutura.rename(columns={
    df_estrutura.columns[1]: "COD_PAI",
    df_estrutura.columns[15]: "COD_FILHO",
    df_estrutura.columns[22]: "QTDE_POR_UNID",
    df_estrutura.columns[18]: "FANTASMA",
    df_estrutura.columns[17]: "DESCRICAO"
})

# 🧹 Limpeza e filtros
df_estrutura = df_estrutura[
    (df_estrutura["FANTASMA"] != "S") &
    (df_estrutura["COD_FILHO"].notna()) &
    (~df_estrutura["DESCRICAO"].str.upper().str.contains('|'.join(DESCR_IGNORAR), na=False))
].copy()

df_estrutura["COD_PAI"] = df_estrutura["COD_PAI"].astype(str).str.strip()
df_estrutura["COD_FILHO"] = df_estrutura["COD_FILHO"].astype(str).str.strip()
df_estrutura["QTDE_POR_UNID"] = pd.to_numeric(df_estrutura["QTDE_POR_UNID"], errors="coerce").fillna(0)

# 🔁 Ignorar conjuntos com final "P", mas manter filhos ligados ao pai final
conjuntos_p = df_estrutura[df_estrutura["COD_PAI"].str.endswith("P")].copy()
filhos_conjuntos_p = conjuntos_p[["COD_FILHO", "QTDE_POR_UNID", "COD_PAI"]].copy()

conjuntos_originais = df_estrutura[~df_estrutura["COD_PAI"].str.endswith("P")].copy()
estrutura_final = pd.concat([conjuntos_originais, filhos_conjuntos_p], ignore_index=True)

# 🧮 Agrupar quantidade a produzir por Produto
df_produzir = df_filtrado[["Produto", "Quantidade_Produzir"]].copy()
df_produzir["Produto"] = df_produzir["Produto"].astype(str).str.strip()
df_produzir = df_produzir.groupby("Produto", as_index=False).sum()

# 🔗 Juntar estrutura com quantidades
estrutura_necessaria = estrutura_final.merge(df_produzir, left_on="COD_PAI", right_on="Produto", how="inner")

# 🧾 Calcular total necessário de cada componente
estrutura_necessaria["QTDE_TOTAL_NECESSARIA"] = (
    estrutura_necessaria["QTDE_POR_UNID"] * estrutura_necessaria["Quantidade_Produzir"]
)

# 📋 Organizar resultado
df_explodido = estrutura_necessaria[[
    "COD_PAI", "COD_FILHO", "QTDE_POR_UNID", "QTDE_TOTAL_NECESSARIA"
]].copy()

st.dataframe(df_explodido, use_container_width=True)

# 📥 Baixar Excel
buffer2 = io.BytesIO()
df_explodido.to_excel(buffer2, index=False)
buffer2.seek(0)

st.download_button(
    label="📥 Baixar Explosão da Estrutura com Totais",
    data=buffer2,
    file_name="Estrutura_Total_Componentes.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
