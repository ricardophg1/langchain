import streamlit as st
from src.components.charts import create_dashboard
from src.analytics.metrics import get_key_metrics
from src.utils.alerts import check_alerts

def dashboard_page():
    st.title("Dashboard Executivo 📊")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        empresa = st.selectbox("Empresa", ["ACME Corp", "Globex Corporation"])
    with col2:
        periodo = st.selectbox("Período", ["Último Mês", "Último Trimestre", "Último Ano"])
    with col3:
        areas = st.multiselect("Áreas", ["Financeiro", "Comercial", "Operacional"])
    
    # KPIs principais
    metrics = get_key_metrics(empresa, periodo)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Receita", metrics['receita'], metrics['receita_delta'])
    with m2:
        st.metric("Margem", metrics['margem'], metrics['margem_delta'])
    with m3:
        st.metric("Market Share", metrics['market_share'], metrics['market_share_delta'])
    with m4:
        st.metric("NPS", metrics['nps'], metrics['nps_delta'])
    
    # Gráficos
    tab1, tab2 = st.tabs(["Desempenho", "Análise Comparativa"])
    with tab1:
        fig = create_dashboard(metrics['data'], "performance")
        st.plotly_chart(fig, use_container_width=True, key="performance_chart")
    
    with tab2:
        fig = create_dashboard(metrics['data'], "comparison")
        st.plotly_chart(fig, use_container_width=True, key="comparison_chart")
    
    # Alertas e Recomendações
    with st.expander("🔔 Alertas e Recomendações"):
        alerts = check_alerts(metrics['data'])
        for alert in alerts:
            st.warning(alert['message'])

    # Atualizar métricas e gráficos com base nas áreas selecionadas
    if areas:
        st.subheader("Métricas por Área")
        for area in areas:
            st.write(f"### {area}")
            area_metrics = get_key_metrics(empresa, periodo, area)  # Supondo que a função get_key_metrics pode lidar com áreas
            st.metric("Receita", area_metrics['receita'], area_metrics['receita_delta'])
            st.metric("Margem", area_metrics['margem'], area_metrics['margem_delta'])
            st.metric("Market Share", area_metrics['market_share'], area_metrics['market_share_delta'])
            st.metric("NPS", area_metrics['nps'], area_metrics['nps_delta'])
            
            fig = create_dashboard(area_metrics['data'], "performance")
            st.plotly_chart(fig, use_container_width=True, key=f"performance_chart_{area}")
            
            fig = create_dashboard(area_metrics['data'], "comparison")
            st.plotly_chart(fig, use_container_width=True, key=f"comparison_chart_{area}")
            
            alerts = check_alerts(area_metrics['data'])
            for alert in alerts:
                st.warning(alert['message'])

if __name__ == '__main__':
    dashboard_page()