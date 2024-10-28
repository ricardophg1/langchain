# src/analytics/metrics.py

def get_key_metrics(empresa, periodo, area=None):
    # Simulação de dados de métricas principais
    metrics = {
        "receita": 1000000,
        "receita_delta": 0.05,
        "margem": 0.25,
        "margem_delta": 0.02,
        "market_share": 0.15,
        "market_share_delta": 0.01,
        "nps": 70,
        "nps_delta": 5,
        "data": {
            "performance": [
                {"date": "2023-01-01", "value": 100},
                {"date": "2023-02-01", "value": 110},
                {"date": "2023-03-01", "value": 105},
            ],
            "comparison": [
                {"date": "2023-01-01", "value": 100, "competitor": 90},
                {"date": "2023-02-01", "value": 110, "competitor": 95},
                {"date": "2023-03-01", "value": 105, "competitor": 100},
            ],
            "receita_var": 0.12,  # Exemplo de variação de receita
            "margem_var": 0.06,   # Exemplo de variação de margem
        }
    }
    
    # Ajustar métricas com base na área, se fornecida
    if area:
        if area == "Financeiro":
            metrics["receita"] *= 1.1
            metrics["margem"] *= 1.05
        elif area == "Comercial":
            metrics["market_share"] *= 1.2
        elif area == "Operacional":
            metrics["nps"] *= 1.1
    
    return metrics