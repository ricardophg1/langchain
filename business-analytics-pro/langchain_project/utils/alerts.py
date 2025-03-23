import streamlit as st
import pandas as pd

def check_alerts():
    """Verifica e exibe alertas"""
    # Exemplo de alerta
    st.warning("⚠️ Alguns indicadores estão abaixo da meta!")

def check_alerts(data):
    """Verifica alertas nos dados financeiros
    
    Args:
        data (pd.DataFrame): DataFrame com os dados financeiros
        
    Returns:
        list: Lista de dicionários com os alertas
    """
    alerts = []
    
    # Verifica tendência de receita
    receitas = data['Receita'].tolist()
    if len(receitas) >= 2 and receitas[-1] < receitas[-2]:
        alerts.append({
            'type': 'warning',
            'message': '⚠️ Queda na receita detectada no último período'
        })
    
    # Verifica margem
    if 'Margem' in data.columns:
        margens = data['Margem'].tolist()
        if len(margens) >= 1 and margens[-1] < 20:
            alerts.append({
                'type': 'warning',
                'message': '⚠️ Margem abaixo do esperado (20%)'
            })
    
    # Verifica market share
    if 'Market_Share' in data.columns:
        market_share = data['Market_Share'].tolist()
        if len(market_share) >= 1 and market_share[-1] < 15:
            alerts.append({
                'type': 'warning',
                'message': '⚠️ Market Share abaixo do esperado (15%)'
            })
    
    # Verifica NPS
    if 'NPS' in data.columns:
        nps = data['NPS'].tolist()
        if len(nps) >= 1 and nps[-1] < 50:
            alerts.append({
                'type': 'warning',
                'message': '⚠️ NPS abaixo do esperado (50)'
            })
    
    # Se não houver alertas, adiciona mensagem positiva
    if not alerts:
        alerts.append({
            'type': 'success',
            'message': '✅ Todos os indicadores estão dentro do esperado'
        })
    
    return alerts
