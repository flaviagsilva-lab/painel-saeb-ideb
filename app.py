
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

                st.info(
                    "A análise do Indicador de "
                    "Rendimento (P) será incorporada "
                    "na etapa 5.10.6."
                )


            elif opcao_comparacao == "Nota SAEB":

                st.info(
                    "A análise da Nota SAEB será "
                    "incorporada na etapa 5.10.7."
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

