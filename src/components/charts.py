# src/components/charts.py

import plotly.express as px

def create_dashboard(data, chart_type):
    if chart_type == "performance":
        df = data["performance"]
        fig = px.line(df, x="date", y="value", title="Desempenho ao longo do tempo")
    elif chart_type == "comparison":
        df = data["comparison"]
        fig = px.line(df, x="date", y=["value", "competitor"], title="Análise Comparativa")
    return fig