import streamlit as st
from src.models.openai_model import get_response
from src.components.chat import create_chat_interface
from src.components.email_button import create_email_button
import pandas as pd
import random

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
            st.info("Funcionalidade de gráficos em desenvolvimento.")

def comercial_page():
    st.set_page_config(layout="wide", page_title="Análise Comercial")
    
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
        st.title("Análise Comercial 🏢")
        
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

            # Chat na coluna lateral (fora do if gerar_relatorio)
            with chat_col:
                create_chat_interface(context_type="comercial")

if __name__ == "__main__":
    comercial_page()