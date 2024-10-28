import streamlit as st
from src.models.openai_model import get_response
from src.components.chat import create_chat_interface
import pandas as pd
import random

def gerar_dados_operacionais(empresa, periodo, meses=12):
    """Gera dados operacionais aleatórios"""
    dados = []
    for mes in range(1, meses + 1):
        dados.append({
            'Empresa': empresa,
            'Período': periodo,
            'Mês': f'Mês {mes}',
            'Eficiência_Produtiva': round(random.uniform(75, 98), 2),
            'Tempo_Setup': round(random.uniform(20, 120), 2),
            'Taxa_Defeitos': round(random.uniform(0.1, 5), 2),
            'Disponibilidade': round(random.uniform(85, 99), 2),
            'Manutenção_Preventiva': round(random.uniform(80, 95), 2),
            'Lead_Time': round(random.uniform(1, 10), 2)
        })
    return pd.DataFrame(dados)

def exibir_dados_operacionais(df, metrica):
    """Exibe análise detalhada dos dados operacionais"""
    st.subheader("📊 Indicadores Operacionais")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    
    metricas_map = {
        "Eficiência Produtiva": {
            'principal': ('Eficiência_Produtiva', '%'),
            'secundarias': [('Taxa_Defeitos', '%'), ('Disponibilidade', '%')]
        },
        "Gestão de Estoque": {
            'principal': ('Lead_Time', 'dias'),
            'secundarias': [('Disponibilidade', '%'), ('Eficiência_Produtiva', '%')]
        },
        "Qualidade": {
            'principal': ('Taxa_Defeitos', '%'),
            'secundarias': [('Eficiência_Produtiva', '%'), ('Manutenção_Preventiva', '%')]
        },
        "Manutenção": {
            'principal': ('Manutenção_Preventiva', '%'),
            'secundarias': [('Disponibilidade', '%'), ('Tempo_Setup', 'min')]
        },
        "Logística": {
            'principal': ('Lead_Time', 'dias'),
            'secundarias': [('Eficiência_Produtiva', '%'), ('Disponibilidade', '%')]
        }
    }

    metricas = metricas_map.get(metrica)
    if metricas:
        with col1:
            principal = metricas['principal']
            st.metric(
                f"{metrica}",
                f"{df[principal[0]].mean():.2f} {principal[1]}",
                f"{df[principal[0]].std():.2f} {principal[1]}"
            )
        with col2:
            sec1 = metricas['secundarias'][0]
            st.metric(
                f"{sec1[0].replace('_', ' ')}",
                f"{df[sec1[0]].mean():.2f} {sec1[1]}",
                f"{df[sec1[0]].std():.2f} {sec1[1]}"
            )
        with col3:
            sec2 = metricas['secundarias'][1]
            st.metric(
                f"{sec2[0].replace('_', ' ')}",
                f"{df[sec2[0]].mean():.2f} {sec2[1]}",
                f"{df[sec2[0]].std():.2f} {sec2[1]}"
            )

    # Dados em formato tabular
    st.subheader("📈 Dados Detalhados")
    st.dataframe(
        df,
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
            file_name=f"dados_operacionais.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        if st.button("📊 Gerar Gráficos", use_container_width=True):
            st.info("Funcionalidade de gráficos em desenvolvimento.")

def operacional_page():
    st.set_page_config(layout="wide", page_title="Análise Operacional")
    
    # Configurações
    EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
    TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
    ANOS = [2024, 2023, 2022, 2021]
    IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
    METRICAS = [
        "Eficiência Produtiva",
        "Gestão de Estoque",
        "Qualidade",
        "Manutenção",
        "Logística"
    ]
    
    # Layout principal
    main_col, chat_col = st.columns([4, 1])
    
    with main_col:
        st.title("Análise Operacional ⚙️")
        
        # Container principal
        with st.container():
            # Seleção de métrica em destaque
            metrica = st.selectbox(
                "Tipo de Análise Operacional:",
                METRICAS,
                key="metrica_operacional"
            )
            
            # Grid de seleção
            col1, col2, col3 = st.columns(3)
            with col1:
                empresa = st.selectbox(
                    'Empresa:',
                    EMPRESAS,
                    key="empresa_operacional"
                )
            with col2:
                trimestre = st.selectbox(
                    'Trimestre:',
                    TRIMESTRES,
                    key="trimestre_operacional"
                )
            with col3:
                ano = st.selectbox(
                    'Ano:',
                    ANOS,
                    key="ano_operacional"
                )
            
            idioma = st.selectbox(
                'Idioma:',
                IDIOMAS,
                key="idioma_operacional"
            )
            
            # Botões de ação
            col1, col2 = st.columns(2)
            with col1:
                gerar_relatorio = st.button(
                    '📝 Gerar Relatório',
                    key="gerar_relatorio_operacional",
                    use_container_width=True
                )
            with col2:
                visualizar_dados = st.button(
                    '📊 Visualizar Dados',
                    key="visualizar_dados_operacional",
                    use_container_width=True
                )
            
            # Geração de dados e relatório
            if visualizar_dados:
                with st.spinner('Carregando dados operacionais...'):
                    periodo = f"{trimestre} {ano}"
                    df = gerar_dados_operacionais(empresa, periodo)
                    exibir_dados_operacionais(df, metrica)
            
            if gerar_relatorio:
                with st.spinner('Gerando relatório operacional...'):
                    periodo = f"{trimestre} {ano}"
                    df = gerar_dados_operacionais(empresa, periodo, meses=1)
                    
                    prompt = f"""
                    Você é um analista operacional experiente.
                    Elabore uma análise operacional detalhada sobre {metrica} para a empresa {empresa} 
                    no período {periodo}.
                    O relatório deve ser escrito em {idioma}.
                    
                    Dados operacionais:
                    {df.to_string()}
                    
                    Inclua:
                    1. Resumo executivo
                    2. Análise dos indicadores operacionais
                    3. Pontos de atenção e oportunidades
                    4. Recomendações técnicas
                    5. Plano de ação sugerido
                    """
                    
                    response = get_response(prompt)
                    
                    if response:
                        st.markdown("### 📝 Relatório de Análise Operacional")
                        st.markdown(response)
                        
                        # Botões de ação para o relatório
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📥 Download do Relatório",
                                response,
                                file_name=f"analise_operacional_{empresa}_{periodo}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                        with col2:
                            if st.button("📋 Copiar", key="copiar_relatorio", use_container_width=True):
                                st.toast("Relatório copiado!")
    
    # Chat na coluna lateral
    with chat_col:
        create_chat_interface(context_type="operacional")

if __name__ == "__main__":
    operacional_page()