import streamlit as st
from langchain_project.components.charts import create_dashboard
from langchain_project.analytics.metrics import get_key_metrics
from langchain_project.utils.alerts import check_alerts

def dashboard_page():
    """Página do dashboard principal"""
    st.title("📊 Dashboard Executivo")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        empresa = st.selectbox(
            "Empresa",
            ["ACME Corp", "Globex Corporation", "Soylent Corp", "Initech", "Umbrella Corporation"]
        )
    with col2:
        periodo = st.selectbox(
            "Período",
            ["Último Mês", "Último Trimestre", "Último Ano"]
        )
    with col3:
        areas = st.multiselect(
            "Áreas",
            ["Financeiro", "Comercial", "Operacional"],
            default=["Financeiro"]
        )
    
    # KPIs principais
    st.markdown("### 📈 Métricas Principais")
    metrics = get_key_metrics(empresa, periodo)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            "Receita",
            metrics['receita'],
            metrics['receita_delta'],
            help="Receita total no período"
        )
    with m2:
        st.metric(
            "Margem",
            metrics['margem'],
            metrics['margem_delta'],
            help="Margem de lucro"
        )
    with m3:
        st.metric(
            "Market Share",
            metrics['market_share'],
            metrics['market_share_delta'],
            help="Participação no mercado"
        )
    with m4:
        st.metric(
            "NPS",
            metrics['nps'],
            metrics['nps_delta'],
            help="Net Promoter Score"
        )
    
    # Gráficos
    st.markdown("### 📊 Análises")
    tab1, tab2 = st.tabs(["📈 Desempenho", "🔄 Análise Comparativa"])
    with tab1:
        fig = create_dashboard(metrics['data'], "performance")
        st.plotly_chart(fig, use_container_width=True, key="performance_chart")
    
    with tab2:
        fig = create_dashboard(metrics['data'], "comparison")
        st.plotly_chart(fig, use_container_width=True, key="comparison_chart")
    
    # Alertas e Recomendações
    st.markdown("### 🔔 Alertas e Recomendações")
    with st.expander("Ver detalhes", expanded=True):
        alerts = check_alerts(metrics['data'])
        for alert in alerts:
            st.warning(alert['message'])

    # Métricas por área
    if areas:
        st.markdown("### 📋 Métricas por Área")
        for area in areas:
            with st.expander(f"{area}", expanded=True):
                st.write(f"Detalhes da área {area}")
                # Aqui você pode adicionar métricas específicas por área
                st.info("Mais métricas serão adicionadas em breve...")

if __name__ == '__main__':
    dashboard_page()
