from src.data.external import (
    get_market_data, 
    get_sector_data, 
    get_competitor_data,
    calculate_market_metrics,
    format_currency,
    format_percentage
)
import pandas as pd
import numpy as np

def market_analysis(empresa_data, period='3M'):
    """
    Realiza análise completa de mercado
    
    Args:
        empresa_data: Dados da empresa
        period: Período de análise
    
    Returns:
        dict: Análise de mercado completa
    """
    try:
        # Obter dados de mercado
        market_data = get_market_data(period)
        competitor_data = get_competitor_data(empresa_data['empresa'])
        sector_data = get_sector_data(empresa_data['sector'])
        
        # Calcular métricas
        metrics = calculate_market_metrics(market_data)
        
        # Análise de market share
        market_share = empresa_data['revenue'].sum() / metrics['total_market_size']
        
        # Análise competitiva
        competitive_position = analyze_competitive_position(
            empresa_data, 
            competitor_data
        )
        
        # Análise de tendências
        trends = analyze_market_trends(market_data, period)
        
        # Montar relatório
        analysis = {
            'market_size': format_currency(metrics['total_market_size']),
            'market_share': format_percentage(market_share),
            'market_position': competitive_position['position'],
            'growth_vs_market': format_percentage(
                empresa_data['growth_rate'].mean() - metrics['average_growth']
            ),
            'trends': trends,
            'recommendations': generate_recommendations(
                empresa_data, 
                metrics, 
                competitive_position
            )
        }
        
        return analysis
    
    except Exception as e:
        print(f"Erro na análise de mercado: {str(e)}")
        return None

def analyze_competitive_position(empresa_data, competitor_data):
    """Analisa posição competitiva"""
    try:
        empresa_metrics = {
            'revenue': empresa_data['revenue'].mean(),
            'market_share': empresa_data['market_share'].mean(),
            'growth': empresa_data['growth_rate'].mean(),
            'satisfaction': empresa_data['customer_satisfaction'].mean()
        }
        
        competitor_metrics = {
            'revenue': competitor_data['revenue'].mean(),
            'market_share': competitor_data['market_share'].mean(),
            'growth': competitor_data['growth_rate'].mean(),
            'satisfaction': competitor_data['customer_satisfaction'].mean()
        }
        
        # Determinar posição
        position = "Líder" if empresa_metrics['market_share'] >= competitor_metrics['market_share'].max() else \
                  "Desafiante" if empresa_metrics['growth'] > competitor_metrics['growth'].mean() else \
                  "Seguidor"
        
        return {
            'position': position,
            'metrics': empresa_metrics,
            'comparison': competitor_metrics
        }
    
    except Exception as e:
        print(f"Erro na análise competitiva: {str(e)}")
        return None

def analyze_market_trends(market_data, period):
    """Analisa tendências de mercado"""
    try:
        trends = {
            'market_growth': market_data.groupby('date')['revenue'].sum().pct_change().mean(),
            'sector_growth': market_data.groupby(['date', 'sector'])['revenue'].sum().unstack().pct_change().mean(),
            'concentration_trend': market_data.groupby('date').apply(
                lambda x: x.nlargest(3, 'market_share')['market_share'].sum()
            ).mean()
        }
        return trends
    
    except Exception as e:
        print(f"Erro na análise de tendências: {str(e)}")
        return None

def generate_recommendations(empresa_data, metrics, position):
    """Gera recomendações baseadas na análise"""
    recommendations = []
    
    try:
        # Recomendações baseadas em market share
        if position['position'] == "Líder":
            recommendations.append(
                "Manter liderança através de inovação e expansão de mercado"
            )
        elif position['position'] == "Desafiante":
            recommendations.append(
                "Focar em segmentos específicos e diferenciação"
            )
        else:
            recommendations.append(
                "Identificar nichos e otimizar eficiência operacional"
            )
        
        # Recomendações baseadas em crescimento
        if empresa_data['growth_rate'].mean() < metrics['average_growth']:
            recommendations.append(
                "Revisar estratégia de crescimento e investir em áreas-chave"
            )
        
        return recommendations
    
    except Exception as e:
        print(f"Erro ao gerar recomendações: {str(e)}")
        return ["Não foi possível gerar recomendações específicas"]