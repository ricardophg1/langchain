import streamlit as st
from src.models.openai_model import get_response
from src.components.chat import create_chat_interface
import pandas as pd
import random
from src.utils.financial_data import dados_financeiros, gerar_dados_aleatorios, formatar_moeda

def gerar_dados_aleatorios(empresa, periodo, meses=12):
    """Gera dados financeiros aleatórios para vários meses"""
    dados = []
    for mes in range(1, meses + 1):
        dados.append({
            'Empresa': empresa,
            'Período': periodo,
            'Mês': f'Mês {mes}',
            'Receita': round(random.uniform(1000000, 5000000), 2),
            'Custos': round(random.uniform(500000, 2000000), 2),
            'Lucro_Bruto': round(random.uniform(300000, 1500000), 2),
            'Despesas_Operacionais': round(random.uniform(200000, 800000), 2),
            'EBITDA': round(random.uniform(150000, 700000), 2),
            'Lucro_Liquido': round(random.uniform(100000, 500000), 2)
        })
    return pd.DataFrame(dados)

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}"

def exibir_dados_detalhados(df):
    """Exibe análise detalhada dos dados"""
    # Métricas principais
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Receita Total",
            formatar_moeda(df['Receita'].sum()),
            delta=formatar_moeda(df['Receita'].mean())
        )
    with col2:
        st.metric(
            "Lucro Bruto Total",
            formatar_moeda(df['Lucro_Bruto'].sum()),
            delta=formatar_moeda(df['Lucro_Bruto'].mean())
        )
    with col3:
        st.metric(
            "EBITDA Total",
            formatar_moeda(df['EBITDA'].sum()),
            delta=formatar_moeda(df['EBITDA'].mean())
        )
    with col4:
        st.metric(
            "Lucro Líquido Total",
            formatar_moeda(df['Lucro_Liquido'].sum()),
            delta=formatar_moeda(df['Lucro_Liquido'].mean())
        )

    # Dados em formato tabular
    st.subheader("📈 Base de Dados Detalhada")
    
    # Formatando os valores monetários
    df_display = df.copy()
    colunas_monetarias = ['Receita', 'Custos', 'Lucro_Bruto', 'Despesas_Operacionais', 'EBITDA', 'Lucro_Liquido']
    for col in colunas_monetarias:
        df_display[col] = df_display[col].apply(formatar_moeda)
    
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
            file_name="dados_financeiros.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        if st.button("📊 Gerar Gráficos", use_container_width=True):
            st.info("Funcionalidade de gráficos em desenvolvimento.")

def gerar_analise(tipo_analise, empresas, trimestres, anos, idiomas):
    """Função auxiliar para gerar interface de análise"""
    with st.container():
        st.subheader(f"📋 {tipo_analise}")
        
        # Grid de seleção
        col1, col2, col3 = st.columns(3)
        
        with col1:
            empresa = st.selectbox(
                'Empresa:',
                empresas,
                key=f"{tipo_analise}_empresa"
            )
        with col2:
            trimestre = st.selectbox(
                'Trimestre:',
                trimestres,
                key=f"{tipo_analise}_trimestre"
            )
        with col3:
            ano = st.selectbox(
                'Ano:',
                anos,
                key=f"{tipo_analise}_ano"
            )
        
        idioma = st.selectbox(
            'Idioma:',
            idiomas,
            key=f"{tipo_analise}_idioma"
        )

        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            gerar_relatorio = st.button(
                '📝 Gerar Relatório',
                key=f"{tipo_analise}_relatorio",
                use_container_width=True
            )
        with col2:
            visualizar_dados = st.button(
                '📊 Visualizar Base de Dados',
                key=f"{tipo_analise}_dados",
                use_container_width=True
            )

        if visualizar_dados:
            with st.spinner('Gerando base de dados... Aguarde um momento.'):
                df = gerar_dados_aleatorios(empresa, f"{trimestre} {ano}")
                exibir_dados_detalhados(df)

        if gerar_relatorio:
            with st.spinner('Gerando relatório... Aguarde um momento.'):
                # Preparar dados
                dados = ""
                if tipo_analise == "Análise de Dados Financeiros":
                    df = gerar_dados_aleatorios(empresa, f"{trimestre} {ano}", meses=1)
                    dados = df.to_string()

                prompt = f"""
                Você é um analista financeiro experiente.
                Elabore uma análise detalhada de {tipo_analise} para a empresa {empresa} 
                no período {trimestre} {ano}.
                O relatório deve ser escrito em {idioma}.
                
                Dados disponíveis:
                {dados}
                
                Inclua:
                1. Resumo executivo
                2. Análise detalhada
                3. Insights principais
                4. Recomendações
                5. Riscos e oportunidades
                """
                
                response = get_response(prompt)
                
                if response:
                    st.markdown("### 📝 Relatório de Análise")
                    st.markdown(response)
                    
                    # Botões de ação
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download do Relatório",
                            response,
                            file_name=f"{tipo_analise}_{empresa}_{trimestre}_{ano}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    with col2:
                        if st.button("📋 Copiar", key=f"{tipo_analise}_copy", use_container_width=True):
                            st.toast("Relatório copiado!")

def financeiro_page():
    st.set_page_config(layout="wide", page_title="Análise Financeira")
    
    # Configurações
    EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
    TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
    ANOS = [2024, 2023, 2022, 2021]
    IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
    
    # Layout principal
    main_col, chat_col = st.columns([4, 1])
    
    with main_col:
        st.title("Análise Financeira 📊")
        
        # Tabs para diferentes análises
        tabs = st.tabs([
            "📈 Dados Financeiros",
            "📊 Balanço Patrimonial",
            "💰 Fluxo de Caixa",
            "📋 Tendências",
            "💵 Receita e Lucro",
            "🌍 Posição de Mercado"
        ])

        with tabs[0]:
            gerar_analise("Análise de Dados Financeiros", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)
        with tabs[1]:
            gerar_analise("Análise do Balanço Patrimonial", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)
        with tabs[2]:
            gerar_analise("Análise do Fluxo de Caixa", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)
        with tabs[3]:
            gerar_analise("Análise de Tendências", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)
        with tabs[4]:
            gerar_analise("Análise de Receita e Lucro", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)
        with tabs[5]:
            gerar_analise("Análise de Posição de Mercado", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)
    
    with chat_col:
        create_chat_interface(context_type="financeira")

if __name__ == "__main__":
    financeiro_page()