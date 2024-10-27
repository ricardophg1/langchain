import streamlit as st
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from pages.financeiro import dados_financeiros
from src.models.openai_model import get_response
import pandas as pd

# Configurações e opções
EMPRESAS = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
TRIMESTRES = ['Q1', 'Q2', 'Q3', 'Q4']
ANOS = [2024, 2023, 2022, 2021]
IDIOMAS = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
ANALISES = [
    "Análise de Dados Financeiros",
    "Análise do Balanço Patrimonial",
    "Análise do Fluxo de Caixa",
    "Análise de Tendências",
    "Análise de Receita e Lucro",
    "Análise de Posição de Mercado"
]

def initialize_session_state():
    """Inicializa variáveis de estado da sessão"""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'selected_params' not in st.session_state:
        st.session_state.selected_params = {
            'empresa': EMPRESAS[0],
            'trimestre': TRIMESTRES[0],
            'ano': ANOS[0],
            'idioma': IDIOMAS[0],
            'analise': ANALISES[0]
        }

def load_environment():
    """Carrega e valida as variáveis de ambiente"""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY não encontrada no arquivo .env")
        st.info("Por favor, configure sua chave API no arquivo .env")
        st.stop()
    return api_key

def create_chat():
    """Cria a seção de chat"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 Chat Assistente")
    
    # Exibir histórico do chat
    for msg in st.session_state.chat_history:
        with st.sidebar.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Input do chat
    message = st.sidebar.text_input("Digite sua pergunta:")
    if message:
        # Adicionar mensagem do usuário
        st.session_state.chat_history.append({"role": "user", "content": message})
        
        # Contexto do último relatório
        context = ""
        if st.session_state.history:
            last_report = st.session_state.history[-1]
            context = f"""
            Último relatório gerado:
            Empresa: {last_report['empresa']}
            Período: {last_report['periodo']}
            Análise: {last_report['analise']}
            """
        
        # Gerar resposta
        prompt = f"""
        Você é um assistente especializado em análise empresarial.
        
        Contexto: {context}
        
        Pergunta: {message}
        
        Forneça uma resposta clara e objetiva.
        """
        
        with st.sidebar.spinner("Gerando resposta..."):
            response = get_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

def create_sidebar():
    """Cria e gerencia a barra lateral com histórico"""
    with st.sidebar:
        st.subheader("📜 Histórico de Relatórios")
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.history = []
            st.session_state.chat_history = []
            st.rerun()
        
        # Exibir histórico
        if st.session_state.history:
            for idx, report in enumerate(reversed(st.session_state.history)):
                with st.expander(f"Relatório {len(st.session_state.history) - idx}"):
                    st.write(f"**Empresa:** {report['empresa']}")
                    st.write(f"**Período:** {report['periodo']}")
                    st.write(f"**Análise:** {report['analise']}")
                    if st.button("Recarregar", key=f"reload_{idx}"):
                        st.session_state.selected_params = report
                        st.rerun()

def generate_report(params):
    """Gera o relatório com os parâmetros fornecidos"""
    try:
        # Template para o prompt
        template = '''
        Você é um analista financeiro experiente.
        Escreva um relatório financeiro detalhado para a empresa "{empresa}" para o período {periodo}.
        O relatório deve ser escrito em {idioma} e incluir a seguinte análise:
        {analise}
        {dados_financeiros}

        Certifique-se de fornecer:
        1. Resumo executivo
        2. Análise detalhada dos dados
        3. Insights principais
        4. Recomendações
        5. Riscos e oportunidades

        Formate o relatório utilizando Markdown para melhor legibilidade.
        '''

        # Preparar dados financeiros
        dados_financeiros_texto = ""
        if params['analise'] == "Análise de Dados Financeiros":
            dados = dados_financeiros(params['empresa'], params['periodo'])
            dados_financeiros_texto = f"\n\nDados Financeiros:\n{dados}"

        # Gerar o prompt
        prompt = template.format(
            empresa=params['empresa'],
            periodo=params['periodo'],
            idioma=params['idioma'],
            analise=params['analise'],
            dados_financeiros=dados_financeiros_texto
        )
        
        # Obter resposta da API
        response = get_response(prompt)
        
        if response:
            # Salvar no histórico
            st.session_state.history.append(params)
            
            # Exibir relatório
            st.subheader('📄 Relatório Gerado:')
            st.markdown(response)
            
            # Botões de ação
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download do Relatório",
                    data=response,
                    file_name=f"relatorio_{params['empresa']}_{params['periodo']}.md",
                    mime="text/markdown"
                )
            with col2:
                if st.button("📋 Copiar"):
                    st.toast("Relatório copiado com sucesso!")
            
            return response
        else:
            st.warning("Não foi possível gerar o relatório. Tente novamente.")
            return None

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        st.error("Por favor, tente novamente. Se o erro persistir, contate o suporte.")
        return None

def main():
    st.set_page_config(page_title="Análise Empresarial IA", page_icon="📊", layout="wide")
    
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Carregar ambiente
    api_key = load_environment()
    
    # Criar barra lateral
    create_sidebar()
    
    # Criar chat
    create_chat()
    
    # Título principal
    st.title('Análise Empresarial com IA 📊')
    
    # Interface principal
    with st.container():
        selected = st.session_state.selected_params
        
        empresa = st.selectbox(
            'Selecione a empresa:', 
            EMPRESAS,
            index=EMPRESAS.index(selected['empresa'])
        )
        
        col1, col2 = st.columns(2)
        with col1:
            trimestre = st.selectbox(
                'Selecione o trimestre:', 
                TRIMESTRES,
                index=TRIMESTRES.index(selected['trimestre'])
            )
            idioma = st.selectbox(
                'Selecione o idioma:', 
                IDIOMAS,
                index=IDIOMAS.index(selected['idioma'])
            )
        with col2:
            ano = st.selectbox(
                'Selecione o ano:', 
                ANOS,
                index=ANOS.index(int(selected['ano']))
            )
            analise = st.selectbox(
                'Selecione a análise:', 
                ANALISES,
                index=ANALISES.index(selected['analise'])
            )
        
        # Atualizar parâmetros selecionados
        params = {
            'empresa': empresa,
            'periodo': f"{trimestre} {ano}",
            'idioma': idioma,
            'analise': analise,
            'trimestre': trimestre,
            'ano': ano
        }
        st.session_state.selected_params = params
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('🚀 Gerar Relatório', type="primary"):
                with st.spinner('Gerando relatório... Aguarde um momento.'):
                    generate_report(params)
        with col2:
            if st.button('📊 Visualizar Dados'):
                with st.spinner('Carregando dados...'):
                    if analise == "Análise de Dados Financeiros":
                        dados = dados_financeiros(empresa, f"{trimestre} {ano}")
                        st.markdown("### 📈 Dados Financeiros")
                        st.markdown(dados)

if __name__ == '__main__':
    main()