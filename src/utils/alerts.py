# src/utils/alerts.py

def check_alerts(data):
    alerts = []
    thresholds = {
        "receita_var": 0.1,  # Exemplo de limite para variação de receita
        "margem_var": 0.05,  # Exemplo de limite para variação de margem
    }
    
    # Verificar variações de receita
    if "receita_var" in data and abs(data['receita_var']) > thresholds['receita_var']:
        alerts.append({"message": f"Alerta: Variação de receita acima do limite: {data['receita_var']}"})
    
    # Verificar variações de margem
    if "margem_var" in data and abs(data['margem_var']) > thresholds['margem_var']:
        alerts.append({"message": f"Alerta: Variação de margem acima do limite: {data['margem_var']}"})
    
    return alerts