
import streamlit as st
import pandas as pd
import unicodedata
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
        "Área de análise",
        [
            "Comparação entre Municípios",
            "Visão Geral",
            "Rankings"
        ],
        index=0,
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

    elif analise_municipal == "Comparação entre Municípios":

        st.markdown(
            "### Comparação entre Municípios"
        )


        # ==========================================
        # MUNICÍPIO DE REFERÊNCIA
        # ==========================================

        municipio_referencia = "Barueri"
        rede_referencia = "Municipal"


        st.markdown(
            "#### Município de referência"
        )

        st.write(
            "**Barueri — Municipal**"
        )


        # ==========================================
        # FUNÇÃO DE NORMALIZAÇÃO
        # ==========================================

        def normalizar_municipio(texto):

            texto = (
                str(texto)
                .strip()
                .lower()
            )

            texto = unicodedata.normalize(
                "NFKD",
                texto
            )

            texto = "".join(
                caractere
                for caractere in texto
                if not unicodedata.combining(
                    caractere
                )
            )

            return texto


        # ==========================================
        # REDES DISPONÍVEIS
        # ==========================================

        ordem_redes = [
            "Municipal",
            "Estadual",
            "Pública"
        ]


        redes_existentes = (
            municipios_filtrados["Rede"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )


        redes_disponiveis = [
            rede
            for rede in ordem_redes
            if rede in redes_existentes
        ]


        if not redes_disponiveis:

            st.warning(
                "Não há redes disponíveis para "
                "os filtros selecionados."
            )

        else:

            # ======================================
            # REDE PARA COMPARAÇÃO
            # ======================================

            rede_comparacao = st.selectbox(
                "Rede para comparação",
                options=redes_disponiveis,
                index=0,
                key="rede_comparacao_principal"
            )


            # ======================================
            # BASE DA REDE SELECIONADA
            # ======================================

            dados_rede_comparacao = (
                municipios_filtrados[
                    municipios_filtrados["Rede"]
                    == rede_comparacao
                ]
                .copy()
            )


            # ======================================
            # MUNICÍPIOS DISPONÍVEIS
            # ======================================

            lista_municipios = sorted(
                dados_rede_comparacao[
                    "Município"
                ]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )


            # Barueri já é a referência fixa
            lista_municipios = [
                municipio
                for municipio in lista_municipios
                if normalizar_municipio(
                    municipio
                )
                != normalizar_municipio(
                    municipio_referencia
                )
            ]


            # ======================================
            # BUSCA DO MUNICÍPIO
            # ======================================

            busca_municipio = st.text_input(
                "Buscar município",
                value="",
                placeholder=(
                    "Digite o nome ou parte do nome"
                ),
                key="busca_municipio_comparacao"
            )


            busca_normalizada = (
                normalizar_municipio(
                    busca_municipio
                )
            )


            # ======================================
            # FILTRO SEM OBRIGAÇÃO DE ACENTO
            # ======================================

            if busca_normalizada:

                municipios_encontrados = [
                    municipio
                    for municipio
                    in lista_municipios
                    if busca_normalizada
                    in normalizar_municipio(
                        municipio
                    )
                ]

            else:

                municipios_encontrados = (
                    lista_municipios
                )


            # ======================================
            # SELEÇÃO MÚLTIPLA
            # ======================================

            municipios_comparacao = (
                st.multiselect(
                    "Municípios para comparar com Barueri",
                    options=municipios_encontrados,
                    default=[],
                    key=(
                        "municipios_"
                        "comparacao_principal"
                    )
                )
            )


            # ======================================
            # RESULTADO DA BUSCA
            # ======================================

            if busca_normalizada:

                if municipios_encontrados:

                    st.caption(
                        f"{len(municipios_encontrados)} "
                        "município(s) encontrado(s)."
                    )

                else:

                    st.warning(
                        "Nenhum município encontrado "
                        "para essa busca na rede "
                        "selecionada."
                    )


            # ======================================
            # O QUE COMPARAR
            # ======================================

            opcao_comparacao = st.selectbox(
                "O que comparar?",
                [
                    "Taxa de Aprovação",
                    "Indicador de Rendimento (P)",
                    "Nota SAEB",
                    "IDEB"
                ],
                index=0,
                key="opcao_comparacao_municipios"
            )


            # ======================================
            # BASE FIXA DE BARUERI
            # ======================================

            dados_barueri_comparacao = (
                municipios_filtrados[
                    (
                        municipios_filtrados[
                            "Município"
                        ]
                        == municipio_referencia
                    )
                    &
                    (
                        municipios_filtrados[
                            "Rede"
                        ]
                        == rede_referencia
                    )
                ]
                .copy()
            )


            dados_barueri_comparacao[
                "Comparação"
            ] = "Barueri - Municipal"


            # ======================================
            # PARTES DA COMPARAÇÃO
            # ======================================

            partes_comparacao = [
                dados_barueri_comparacao
            ]


            for municipio in municipios_comparacao:

                dados_municipio = (
                    dados_rede_comparacao[
                        dados_rede_comparacao[
                            "Município"
                        ]
                        == municipio
                    ]
                    .copy()
                )


                dados_municipio[
                    "Comparação"
                ] = (
                    municipio
                    + " - "
                    + rede_comparacao
                )


                partes_comparacao.append(
                    dados_municipio
                )


            dados_comparacao = pd.concat(
                partes_comparacao,
                ignore_index=True
            )


            # ======================================
            # RESUMO
            # ======================================

            st.markdown(
                "#### Seleção atual"
            )


            st.write(
                "**Referência:** "
                "Barueri — Municipal"
            )


            st.write(
                "**Rede comparada:** "
                f"{rede_comparacao}"
            )


            if municipios_comparacao:

                st.write(
                    "**Municípios adicionais:** "
                    + " | ".join(
                        municipios_comparacao
                    )
                )

            else:

                st.caption(
                    "Nenhum município adicional "
                    "selecionado. "
                    "Os resultados de Barueri "
                    "continuam disponíveis."
                )


            st.write(
                "**Indicador selecionado:** "
                f"{opcao_comparacao}"
            )


            # ======================================
            # CONFERÊNCIA DA BASE PREPARADA
            # ======================================

            if dados_barueri_comparacao.empty:

                st.warning(
                    "Não foram encontrados resultados "
                    "de Barueri — Municipal para os "
                    "filtros selecionados."
                )

            else:

                st.caption(
                    "Barueri permanece como referência "
                    "em todas as análises, mesmo sem "
                    "outro município selecionado."
                )


            # ======================================
            # ÁREA DOS GRÁFICOS
            # ======================================

            # ======================================
            # TAXA DE APROVAÇÃO
            # ======================================

            if opcao_comparacao == "Taxa de Aprovação":

                st.markdown(
                    "### Taxa de Aprovação"
                )


                # ==================================
                # TIPO DE VISUALIZAÇÃO
                # ==================================

                visualizacao_aprovacao = st.selectbox(
                    "Visualização da aprovação",
                    [
                        "Aprovação Geral",
                        "Por série/ano"
                    ],
                    index=0,
                    key="visualizacao_aprovacao_municipios"
                )


                # ==================================
                # ANOS
                # ==================================

                anos_comparacao = [
                    str(ano)
                    for ano in anos_disponiveis
                    if (
                        ano_inicial
                        <= ano
                        <= ano_final
                    )
                ]


                dados_aprovacao = (
                    dados_comparacao
                    .copy()
                )


                dados_aprovacao["Ano"] = (
                    pd.to_numeric(
                        dados_aprovacao["Ano"],
                        errors="coerce"
                    )
                    .astype("Int64")
                    .astype(str)
                )


                # ==================================
                # ESCALA DINÂMICA
                # ==================================

                def calcular_escala_aprovacao(
                    serie_valores
                ):

                    valores_validos = (
                        pd.to_numeric(
                            serie_valores,
                            errors="coerce"
                        )
                        .dropna()
                    )


                    if valores_validos.empty:

                        return 0, 100


                    valor_minimo = float(
                        valores_validos.min()
                    )


                    limite_inferior = max(
                        0,
                        valor_minimo - 5
                    )


                    limite_inferior = (
                        int(
                            limite_inferior // 5
                        )
                        * 5
                    )


                    return (
                        limite_inferior,
                        100
                    )


                # ==================================
                # APROVAÇÃO GERAL
                # ==================================

                if (
                    visualizacao_aprovacao
                    == "Aprovação Geral"
                ):

                    for etapa in etapas_selecionadas:

                        st.markdown(
                            f"#### {etapa}"
                        )


                        dados_etapa = (
                            dados_aprovacao[
                                dados_aprovacao[
                                    "Etapa"
                                ]
                                == etapa
                            ]
                            .copy()
                        )


                        dados_etapa[
                            "Aprovação Geral"
                        ] = pd.to_numeric(
                            dados_etapa[
                                "Aprovação Geral"
                            ],
                            errors="coerce"
                        )


                        dados_etapa = (
                            dados_etapa[
                                [
                                    "Município",
                                    "Rede",
                                    "Comparação",
                                    "Ano",
                                    "Aprovação Geral"
                                ]
                            ]
                            .dropna(
                                subset=[
                                    "Aprovação Geral"
                                ]
                            )
                        )


                        if dados_etapa.empty:

                            st.info(
                                "Não há resultados de "
                                "Aprovação Geral para "
                                "esta etapa e período."
                            )

                            continue


                        (
                            escala_minima,
                            escala_maxima
                        ) = calcular_escala_aprovacao(
                            dados_etapa[
                                "Aprovação Geral"
                            ]
                        )


                        # ==========================
                        # LINHAS
                        # ==========================

                        linhas_grafico = (
                            alt.Chart(
                                dados_etapa
                            )
                            .mark_line(
                                point=True
                            )
                            .encode(

                                x=alt.X(
                                    "Ano:O",
                                    title="Ano",
                                    sort=anos_comparacao,
                                    axis=alt.Axis(
                                        labelAngle=0
                                    )
                                ),

                                y=alt.Y(
                                    "Aprovação Geral:Q",
                                    title=(
                                        "Taxa de Aprovação (%)"
                                    ),
                                    scale=alt.Scale(
                                        domain=[
                                            escala_minima,
                                            escala_maxima
                                        ]
                                    ),
                                    axis=alt.Axis(
                                        format=".0f"
                                    )
                                ),

                                color=alt.Color(
                                    "Comparação:N",
                                    title=(
                                        "Município / Rede"
                                    )
                                ),

                                strokeWidth=alt.condition(
                                    (
                                        alt.datum.Município
                                        == municipio_referencia
                                    ),
                                    alt.value(4),
                                    alt.value(2)
                                ),

                                tooltip=[
                                    alt.Tooltip(
                                        "Município:N",
                                        title="Município"
                                    ),

                                    alt.Tooltip(
                                        "Rede:N",
                                        title="Rede"
                                    ),

                                    alt.Tooltip(
                                        "Ano:O",
                                        title="Ano"
                                    ),

                                    alt.Tooltip(
                                        "Aprovação Geral:Q",
                                        title="Aprovação",
                                        format=".1f"
                                    )
                                ]
                            )
                        )


                        # ==========================
                        # VALORES
                        # ==========================

                        valores_grafico = (
                            alt.Chart(
                                dados_etapa
                            )
                            .mark_text(
                                dy=-12,
                                fontSize=11
                            )
                            .encode(

                                x=alt.X(
                                    "Ano:O",
                                    sort=anos_comparacao
                                ),

                                y=alt.Y(
                                    "Aprovação Geral:Q",
                                    scale=alt.Scale(
                                        domain=[
                                            escala_minima,
                                            escala_maxima
                                        ]
                                    )
                                ),

                                text=alt.Text(
                                    "Aprovação Geral:Q",
                                    format=".1f"
                                ),

                                color=alt.Color(
                                    "Comparação:N"
                                )
                            )
                        )


                        grafico_aprovacao = (
                            linhas_grafico
                            + valores_grafico
                        ).properties(
                            height=430
                        )


                        st.altair_chart(
                            grafico_aprovacao,
                            use_container_width=True
                        )


                # ==================================
                # APROVAÇÃO POR SÉRIE / ANO
                # ==================================

                else:

                    # ==================================
                    # MUNICÍPIOS ESPERADOS
                    # ==================================

                    comparacoes_esperadas = [
                        "Barueri - Municipal"
                    ]


                    for municipio in municipios_comparacao:

                        comparacoes_esperadas.append(
                            municipio
                            + " - "
                            + rede_comparacao
                        )


                    for etapa in etapas_selecionadas:

                        st.markdown(
                            f"#### {etapa}"
                        )


                        # ==============================
                        # SÉRIES DA ETAPA
                        # ==============================

                        if etapa == "Fundamental I":

                            series_etapa = [
                                "1º",
                                "2º",
                                "3º",
                                "4º",
                                "5º"
                            ]

                        else:

                            series_etapa = [
                                "6º",
                                "7º",
                                "8º",
                                "9º"
                            ]


                        series_disponiveis = [
                            serie
                            for serie
                            in series_etapa
                            if serie
                            in dados_aprovacao.columns
                        ]


                        if not series_disponiveis:

                            st.info(
                                "Não há taxas de aprovação "
                                "por série disponíveis "
                                "para esta etapa."
                            )

                            continue


                        dados_etapa = (
                            dados_aprovacao[
                                dados_aprovacao[
                                    "Etapa"
                                ]
                                == etapa
                            ]
                            .copy()
                        )


                        if dados_etapa.empty:

                            st.info(
                                "Não há resultados "
                                "disponíveis para esta etapa."
                            )

                            continue


                        # ==============================
                        # CONVERSÃO PARA NUMÉRICO
                        # ==============================

                        for serie in series_disponiveis:

                            dados_etapa[
                                serie
                            ] = pd.to_numeric(
                                dados_etapa[
                                    serie
                                ],
                                errors="coerce"
                            )


                        # ==============================
                        # GRÁFICO POR MUNICÍPIO
                        # ==============================

                        for comparacao in (
                            comparacoes_esperadas
                        ):

                            st.markdown(
                                f"##### {comparacao}"
                            )


                            dados_municipio_serie = (
                                dados_etapa[
                                    dados_etapa[
                                        "Comparação"
                                    ]
                                    == comparacao
                                ]
                                .copy()
                            )


                            if (
                                dados_municipio_serie.empty
                            ):

                                st.caption(
                                    "Não há resultados "
                                    "disponíveis para este "
                                    "município, rede e etapa."
                                )

                                continue


                            # --------------------------
                            # FORMATO LONGO
                            # --------------------------

                            dados_longos = (
                                dados_municipio_serie[
                                    [
                                        "Ano",
                                        *series_disponiveis
                                    ]
                                ]
                                .melt(
                                    id_vars=[
                                        "Ano"
                                    ],
                                    value_vars=(
                                        series_disponiveis
                                    ),
                                    var_name="Série",
                                    value_name=(
                                        "Taxa de Aprovação"
                                    )
                                )
                            )


                            dados_longos[
                                "Taxa de Aprovação"
                            ] = pd.to_numeric(
                                dados_longos[
                                    "Taxa de Aprovação"
                                ],
                                errors="coerce"
                            )


                            dados_longos = (
                                dados_longos
                                .dropna(
                                    subset=[
                                        "Taxa de Aprovação"
                                    ]
                                )
                            )


                            if dados_longos.empty:

                                st.caption(
                                    "O município possui "
                                    "registro nesta etapa, "
                                    "mas não há taxas de "
                                    "aprovação por série/ano "
                                    "disponíveis no período "
                                    "selecionado."
                                )

                                continue


                            # ==========================
                            # ESCALA DINÂMICA
                            # ==========================

                            (
                                escala_minima,
                                escala_maxima
                            ) = calcular_escala_aprovacao(
                                dados_longos[
                                    "Taxa de Aprovação"
                                ]
                            )


                            # ==========================
                            # LINHAS + LEGENDA
                            # ==========================

                            linhas_series = (
                                alt.Chart(
                                    dados_longos
                                )
                                .mark_line(
                                    point=True
                                )
                                .encode(

                                    x=alt.X(
                                        "Ano:O",
                                        title="Ano",
                                        sort=anos_comparacao,
                                        axis=alt.Axis(
                                            labelAngle=0
                                        )
                                    ),

                                    y=alt.Y(
                                        "Taxa de Aprovação:Q",
                                        title=(
                                            "Taxa de Aprovação (%)"
                                        ),
                                        scale=alt.Scale(
                                            domain=[
                                                escala_minima,
                                                escala_maxima
                                            ]
                                        ),
                                        axis=alt.Axis(
                                            format=".0f"
                                        )
                                    ),

                                    color=alt.Color(
                                        "Série:N",
                                        title="Série / Ano",
                                        sort=series_disponiveis,
                                        legend=alt.Legend(
                                            orient="bottom",
                                            direction="horizontal"
                                        )
                                    ),

                                    tooltip=[
                                        alt.Tooltip(
                                            "Ano:O",
                                            title="Ano"
                                        ),

                                        alt.Tooltip(
                                            "Série:N",
                                            title="Série"
                                        ),

                                        alt.Tooltip(
                                            "Taxa de Aprovação:Q",
                                            title="Aprovação",
                                            format=".1f"
                                        )
                                    ]
                                )
                            )


                            # ==========================
                            # VALORES
                            # SEM INTERFERIR NA LEGENDA
                            # ==========================

                            valores_series = (
                                alt.Chart(
                                    dados_longos
                                )
                                .mark_text(
                                    dy=-11,
                                    fontSize=10
                                )
                                .encode(

                                    x=alt.X(
                                        "Ano:O",
                                        sort=anos_comparacao
                                    ),

                                    y=alt.Y(
                                        "Taxa de Aprovação:Q",
                                        scale=alt.Scale(
                                            domain=[
                                                escala_minima,
                                                escala_maxima
                                            ]
                                        )
                                    ),

                                    text=alt.Text(
                                        "Taxa de Aprovação:Q",
                                        format=".1f"
                                    ),

                                    detail=alt.Detail(
                                        "Série:N"
                                    )
                                )
                            )


                            grafico_series = (
                                linhas_series
                                + valores_series
                            ).properties(
                                height=420
                            )


                            st.altair_chart(
                                grafico_series,
                                use_container_width=True
                            )


                st.caption(
                    "A escala vertical é ajustada "
                    "automaticamente aos valores "
                    "apresentados, mantendo 100% "
                    "como limite superior. "
                    "Barueri permanece como referência "
                    "pela Rede Municipal."
                )


            # ======================================
            # DEMAIS INDICADORES
            # ======================================

            elif (
                opcao_comparacao
                == "Indicador de Rendimento (P)"
            ):

                st.markdown(
                    "### Indicador de Rendimento (P)"
                )


                # ==================================
                # TIPO DE VISUALIZAÇÃO
                # ==================================

                visualizacao_p = st.selectbox(
                    "Visualização do rendimento",
                    [
                        "Evolução do P",
                        "P × Taxa de Aprovação"
                    ],
                    index=0,
                    key="visualizacao_p_municipios"
                )


                # ==================================
                # PREPARAÇÃO DOS DADOS
                # ==================================

                dados_p = (
                    dados_comparacao
                    .copy()
                )


                dados_p["Ano"] = (
                    pd.to_numeric(
                        dados_p["Ano"],
                        errors="coerce"
                    )
                    .astype("Int64")
                    .astype(str)
                )


                dados_p["P"] = pd.to_numeric(
                    dados_p["P"],
                    errors="coerce"
                )


                dados_p["Aprovação Geral"] = (
                    pd.to_numeric(
                        dados_p[
                            "Aprovação Geral"
                        ],
                        errors="coerce"
                    )
                )


                anos_comparacao_p = [
                    str(ano)
                    for ano in anos_disponiveis
                    if (
                        ano_inicial
                        <= ano
                        <= ano_final
                    )
                ]


                # ==================================
                # ESCALA DINÂMICA DO P
                # ==================================

                def calcular_escala_p(
                    serie_valores
                ):

                    valores_validos = (
                        pd.to_numeric(
                            serie_valores,
                            errors="coerce"
                        )
                        .dropna()
                    )


                    if valores_validos.empty:

                        return 0, 1


                    valor_minimo = float(
                        valores_validos.min()
                    )


                    limite_inferior = max(
                        0,
                        valor_minimo - 0.05
                    )


                    # Arredondar para baixo
                    # em intervalos de 0,05
                    limite_inferior = (
                        int(
                            limite_inferior
                            / 0.05
                        )
                        * 0.05
                    )


                    limite_inferior = round(
                        limite_inferior,
                        2
                    )


                    return (
                        limite_inferior,
                        1
                    )


                # ==================================
                # EVOLUÇÃO DO P
                # ==================================

                if (
                    visualizacao_p
                    == "Evolução do P"
                ):

                    for etapa in etapas_selecionadas:

                        st.markdown(
                            f"#### {etapa}"
                        )


                        dados_etapa_p = (
                            dados_p[
                                dados_p[
                                    "Etapa"
                                ]
                                == etapa
                            ]
                            .copy()
                        )


                        dados_etapa_p = (
                            dados_etapa_p[
                                [
                                    "Município",
                                    "Rede",
                                    "Comparação",
                                    "Ano",
                                    "P"
                                ]
                            ]
                            .dropna(
                                subset=[
                                    "P"
                                ]
                            )
                        )


                        if dados_etapa_p.empty:

                            st.info(
                                "Não há resultados do "
                                "Indicador de Rendimento (P) "
                                "para esta etapa e período."
                            )

                            continue


                        # ==========================
                        # ESCALA
                        # ==========================

                        (
                            escala_p_minima,
                            escala_p_maxima
                        ) = calcular_escala_p(
                            dados_etapa_p["P"]
                        )


                        # ==========================
                        # LINHAS
                        # ==========================

                        linhas_p = (
                            alt.Chart(
                                dados_etapa_p
                            )
                            .mark_line(
                                point=True
                            )
                            .encode(

                                x=alt.X(
                                    "Ano:O",
                                    title="Ano",
                                    sort=anos_comparacao_p,
                                    axis=alt.Axis(
                                        labelAngle=0
                                    )
                                ),

                                y=alt.Y(
                                    "P:Q",
                                    title=(
                                        "Indicador de "
                                        "Rendimento (P)"
                                    ),
                                    scale=alt.Scale(
                                        domain=[
                                            escala_p_minima,
                                            escala_p_maxima
                                        ]
                                    ),
                                    axis=alt.Axis(
                                        format=".2f"
                                    )
                                ),

                                color=alt.Color(
                                    "Comparação:N",
                                    title=(
                                        "Município / Rede"
                                    )
                                ),

                                strokeWidth=alt.condition(
                                    (
                                        alt.datum.Município
                                        == municipio_referencia
                                    ),
                                    alt.value(4),
                                    alt.value(2)
                                ),

                                tooltip=[
                                    alt.Tooltip(
                                        "Município:N",
                                        title="Município"
                                    ),

                                    alt.Tooltip(
                                        "Rede:N",
                                        title="Rede"
                                    ),

                                    alt.Tooltip(
                                        "Ano:O",
                                        title="Ano"
                                    ),

                                    alt.Tooltip(
                                        "P:Q",
                                        title="P",
                                        format=".3f"
                                    )
                                ]
                            )
                        )


                        # ==========================
                        # VALORES
                        # ==========================

                        valores_p = (
                            alt.Chart(
                                dados_etapa_p
                            )
                            .mark_text(
                                dy=-12,
                                fontSize=11
                            )
                            .encode(

                                x=alt.X(
                                    "Ano:O",
                                    sort=anos_comparacao_p
                                ),

                                y=alt.Y(
                                    "P:Q",
                                    scale=alt.Scale(
                                        domain=[
                                            escala_p_minima,
                                            escala_p_maxima
                                        ]
                                    )
                                ),

                                text=alt.Text(
                                    "P:Q",
                                    format=".3f"
                                ),

                                detail=alt.Detail(
                                    "Comparação:N"
                                )
                            )
                        )


                        grafico_p = (
                            linhas_p
                            + valores_p
                        ).properties(
                            height=430
                        )


                        st.altair_chart(
                            grafico_p,
                            use_container_width=True
                        )


                # ==================================
                # P × TAXA DE APROVAÇÃO
                # ==================================

                else:

                    st.caption(
                        "Cada ponto representa uma edição "
                        "do indicador. A posição horizontal "
                        "corresponde à Taxa de Aprovação "
                        "Geral e a posição vertical ao "
                        "Indicador de Rendimento (P)."
                    )


                    for etapa in etapas_selecionadas:

                        st.markdown(
                            f"#### {etapa}"
                        )


                        dados_relacao_p = (
                            dados_p[
                                dados_p[
                                    "Etapa"
                                ]
                                == etapa
                            ]
                            .copy()
                        )


                        dados_relacao_p = (
                            dados_relacao_p[
                                [
                                    "Município",
                                    "Rede",
                                    "Comparação",
                                    "Ano",
                                    "P",
                                    "Aprovação Geral"
                                ]
                            ]
                            .dropna(
                                subset=[
                                    "P",
                                    "Aprovação Geral"
                                ]
                            )
                        )


                        if dados_relacao_p.empty:

                            st.info(
                                "Não há resultados simultâneos "
                                "de P e Taxa de Aprovação para "
                                "esta etapa e período."
                            )

                            continue


                        # ==========================
                        # ESCALA DO P
                        # ==========================

                        (
                            escala_p_minima,
                            escala_p_maxima
                        ) = calcular_escala_p(
                            dados_relacao_p["P"]
                        )


                        # ==========================
                        # ESCALA DA APROVAÇÃO
                        # ==========================

                        aprovacao_minima = float(
                            dados_relacao_p[
                                "Aprovação Geral"
                            ].min()
                        )


                        escala_aprovacao_minima = max(
                            0,
                            aprovacao_minima - 5
                        )


                        escala_aprovacao_minima = (
                            int(
                                escala_aprovacao_minima
                                // 5
                            )
                            * 5
                        )


                        # ==========================
                        # GRÁFICO DE RELAÇÃO
                        # ==========================

                        grafico_relacao_p = (
                            alt.Chart(
                                dados_relacao_p
                            )
                            .mark_circle(
                                size=120
                            )
                            .encode(

                                x=alt.X(
                                    "Aprovação Geral:Q",
                                    title=(
                                        "Taxa de Aprovação "
                                        "Geral (%)"
                                    ),
                                    scale=alt.Scale(
                                        domain=[
                                            escala_aprovacao_minima,
                                            100
                                        ]
                                    ),
                                    axis=alt.Axis(
                                        format=".0f"
                                    )
                                ),

                                y=alt.Y(
                                    "P:Q",
                                    title=(
                                        "Indicador de "
                                        "Rendimento (P)"
                                    ),
                                    scale=alt.Scale(
                                        domain=[
                                            escala_p_minima,
                                            escala_p_maxima
                                        ]
                                    ),
                                    axis=alt.Axis(
                                        format=".2f"
                                    )
                                ),

                                color=alt.Color(
                                    "Comparação:N",
                                    title=(
                                        "Município / Rede"
                                    )
                                ),

                                tooltip=[
                                    alt.Tooltip(
                                        "Município:N",
                                        title="Município"
                                    ),

                                    alt.Tooltip(
                                        "Rede:N",
                                        title="Rede"
                                    ),

                                    alt.Tooltip(
                                        "Ano:O",
                                        title="Ano"
                                    ),

                                    alt.Tooltip(
                                        "Aprovação Geral:Q",
                                        title="Aprovação",
                                        format=".1f"
                                    ),

                                    alt.Tooltip(
                                        "P:Q",
                                        title="P",
                                        format=".3f"
                                    )
                                ]
                            )
                            .properties(
                                height=430
                            )
                        )


                        # ==========================
                        # ANO JUNTO AO PONTO
                        # ==========================

                        rotulos_ano_p = (
                            alt.Chart(
                                dados_relacao_p
                            )
                            .mark_text(
                                dx=10,
                                dy=-8,
                                fontSize=10
                            )
                            .encode(

                                x=alt.X(
                                    "Aprovação Geral:Q",
                                    scale=alt.Scale(
                                        domain=[
                                            escala_aprovacao_minima,
                                            100
                                        ]
                                    )
                                ),

                                y=alt.Y(
                                    "P:Q",
                                    scale=alt.Scale(
                                        domain=[
                                            escala_p_minima,
                                            escala_p_maxima
                                        ]
                                    )
                                ),

                                text=alt.Text(
                                    "Ano:O"
                                ),

                                detail=alt.Detail(
                                    "Comparação:N"
                                )
                            )
                        )


                        grafico_relacao_final = (
                            grafico_relacao_p
                            + rotulos_ano_p
                        )


                        st.altair_chart(
                            grafico_relacao_final,
                            use_container_width=True
                        )


                st.caption(
                    "Barueri permanece como referência "
                    "pela Rede Municipal. Os municípios "
                    "adicionais utilizam exclusivamente "
                    "a rede selecionada para comparação."
                )


            elif opcao_comparacao == "Nota SAEB":

                st.markdown(
                    "### Nota SAEB"
                )


                # ==================================
                # DISCIPLINAS
                # ==================================

                disciplinas_saeb = st.multiselect(
                    "Disciplinas",
                    [
                        "Matemática",
                        "Língua Portuguesa"
                    ],
                    default=[
                        "Matemática",
                        "Língua Portuguesa"
                    ],
                    key="disciplinas_saeb_municipios"
                )


                # ==================================
                # TIPO DE VISUALIZAÇÃO
                # ==================================

                visualizacao_saeb = st.selectbox(
                    "Visualização da Nota SAEB",
                    [
                        "Evolução das proficiências",
                        "Nota Média Padronizada (N)",
                        "Proficiências × N"
                    ],
                    index=0,
                    key="visualizacao_saeb_municipios"
                )


                # ==================================
                # PREPARAÇÃO DOS DADOS
                # ==================================

                dados_saeb = (
                    dados_comparacao
                    .copy()
                )


                dados_saeb["Ano"] = (
                    pd.to_numeric(
                        dados_saeb["Ano"],
                        errors="coerce"
                    )
                    .astype("Int64")
                    .astype(str)
                )


                for coluna_saeb in [
                    "Matemática",
                    "Língua Portuguesa",
                    "N"
                ]:

                    if coluna_saeb in dados_saeb.columns:

                        dados_saeb[
                            coluna_saeb
                        ] = pd.to_numeric(
                            dados_saeb[
                                coluna_saeb
                            ],
                            errors="coerce"
                        )


                anos_comparacao_saeb = [
                    str(ano)
                    for ano in anos_disponiveis
                    if (
                        ano_inicial
                        <= ano
                        <= ano_final
                    )
                ]


                # ==================================
                # CLASSIFICAÇÃO DOS NÍVEIS
                # ==================================

                def classificar_nivel_saeb(
                    valor,
                    etapa
                ):

                    if pd.isna(valor):

                        return None


                    valor = float(valor)


                    if etapa == "Fundamental I":

                        if valor < 125:
                            return "Nível 0"

                        elif valor < 150:
                            return "Nível 1"

                        elif valor < 175:
                            return "Nível 2"

                        elif valor < 200:
                            return "Nível 3"

                        elif valor < 225:
                            return "Nível 4"

                        elif valor < 250:
                            return "Nível 5"

                        elif valor < 275:
                            return "Nível 6"

                        elif valor < 300:
                            return "Nível 7"

                        elif valor < 325:
                            return "Nível 8"

                        elif valor < 350:
                            return "Nível 9"

                        else:
                            return "Nível 10"


                    else:

                        if valor < 200:
                            return "Nível 0"

                        elif valor < 225:
                            return "Nível 1"

                        elif valor < 250:
                            return "Nível 2"

                        elif valor < 275:
                            return "Nível 3"

                        elif valor < 300:
                            return "Nível 4"

                        elif valor < 325:
                            return "Nível 5"

                        elif valor < 350:
                            return "Nível 6"

                        elif valor < 375:
                            return "Nível 7"

                        elif valor < 400:
                            return "Nível 8"

                        else:
                            return "Nível 9"


                # ==================================
                # ESCALA DINÂMICA DA PROFICIÊNCIA
                # ==================================

                def calcular_escala_proficiência(
                    serie_valores
                ):

                    valores_validos = (
                        pd.to_numeric(
                            serie_valores,
                            errors="coerce"
                        )
                        .dropna()
                    )


                    if valores_validos.empty:

                        return 0, 400


                    valor_minimo = float(
                        valores_validos.min()
                    )

                    valor_maximo = float(
                        valores_validos.max()
                    )


                    limite_inferior = max(
                        0,
                        valor_minimo - 20
                    )


                    limite_superior = (
                        valor_maximo + 20
                    )


                    limite_inferior = (
                        int(
                            limite_inferior
                            // 25
                        )
                        * 25
                    )


                    limite_superior = (
                        int(
                            (
                                limite_superior
                                + 24
                            )
                            // 25
                        )
                        * 25
                    )


                    return (
                        limite_inferior,
                        limite_superior
                    )


                # ==================================
                # ESCALA DINÂMICA DO N
                # ==================================

                def calcular_escala_n(
                    serie_valores
                ):

                    valores_validos = (
                        pd.to_numeric(
                            serie_valores,
                            errors="coerce"
                        )
                        .dropna()
                    )


                    if valores_validos.empty:

                        return 0, 10


                    valor_minimo = float(
                        valores_validos.min()
                    )

                    valor_maximo = float(
                        valores_validos.max()
                    )


                    limite_inferior = max(
                        0,
                        valor_minimo - 0.5
                    )


                    limite_superior = min(
                        10,
                        valor_maximo + 0.5
                    )


                    limite_inferior = (
                        int(
                            limite_inferior
                            * 2
                        )
                        / 2
                    )


                    limite_superior = (
                        int(
                            (
                                limite_superior
                                * 2
                            )
                            + 0.999
                        )
                        / 2
                    )


                    return (
                        limite_inferior,
                        limite_superior
                    )


                # ==================================
                # EVOLUÇÃO DAS PROFICIÊNCIAS
                # ==================================

                if (
                    visualizacao_saeb
                    == "Evolução das proficiências"
                ):

                    if not disciplinas_saeb:

                        st.warning(
                            "Selecione pelo menos uma "
                            "disciplina."
                        )


                    else:

                        for etapa in etapas_selecionadas:

                            st.markdown(
                                f"#### {etapa}"
                            )


                            dados_etapa_saeb = (
                                dados_saeb[
                                    dados_saeb[
                                        "Etapa"
                                    ]
                                    == etapa
                                ]
                                .copy()
                            )


                            if dados_etapa_saeb.empty:

                                st.info(
                                    "Não há resultados "
                                    "disponíveis para esta etapa."
                                )

                                continue


                            # ======================
                            # UM GRÁFICO POR DISCIPLINA
                            # ======================

                            for disciplina in (
                                disciplinas_saeb
                            ):

                                if (
                                    disciplina
                                    not in
                                    dados_etapa_saeb.columns
                                ):

                                    continue


                                dados_disciplina = (
                                    dados_etapa_saeb[
                                        [
                                            "Município",
                                            "Rede",
                                            "Comparação",
                                            "Ano",
                                            disciplina
                                        ]
                                    ]
                                    .dropna(
                                        subset=[
                                            disciplina
                                        ]
                                    )
                                    .copy()
                                )


                                if dados_disciplina.empty:

                                    st.info(
                                        f"Não há resultados "
                                        f"de {disciplina} para "
                                        "esta etapa e período."
                                    )

                                    continue


                                # ==================
                                # NÍVEL
                                # ==================

                                dados_disciplina[
                                    "Nível"
                                ] = dados_disciplina[
                                    disciplina
                                ].apply(
                                    lambda valor:
                                        classificar_nivel_saeb(
                                            valor,
                                            etapa
                                        )
                                )


                                (
                                    escala_saeb_minima,
                                    escala_saeb_maxima
                                ) = calcular_escala_proficiência(
                                    dados_disciplina[
                                        disciplina
                                    ]
                                )


                                st.markdown(
                                    f"##### {disciplina}"
                                )


                                # ==================
                                # LINHAS
                                # ==================

                                linhas_saeb = (
                                    alt.Chart(
                                        dados_disciplina
                                    )
                                    .mark_line(
                                        point=True
                                    )
                                    .encode(

                                        x=alt.X(
                                            "Ano:O",
                                            title="Ano",
                                            sort=(
                                                anos_comparacao_saeb
                                            ),
                                            axis=alt.Axis(
                                                labelAngle=0
                                            )
                                        ),

                                        y=alt.Y(
                                            f"{disciplina}:Q",
                                            title=(
                                                f"Nota SAEB - "
                                                f"{disciplina}"
                                            ),
                                            scale=alt.Scale(
                                                domain=[
                                                    escala_saeb_minima,
                                                    escala_saeb_maxima
                                                ]
                                            ),
                                            axis=alt.Axis(
                                                format=".0f"
                                            )
                                        ),

                                        color=alt.Color(
                                            "Comparação:N",
                                            title=(
                                                "Município / Rede"
                                            ),
                                            legend=alt.Legend(
                                                orient="bottom",
                                                direction="horizontal"
                                            )
                                        ),

                                        strokeWidth=alt.condition(
                                            (
                                                alt.datum.Município
                                                == municipio_referencia
                                            ),
                                            alt.value(4),
                                            alt.value(2)
                                        ),

                                        tooltip=[
                                            alt.Tooltip(
                                                "Município:N",
                                                title="Município"
                                            ),

                                            alt.Tooltip(
                                                "Rede:N",
                                                title="Rede"
                                            ),

                                            alt.Tooltip(
                                                "Ano:O",
                                                title="Ano"
                                            ),

                                            alt.Tooltip(
                                                f"{disciplina}:Q",
                                                title=disciplina,
                                                format=".1f"
                                            ),

                                            alt.Tooltip(
                                                "Nível:N",
                                                title="Nível"
                                            )
                                        ]
                                    )
                                )


                                # ==================
                                # VALORES
                                # ==================

                                valores_saeb = (
                                    alt.Chart(
                                        dados_disciplina
                                    )
                                    .mark_text(
                                        dy=-12,
                                        fontSize=10
                                    )
                                    .encode(

                                        x=alt.X(
                                            "Ano:O",
                                            sort=(
                                                anos_comparacao_saeb
                                            )
                                        ),

                                        y=alt.Y(
                                            f"{disciplina}:Q",
                                            scale=alt.Scale(
                                                domain=[
                                                    escala_saeb_minima,
                                                    escala_saeb_maxima
                                                ]
                                            )
                                        ),

                                        text=alt.Text(
                                            f"{disciplina}:Q",
                                            format=".1f"
                                        ),

                                        detail=alt.Detail(
                                            "Comparação:N"
                                        )
                                    )
                                )


                                grafico_saeb = (
                                    linhas_saeb
                                    + valores_saeb
                                ).properties(
                                    height=430
                                )


                                st.altair_chart(
                                    grafico_saeb,
                                    use_container_width=True
                                )


                # ==================================
                # NOTA MÉDIA PADRONIZADA (N)
                # ==================================

                elif (
                    visualizacao_saeb
                    == "Nota Média Padronizada (N)"
                ):

                    for etapa in etapas_selecionadas:

                        st.markdown(
                            f"#### {etapa}"
                        )


                        dados_n = (
                            dados_saeb[
                                dados_saeb[
                                    "Etapa"
                                ]
                                == etapa
                            ]
                            [
                                [
                                    "Município",
                                    "Rede",
                                    "Comparação",
                                    "Ano",
                                    "N"
                                ]
                            ]
                            .dropna(
                                subset=[
                                    "N"
                                ]
                            )
                            .copy()
                        )


                        if dados_n.empty:

                            st.info(
                                "Não há resultados da "
                                "Nota Média Padronizada (N) "
                                "para esta etapa e período."
                            )

                            continue


                        (
                            escala_n_minima,
                            escala_n_maxima
                        ) = calcular_escala_n(
                            dados_n["N"]
                        )


                        linhas_n = (
                            alt.Chart(
                                dados_n
                            )
                            .mark_line(
                                point=True
                            )
                            .encode(

                                x=alt.X(
                                    "Ano:O",
                                    title="Ano",
                                    sort=(
                                        anos_comparacao_saeb
                                    ),
                                    axis=alt.Axis(
                                        labelAngle=0
                                    )
                                ),

                                y=alt.Y(
                                    "N:Q",
                                    title=(
                                        "Nota Média "
                                        "Padronizada (N)"
                                    ),
                                    scale=alt.Scale(
                                        domain=[
                                            escala_n_minima,
                                            escala_n_maxima
                                        ]
                                    ),
                                    axis=alt.Axis(
                                        format=".1f"
                                    )
                                ),

                                color=alt.Color(
                                    "Comparação:N",
                                    title=(
                                        "Município / Rede"
                                    ),
                                    legend=alt.Legend(
                                        orient="bottom",
                                        direction="horizontal"
                                    )
                                ),

                                strokeWidth=alt.condition(
                                    (
                                        alt.datum.Município
                                        == municipio_referencia
                                    ),
                                    alt.value(4),
                                    alt.value(2)
                                ),

                                tooltip=[
                                    alt.Tooltip(
                                        "Município:N",
                                        title="Município"
                                    ),

                                    alt.Tooltip(
                                        "Rede:N",
                                        title="Rede"
                                    ),

                                    alt.Tooltip(
                                        "Ano:O",
                                        title="Ano"
                                    ),

                                    alt.Tooltip(
                                        "N:Q",
                                        title="N",
                                        format=".2f"
                                    )
                                ]
                            )
                        )


                        valores_n = (
                            alt.Chart(
                                dados_n
                            )
                            .mark_text(
                                dy=-12,
                                fontSize=10
                            )
                            .encode(

                                x=alt.X(
                                    "Ano:O",
                                    sort=(
                                        anos_comparacao_saeb
                                    )
                                ),

                                y=alt.Y(
                                    "N:Q",
                                    scale=alt.Scale(
                                        domain=[
                                            escala_n_minima,
                                            escala_n_maxima
                                        ]
                                    )
                                ),

                                text=alt.Text(
                                    "N:Q",
                                    format=".2f"
                                ),

                                detail=alt.Detail(
                                    "Comparação:N"
                                )
                            )
                        )


                        grafico_n = (
                            linhas_n
                            + valores_n
                        ).properties(
                            height=430
                        )


                        st.altair_chart(
                            grafico_n,
                            use_container_width=True
                        )


                # ==================================
                # PROFICIÊNCIAS × N
                # ==================================

                else:

                    if not disciplinas_saeb:

                        st.warning(
                            "Selecione pelo menos uma "
                            "disciplina."
                        )


                    else:

                        st.caption(
                            "Cada ponto representa uma "
                            "edição. A proficiência da "
                            "disciplina selecionada aparece "
                            "no eixo horizontal e a Nota "
                            "Média Padronizada (N) no eixo "
                            "vertical."
                        )


                        for etapa in etapas_selecionadas:

                            st.markdown(
                                f"#### {etapa}"
                            )


                            dados_etapa_relacao = (
                                dados_saeb[
                                    dados_saeb[
                                        "Etapa"
                                    ]
                                    == etapa
                                ]
                                .copy()
                            )


                            for disciplina in (
                                disciplinas_saeb
                            ):

                                if (
                                    disciplina
                                    not in
                                    dados_etapa_relacao.columns
                                ):

                                    continue


                                dados_relacao_n = (
                                    dados_etapa_relacao[
                                        [
                                            "Município",
                                            "Rede",
                                            "Comparação",
                                            "Ano",
                                            disciplina,
                                            "N"
                                        ]
                                    ]
                                    .dropna(
                                        subset=[
                                            disciplina,
                                            "N"
                                        ]
                                    )
                                    .copy()
                                )


                                if dados_relacao_n.empty:

                                    st.info(
                                        f"Não há resultados "
                                        f"simultâneos de "
                                        f"{disciplina} e N "
                                        "para esta etapa."
                                    )

                                    continue


                                dados_relacao_n[
                                    "Nível"
                                ] = dados_relacao_n[
                                    disciplina
                                ].apply(
                                    lambda valor:
                                        classificar_nivel_saeb(
                                            valor,
                                            etapa
                                        )
                                )


                                (
                                    escala_saeb_minima,
                                    escala_saeb_maxima
                                ) = calcular_escala_proficiência(
                                    dados_relacao_n[
                                        disciplina
                                    ]
                                )


                                (
                                    escala_n_minima,
                                    escala_n_maxima
                                ) = calcular_escala_n(
                                    dados_relacao_n["N"]
                                )


                                st.markdown(
                                    f"##### {disciplina} × N"
                                )


                                pontos_relacao_n = (
                                    alt.Chart(
                                        dados_relacao_n
                                    )
                                    .mark_circle(
                                        size=120
                                    )
                                    .encode(

                                        x=alt.X(
                                            f"{disciplina}:Q",
                                            title=disciplina,
                                            scale=alt.Scale(
                                                domain=[
                                                    escala_saeb_minima,
                                                    escala_saeb_maxima
                                                ]
                                            )
                                        ),

                                        y=alt.Y(
                                            "N:Q",
                                            title=(
                                                "Nota Média "
                                                "Padronizada (N)"
                                            ),
                                            scale=alt.Scale(
                                                domain=[
                                                    escala_n_minima,
                                                    escala_n_maxima
                                                ]
                                            )
                                        ),

                                        color=alt.Color(
                                            "Comparação:N",
                                            title=(
                                                "Município / Rede"
                                            ),
                                            legend=alt.Legend(
                                                orient="bottom",
                                                direction="horizontal"
                                            )
                                        ),

                                        tooltip=[
                                            alt.Tooltip(
                                                "Município:N",
                                                title="Município"
                                            ),

                                            alt.Tooltip(
                                                "Rede:N",
                                                title="Rede"
                                            ),

                                            alt.Tooltip(
                                                "Ano:O",
                                                title="Ano"
                                            ),

                                            alt.Tooltip(
                                                f"{disciplina}:Q",
                                                title=disciplina,
                                                format=".1f"
                                            ),

                                            alt.Tooltip(
                                                "N:Q",
                                                title="N",
                                                format=".2f"
                                            ),

                                            alt.Tooltip(
                                                "Nível:N",
                                                title="Nível"
                                            )
                                        ]
                                    )
                                )


                                rotulos_ano_n = (
                                    alt.Chart(
                                        dados_relacao_n
                                    )
                                    .mark_text(
                                        dx=10,
                                        dy=-8,
                                        fontSize=10
                                    )
                                    .encode(

                                        x=alt.X(
                                            f"{disciplina}:Q",
                                            scale=alt.Scale(
                                                domain=[
                                                    escala_saeb_minima,
                                                    escala_saeb_maxima
                                                ]
                                            )
                                        ),

                                        y=alt.Y(
                                            "N:Q",
                                            scale=alt.Scale(
                                                domain=[
                                                    escala_n_minima,
                                                    escala_n_maxima
                                                ]
                                            )
                                        ),

                                        text=alt.Text(
                                            "Ano:O"
                                        ),

                                        detail=alt.Detail(
                                            "Comparação:N"
                                        )
                                    )
                                )


                                grafico_relacao_n = (
                                    pontos_relacao_n
                                    + rotulos_ano_n
                                ).properties(
                                    height=430
                                )


                                st.altair_chart(
                                    grafico_relacao_n,
                                    use_container_width=True
                                )


                st.caption(
                    "Barueri permanece como referência "
                    "pela Rede Municipal. Os níveis de "
                    "proficiência são determinados de "
                    "acordo com a etapa de ensino."
                )


            elif opcao_comparacao == "IDEB":

                st.info(
                    "A análise do IDEB será "
                    "incorporada na etapa 5.10.8."
                )


    elif analise_municipal == "Evolução":

        st.markdown("### Evolução dos Indicadores")


        # ==========================================
        # NORMALIZAÇÃO DOS NOMES
        # ==========================================

        def normalizar_texto(texto):

            texto = str(texto).strip().lower()

            texto = unicodedata.normalize(
                "NFKD",
                texto
            )

            texto = "".join(
                caractere
                for caractere in texto
                if not unicodedata.combining(
                    caractere
                )
            )

            return texto


        # ==========================================
        # BASE DA EVOLUÇÃO
        # ==========================================

        dados_evolucao = municipios_filtrados.copy()


        # ==========================================
        # REFERÊNCIA FIXA
        # ==========================================

        municipio_referencia = "Barueri"
        rede_referencia = "Municipal"


        st.markdown(
            "#### Município de referência"
        )

        st.write(
            "**Barueri — Municipal**"
        )


        # ==========================================
        # DADOS DE BARUERI
        # ==========================================

        dados_barueri = dados_evolucao[
            (
                dados_evolucao["Município"]
                == municipio_referencia
            )
            &
            (
                dados_evolucao["Rede"]
                == rede_referencia
            )
        ].copy()


        # ==========================================
        # REDE PARA COMPARAÇÃO
        # ==========================================

        ordem_redes = [
            "Municipal",
            "Estadual",
            "Pública"
        ]


        redes_existentes = (
            dados_evolucao["Rede"]
            .dropna()
            .unique()
            .tolist()
        )


        redes_disponiveis = [
            rede
            for rede in ordem_redes
            if rede in redes_existentes
        ]


        rede_comparacao = st.selectbox(
            "Rede para comparação",
            options=redes_disponiveis,
            index=0,
            key="rede_comparacao_evolucao"
        )


        # ==========================================
        # MUNICÍPIOS DISPONÍVEIS NA REDE
        # ==========================================

        dados_rede = dados_evolucao[
            dados_evolucao["Rede"]
            == rede_comparacao
        ].copy()


        lista_municipios = sorted(
            dados_rede["Município"]
            .dropna()
            .unique()
            .tolist()
        )


        # Barueri já é a referência
        lista_municipios = [
            municipio
            for municipio in lista_municipios
            if municipio != municipio_referencia
        ]


        # ==========================================
        # NOMES NORMALIZADOS PARA PESQUISA
        # ==========================================

        mapa_municipios = {
            normalizar_texto(municipio):
                municipio
            for municipio in lista_municipios
        }


        opcoes_municipios = sorted(
            mapa_municipios.keys()
        )


        # ==========================================
        # SELEÇÃO MÚLTIPLA DOS MUNICÍPIOS
        # ==========================================

        municipios_normalizados = st.multiselect(
            "Municípios para comparar com Barueri",
            options=opcoes_municipios,
            default=[],
            format_func=lambda nome:
                mapa_municipios[nome],
            key="municipios_comparacao_evolucao"
        )


        municipios_comparacao = [
            mapa_municipios[nome]
            for nome in municipios_normalizados
        ]


        # ==========================================
        # INDICADOR
        # ==========================================

        indicadores = {
            "IDEB":
                "IDEB",

            "Matemática":
                "Matemática",

            "Língua Portuguesa":
                "Língua Portuguesa",

            "Nota Média Padronizada (N)":
                "N",

            "Indicador de Rendimento (P)":
                "P",

            "Taxa de Aprovação Geral":
                "Aprovação Geral"
        }


        indicador_escolhido = st.selectbox(
            "Indicador",
            options=list(
                indicadores.keys()
            ),
            index=0,
            key="indicador_evolucao"
        )


        coluna_indicador = indicadores[
            indicador_escolhido
        ]


        # ==========================================
        # IDENTIFICAÇÃO DE BARUERI NO GRÁFICO
        # ==========================================

        dados_barueri[
            "Comparação"
        ] = "Barueri - Municipal"


        partes_comparacao = [
            dados_barueri
        ]


        # ==========================================
        # MUNICÍPIOS COMPARADOS
        # ==========================================

        for municipio in municipios_comparacao:

            dados_municipio = dados_rede[
                dados_rede["Município"]
                == municipio
            ].copy()


            dados_municipio[
                "Comparação"
            ] = (
                municipio
                + " - "
                + rede_comparacao
            )


            partes_comparacao.append(
                dados_municipio
            )


        dados_grafico = pd.concat(
            partes_comparacao,
            ignore_index=True
        )


        # ==========================================
        # FILTRAGEM DO INDICADOR
        # ==========================================

        dados_grafico = dados_grafico[
            [
                "Município",
                "Rede",
                "Comparação",
                "Etapa",
                "Ano",
                coluna_indicador
            ]
        ].dropna(
            subset=[
                coluna_indicador
            ]
        )


        # ==========================================
        # ANOS COMO CATEGORIAS
        # ==========================================

        dados_grafico["Ano"] = (
            dados_grafico["Ano"]
            .astype(int)
            .astype(str)
        )


        anos_grafico = [
            str(ano)
            for ano in anos_disponiveis
            if (
                ano_inicial
                <= ano
                <= ano_final
            )
        ]


        # ==========================================
        # RESUMO DA SELEÇÃO
        # ==========================================

        st.markdown(
            "#### Comparação selecionada"
        )


        st.write(
            "**Referência:** "
            "Barueri — Municipal"
        )


        st.write(
            "**Rede comparada:** "
            f"{rede_comparacao}"
        )


        if municipios_comparacao:

            st.write(
                "**Municípios:** "
                + " | ".join(
                    municipios_comparacao
                )
            )

        else:

            st.caption(
                "Nenhum município comparativo "
                "selecionado."
            )


        st.caption(
            f"Indicador: "
            f"{indicador_escolhido}"
        )


        # ==========================================
        # PADRÃO DE DESEMPENHO
        # ==========================================

        coluna_padrao = None

        if indicador_escolhido == "Matemática":

            coluna_padrao = (
                "Padrão Matemática"
            )

        elif (
            indicador_escolhido
            == "Língua Portuguesa"
        ):

            coluna_padrao = (
                "Padrão Língua Portuguesa"
            )


        # ==========================================
        # CORES DOS PADRÕES
        # ==========================================

        cores_padroes = {
            "Abaixo do básico":
                "#E53935",

            "Básico":
                "#F9A825",

            "Adequado":
                "#43A047",

            "Avançado":
                "#1E88E5"
        }


        # ==========================================
        # PADRÃO DE DESEMPENHO
        # ==========================================

        coluna_padrao = None

        if indicador_escolhido == "Matemática":

            coluna_padrao = (
                "Padrão Matemática"
            )

        elif (
            indicador_escolhido
            == "Língua Portuguesa"
        ):

            coluna_padrao = (
                "Padrão Língua Portuguesa"
            )


        # ==========================================
        # CORES DOS PADRÕES
        # ==========================================

        cores_padroes = {
            "Abaixo do básico":
                "#E53935",

            "Básico":
                "#F9A825",

            "Adequado":
                "#43A047",

            "Avançado":
                "#1E88E5"
        }


        # ==========================================
        # GRÁFICOS POR ETAPA
        # ==========================================

        for etapa in etapas_selecionadas:

            dados_etapa = dados_grafico[
                dados_grafico["Etapa"]
                == etapa
            ].copy()


            st.markdown(
                f"##### {etapa}"
            )


            if dados_etapa.empty:

                st.warning(
                    "Não há resultados disponíveis "
                    "para esta etapa e os filtros "
                    "selecionados."
                )

                continue


            # ======================================
            # LINHAS
            # ======================================

            linhas = alt.Chart(
                dados_etapa
            ).mark_line().encode(

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
                    "Comparação:N",
                    title="Município / Rede"
                ),

                strokeWidth=alt.condition(
                    (
                        alt.datum.Município
                        == municipio_referencia
                    ),
                    alt.value(4),
                    alt.value(2)
                ),

                tooltip=[
                    alt.Tooltip(
                        "Município:N",
                        title="Município"
                    ),

                    alt.Tooltip(
                        "Rede:N",
                        title="Rede"
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


            # ======================================
            # PONTOS COM PADRÃO DE DESEMPENHO
            # ======================================

            if (
                coluna_padrao is not None
                and
                coluna_padrao
                in dados_evolucao.columns
            ):

                dados_padrao = (
                    dados_evolucao[
                        (
                            dados_evolucao[
                                "Município"
                            ].isin(
                                [
                                    municipio_referencia
                                ]
                                +
                                municipios_comparacao
                            )
                        )
                    ]
                    .copy()
                )


                # Barueri sempre Municipal
                mascara_barueri = (
                    (
                        dados_padrao[
                            "Município"
                        ]
                        == municipio_referencia
                    )
                    &
                    (
                        dados_padrao[
                            "Rede"
                        ]
                        == rede_referencia
                    )
                )


                # Municípios comparados
                mascara_comparacao = (
                    (
                        dados_padrao[
                            "Município"
                        ]
                        .isin(
                            municipios_comparacao
                        )
                    )
                    &
                    (
                        dados_padrao[
                            "Rede"
                        ]
                        == rede_comparacao
                    )
                )


                dados_padrao = dados_padrao[
                    (
                        mascara_barueri
                        |
                        mascara_comparacao
                    )
                    &
                    (
                        dados_padrao[
                            "Etapa"
                        ]
                        == etapa
                    )
                ].copy()


                dados_padrao = dados_padrao[
                    [
                        "Município",
                        "Rede",
                        "Etapa",
                        "Ano",
                        coluna_indicador,
                        coluna_padrao
                    ]
                ].dropna(
                    subset=[
                        coluna_indicador
                    ]
                )


                dados_padrao["Ano"] = (
                    dados_padrao["Ano"]
                    .astype(int)
                    .astype(str)
                )


                pontos = alt.Chart(
                    dados_padrao
                ).mark_point(
                    filled=True,
                    size=120,
                    stroke="white",
                    strokeWidth=1
                ).encode(

                    x=alt.X(
                        "Ano:O",
                        sort=anos_grafico
                    ),

                    y=alt.Y(
                        f"{coluna_indicador}:Q"
                    ),

                    color=alt.Color(
                        f"{coluna_padrao}:N",
                        title=(
                            "Padrão de desempenho"
                        ),
                        scale=alt.Scale(
                            domain=[
                                "Abaixo do básico",
                                "Básico",
                                "Adequado",
                                "Avançado"
                            ],
                            range=[
                                cores_padroes[
                                    "Abaixo do básico"
                                ],
                                cores_padroes[
                                    "Básico"
                                ],
                                cores_padroes[
                                    "Adequado"
                                ],
                                cores_padroes[
                                    "Avançado"
                                ]
                            ]
                        )
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "Município:N",
                            title="Município"
                        ),

                        alt.Tooltip(
                            "Rede:N",
                            title="Rede"
                        ),

                        alt.Tooltip(
                            "Ano:O",
                            title="Ano"
                        ),

                        alt.Tooltip(
                            f"{coluna_indicador}:Q",
                            title=(
                                indicador_escolhido
                            ),
                            format=".2f"
                        ),

                        alt.Tooltip(
                            f"{coluna_padrao}:N",
                            title=(
                                "Padrão de desempenho"
                            )
                        )
                    ]
                )


                grafico = (
                    linhas
                    + pontos
                ).properties(
                    height=430
                )


            else:

                pontos = alt.Chart(
                    dados_etapa
                ).mark_point(
                    filled=True,
                    size=80
                ).encode(

                    x=alt.X(
                        "Ano:O",
                        sort=anos_grafico
                    ),

                    y=alt.Y(
                        f"{coluna_indicador}:Q"
                    ),

                    color=alt.Color(
                        "Comparação:N",
                        title="Município / Rede"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "Município:N",
                            title="Município"
                        ),

                        alt.Tooltip(
                            "Rede:N",
                            title="Rede"
                        ),

                        alt.Tooltip(
                            "Ano:O",
                            title="Ano"
                        ),

                        alt.Tooltip(
                            f"{coluna_indicador}:Q",
                            title=(
                                indicador_escolhido
                            ),
                            format=".2f"
                        )
                    ]
                )


                grafico = (
                    linhas
                    + pontos
                ).properties(
                    height=430
                )


            st.altair_chart(
                grafico,
                use_container_width=True
            )


        st.caption(
            "Barueri utiliza a Rede Municipal "
            "como referência. Os municípios "
            "selecionados utilizam exclusivamente "
            "os resultados da rede escolhida. "
            "Pública, Municipal e Estadual são "
            "mantidas como categorias distintas "
            "da base original."
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

