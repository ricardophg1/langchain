# financeiro.py
def dados_financeiros(empresa, periodo):
    # Simulação de dados financeiros para a empresa e período fornecidos
    dados = {
        "ACME Corp": {
            "Q1 2021": "Receita: $1M, Lucro: $200K",
            "Q2 2021": "Receita: $1.2M, Lucro: $250K",
            # Adicione mais dados conforme necessário
        },
        "Globex Corporation": {
            "Q1 2021": "Receita: $2M, Lucro: $500K",
            "Q2 2021": "Receita: $2.5M, Lucro: $600K",
            # Adicione mais dados conforme necessário
        },
        # Adicione mais empresas conforme necessário
    }
    return dados.get(empresa, {}).get(periodo, "Dados financeiros não disponíveis para o período selecionado.")