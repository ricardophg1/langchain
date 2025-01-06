import streamlit as st
from langchain_project.models.openai_model import get_response
from langchain_project.components.chat import create_chat_interface
from langchain_project.components.email_button import create_email_button
import pandas as pd
import random
from dotenv import load_dotenv
import os
import plotly.express as px
import plotly.graph_objects as go

def gerar_graficos_comerciais(df, metrica):
    """Gera gráficos comerciais baseados na métrica selecionada"""
    st.subheader("📈 Análise Gráfica")
    
    # Gráfico 1: Evolução temporal
    fig1 = px.line(df, x='Mês', y='Vendas_Total', 
                   title='Evolução das Vendas Totais',
                   labels={'Vendas_Total': 'Vendas Totais (R$)', 'Mês': 'Período'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Comparação de canais
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Vendas Online', x=df['Mês'], y=df['Vendas_Online']))
    fig2.add_trace(go.Bar(name='Vendas Físicas', x=df['Mês'], y=df['Vendas_Fisicas']))
    fig2.update_layout(barmode='group', title='Comparação de Canais de Venda',
                      yaxis_title='Vendas (R$)', xaxis_title='Período')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico 3: Específico para cada tipo de análise
    if metrica == "Vendas por Canal":
        # Gráfico de pizza com distribuição de vendas
        total_vendas = df['Vendas_Total'].sum()
        total_online = df['Vendas_Online'].sum()
        total_fisico = df['Vendas_Fisicas'].sum()
        
        fig3 = px.pie(values=[total_online, total_fisico],
                     names=['Vendas Online', 'Vendas Físicas'],
                     title='Distribuição de Vendas por Canal')
        st.plotly_chart(fig3, use_container_width=True)
        
    elif metrica == "Performance de Produtos":
        # Gráfico de linha com ticket médio e taxa de conversão
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df['Mês'], y=df['Ticket_Medio'],
                                name='Ticket Médio', yaxis='y'))
        fig3.add_trace(go.Scatter(x=df['Mês'], y=df['Taxa_Conversao'],
                                name='Taxa de Conversão', yaxis='y2'))
        fig3.update_layout(
            title='Performance de Vendas',
            yaxis=dict(title='Ticket Médio (R$)'),
            yaxis2=dict(title='Taxa de Conversão (%)', overlaying='y', side='right')
        )
        st.plotly_chart(fig3, use_container_width=True)
        
    elif metrica == "Análise de Clientes":
        # Gráfico de barras com novos clientes e linha com NPS
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df['Mês'], y=df['Novos_Clientes'],
                            name='Novos Clientes'))
        fig3.add_trace(go.Scatter(x=df['Mês'], y=df['NPS'],
                                name='NPS', yaxis='y2'))
        fig3.update_layout(
            title='Aquisição de Clientes e Satisfação',
            yaxis=dict(title='Novos Clientes'),
            yaxis2=dict(title='NPS', overlaying='y', side='right')
        )
        st.plotly_chart(fig3, use_container_width=True)
        
    elif metrica == "Eficiência da Força de Vendas":
        # Gráfico de dispersão entre taxa de conversão e ticket médio
        fig3 = px.scatter(df, x='Taxa_Conversao', y='Ticket_Medio',
                         size='Vendas_Total', title='Eficiência de Vendas',
                         labels={'Taxa_Conversao': 'Taxa de Conversão (%)',
                                'Ticket_Medio': 'Ticket Médio (R$)'})
        st.plotly_chart(fig3, use_container_width=True)
        
    elif metrica == "Market Share":
        # Gráfico de área para vendas totais
        fig3 = px.area(df, x='Mês', y='Vendas_Total',
                      title='Evolução do Market Share',
                      labels={'Vendas_Total': 'Vendas Totais (R$)',
                             'Mês': 'Período'})
        st.plotly_chart(fig3, use_container_width=True)

def gerar_dados_comerciais(empresa, periodo, meses=12):
    """Gera dados comerciais aleatórios"""
    dados = []
    for mes in range(1, meses + 1):
        dados.append({
            'Empresa': empresa,
            'Período': periodo,
            'Mês': f'Mês {mes}',
            'Vendas_Total': round(random.uniform(800000, 3000000), 2),
            'Vendas_Online': round(random.uniform(200000, 1000000), 2),
            'Vendas_Fisicas': round(random.uniform(400000, 1500000), 2),
            'Novos_Clientes': round(random.uniform(50, 300)),
            'Taxa_Conversao': round(random.uniform(2, 15), 2),
            'NPS': round(random.uniform(30, 90), 1),
            'Ticket_Medio': round(random.uniform(100, 1000), 2)
        })
    return pd.DataFrame(dados)

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}"

def exibir_dados_comerciais(df, metrica):
    """Exibe análise detalhada dos dados comerciais"""
    # Armazenar DataFrame na sessão
    st.session_state.df_comercial = df
    st.session_state.metrica_comercial_atual = metrica
    
    st.subheader("📊 Indicadores Comerciais")
    
    # Métricas principais baseadas no tipo de análise
    metricas_map = {
        "Vendas por Canal": {
            'metricas': [
                ('Vendas_Total', 'Vendas Totais', 'R$'),
                ('Vendas_Online', 'Vendas Online', 'R$'),
                ('Vendas_Fisicas', 'Vendas Físicas', 'R$')
            ]
        },
        "Performance de Produtos": {
            'metricas': [
                ('Ticket_Medio', 'Ticket Médio', 'R$'),
                ('Taxa_Conversao', 'Taxa de Conversão', '%'),
                ('Vendas_Total', 'Vendas Totais', 'R$')
            ]
        },
        "Análise de Clientes": {
            'metricas': [
                ('Novos_Clientes', 'Novos Clientes', ''),
                ('NPS', 'NPS', ''),
                ('Ticket_Medio', 'Ticket Médio', 'R$')
            ]
        },
        "Eficiência da Força de Vendas": {
            'metricas': [
                ('Taxa_Conversao', 'Taxa de Conversão', '%'),
                ('Vendas_Total', 'Vendas por Vendedor', 'R$'),
                ('Ticket_Medio', 'Ticket Médio', 'R$')
            ]
        },
        "Market Share": {
            'metricas': [
                ('Vendas_Total', 'Vendas Totais', 'R$'),
                ('Taxa_Conversao', 'Market Share', '%'),
                ('Novos_Clientes', 'Novos Clientes', '')
            ]
        }
    }

    # Exibir métricas específicas
    if metrica in metricas_map:
        col1, col2, col3 = st.columns(3)
        metricas = metricas_map[metrica]['metricas']
        
        columns = [col1, col2, col3]
        for i, (coluna, label, unidade) in enumerate(metricas):
            with columns[i]:
                valor = df[coluna].mean()
                delta = df[coluna].std()
                
                if unidade == 'R$':
                    valor_formatado = formatar_moeda(valor)
                    delta_formatado = formatar_moeda(delta)
                else:
                    valor_formatado = f"{valor:.2f}{unidade}"
                    delta_formatado = f"{delta:.2f}{unidade}"
                
                st.metric(
                    label,
                    valor_formatado,
                    delta_formatado
                )

    # Dados em formato tabular
    st.subheader("📈 Dados Detalhados")
    
    # Formatando valores monetários
    df_display = df.copy()
    colunas_monetarias = ['Vendas_Total', 'Vendas_Online', 'Vendas_Fisicas', 'Ticket_Medio']
    for col in colunas_monetarias:
        df_display[col] = df_display[col].apply(formatar_moeda)
    
    # Formatando percentuais
    df_display['Taxa_Conversao'] = df_display['Taxa_Conversao'].apply(lambda x: f"{x:.2f}%")
    df_display['NPS'] = df_display['NPS'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

    # Botões de ação
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download dos Dados (CSV)",
            data=csv,
            file_name=f"dados_comerciais_{metrica.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        if st.button("📊 Gerar Gráficos", use_container_width=True):
            if 'df_comercial' in st.session_state and 'metrica_comercial_atual' in st.session_state:
                gerar_graficos_comerciais(st.session_state.df_comercial, st.session_state.metrica_comercial_atual)
            else:
                st.warning("Por favor, visualize os dados primeiro antes de gerar os gráficos.")

def comercial_page():
    """Página de análise comercial"""
    st.title("Análise Comercial 🏢")
    
    # Garantir que a chave da API esteja carregada
    if 'openai_api_key' not in st.session_state:
        load_dotenv()
        st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not st.session_state.openai_api_key:
            st.error("⚠️ Chave da API OpenAI não encontrada!")
            st.info("Por favor, configure sua chave API no arquivo .env")
            st.stop()

    # Configurações
    EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
    TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
    ANOS = [2024, 2023, 2022, 2021]
    IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
    METRICAS = [
        "Vendas por Canal",
        "Performance de Produtos",
        "Análise de Clientes",
        "Eficiência da Força de Vendas",
        "Market Share"
    ]
    
    # Layout principal
    main_col, chat_col = st.columns([4, 1])
    
    with main_col:
        # Container principal
        with st.container():
            # Seleção de métrica em destaque
            metrica = st.selectbox(
                "Tipo de Análise Comercial:",
                METRICAS,
                key="metrica_comercial"
            )
            
            # Grid de seleção
            col1, col2, col3 = st.columns(3)
            with col1:
                empresa = st.selectbox(
                    'Empresa:',
                    EMPRESAS,
                    key="empresa_comercial"
                )
            with col2:
                trimestre = st.selectbox(
                    'Trimestre:',
                    TRIMESTRES,
                    key="trimestre_comercial"
                )
            with col3:
                ano = st.selectbox(
                    'Ano:',
                    ANOS,
                    key="ano_comercial"
                )
            
            idioma = st.selectbox(
                'Idioma:',
                IDIOMAS,
                key="idioma_comercial"
            )
            
            # Botões de ação
            col1, col2 = st.columns(2)
            with col1:
                gerar_relatorio = st.button(
                    '📝 Gerar Relatório',
                    key="gerar_relatorio_comercial",
                    use_container_width=True
                )
            with col2:
                visualizar_dados = st.button(
                    '📊 Visualizar Dados',
                    key="visualizar_dados_comercial",
                    use_container_width=True
                )
            
            # Geração de dados e relatório
            if visualizar_dados:
                with st.spinner('Carregando dados comerciais...'):
                    periodo = f"{trimestre} {ano}"
                    df = gerar_dados_comerciais(empresa, periodo)
                    exibir_dados_comerciais(df, metrica)
            
            if gerar_relatorio:
                with st.spinner('Gerando relatório comercial...'):
                    periodo = f"{trimestre} {ano}"
                    df = gerar_dados_comerciais(empresa, periodo, meses=1)
                    
                    prompt = f"""
                    Você é um analista comercial experiente.
                    Elabore uma análise comercial detalhada sobre {metrica} para a empresa {empresa} 
                    no período {periodo}.
                    O relatório deve ser escrito em {idioma}.
                    
                    Dados comerciais:
                    {df.to_string()}
                    
                    Inclua:
                    1. Resumo executivo
                    2. Análise detalhada dos indicadores comerciais
                    3. Comparação com mercado e benchmarks
                    4. Recomendações estratégicas
                    5. Plano de ação comercial
                    """
                    
                    response = get_response(prompt)
                    
                    if response:
                        # Container para o relatório
                        report_container = st.container()
                        
                        with report_container:
                            st.markdown("### 📝 Relatório de Análise Comercial")
                            st.markdown(response)
                            
                            # Parâmetros completos para o email
                            params = {
                                'empresa': empresa,
                                'periodo': periodo,
                                'idioma': idioma,
                                'analise': metrica,
                                'trimestre': trimestre,
                                'ano': ano
                            }
                            
                            # Container para botões
                            button_container = st.container()
                            with button_container:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="📥 Download do Relatório",
                                        data=response,
                                        file_name=f"relatorio_comercial_{empresa}_{periodo}.md",
                                        mime="text/markdown",
                                        use_container_width=True
                                    )
                                with col2:
                                    create_email_button(response, params)

    # Chat fora de qualquer coluna
    create_chat_interface(context_type="comercial")

if __name__ == "__main__":
    comercial_page()