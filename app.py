
import streamlit as st
import pandas as pd
from pathlib import Path


# ==================================================
# CONFIGURAÇÃO
# ==================================================

st.set_page_config(
    page_title="Painel de Indicadores Educacionais",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# PASTA DA APLICAÇÃO
# ==================================================

PASTA_APP = Path(__file__).resolve().parent


# ==================================================
# CARREGAMENTO DAS BASES
# ==================================================

@st.cache_data
def carregar_bases():

    municipios = pd.read_csv(
        PASTA_APP / "base_municipios.csv",
        encoding="utf-8-sig"
    )

    escolas = pd.read_csv(
        PASTA_APP / "base_escolas.csv",
        encoding="utf-8-sig"
    )

    investimento = pd.read_csv(
        PASTA_APP / "investimento_inep.csv",
        encoding="utf-8-sig"
    )

    return municipios, escolas, investimento


base_municipios, base_escolas, investimento_inep = carregar_bases()


# ==================================================
# PREPARAÇÃO DOS ANOS
# ==================================================

base_municipios["Ano"] = pd.to_numeric(
    base_municipios["Ano"],
    errors="coerce"
)

base_escolas["Ano"] = pd.to_numeric(
    base_escolas["Ano"],
    errors="coerce"
)


# ==================================================
# TÍTULO
# ==================================================

st.title("Painel de Indicadores Educacionais")

st.caption(
    "Estado de São Paulo | Série histórica 2005–2025"
)


# ==================================================
# RESUMO GERAL
# ==================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Municípios",
        base_municipios["Município"].nunique()
    )

with col2:
    st.metric(
        "Escolas",
        base_escolas["Escola"].nunique()
    )

with col3:
    st.metric(
        "Edições analisadas",
        base_municipios["Ano"].nunique()
    )


st.divider()


# ==================================================
# FILTROS GERAIS
# ==================================================

st.subheader("Filtros")


# --------------------------------------------------
# PERÍODO
# --------------------------------------------------

anos_disponiveis = sorted(
    base_municipios["Ano"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

periodo = st.select_slider(
    "Período de análise",
    options=anos_disponiveis,
    value=(
        anos_disponiveis[0],
        anos_disponiveis[-1]
    ),
    key="periodo_analise"
)

ano_inicial, ano_final = periodo


# --------------------------------------------------
# ETAPAS
# --------------------------------------------------

st.markdown("**Etapas de ensino**")

col_fi, col_fii = st.columns(2)

with col_fi:

    fundamental_i = st.checkbox(
        "Fundamental I",
        value=True,
        key="fundamental_i"
    )

with col_fii:

    fundamental_ii = st.checkbox(
        "Fundamental II",
        value=True,
        key="fundamental_ii"
    )


etapas_selecionadas = []

if fundamental_i:
    etapas_selecionadas.append(
        "Fundamental I"
    )

if fundamental_ii:
    etapas_selecionadas.append(
        "Fundamental II"
    )


# ==================================================
# SELEÇÃO ATUAL
# ==================================================

st.divider()

st.subheader("Seleção atual")

col_periodo, col_etapas = st.columns(2)

with col_periodo:

    st.write(
        f"**Período:** {ano_inicial} a {ano_final}"
    )

with col_etapas:

    if etapas_selecionadas:

        st.write(
            "**Etapas:** "
            + " | ".join(etapas_selecionadas)
        )

    else:

        st.write(
            "**Etapas:** nenhuma selecionada"
        )


if not etapas_selecionadas:

    st.warning(
        "Selecione pelo menos uma etapa de ensino."
    )

else:

    st.success(
        "Filtros definidos com sucesso."
    )


# ==================================================
# NAVEGAÇÃO PRINCIPAL
# ==================================================

st.divider()

st.header("Análises")

aba_municipios, aba_escolas, aba_investimento = st.tabs(
    [
        "Municípios",
        "Escolas",
        "Investimento"
    ]
)


# ==================================================
# MUNICÍPIOS
# ==================================================

with aba_municipios:

    st.subheader("Análises dos Municípios")

    st.write(
        "Nesta área serão apresentados os indicadores "
        "educacionais, a evolução histórica e as "
        "comparações entre municípios."
    )


# ==================================================
# ESCOLAS
# ==================================================

with aba_escolas:

    st.subheader("Análises das Escolas")

    st.write(
        "Nesta área serão apresentados os indicadores "
        "educacionais, a evolução histórica e as "
        "comparações entre escolas."
    )


# ==================================================
# INVESTIMENTO
# ==================================================

with aba_investimento:

    st.subheader("Investimento por Estudante")

    st.write(
        "Nesta área será apresentada a evolução do "
        "investimento público por estudante com base "
        "nos dados disponibilizados pelo INEP."
    )

