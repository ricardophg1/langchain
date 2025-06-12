import streamlit as st
from langchain_project.models.openai_model import get_response
from langchain_project.components.chat import create_chat_interface
from langchain_project.components.email_button import create_email_button
from langchain_project.utils.financial_data import dados_financeiros, calcular_metricas
import plotly.express as px
import pandas as pd

def financeiro_page():
    """Página de análise financeira"""
    st.title("💰 Análise Financeira")
    
    # Filtros em uma linha
    col1, col2, col3 = st.columns(3)
    with col1:
        empresa = st.selectbox(
            "Empresa",
            ["ACME Corp", "Globex Corporation", "Soylent Corp", "Initech", "Umbrella Corporation"]
        )
    with col2:
        periodo = st.selectbox(
            "Período",
            ["Último Mês", "Último Trimestre", "Último Ano"]
        )
    with col3:
        tipo_analise = st.selectbox(
            "Tipo de Análise",
            ["Receita", "Custos", "Margem", "Fluxo de Caixa"]
        )
    
    # Dados financeiros
    df = dados_financeiros(empresa, periodo)
    metricas = calcular_metricas(df)
    
    # KPIs
    st.markdown("### 📊 Métricas Principais")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            "Receita Total",
            metricas['receita'],
            metricas['receita_delta'],
            help="Receita total no período"
        )
    with m2:
        st.metric(
            "Custos",
            metricas['despesas'],
            metricas['despesas_delta'],
            help="Total de custos no período"
        )
    with m3:
        st.metric(
            "Margem",
            metricas['margem'],
            metricas['margem_delta'],
            help="Margem de lucro"
        )
    with m4:
        st.metric(
            "ROI",
            metricas['roi'],
            metricas['roi_delta'],
            help="Retorno sobre investimento"
        )
    
    # Gráficos
    st.markdown("### 📈 Análises")
    
    # Gráfico de linha para evolução temporal
    fig_evolucao = px.line(
        df,
        x='Data',
        y=['Receita', 'Despesas', 'Lucro'],
        title='Evolução Financeira'
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Duas colunas para os outros gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras para comparação
        fig_comparativo = px.bar(
            df,
            x='Data',
            y=['Receita', 'Despesas'],
            title='Comparativo Receita vs Despesas',
            barmode='group'
        )
        st.plotly_chart(fig_comparativo, use_container_width=True)
    
    with col2:
        # Gráfico de dispersão para análise de correlação
        fig_correlacao = px.scatter(
            df,
            x='Receita',
            y='Lucro',
            title='Correlação Receita vs Lucro',
            trendline="ols",
            trendline_color_override="#2ecc71"
        )
        fig_correlacao.update_layout(
            xaxis_title='Receita (R$)',
            yaxis_title='Lucro (R$)',
            template='plotly_white',
            showlegend=True
        )
        st.plotly_chart(fig_correlacao, use_container_width=True)
    
    # Alertas
    with st.expander("⚠️ Alertas", expanded=True):
        if float(metricas['despesas_delta'].strip('%+')) > 5:
            st.warning(f"Custos operacionais aumentaram {metricas['despesas_delta']} no último período")
        if float(metricas['margem'].strip('%')) < 30:
            st.info(f"Oportunidade: Margem atual de {metricas['margem']} pode ser melhorada")
    
    # Chat e Email - fora das colunas
    st.markdown("---")
    st.markdown("### 💬 Assistente Financeiro")
    
    # Interface de chat
    response = create_chat_interface("financeiro")
    
    # Se houver resposta, mostrar botão de email
    if response:
        params = {
            'empresa': empresa,
            'periodo': periodo,
            'tipo_analise': tipo_analise
        }
        create_email_button(response, params)

if __name__ == "__main__":
    financeiro_page()
