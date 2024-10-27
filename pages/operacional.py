import streamlit as st
from src.models.openai_model import get_response

def operacional_page():
    st.title("Análise Operacional ⚙️")
    
    # Configurações
    EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
    TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
    ANOS = [2024, 2023, 2022, 2021]
    IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
    
    # Métricas operacionais
    METRICAS = [
        "Eficiência Produtiva",
        "Gestão de Estoque",
        "Qualidade",
        "Manutenção",
        "Logística"
    ]
    
    # Interface principal
    metrica = st.selectbox("Selecione a métrica:", METRICAS)
    
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.selectbox('Empresa:', EMPRESAS)
        trimestre = st.selectbox('Trimestre:', TRIMESTRES)
        idioma = st.selectbox('Idioma:', IDIOMAS)
    with col2:
        ano = st.selectbox('Ano:', ANOS)
    
    if st.button('🚀 Gerar Análise Operacional'):
        periodo = f"{trimestre} {ano}"
        
        with st.spinner('Gerando análise... Aguarde um momento.'):
            prompt = f"""
            Você é um analista operacional experiente.
            Elabore uma análise operacional detalhada sobre {metrica} para a empresa {empresa} no período {periodo}.
            O relatório deve ser escrito em {idioma}.
            
            Inclua:
            1. Resumo executivo
            2. Indicadores de performance operacional
            3. Análise de eficiência
            4. Pontos de melhoria
            5. Recomendações técnicas
            """
            
            response = get_response(prompt)
            
            if response:
                st.markdown(response)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download da Análise",
                        response,
                        file_name=f"analise_operacional_{empresa}_{periodo}.md",
                        mime="text/markdown"
                    )
                with col2:
                    if st.button("📋 Copiar"):
                        st.toast("Análise copiada!")

if __name__ == "__main__":
    operacional_page()