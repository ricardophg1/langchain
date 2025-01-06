import pandas as pd
import random
from datetime import datetime, timedelta

def formatar_moeda(valor):
    """Formata valor em moeda (R$)"""
    return f"R$ {valor:,.2f}"

def gerar_dados_aleatorios(empresa, periodo, meses=12):
    """Gera dados financeiros aleatórios para vários meses
    
    Args:
        empresa (str): Nome da empresa
        periodo (str): Período de análise
        meses (int): Número de meses para gerar dados
        
    Returns:
        pd.DataFrame: DataFrame com dados financeiros
    """
    # Data inicial
    data_inicial = datetime.now() - timedelta(days=meses*30)
    datas = [data_inicial + timedelta(days=i*30) for i in range(meses)]
    
    # Gerar dados aleatórios com tendência crescente
    base_receita = random.uniform(800000, 1200000)
    base_despesas = base_receita * random.uniform(0.6, 0.8)
    
    dados = []
    for i in range(meses):
        # Adicionar variação e tendência
        fator_crescimento = 1 + (i * 0.02)  # 2% de crescimento ao mês
        variacao = random.uniform(-0.1, 0.1)  # ±10% de variação
        
        receita = base_receita * fator_crescimento * (1 + variacao)
        despesas = base_despesas * fator_crescimento * (1 + variacao * 0.8)
        lucro = receita - despesas
        margem = (lucro / receita) * 100
        
        dados.append({
            'Data': datas[i],
            'Mês': datas[i].strftime('%b/%Y'),
            'Empresa': empresa,
            'Receita': receita,
            'Despesas': despesas,
            'Lucro': lucro,
            'Margem': margem,
            'ROI': (lucro / despesas) * 100,
            'Market_Share': random.uniform(10, 30),
            'NPS': random.uniform(30, 90)
        })
    
    return pd.DataFrame(dados)

def dados_financeiros(empresa=None, periodo=None):
    """Retorna dados financeiros para análise
    
    Args:
        empresa (str, optional): Nome da empresa. Se None, usa primeira empresa.
        periodo (str, optional): Período de análise. Se None, usa último ano.
        
    Returns:
        pd.DataFrame: DataFrame com dados financeiros
    """
    if empresa is None:
        empresa = "ACME Corp"
    if periodo is None:
        periodo = "Último Ano"
        
    # Definir número de meses baseado no período
    if periodo == "Último Mês":
        meses = 1
    elif periodo == "Último Trimestre":
        meses = 3
    else:  # Último Ano
        meses = 12
        
    return gerar_dados_aleatorios(empresa, periodo, meses)

def calcular_metricas(df):
    """Calcula métricas financeiras principais
    
    Args:
        df (pd.DataFrame): DataFrame com dados financeiros
        
    Returns:
        dict: Dicionário com métricas calculadas
    """
    # Últimos valores
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2] if len(df) > 1 else ultimo
    
    # Calcular variações
    var_receita = ((ultimo['Receita'] / penultimo['Receita']) - 1) * 100
    var_despesas = ((ultimo['Despesas'] / penultimo['Despesas']) - 1) * 100
    var_margem = ultimo['Margem'] - penultimo['Margem']
    var_roi = ultimo['ROI'] - penultimo['ROI']
    
    return {
        'receita': formatar_moeda(ultimo['Receita']),
        'receita_delta': f"{var_receita:+.1f}%",
        'despesas': formatar_moeda(ultimo['Despesas']),
        'despesas_delta': f"{var_despesas:+.1f}%",
        'margem': f"{ultimo['Margem']:.1f}%",
        'margem_delta': f"{var_margem:+.1f}%",
        'roi': f"{ultimo['ROI']:.1f}%",
        'roi_delta': f"{var_roi:+.1f}%"
    }
