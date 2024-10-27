import streamlit as st
from src.models.openai_model import get_response
import pandas as pd

def initialize_comercial_state():
    """Inicializa estado específico da página comercial"""
    if 'comercial_empresa' not in st.session_state:
        st.session_state.comercial_empresa = 'ACME Corp'
    if 'comercial_trimestre' not in st.session_state:
        st.session_state.comercial_trimestre = 'Q1'
    if 'comercial_ano' not in st.session_state:
        st.session_state.comercial_ano = 2024
    if 'comercial_idioma' not in st.session_state:
        st.session_state.comercial_idioma = 'Português'
    if 'comercial_metrica' not in st.session_state:
        st.session_state.comercial_metrica = 'Vendas por Canal'

def comercial_page():
    # Inicializar estado
    initialize_comercial_state()
    
    st.title("Análise Comercial 🏢")
    
    # Configurações
    EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
    TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
    ANOS = [2024, 2023, 2022, 2021]
    IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
    METRICAS = [
        "Vendas por Canal",
        "Performance de Produtos",
        "Análise de Clientes",
        "Eficiência da Força de Vendas",
        "Market Share"
    ]
    
    # Interface principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metrica = st.selectbox(
            "Selecione a métrica:",
            METRICAS,
            index=METRICAS.index(st.session_state.comercial_metrica),
            key='comercial_metrica'
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            empresa = st.selectbox(
                'Empresa:',
                EMPRESAS,
                index=EMPRESAS.index(st.session_state.comercial_empresa),
                key='comercial_empresa'
            )
            trimestre = st.selectbox(
                'Trimestre:',
                TRIMESTRES,
                index=TRIMESTRES.index(st.session_state.comercial_trimestre),
                key='comercial_trimestre'
            )
        with col_b:
            ano = st.selectbox(
                'Ano:',
                ANOS,
                index=ANOS.index(st.session_state.comercial_ano),
                key='comercial_ano'
            )
            idioma = st.selectbox(
                'Idioma:',
                IDIOMAS,
                index=IDIOMAS.index(st.session_state.comercial_idioma),
                key='comercial_idioma'
            )
        
        if st.button('🚀 Gerar Análise Comercial'):
            periodo = f"{trimestre} {ano}"
            
            with st.spinner('Gerando análise... Aguarde um momento.'):
                prompt = f"""
                Você é um analista comercial experiente.
                Elabore uma análise comercial detalhada sobre {metrica} para a empresa {empresa} no período {periodo}.
                O relatório deve ser escrito em {idioma}.
                
                Inclua:
                1. Resumo executivo
                2. Análise detalhada dos dados comerciais
                3. Comparação com períodos anteriores
                4. Recomendações estratégicas
                5. Oportunidades de melhoria
                """
                
                response = get_response(prompt)
                
                if response:
                    st.markdown(response)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download da Análise",
                            response,
                            file_name=f"analise_comercial_{empresa}_{periodo}.md",
                            mime="text/markdown"
                        )
                    with col2:
                        if st.button("📋 Copiar"):
                            st.toast("Análise copiada!")
    
    with col2:
        st.subheader("💬 Chat Assistente")
        
        # Chat input
        chat_input = st.text_input(
            "Faça uma pergunta sobre a análise...",
            key=f"chat_input_{st.session_state.get('chat_input_key', 0)}"
        )
        
        if chat_input:
            with st.spinner("Processando sua pergunta..."):
                chat_prompt = f"""
                Contexto: Análise comercial para {empresa}, métrica {metrica}, período {trimestre} {ano}
                
                Pergunta do usuário: {chat_input}
                """
                
                chat_response = get_response(chat_prompt)
                st.markdown(chat_response)

if __name__ == "__main__":
    comercial_page()