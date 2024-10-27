# src/load_sample_data.py

from .sample_data import SAMPLE_DATA, COMMERCIAL_METRICS, OPERATIONAL_METRICS
import pandas as pd

def load_company_data(company_name):
    """Carrega dados de uma empresa específica"""
    return SAMPLE_DATA.get(company_name, {})

def load_commercial_metrics():
    """Carrega métricas comerciais"""
    return COMMERCIAL_METRICS

def load_operational_metrics():
    """Carrega métricas operacionais"""
    return OPERATIONAL_METRICS

def create_sample_dataframe(company_name, period):
    """Cria um DataFrame de exemplo com dados históricos"""
    data = {
        'Período': [period],
        'Empresa': [company_name],
        'Dados': [load_company_data(company_name)]
    }
    return pd.DataFrame(data)