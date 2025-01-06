import streamlit as st
import pandas as pd

def file_importer():
    """Componente para importação de arquivos"""
    uploaded_file = st.file_uploader("Escolha um arquivo", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("✅ Arquivo importado com sucesso!")
            return df
        except Exception as e:
            st.error(f"❌ Erro ao importar arquivo: {str(e)}")
    return None
