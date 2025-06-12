import streamlit as st
from langchain_project.models.openai_model import get_response
from langchain_project.components.chat import create_chat_interface
from langchain_project.components.email_button import create_email_button
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

def gerar_dados_operacionais(empresa, periodo, meses=12):
    """Gera dados operacionais aleatórios
    
    Args:
        empresa (str): Nome da empresa
        periodo (str): Período de análise
        meses (int): Número de meses para gerar dados
        
    Returns:
        pd.DataFrame: DataFrame com dados operacionais
    """
    data_inicial = datetime.now() - timedelta(days=meses*30)
    datas = [data_inicial + timedelta(days=i*30) for i in range(meses)]
    
    dados = []
    for i in range(meses):
        # Adicionar tendência e variação
        fator_tempo = 1 + (i * 0.01)  # 1% de melhoria ao mês
        variacao = random.uniform(-0.1, 0.1)  # ±10% de variação
        
        # Métricas base
        producao_base = random.uniform(8000, 12000)
        eficiencia_base = random.uniform(75, 95)
        qualidade_base = random.uniform(95, 99)
        manutencao_base = random.uniform(85, 95)
        
        dados.append({
            'Data': datas[i],
            'Mês': datas[i].strftime('%b/%Y'),
            'Empresa': empresa,
            'Produção': producao_base * fator_tempo * (1 + variacao),
            'Eficiência': eficiencia_base * fator_tempo * (1 + variacao * 0.5),
            'Qualidade': qualidade_base * fator_tempo * (1 + variacao * 0.3),
            'Manutenção': manutencao_base * fator_tempo * (1 + variacao * 0.4),
            'Paradas': random.randint(2, 8),
            'Retrabalho': random.uniform(1, 5),
            'Produtividade': random.uniform(80, 98)
        })
    
    return pd.DataFrame(dados)

def calcular_metricas_operacionais(df):
    """Calcula métricas operacionais principais
    
    Args:
        df (pd.DataFrame): DataFrame com dados operacionais
        
    Returns:
        dict: Dicionário com métricas calculadas
    """
    # Últimos valores
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2] if len(df) > 1 else ultimo
    
    # Calcular variações
    var_producao = ((ultimo['Produção'] / penultimo['Produção']) - 1) * 100
    var_eficiencia = ultimo['Eficiência'] - penultimo['Eficiência']
    var_qualidade = ultimo['Qualidade'] - penultimo['Qualidade']
    var_manutencao = ultimo['Manutenção'] - penultimo['Manutenção']
    
    return {
        'producao': f"{ultimo['Produção']:,.0f}",
        'producao_delta': f"{var_producao:+.1f}%",
        'eficiencia': f"{ultimo['Eficiência']:.1f}%",
        'eficiencia_delta': f"{var_eficiencia:+.1f}%",
        'qualidade': f"{ultimo['Qualidade']:.1f}%",
        'qualidade_delta': f"{var_qualidade:+.1f}%",
        'manutencao': f"{ultimo['Manutenção']:.1f}%",
        'manutencao_delta': f"{var_manutencao:+.1f}%"
    }

def operacional_page():
    """Página de análise operacional"""
    st.title("⚙️ Análise Operacional")
    
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
            ["Produção", "Eficiência", "Qualidade", "Manutenção"]
        )
    
    # Dados operacionais
    meses = 12 if periodo == "Último Ano" else (3 if periodo == "Último Trimestre" else 1)
    df = gerar_dados_operacionais(empresa, periodo, meses)
    metricas = calcular_metricas_operacionais(df)
    
    # KPIs
    st.markdown("### 📊 Métricas Principais")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            "Produção",
            metricas['producao'],
            metricas['producao_delta'],
            help="Produção total no período"
        )
    with m2:
        st.metric(
            "Eficiência",
            metricas['eficiencia'],
            metricas['eficiencia_delta'],
            help="Eficiência operacional"
        )
    with m3:
        st.metric(
            "Qualidade",
            metricas['qualidade'],
            metricas['qualidade_delta'],
            help="Índice de qualidade"
        )
    with m4:
        st.metric(
            "Manutenção",
            metricas['manutencao'],
            metricas['manutencao_delta'],
            help="Disponibilidade de equipamentos"
        )
    
    # Gráficos
    st.markdown("### 📈 Análises")
    
    # Gráfico de linha para evolução temporal
    fig_evolucao = px.line(
        df,
        x='Data',
        y=['Produção', 'Produtividade'],
        title='Evolução da Produção e Produtividade'
    )
    fig_evolucao.update_layout(
        xaxis_title='Período',
        yaxis_title='Valor',
        template='plotly_white'
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Duas colunas para os outros gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras para eficiência e qualidade
        fig_eficiencia = px.bar(
            df,
            x='Data',
            y=['Eficiência', 'Qualidade'],
            title='Eficiência vs Qualidade',
            barmode='group'
        )
        fig_eficiencia.update_layout(
            xaxis_title='Período',
            yaxis_title='Percentual (%)',
            template='plotly_white'
        )
        st.plotly_chart(fig_eficiencia, use_container_width=True)
    
    with col2:
        # Gráfico de dispersão para análise de correlação
        fig_correlacao = px.scatter(
            df,
            x='Produtividade',
            y='Qualidade',
            title='Correlação Produtividade vs Qualidade',
            trendline="ols",
            trendline_color_override="#2ecc71"
        )
        fig_correlacao.update_layout(
            xaxis_title='Produtividade (%)',
            yaxis_title='Qualidade (%)',
            template='plotly_white',
            showlegend=True
        )
        st.plotly_chart(fig_correlacao, use_container_width=True)
    
    # Alertas
    with st.expander("⚠️ Alertas", expanded=True):
        if float(metricas['eficiencia'].strip('%')) < 85:
            st.warning(f"Eficiência abaixo da meta (85%): {metricas['eficiencia']}")
        if float(metricas['qualidade'].strip('%')) < 98:
            st.warning(f"Qualidade abaixo da meta (98%): {metricas['qualidade']}")
        if float(metricas['manutencao'].strip('%')) < 90:
            st.warning(f"Disponibilidade de equipamentos abaixo da meta (90%): {metricas['manutencao']}")
        if all([
            float(metricas['eficiencia'].strip('%')) >= 85,
            float(metricas['qualidade'].strip('%')) >= 98,
            float(metricas['manutencao'].strip('%')) >= 90
        ]):
            st.success("✅ Todos os indicadores estão dentro das metas!")
    
    # Chat e Email
    st.markdown("---")
    st.markdown("### 💬 Assistente Operacional")
    
    # Interface de chat
    response = create_chat_interface("operacional")
    
    # Se houver resposta, mostrar botão de email
    if response:
        params = {
            'empresa': empresa,
            'periodo': periodo,
            'tipo_analise': tipo_analise
        }
        create_email_button(response, params)

if __name__ == "__main__":
    operacional_page()
