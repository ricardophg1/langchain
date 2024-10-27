import streamlit as st
from src.models.openai_model import get_response
import random
import pandas as pd

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

def dados_financeiros(empresa, periodo):
    """Retorna dados financeiros formatados"""
    dados = gerar_dados_aleatorios(empresa, periodo, meses=1).iloc[0]
    return f"""
Dados Financeiros para {empresa} - {periodo}:
- Receita: {formatar_moeda(dados['Receita'])}
- Custos: {formatar_moeda(dados['Custos'])}
- Lucro Bruto: {formatar_moeda(dados['Lucro_Bruto'])}
- Despesas Operacionais: {formatar_moeda(dados['Despesas_Operacionais'])}
- EBITDA: {formatar_moeda(dados['EBITDA'])}
- Lucro Líquido: {formatar_moeda(dados['Lucro_Liquido'])}
"""

def exibir_dados_detalhados(df):
    """Exibe análise detalhada dos dados"""
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Receita Total", formatar_moeda(df['Receita'].sum()))
    with col2:
        st.metric("Lucro Bruto Total", formatar_moeda(df['Lucro_Bruto'].sum()))
    with col3:
        st.metric("EBITDA Total", formatar_moeda(df['EBITDA'].sum()))
    with col4:
        st.metric("Lucro Líquido Total", formatar_moeda(df['Lucro_Liquido'].sum()))

    # Dados em formato tabular
    st.subheader("📊 Base de Dados Detalhada")
    
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

    # Botão para download dos dados
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download da Base de Dados (CSV)",
        data=csv,
        file_name="dados_financeiros.csv",
        mime="text/csv"
    )

def gerar_analise(tipo_analise, empresas, trimestres, anos, idiomas):
    """Função auxiliar para gerar interface de análise"""
    col1, col2 = st.columns(2)
    
    with col1:
        empresa = st.selectbox(
            'Empresa:', empresas, 
            key=f"{tipo_analise}_empresa"
        )
        trimestre = st.selectbox(
            'Trimestre:', trimestres,
            key=f"{tipo_analise}_trimestre"
        )
        idioma = st.selectbox(
            'Idioma:', idiomas,
            key=f"{tipo_analise}_idioma"
        )
    
    with col2:
        ano = st.selectbox(
            'Ano:', anos,
            key=f"{tipo_analise}_ano"
        )

    # Botões de ação
    col1, col2 = st.columns(2)
    with col1:
        gerar_relatorio = st.button('📝 Gerar Relatório', key=f"{tipo_analise}_relatorio")
    with col2:
        visualizar_dados = st.button('📊 Visualizar Base de Dados', key=f"{tipo_analise}_dados")
    
    periodo = f"{trimestre} {ano}"

    # Gerar e exibir dados se solicitado
    if visualizar_dados:
        with st.spinner('Gerando base de dados... Aguarde um momento.'):
            df = gerar_dados_aleatorios(empresa, periodo)
            exibir_dados_detalhados(df)
    
    # Gerar e exibir relatório se solicitado
    if gerar_relatorio:
        with st.spinner('Gerando relatório... Aguarde um momento.'):
            prompt = f"""
            Você é um analista financeiro experiente.
            Escreva um relatório detalhado de {tipo_analise} para a empresa {empresa} no período {periodo}.
            O relatório deve ser escrito em {idioma}.
            
            {dados_financeiros(empresa, periodo) if tipo_analise == "Análise de Dados Financeiros" else ""}
            
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
                
                # Botões de ação para o relatório
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download do Relatório",
                        response,
                        file_name=f"{tipo_analise}_{empresa}_{periodo}.md",
                        mime="text/markdown"
                    )
                with col2:
                    if st.button("📋 Copiar", key=f"{tipo_analise}_copy"):
                        st.toast("Relatório copiado!")

def financeiro_page():
    st.title("Análise Financeira 📊")

    # Configurações
    EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
    TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
    ANOS = [2024, 2023, 2022, 2021]
    IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
    
    # Criar tabs para diferentes tipos de análise
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Dados Financeiros",
        "📊 Balanço Patrimonial",
        "💰 Fluxo de Caixa",
        "📋 Tendências",
        "💵 Receita e Lucro",
        "🌍 Posição de Mercado"
    ])

    with tab1:
        st.subheader("Análise de Dados Financeiros")
        gerar_analise("Análise de Dados Financeiros", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)

    with tab2:
        st.subheader("Análise do Balanço Patrimonial")
        gerar_analise("Análise do Balanço Patrimonial", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)

    with tab3:
        st.subheader("Análise do Fluxo de Caixa")
        gerar_analise("Análise do Fluxo de Caixa", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)

    with tab4:
        st.subheader("Análise de Tendências")
        gerar_analise("Análise de Tendências", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)

    with tab5:
        st.subheader("Análise de Receita e Lucro")
        gerar_analise("Análise de Receita e Lucro", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)

    with tab6:
        st.subheader("Análise de Posição de Mercado")
        gerar_analise("Análise de Posição de Mercado", EMPRESAS, TRIMESTRES, ANOS, IDIOMAS)

if __name__ == "__main__":
    financeiro_page()