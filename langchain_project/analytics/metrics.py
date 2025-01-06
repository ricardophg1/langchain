import pandas as pd
import random

def get_key_metrics(empresa: str, periodo: str) -> dict:
    """Obtém métricas principais para o dashboard
    
    Args:
        empresa (str): Nome da empresa
        periodo (str): Período de análise
        
    Returns:
        dict: Dicionário com métricas e dados
    """
    # Simulando dados
    receita = random.uniform(1000000, 5000000)
    receita_delta = f"{random.uniform(-10, 20):.1f}%"
    
    margem = random.uniform(20, 40)
    margem_delta = f"{random.uniform(-5, 10):.1f}%"
    
    market_share = random.uniform(10, 30)
    market_share_delta = f"{random.uniform(-3, 8):.1f}%"
    
    nps = random.uniform(30, 90)
    nps_delta = f"{random.uniform(-5, 10):.1f}"
    
    # Gerando dados históricos
    dates = pd.date_range(start='2023-01-01', periods=12, freq='M')
    data = pd.DataFrame({
        'Data': dates,
        'Receita': [random.uniform(800000, 1200000) for _ in range(12)],
        'Despesas': [random.uniform(600000, 900000) for _ in range(12)],
        'Margem': [random.uniform(15, 45) for _ in range(12)],
        'Market_Share': [random.uniform(8, 32) for _ in range(12)],
        'NPS': [random.uniform(25, 95) for _ in range(12)]
    })
    
    return {
        'receita': f"R$ {receita:,.2f}",
        'receita_delta': receita_delta,
        'margem': f"{margem:.1f}%",
        'margem_delta': margem_delta,
        'market_share': f"{market_share:.1f}%",
        'market_share_delta': market_share_delta,
        'nps': f"{nps:.1f}",
        'nps_delta': nps_delta,
        'data': data
    }
