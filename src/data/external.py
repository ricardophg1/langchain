import pandas as pd
import random
from datetime import datetime, timedelta
import os
import requests

class MarketDataAPI:
    """Simulação de API de dados de mercado"""
    def __init__(self):
        self.base_revenue = 1_000_000
        self.companies = [
            'ACME Corp', 'Globex Corporation', 'Soylent Corp', 
            'Initech', 'Umbrella Corporation'
        ]
        self.sectors = ['Tecnologia', 'Manufatura', 'Varejo', 'Serviços']

    def generate_market_data(self, period_start, period_end):
        """Gera dados simulados de mercado"""
        data = []
        current_date = period_start
        
        while current_date <= period_end:
            for company in self.companies:
                for sector in self.sectors:
                    revenue = self.base_revenue * (1 + random.uniform(-0.2, 0.3))
                    market_share = random.uniform(0.05, 0.25)
                    growth = random.uniform(-0.1, 0.2)
                    
                    data.append({
                        'date': current_date,
                        'company': company,
                        'sector': sector,
                        'revenue': revenue,
                        'market_share': market_share,
                        'growth_rate': growth,
                        'employees': random.randint(100, 5000),
                        'customer_satisfaction': random.uniform(3.5, 4.8)
                    })
            current_date += timedelta(days=1)
        
        return pd.DataFrame(data)

def get_market_data(period='1M', source='internal'):
    """
    Obtém dados de mercado de várias fontes
    
    Args:
        period (str): Período dos dados ('1M', '3M', '6M', '1Y')
        source (str): Fonte dos dados ('internal', 'api', 'file')
    
    Returns:
        pd.DataFrame: Dados de mercado
    """
    try:
        if source == 'internal':
            # Usar dados simulados
            api = MarketDataAPI()
            end_date = datetime.now()
            
            period_map = {
                '1M': timedelta(days=30),
                '3M': timedelta(days=90),
                '6M': timedelta(days=180),
                '1Y': timedelta(days=365)
            }
            
            start_date = end_date - period_map.get(period, timedelta(days=30))
            return api.generate_market_data(start_date, end_date)
        
        elif source == 'api':
            # Exemplo de integração com API externa
            api_key = os.getenv('MARKET_API_KEY')
            if not api_key:
                raise ValueError("API key não encontrada")
            
            url = f"https://api.market-data.com/v1/market-data?period={period}&key={api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return pd.DataFrame(response.json()['data'])
            else:
                raise Exception(f"Erro ao obter dados: {response.status_code}")
        
        elif source == 'file':
            # Ler dados de arquivo local
            file_path = os.path.join('data', 'external', f'market_data_{period}.csv')
            if os.path.exists(file_path):
                return pd.read_csv(file_path)
            else:
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        else:
            raise ValueError(f"Fonte de dados não suportada: {source}")
    
    except Exception as e:
        print(f"Erro ao obter dados de mercado: {str(e)}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

def get_sector_data(sector, period='1M'):
    """Obtém dados específicos de um setor"""
    market_data = get_market_data(period)
    return market_data[market_data['sector'] == sector]

def get_competitor_data(company, period='1M'):
    """Obtém dados dos competidores"""
    market_data = get_market_data(period)
    return market_data[market_data['company'] != company]

def calculate_market_metrics(data):
    """Calcula métricas de mercado"""
    metrics = {
        'total_market_size': data['revenue'].sum(),
        'average_growth': data['growth_rate'].mean(),
        'market_concentration': data.groupby('company')['market_share'].sum().max(),
        'sector_distribution': data.groupby('sector')['revenue'].sum().to_dict()
    }
    return metrics

# Funções auxiliares
def format_currency(value):
    """Formata valor como moeda"""
    return f"R$ {value:,.2f}"

def format_percentage(value):
    """Formata valor como percentual"""
    return f"{value:.1%}"

# Exemplo de uso:
if __name__ == "__main__":
    # Teste das funções
    data = get_market_data('3M')
    print("\nTamanho do mercado:", format_currency(data['revenue'].sum()))
    print("\nDistribuição por setor:")
    print(data.groupby('sector')['revenue'].sum())