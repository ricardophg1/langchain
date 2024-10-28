import random
import pandas as pd

def gerar_dados_aleatorios(empresa, periodo, meses=1):
    """Gera dados financeiros aleatórios"""
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