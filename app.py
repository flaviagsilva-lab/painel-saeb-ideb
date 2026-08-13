
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path


# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================

st.set_page_config(
    page_title="Painel de Indicadores Educacionais",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# LOCALIZAÇÃO DOS ARQUIVOS
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
# CABEÇALHO
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


# Período

anos_disponiveis = sorted(
    base_municipios["Ano"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

ano_inicial, ano_final = st.select_slider(
    "Período de análise",
    options=anos_disponiveis,
    value=(
        anos_disponiveis[0],
        anos_disponiveis[-1]
    ),
    key="periodo_analise"
)


# Etapas

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
    etapas_selecionadas.append("Fundamental I")

if fundamental_ii:
    etapas_selecionadas.append("Fundamental II")


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

    st.stop()


# ==================================================
# FILTRAGEM DAS BASES
# ==================================================

municipios_filtrados = base_municipios[
    (base_municipios["Ano"] >= ano_inicial)
    &
    (base_municipios["Ano"] <= ano_final)
    &
    (base_municipios["Etapa"].isin(etapas_selecionadas))
].copy()


escolas_filtradas = base_escolas[
    (base_escolas["Ano"] >= ano_inicial)
    &
    (base_escolas["Ano"] <= ano_final)
    &
    (base_escolas["Etapa"].isin(etapas_selecionadas))
].copy()


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

    analise_municipal = st.selectbox(
        "Tipo de análise",
        [
            "Visão Geral",
            "Evolução",
            "Comparação entre Municípios",
            "Matemática",
            "Língua Portuguesa",
            "Aprovação e Rendimento",
            "IDEB e Metas",
            "Rankings"
        ],
        key="analise_municipal"
    )


    # ----------------------------------------------
    # VISÃO GERAL
    # ----------------------------------------------

    if analise_municipal == "Visão Geral":

        st.markdown("### Visão Geral")

        total_municipios = (
            municipios_filtrados["Município"]
            .nunique()
        )

        total_edicoes = (
            municipios_filtrados["Ano"]
            .nunique()
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Municípios disponíveis",
                total_municipios
            )

        with col2:
            st.metric(
                "Edições no período",
                total_edicoes
            )


    # ----------------------------------------------
    # OUTRAS ANÁLISES
    # ----------------------------------------------

    elif analise_municipal == "Evolução":

        st.markdown("### Evolução dos Indicadores")


        # ==========================================
        # BASE DA REDE PÚBLICA
        # ==========================================

        dados_evolucao = municipios_filtrados[
            municipios_filtrados["Rede"] == "Pública"
        ].copy()


        # ==========================================
        # MUNICÍPIOS DISPONÍVEIS
        # ==========================================

        lista_municipios = sorted(
            dados_evolucao["Município"]
            .dropna()
            .unique()
            .tolist()
        )


        # Barueri permanece sempre no gráfico
        municipio_referencia = "Barueri"


        outros_municipios = [
            municipio
            for municipio in lista_municipios
            if municipio != municipio_referencia
        ]


        municipios_comparacao = st.multiselect(
            "Municípios para comparar com Barueri",
            options=outros_municipios,
            default=[],
            key="municipios_comparacao_evolucao"
        )


        municipios_selecionados = [
            municipio_referencia
        ] + municipios_comparacao


        # ==========================================
        # INDICADOR
        # ==========================================

        indicadores = {
            "IDEB": "IDEB",
            "Matemática": "Matemática",
            "Língua Portuguesa": "Língua Portuguesa",
            "Nota Média Padronizada (N)": "N",
            "Indicador de Rendimento (P)": "P",
            "Taxa de Aprovação Geral": "Aprovação Geral"
        }


        indicador_escolhido = st.selectbox(
            "Indicador",
            options=list(indicadores.keys()),
            index=0,
            key="indicador_evolucao"
        )


        coluna_indicador = indicadores[
            indicador_escolhido
        ]


        # ==========================================
        # FILTRAGEM
        # ==========================================

        dados_grafico = dados_evolucao[
            dados_evolucao["Município"]
            .isin(municipios_selecionados)
        ].copy()


        dados_grafico = dados_grafico[
            [
                "Município",
                "Etapa",
                "Ano",
                coluna_indicador
            ]
        ].dropna(
            subset=[coluna_indicador]
        )


        # Ano será tratado como categoria
        dados_grafico["Ano"] = (
            dados_grafico["Ano"]
            .astype(int)
            .astype(str)
        )


        # Ordem exata das edições selecionadas
        anos_grafico = [
            str(ano)
            for ano in anos_disponiveis
            if ano_inicial <= ano <= ano_final
        ]


        # ==========================================
        # TÍTULO DA COMPARAÇÃO
        # ==========================================

        if municipios_comparacao:

            municipios_texto = (
                "Barueri × "
                + " × ".join(municipios_comparacao)
            )

        else:

            municipios_texto = "Barueri"


        st.markdown(
            f"#### {municipios_texto}"
        )

        st.caption(
            f"Indicador: {indicador_escolhido}"
        )


        # ==========================================
        # GRÁFICOS POR ETAPA
        # ==========================================

        for etapa in etapas_selecionadas:

            dados_etapa = dados_grafico[
                dados_grafico["Etapa"] == etapa
            ].copy()


            st.markdown(
                f"##### {etapa}"
            )


            if dados_etapa.empty:

                st.warning(
                    "Não há resultados disponíveis "
                    "para esta etapa e os filtros selecionados."
                )

                continue


            # Linha principal
            linhas = alt.Chart(
                dados_etapa
            ).mark_line(
                point=True
            ).encode(

                x=alt.X(
                    "Ano:O",
                    title="Ano",
                    sort=anos_grafico,
                    axis=alt.Axis(
                        labelAngle=0
                    )
                ),

                y=alt.Y(
                    f"{coluna_indicador}:Q",
                    title=indicador_escolhido,
                    scale=alt.Scale(
                        zero=False
                    )
                ),

                color=alt.Color(
                    "Município:N",
                    title="Município"
                ),

                strokeWidth=alt.condition(
                    alt.datum.Município
                    == municipio_referencia,
                    alt.value(4),
                    alt.value(2)
                ),

                tooltip=[
                    alt.Tooltip(
                        "Município:N",
                        title="Município"
                    ),
                    alt.Tooltip(
                        "Ano:O",
                        title="Ano"
                    ),
                    alt.Tooltip(
                        f"{coluna_indicador}:Q",
                        title=indicador_escolhido,
                        format=".2f"
                    )
                ]
            )


            grafico = linhas.properties(
                height=430
            ).interactive()


            st.altair_chart(
                grafico,
                use_container_width=True
            )


        # ==========================================
        # PADRÃO DE DESEMPENHO
        # ==========================================

        if indicador_escolhido in [
            "Matemática",
            "Língua Portuguesa"
        ]:

            if indicador_escolhido == "Matemática":

                coluna_padrao = (
                    "Padrão Matemática"
                )

            else:

                coluna_padrao = (
                    "Padrão Língua Portuguesa"
                )


            dados_padrao = dados_evolucao[
                dados_evolucao["Município"]
                .isin(municipios_selecionados)
            ][
                [
                    "Município",
                    "Etapa",
                    "Ano",
                    coluna_indicador,
                    coluna_padrao
                ]
            ].dropna(
                subset=[coluna_indicador]
            )


            dados_padrao = dados_padrao[
                dados_padrao["Etapa"]
                .isin(etapas_selecionadas)
            ]


            dados_padrao = dados_padrao.sort_values(
                by=[
                    "Ano",
                    "Etapa",
                    "Município"
                ]
            )


            dados_padrao = dados_padrao.rename(
                columns={
                    coluna_indicador:
                        "Proficiência",

                    coluna_padrao:
                        "Padrão de desempenho"
                }
            )


            st.markdown(
                "#### Padrões de desempenho"
            )


            st.dataframe(
                dados_padrao,
                hide_index=True,
                use_container_width=True
            )


        st.caption(
            "Barueri permanece como município de "
            "referência. Os resultados municipais "
            "correspondem à Rede Pública."
        )


    else:

        lista_municipios = sorted(
            municipios_filtrados["Município"]
            .dropna()
            .unique()
            .tolist()
        )

        municipio_selecionado = st.selectbox(
            "Município",
            lista_municipios,
            key="municipio_selecionado"
        )

        st.write(
            "Município selecionado: "
            f"**{municipio_selecionado}**"
        )

        st.info(
            "As visualizações desta análise "
            "serão incluídas nas próximas etapas."
        )


# ==================================================
# ESCOLAS
# ==================================================

with aba_escolas:

    st.subheader("Análises das Escolas")

    st.write(
        "As análises das escolas serão "
        "desenvolvidas posteriormente."
    )


# ==================================================
# INVESTIMENTO
# ==================================================

with aba_investimento:

    st.subheader("Investimento por Estudante")

    st.write(
        "As análises de investimento serão "
        "desenvolvidas posteriormente."
    )

