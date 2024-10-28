import streamlit as st
import pandas as pd
from src.utils.file_processor import read_file, analyze_data, preview_data

# src/components/file_importer.py

def file_importer():
    """Componente para importação de arquivos"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Importação de Dados")
    
    # Upload do arquivo
    uploaded_file = st.sidebar.file_uploader(
        "Selecione um arquivo para importar:",
        type=['csv', 'json', 'txt'],
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        # Ler arquivo
        df = read_file(uploaded_file)
        
        if df is not None:
            # Analisar dados e sugerir área
            suggested_area = analyze_data(df)
            
            # Preview seguro dos dados
            preview_df = preview_data(df)
            
            if preview_df is not None:
                # Seleção da área
                area_options = ['Financeiro', 'Comercial', 'Operacional']
                selected_area = st.sidebar.selectbox(
                    "Selecione a área para importação:",
                    area_options,
                    index=area_options.index(suggested_area) if suggested_area in area_options else 0,
                    key="import_area"
                )
                
                # Preview dos dados
                st.sidebar.markdown("### Preview dos dados")
                st.sidebar.dataframe(preview_df, use_container_width=True)
                
                # Confirmar importação
                if st.sidebar.button("✅ Confirmar Importação", use_container_width=True):
                    try:
                        # Salvar no session state baseado na área
                        data_key = f"{selected_area.lower()}_data"
                        if data_key not in st.session_state:
                            st.session_state[data_key] = []
                        
                        st.session_state[data_key].append({
                            'name': uploaded_file.name,
                            'data': df,
                            'timestamp': pd.Timestamp.now()
                        })
                        
                        st.sidebar.success(f"Dados importados com sucesso para área {selected_area}!")
                        
                    except Exception as e:
                        st.sidebar.error(f"Erro ao importar dados: {str(e)}")