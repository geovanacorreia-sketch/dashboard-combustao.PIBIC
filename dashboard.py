#dashboard
import streamlit as st
from graphviz import Digraph
import pandas as pd
from simulador_de_combustao import (COMBUSTIVEIS, GASES_PRODUTOS, executar_simulacao)
st.set_page_config(
    page_title="Simulador de Combustão",
    page_icon="🔥",
    layout="wide")
def exibir_composicao(resultado, base_selecionada):
    """Exibe a composição na base selecionada."""
    if "Base Seca" in base_selecionada:
        # Usar base seca
        df_saida = pd.DataFrame({
            "Espécie": resultado["correntes_saida_seca"].keys(),
            "Vazão (mol/s)": resultado["correntes_saida_seca"].values(),
            "Fração molar (%)": resultado["fracoes_molares_seca"].values()
        })
        titulo = "Composição dos Gases (Base Seca - sem H₂O)"
    else:
        # Usar base úmida
        df_saida = pd.DataFrame({
            "Espécie": resultado["correntes_saida"].keys(),
            "Vazão (mol/s)": resultado["correntes_saida"].values(),
            "Fração molar (%)": resultado["fracoes_molares_umida"].values()
        })
        titulo = "Composição dos Gases (Base Úmida - com H₂O)"
    return df_saida, titulo

tab1, tab2, tab3 = st.tabs(["🔥 Simulação", "📚 Base Teórica", "Banco de Dados"])
# ABA 1 - SIMULAÇÃO
with tab1:
    # CABEÇALHO
    st.markdown(
        "<h1 style='text-align:center;'>🔥 Simulador de Combustão</h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<h4 style='text-align:center;'>Análise de Balanço de Massa e Energia</h4>",
        unsafe_allow_html=True)
    st.divider()
    # SIDEBAR
    with st.sidebar:
        st.header("⚙️ Configurações de Entrada")
        combustivel = st.selectbox(
            "Combustível",
            list(COMBUSTIVEIS.keys()))
        vazao = st.number_input(
            "Vazão molar do combustível (mol/s)",
            min_value=0.01,
            value=100.0,
            step=1.0)
        conversao = st.slider(
            "Conversão (%)",
            min_value=0,
            max_value=100,
            value=90)
        seletividade = st.slider(
            "Seletividade para CO₂ (%)",
            min_value=0,
            max_value=100,
            value=95)
        excesso_ar = st.slider(
            "Excesso de Ar (%)",
            min_value=0,
            max_value=300,
            value=20)
        T_chamine = st.number_input(
            "Temperatura da Chaminé (°C)",
            min_value=25.0,
            value=300.0,
            step=10.0)
        # SELETOR DE BASE 
        st.divider()
        st.subheader("Opções de Visualização")
        base_selecionada = st.radio(
            "Base de cálculo para composição:",
            ["Base Úmida (com H₂O)", "Base Seca (sem H₂O)"],
            index=0,
            help="Base úmida inclui o vapor d'água nos cálculos. Base seca exclui a água."
        )
        resultado = executar_simulacao(
            combustivel_nome=combustivel,
            vazao=vazao,
            conversao=conversao,
            seletividade=seletividade,
            excesso_ar=excesso_ar,
            T_chamine=T_chamine)
    # KPIs
    st.subheader("📊 Parâmetros de Operação")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ar Teórico (mol/s)",
            f"{resultado['o2_teorico']*4.76:.1f}")
    with col2:
        st.metric("Ar Real (mol/s)",
            f"{resultado['ar_real']:.1f}")
    with col3:
        st.metric("Q Combustão (kJ/s)",
            f"{resultado['q_comb']:.1f}")
    with col4:
        st.metric("Eficiência (%)",
            f"{resultado['eficiencia']:.1f}")
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Q Chaminé (kJ/s)",
            f"{resultado['q_chamine']:.1f}")
    with col6:
        st.metric("Q Útil (kJ/s)",
            f"{resultado['q_util']:.1f}")
    with col7:
        st.metric("O₂ Excedente (mol/s)",
            f"{resultado['correntes_saida']['O2']:.1f}")
    with col8:
        st.metric("Combustível Não Reagido",
            f"{resultado['combustivel_nao_reagido']:.1f}")
    st.divider()
    # TABELA DE CORRENTES
    st.subheader("Correntes de Saída")
    df_saida, titulo = exibir_composicao(resultado, base_selecionada)
    st.caption(f"💧 Água produzida: {resultado['agua_produzida']:.2f} mol/s")
    st.caption(f"📊 Total de gases (úmido): {resultado['total_saida']:.2f} mol/s")
    st.caption(f"📊 Total de gases (seco): {resultado['total_seco']:.2f} mol/s")
    st.dataframe(df_saida, use_container_width=True)
    # Gráfico de composição
    st.subheader(titulo)
    st.bar_chart(df_saida.set_index("Espécie")["Vazão (mol/s)"])
    # COMPARAÇÃO BASE SECA vs ÚMIDA
    with st.expander(" Comparação entre Bases Seca e Úmida"):
        st.markdown("""
        ### Base Úmida vs Base Seca
        
        **Base Úmida:** Considera todo o vapor d'água produzido.
        **Base Seca:** Exclui o vapor d'água, mais comum em normas ambientais.
        """)
        # Criar tabela comparativa
        df_comparacao = pd.DataFrame({
            "Espécie": list(resultado["fracoes_molares_umida"].keys()),
            "Base Úmida (%)": list(resultado["fracoes_molares_umida"].values()),
            "Base Seca (%)": [
                resultado["fracoes_molares_seca"].get(esp, 0) 
                for esp in resultado["fracoes_molares_umida"].keys()
            ]
        })
        # Calcular diferença
        df_comparacao["Diferença"] = (
            df_comparacao["Base Seca (%)"] - df_comparacao["Base Úmida (%)"])
        st.dataframe(df_comparacao, use_container_width=True)
        # Gráfico comparativo
        st.bar_chart(
            df_comparacao.set_index("Espécie")[["Base Úmida (%)", "Base Seca (%)"]])
        st.info("""
        💡 **Observação:** 
        - As concentrações em base seca são sempre maiores (menos diluídas)
        - Quanto mais água é produzida, maior a diferença entre as bases
        - Normas ambientais geralmente usam base seca para emissões
        """)
    # ENERGIA
    st.subheader("Fluxo de Energia")
    df_energia = pd.DataFrame({
        "Variável": [
            "Q Combustão",
            "Q Chaminé",
            "Q Útil"],
        "Valor": [
            resultado["q_comb"],
            resultado["q_chamine"],
            resultado["q_util"]
        ]})
    st.dataframe(df_energia, use_container_width=True)
    # GRÁFICO DE DISTRIBUIÇÃO ENERGÉTICA
    st.subheader("Distribuição Energética")
    df_energia_dist = pd.DataFrame({
        "Energia": ["Energia Útil", "Perda Chaminé"],
        "Valor": [resultado["q_util"], resultado["q_chamine"]]})
    st.bar_chart(df_energia_dist.set_index("Energia"))
    # DISTRIBUIÇÃO ENERGÉTICA (Sankey)
    import plotly.graph_objects as go
    st.subheader("Fluxograma Energético")
    labels = [
        f"Q Combustão\n{resultado['q_comb']:.0f} kJ/s",
        f"Energia Útil\n{resultado['q_util']:.0f} kJ/s",
        f"Perda Chaminé\n{resultado['q_chamine']:.0f} kJ/s"]
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(pad=25, thickness=28, line=dict(color="black", width=0.5),
            label=labels,
            color=[
                "#F39C12",   # Laranja
                "#27AE60",   # Verde
                "#E74C3C"    # Vermelho
                ]),
        link=dict(source=[0, 0], target=[1, 2],
                  value=[resultado["q_util"], resultado["q_chamine"]],
                  color=["rgba(39,174,96,0.45)", "rgba(231,76,60,0.45)"])))
    fig.update_layout(
        title="Distribuição da Energia Liberada",
        font_size=14,
        height=420)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("📖 Como interpretar o diagrama"):
        st.markdown("""
        A energia liberada na combustão é dividida em duas parcelas.
        **Q Combustão: É toda a energia gerada pela reação química.**
                        
        **Energia Útil: É a parcela efetivamente aproveitada pelo processo.**
                        
        **Perda pela Chaminé: É a energia transportada pelos gases quentes que deixam o sistema.**
        A largura das setas é proporcional à quantidade de energia.
        Quanto maior a seta verde e menor a vermelha, maior a eficiência térmica.""")
    # SENSIBILIDADE
    st.subheader("Sensibilidade da Eficiência")
    lista_excesso = list(range(0, 101, 10))
    eficiencias = []
    for excesso in lista_excesso:
        r = executar_simulacao(
            combustivel_nome=combustivel,
            vazao=vazao,
            conversao=conversao,
            seletividade=seletividade,
            excesso_ar=excesso,
            T_chamine=T_chamine)
        eficiencias.append(r["eficiencia"])
    df_sensibilidade = pd.DataFrame({
        "Excesso de Ar (%)": lista_excesso,
        "Eficiência (%)": eficiencias})
    st.line_chart(df_sensibilidade.set_index("Excesso de Ar (%)"))
    # DOWNLOAD
    st.download_button(
        label="📥 Baixar Resultados CSV",
        data=df_saida.to_csv(index=False),
        file_name="resultado_combustao.csv",
        mime="text/csv")
    with st.expander("🔍 Resultados completos"):
        st.json(resultado)
# ABA 2 - BASE TEÓRICA
with tab2:
    st.header("📚 Base Teórica")
    st.subheader("Visão Geral do Processo")
    st.info("""
    Este fluxograma representa o processo de combustão utilizado no simulador.
    Os parâmetros de entrada são informados pelo usuário e os resultados
    apresentam a composição dos gases de chaminé e o balanço de massa e energia.
    """)
    st.image("fluxograma.jpg",
        caption="Esquema simplificado do processo de combustão",
        use_container_width=True)
    st.divider()
    st.markdown("""
    ## 1. Reações de Combustão
    A combustão é uma reação rápida entre um combustível e o oxigênio. Os principais elementos dos combustíveis comuns (carvão, óleo, gás natural) são o carbono, o hidrogênio e o enxofre. Quando esses elementos reagem completamente com o oxigênio, o carbono é convertido em CO₂, o hidrogênio em H₂O e o enxofre em SO₂.
    ### Combustão Completa
    Todo o carbono é convertido em dióxido de carbono (CO₂).
    Exemplo para o metano:
    CH₄ + 2 O₂ → CO₂ + 2 H₂O
    ### Combustão Incompleta
    Parte do carbono é convertida em monóxido de carbono (CO).
    CH₄ + 1,5 O₂ → CO + 2 H₂O
    """)
    st.markdown("""## Estequiometria Geral
                Para um combustível genérico: CₓHᵧO𝓏
                Combustão completa: CₓHᵧO𝓏 + (x + y/4 − z/2) O₂ → x CO₂ + y/2 H₂O
                Combustão incompleta: CₓHᵧO𝓏 + (x/2 + y/4 − z/2) O₂ → x CO + y/2 H₂O""")
    dados = COMBUSTIVEIS[combustivel]
    st.divider()
    st.markdown("""
    ## 2. Conversão
    A conversão representa a fração do combustível que efetivamente reage.
                
    Equação:
    X = (Combustível Reagido) / (Combustível Alimentado)
                
    - Conversão = 100% → todo combustível reage.
    - Conversão < 100% → parte do combustível sai sem reagir.
    """)
    st.divider()
    st.markdown("""
    ## 3. Seletividade
    A seletividade indica quanto do combustível reagido segue para a rota desejada.
                
    Neste simulador:
    - Produto desejado: CO₂
    - Produto indesejado: CO
    Equação:
    S = CO₂ produzido / (CO₂ produzido + CO produzido)
    - S = 100% → combustão totalmente completa.
    - S < 100% → formação de CO.
    """)
    st.divider()
    st.markdown("""
    ## 4. Excesso de Ar
    O excesso de ar representa a quantidade de ar fornecida acima da necessidade
    estequiométrica.
                
    Nota: O Ar Teórico é sempre calculado assumindo conversão de 100% e combustão 100% completa (CO₂), independente do resultado real do reator.
    Equação:
    Excesso de Ar (%) =
    ((Ar Real - Ar Teórico) / Ar Teórico) × 100
    Consequências:
    - Reduz formação de CO
    - Melhora a conversão
    - Aumenta perdas térmicas pela chaminé
    """)
    st.divider()
    st.markdown("""
    ## 5. Balanço de Massa
    Baseado na Lei da Conservação da Massa:
    Entrada = Saída + Acumulação
                
    Em regime permanente:
    Entrada = Saída
                
    O simulador calcula:
    - Consumo de combustível
    - Consumo de oxigênio
    - Formação de CO₂
    - Formação de CO
    - Formação de H₂O
    - Oxigênio excedente
    - Nitrogênio do ar
                
    Nitrogênio do ar: Entra no sistema como inerte. 
    Para os cálculos, assume-se a composição molar do ar como 21% (O₂) e 79% (N₂).
                
    Composição dos Gases: Os resultados podem ser expressos em Base Úmida (contando o H₂O produzido) ou Base Seca (fração molar dos gases em base livre de água).
    """)
    st.divider()
    st.markdown("""
    ## 6. Balanço de Energia
    Baseado na Primeira Lei da Termodinâmica:
    Entrada de Energia = Saída de Energia
    O simulador calcula:
    ### Calor de Combustão: Energia liberada pela reação química.
    Calculado a partir do Calor de Reação padrão utilizando as entalpias de formação dos reagentes e produtos à temperatura de referência (25 °C).
    ### Perda pela Chaminé:Energia carregada pelos gases quentes.
    Calculada pelo somatório das entalpias sensíveis dos gases de saída           
    ### Calor Útil
    Q útil = Q combustão − Q chaminé
    ### Eficiência Térmica
    Eficiência (%) =
    (Q útil / Q combustão) × 100""")
    st.divider()
    st.markdown("""
    ## 7. Base Seca vs Base Úmida
    ### O que são?
    - **Base Úmida**: Fração molar considerando TODOS os gases, incluindo vapor d'água
    - **Base Seca**: Fração molar EXCLUINDO o vapor d'água
    ### Por que usar ambas?
    - **Normas Ambientais**: Muitas legislações usam base seca
    - **Comparação**: Dados da literatura frequentemente em base seca
    - **Equipamentos**: Alguns analisadores medem em base seca""")
# ABA 3 - BANCO DE DADOS
with tab3:
    st.header("Banco de Dados")
    st.subheader("Combustíveis")
    df_comb = pd.DataFrame(COMBUSTIVEIS).T
    st.dataframe(df_comb, use_container_width=True)
    st.subheader("Gases e Produtos")
    df_gases = pd.DataFrame(GASES_PRODUTOS).T
    st.dataframe(df_gases, use_container_width=True)

