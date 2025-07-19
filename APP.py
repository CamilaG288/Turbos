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
st.subheader("📊 Cálculo Total de Componentes - Nível 1 e 2")

# Carregar estrutura
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA, header=0)

# Lista para ignorar por descrição
DESCR_IGNORAR = [
    "SACO PLASTICO", "CAIXA", "PLAQUETA", "REBITE", "ETIQUETA", "CERTIFICADO", "CINTA PLASTICA"
]

# Renomear colunas por índice
df_estrutura = df_estrutura.rename(columns={
    df_estrutura.columns[1]: "COD_PAI",
    df_estrutura.columns[15]: "COD_FILHO",
    df_estrutura.columns[22]: "QTDE_POR_UNID",
    df_estrutura.columns[18]: "FANTASMA",
    df_estrutura.columns[17]: "DESCRICAO"
})

# Limpar e padronizar
df_estrutura = df_estrutura[
    (df_estrutura["FANTASMA"] != "S") &
    (df_estrutura["COD_FILHO"].notna()) &
    (~df_estrutura["DESCRICAO"].str.upper().str.contains('|'.join(DESCR_IGNORAR), na=False))
].copy()

df_estrutura["COD_PAI"] = df_estrutura["COD_PAI"].astype(str).str.strip()
df_estrutura["COD_FILHO"] = df_estrutura["COD_FILHO"].astype(str).str.strip()
df_estrutura["QTDE_POR_UNID"] = pd.to_numeric(df_estrutura["QTDE_POR_UNID"], errors="coerce").fillna(0)

# Filtrar pais finais que precisam ser produzidos
df_produzir = df_filtrado[["Produto", "Quantidade_Produzir"]].copy()
df_produzir["Produto"] = df_produzir["Produto"].astype(str).str.strip()
df_produzir = df_produzir.groupby("Produto", as_index=False).sum()
codigos_pais_finais = set(df_produzir["Produto"])

# Separar filhos diretos (nível 1)
nivel1 = df_estrutura[
    df_estrutura["COD_PAI"].isin(codigos_pais_finais) &
    (~df_estrutura["COD_FILHO"].str.endswith("P"))
].copy()
nivel1["PAI_FINAL"] = nivel1["COD_PAI"]

# Identificar conjuntos com final "P" (nível 1.5)
conjuntos_p = df_estrutura[
    df_estrutura["COD_PAI"].isin(codigos_pais_finais) &
    (df_estrutura["COD_FILHO"].str.endswith("P"))
].copy()

# Agora buscar os filhos desses conjuntos (nível 2)
filhos_nivel2 = df_estrutura[
    df_estrutura["COD_PAI"].isin(conjuntos_p["COD_FILHO"])
].copy()

# Atribuir o pai final original
conjunto_para_pai_final = dict(zip(conjuntos_p["COD_FILHO"], conjuntos_p["COD_PAI"]))
filhos_nivel2["PAI_FINAL"] = filhos_nivel2["COD_PAI"].map(conjunto_para_pai_final)

# Juntar níveis 1 e 2 (com pai final certo)
estrutura_n1n2 = pd.concat([
    nivel1[["PAI_FINAL", "COD_FILHO", "QTDE_POR_UNID"]],
    filhos_nivel2[["PAI_FINAL", "COD_FILHO", "QTDE_POR_UNID"]]
], ignore_index=True)

# Juntar com quantidade a produzir
estrutura_necessaria = estrutura_n1n2.merge(df_produzir, left_on="PAI_FINAL", right_on="Produto", how="inner")

# Calcular total necessário
estrutura_necessaria["QTDE_TOTAL_NECESSARIA"] = (
    estrutura_necessaria["QTDE_POR_UNID"] * estrutura_necessaria["Quantidade_Produzir"]
)

# Visualização final
df_explodido = estrutura_necessaria[[
    "PAI_FINAL", "COD_FILHO", "QTDE_POR_UNID", "QTDE_TOTAL_NECESSARIA"
]].rename(columns={"PAI_FINAL": "COD_PAI"})

st.dataframe(df_explodido, use_container_width=True)

# Download Excel
buffer = io.BytesIO()
df_explodido.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Baixar Estrutura Nível 1 e 2",
    data=buffer,
    file_name="Explosao_Estrutura_Nivel_1e2.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
