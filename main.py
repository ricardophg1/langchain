import streamlit as st
import os
from src.utils.auth import check_authentication, check_credentials
from src.components.charts import create_dashboard
from src.utils.alerts import check_alerts
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from src.utils.financial_data import dados_financeiros
from src.models.openai_model import get_response
from src.components.file_importer import file_importer  # Adicionar esta linha
from src.components.email_button import create_email_button  # Adicionar esta linha
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
    if 'selected_params' not in st.session_state:
        st.session_state.selected_params = {
            'empresa': EMPRESAS[0],
            'trimestre': TRIMESTRES[0],
            'ano': ANOS[0],
            'idioma': IDIOMAS[0],
            'analise': ANALISES[0]
        }
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = []
    if 'commercial_data' not in st.session_state:
        st.session_state.commercial_data = []
    if 'operational_data' not in st.session_state:
        st.session_state.operational_data = []

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
    st.markdown("---")
    st.subheader("💬 Chat Assistente")
    
    # Exibir histórico do chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Input do chat
    message = st.text_input(
        "Digite sua pergunta:",
        key=f"chat_input_{st.session_state.chat_input_key}"
    )
    
    # Função para processar mensagem
    def process_message():
        if message.strip():
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
            
            with st.spinner("Gerando resposta..."):
                response = get_response(prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state.chat_input_key += 1  # Incrementa para limpar o input
                st.rerun()

    # Botão de enviar e handler do Enter
    col1, col2 = st.columns([6,1])
    with col1:
        # Usar on_change para capturar o Enter
        st.text_input(
            "",
            value=message if message else "",
            key="chat_message_trigger",
            on_change=process_message if message else None,
            label_visibility="collapsed"
        )
    with col2:
        if st.button("↵", use_container_width=True):
            process_message()

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
        # Mapeamento de idiomas para instruções específicas
        idioma_map = {
            'Português': {
                'language': 'português do Brasil',
                'instruction': 'Escreva em português formal e claro'
            },
            'Inglês': {
                'language': 'English',
                'instruction': 'Write in formal and clear English'
            },
            'Espanhol': {
                'language': 'Español',
                'instruction': 'Escriba en español formal y claro'
            },
            'Francês': {
                'language': 'Français',
                'instruction': 'Écrivez en français formel et clair'
            },
            'Alemão': {
                'language': 'Deutsch',
                'instruction': 'Schreiben Sie in formellem und klarem Deutsch'
            }
        }

        idioma_config = idioma_map.get(params['idioma'])
        
        # Template para o prompt com instruções específicas de idioma
        template = f'''
        Você é um analista financeiro experiente.
        {idioma_config['instruction']}.
        
        Gere um relatório financeiro detalhado em {idioma_config['language']} para:
        Empresa: {params['empresa']}
        Período: {params['periodo']}
        Tipo de Análise: {params['analise']}
        
        Estruture o relatório com os seguintes tópicos:
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
            template += f"\n\nUtilize os seguintes dados para a análise:\n{dados_financeiros_texto}"

        # Adicionar instrução extra de idioma no final
        template += f"\n\nIMPORTANTE: Todo o relatório deve ser escrito em {idioma_config['language']}."
        
        # Obter resposta da API
        response = get_response(template)
        
        if response:
        # Container para o relatório
            report_container = st.container()
            with report_container:
                st.subheader('📄 Relatório Gerado:')
                st.markdown(response)
                
                # Container para os botões
                button_container = st.container()
                with button_container:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download do Relatório",
                            data=response,
                            file_name=f"relatorio_{params['empresa']}_{params['periodo']}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    with col2:
                        create_email_button(response, params)
            
            return response
        else:
            st.warning("Não foi possível gerar o relatório. Tente novamente.")
            return None

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        st.error("Por favor, tente novamente. Se o erro persistir, contate o suporte.")
        return None

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        st.error("Por favor, tente novamente. Se o erro persistir, contate o suporte.")
        return None

def main():
    # Configuração da página
    st.set_page_config(page_title="Sistema de Análise Empresarial",
                      page_icon="📊",
                      layout="wide")
    
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Carregar ambiente
    api_key = load_environment()
    
    # Sistema de autenticação
    if not check_authentication():
        with st.container():
            st.title("🔐 Login")
            with st.form("login_form"):
                username = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar")
                
                if submit:
                    if check_credentials(username, password):
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos")
        return

    # Se chegou aqui, está autenticado
    # Mostrar informações do usuário na sidebar
    with st.sidebar:
        st.info(f"👤 Usuário: {os.getenv('APP_USERNAME', 'admin')}")
        if st.button("📤 Logout"):
            from src.utils.auth import logout_user
            logout_user()
            st.rerun()

    # Sidebar com navegação
    menu = st.sidebar.selectbox(
        "Navegação",
        ["Principal", "Dashboard", "Financeiro", "Comercial", "Operacional"]
    )
    
    # Importador de arquivos
    file_importer()
    
    if menu == "Principal":
        show_main_page()
    elif menu == "Dashboard":
        from pages.dashboard import dashboard_page
        dashboard_page()
    elif menu == "Financeiro":
        from pages.financeiro import financeiro_page
        financeiro_page()
    elif menu == "Comercial":
        from pages.comercial import comercial_page
        comercial_page()
    elif menu == "Operacional":
        from pages.operacional import operacional_page
        operacional_page()

def show_login():
    """Mostra a tela de login"""
    with st.container():
        st.title("Login")
        with st.form("login_form"):
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            if st.form_submit_button("Entrar"):
                if check_credentials(
                    st.session_state.username,
                    st.session_state.password
                ):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")

def show_main_page():
    """Mostra a página principal"""
    # Layout principal
    main_col, chat_col = st.columns([4, 1])
    
    with main_col:
        st.title('Análise Empresarial com IA 📊')
        
        # Interface principal
        with st.container():
            selected = st.session_state.selected_params
            
            # Seleção de empresa
            empresa = st.selectbox(
                'Selecione a empresa:', 
                EMPRESAS,
                index=EMPRESAS.index(selected['empresa'])
            )
            
            # Seleção de parâmetros em duas colunas
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
            
            # Botões de ação em duas colunas
            col1, col2 = st.columns(2)
            with col1:
                if st.button('🚀 Gerar Relatório', type="primary", use_container_width=True):
                    with st.spinner('Gerando relatório... Aguarde um momento.'):
                        generate_report(params)
            with col2:
                if st.button('📊 Visualizar Dados', use_container_width=True):
                    with st.spinner('Carregando dados...'):
                        if analise == "Análise de Dados Financeiros":
                            dados = dados_financeiros(empresa, f"{trimestre} {ano}")
                            st.markdown("### 📈 Dados Financeiros")
                            st.markdown(dados)
        
        # Se houver gráficos para mostrar
        if 'show_charts' in st.session_state and st.session_state.show_charts:
            show_charts(params)
    
    # Barra lateral com histórico
    create_sidebar()
    
    # Chat na coluna da direita
    with chat_col:
        create_chat()

def show_charts(params):
    """Mostra os gráficos quando necessário"""
    with st.container():
        st.subheader("📈 Análise Visual")
        
        # Criar abas para diferentes visualizações
        tab1, tab2, tab3 = st.tabs(["Tendências", "Comparativo", "Detalhes"])
        
        with tab1:
            from src.components.charts import create_trend_chart
            fig = create_trend_chart(params)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            from src.components.charts import create_comparison_chart
            fig = create_comparison_chart(params)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            from src.components.charts import create_detail_chart
            fig = create_detail_chart(params)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()