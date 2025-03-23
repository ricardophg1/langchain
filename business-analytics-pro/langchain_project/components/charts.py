import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from langchain_project.utils.financial_data import dados_financeiros

def create_dashboard(data=None, chart_type="performance"):
    """Cria gráficos para o dashboard
    
    Args:
        data (pd.DataFrame): DataFrame com os dados para o gráfico
        chart_type (str): Tipo de gráfico ('performance' ou 'comparison')
    
    Returns:
        plotly.graph_objects.Figure: Figura do gráfico
    """
    if data is None:
        data = dados_financeiros()
    
    if chart_type == "performance":
        # Gráfico de linha para evolução temporal
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['Data'],
            y=data['Receita'],
            name='Receita',
            line=dict(color='#2ecc71', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=data['Data'],
            y=data['Despesas'],
            name='Despesas',
            line=dict(color='#e74c3c', width=2)
        ))
        fig.update_layout(
            title='Evolução Financeira',
            xaxis_title='Período',
            yaxis_title='Valor (R$)',
            template='plotly_white',
            height=400
        )
        return fig
    
    elif chart_type == "comparison":
        # Gráfico de barras para comparação
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['Data'],
            y=data['Market_Share'],
            name='Market Share',
            marker_color='#3498db'
        ))
        fig.add_trace(go.Bar(
            x=data['Data'],
            y=data['NPS'],
            name='NPS',
            marker_color='#9b59b6'
        ))
        fig.update_layout(
            title='Comparativo Market Share vs NPS',
            xaxis_title='Período',
            yaxis_title='Valor',
            template='plotly_white',
            height=400,
            barmode='group'
        )
        return fig
    
    else:
        # Gráfico padrão
        fig = px.line(data, x='Data', y='Receita', title='Evolução da Receita')
        fig.update_layout(
            xaxis_title='Período',
            yaxis_title='Receita (R$)',
            template='plotly_white',
            height=400
        )
        return fig

def create_trend_chart(params):
    """Cria gráfico de tendências"""
    df = dados_financeiros()
    fig = px.line(df, x='Mês', y='Receita', title='Tendência de Receita')
    return fig

def create_comparison_chart(params):
    """Cria gráfico comparativo"""
    df = dados_financeiros()
    fig = px.bar(df, x='Mês', y=['Receita', 'Despesas'],
                 title='Comparativo Receita vs Despesas')
    return fig

def create_detail_chart(params):
    """Cria gráfico detalhado"""
    df = dados_financeiros()
    fig = px.scatter(df, x='Receita', y='Lucro',
                     title='Relação Receita vs Lucro')
    return fig
