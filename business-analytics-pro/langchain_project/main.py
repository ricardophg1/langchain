import streamlit as st
import os
import pandas as pd
from datetime import datetime
import logging
from dotenv import load_dotenv

# Importar componentes da plataforma
from langchain_project.security_system import SecurityManager, create_mock_users_db
from langchain_project.multi_tenancy import TenantManager, TenantConfig
from langchain_project.data_connector import DataConnector
from langchain_project.erp_crm_integration import IntegrationManager
from langchain_project.analytics.predictive_analysis import PredictiveAnalysis

# Importar componentes existentes
from langchain_project.components.charts import create_dashboard
from langchain_project.components.chat import create_chat_interface
from langchain_project.components.email_button import create_email_button
from langchain_project.components.file_importer import file_importer
from langchain_project.components.sidebar import create_report_history
from langchain_project.utils.financial_data import calcular_metricas
from langchain_project.models.openai_model import get_response

# Carregar páginas
from langchain_project.pages.dashboard import dashboard_page
from langchain_project.pages.financeiro import financeiro_page
from langchain_project.pages.comercial import comercial_page
from langchain_project.pages.operacional import operacional_page

# Configurações globais
VERSION = "2.0.0"
APP_NAME = "Business Analytics Pro"
ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "development")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

def initialize_environment():
    """Inicializa o ambiente da aplicação"""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar variáveis críticas
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        return False
        
    # Criar diretórios necessários
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    
    logger.info(f"Ambiente inicializado: {ENVIRONMENT}")
    return True

def initialize_components():
    """Inicializa os componentes principais da aplicação"""
    # Inicializar gerenciador de segurança
    security_manager = SecurityManager()
    
    # Inicializar gerenciador de tenants
    tenant_manager = TenantManager()
    
    # Inicializar conector de dados
    data_connector = DataConnector()
    
    # Inicializar gerenciador de integrações
    integration_manager = IntegrationManager()
    
    # Inicializar análise preditiva
    predictive_analysis = PredictiveAnalysis()
    
    # Armazenar componentes na sessão
    st.session_state.security_manager = security_manager
    st.session_state.tenant_manager = tenant_manager
    st.session_state.data_connector = data_connector
    st.session_state.integration_manager = integration_manager
    st.session_state.predictive_analysis = predictive_analysis
    
    # Carregar banco de usuários mockado (substituir por real em produção)
    st.session_state.users_db = create_mock_users_db()
    
    logger.info("Componentes inicializados")
    return True

def show_landing_page():
    """Exibe a landing page para usuários não autenticados"""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem;">
            <h1>🚀 Business Analytics Pro</h1>
            <h3>Transforme seus dados em insights acionáveis</h3>
            <p style="font-size: 1.2rem;">
                Uma plataforma avançada de análise empresarial potencializada por IA
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Layout de 3 colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            ### 📊 Análise 360°
            - Financeira
            - Comercial
            - Operacional
            - Dashboards integrados
            """
        )
        
    with col2:
        st.markdown(
            """
            ### 🤖 IA Avançada
            - Previsões de tendências
            - Recomendações acionáveis
            - Assistente virtual
            - Relatórios automatizados
            """
        )
        
    with col3:
        st.markdown(
            """
            ### 🔌 Integrações
            - Conexão com ERPs
            - Conexão com CRMs
            - Exportação de dados
            - APIs personalizadas
            """
        )
    
    # CTA para login
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem;">
            <h3>Acesse agora mesmo!</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_admin_sidebar():
    """Cria sidebar para usuários admin"""
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.full_name}")
        st.markdown(f"**Função:** {st.session_state.user.role.capitalize()}")
        
        if st.button("📤 Logout", key="logout_button"):
            st.session_state.security_manager.streamlit_logout()
            st.experimental_rerun()
        
        # Seleção de tenant
        st.markdown("---")
        st.session_state.tenant_manager.select_tenant_ui()
        st.session_state.tenant_manager.show_tenant_info_ui()
        
        # Menu de navegação
        st.markdown("---")
        st.markdown("### 📌 Navegação")
        menu = st.radio(
            "Escolha uma página",
            ["Home", "Dashboard", "Financeiro", "Comercial", "Operacional", "Configurações"]
        )
        
        return menu

def create_user_sidebar():
    """Cria sidebar para usuários regulares"""
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.full_name}")
        st.markdown(f"**Função:** {st.session_state.user.role.capitalize()}")
        
        if st.button("📤 Logout", key="logout_button"):
            st.session_state.security_manager.streamlit_logout()
            st.experimental_rerun()
        
        # Menu de navegação - apenas módulos permitidos
        st.markdown("---")
        st.markdown("### 📌 Navegação")
        
        menu_options = ["Home"]
        
        # Adicionar opções baseadas nas permissões
        if st.session_state.security_manager.check_permission(st.session_state.user, "view_dashboard"):
            menu_options.append("Dashboard")
        if st.session_state.security_manager.check_permission(st.session_state.user, "view_financial"):
            menu_options.append("Financeiro")
        if st.session_state.security_manager.check_permission(st.session_state.user, "view_commercial"):
            menu_options.append("Comercial")
        if st.session_state.security_manager.check_permission(st.session_state.user, "view_operational"):
            menu_options.append("Operacional")
        
        menu = st.radio(
            "Escolha uma página",
            menu_options
        )
        
        # Importador de arquivos
        if st.session_state.security_manager.check_permission(st.session_state.user, "upload_files"):
            st.markdown("---")
            st.markdown("### 📁 Importar Arquivos")
            file_importer()
        
        return menu

def show_home_page():
    """Exibe a página inicial para usuários autenticados"""
    tenant_id = st.session_state.current_tenant
    tenant = st.session_state.tenant_manager.get_tenant(tenant_id)
    
    st.title(f"🏢 Bem-vindo(a) à {tenant.name}")
    
    # Verificar se o assistente de IA está habilitado
    ai_enabled = tenant.features.get("ai_assistant", False)
    
    # Descrição
    st.markdown(f"""
    ### Seu assistente empresarial personalizado
    
    Este sistema está configurado para ajudar você a:
    
    - 📊 **Análise Financeira**: Acompanhe indicadores financeiros, tendências e oportunidades
    - 🎯 **Análise Comercial**: Monitore vendas, clientes e estratégias comerciais
    - ⚙️ **Análise Operacional**: Gerencie processos, eficiência e qualidade
    - 📈 **Dashboard**: Visualize todos os indicadores importantes em um só lugar
    
    Escolha uma das opções no menu lateral para começar!
    """)
    
    # Métricas principais
    st.markdown("### 📈 Métricas Principais")
    
    # Obter dados reais se disponíveis, caso contrário usar simulados
    try:
        # Tentar obter dados de integração
        tenant_config = TenantConfig(tenant_id)
        financial_integration = tenant_config.get_config_value("integrations.erp")
        
        if financial_integration and financial_integration in st.session_state.integration_manager.integrations:
            # Obter dados da integração
            start_date = (datetime.now().replace(day=1) - pd.DateOffset(months=1)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            df = st.session_state.integration_manager.get_financial_data(
                financial_integration, start_date, end_date
            )
            
            if df is not None and not df.empty:
                # Usar dados reais
                metrics = calcular_metricas(df)
            else:
                # Usar dados simulados como fallback
                from langchain_project.analytics.metrics import get_key_metrics
                metrics_data = get_key_metrics(tenant.name, "Último Mês")
                metrics = {
                    'receita': metrics_data['receita'],
                    'receita_delta': metrics_data['receita_delta'],
                    'margem': metrics_data['margem'],
                    'margem_delta': metrics_data['margem_delta']
                }
        else:
            # Usar dados simulados
            from langchain_project.analytics.metrics import get_key_metrics
            metrics_data = get_key_metrics(tenant.name, "Último Mês")
            metrics = {
                'receita': metrics_data['receita'],
                'receita_delta': metrics_data['receita_delta'],
                'margem': metrics_data['margem'],
                'margem_delta': metrics_data['margem_delta']
            }
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {str(e)}")
        # Usar dados simulados em caso de erro
        from langchain_project.analytics.metrics import get_key_metrics
        metrics_data = get_key_metrics(tenant.name, "Último Mês")
        metrics = {
            'receita': metrics_data['receita'],
            'receita_delta': metrics_data['receita_delta'],
            'margem': metrics_data['margem'],
            'margem_delta': metrics_data['margem_delta']
        }
    
    # Exibir métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Receita Mensal",
            metrics['receita'],
            metrics['receita_delta'],
            help="Receita total do último mês"
        )
    with col2:
        st.metric(
            "Novos Clientes",
            "48",
            "+8",
            help="Novos clientes no último mês"
        )
    with col3:
        st.metric(
            "Eficiência",
            "92%",
            "+3%",
            help="Eficiência operacional"
        )
    with col4:
        st.metric(
            "Margem",
            metrics['margem'],
            metrics['margem_delta'],
            help="Margem de lucro"
        )
    
    # Chat assistente - apenas se recurso habilitado
    if ai_enabled:
        st.markdown("---")
        st.markdown("### 💬 Assistente IA")
        create_chat_interface("home")
    else:
        st.info("💡 O assistente de IA não está habilitado para sua organização. Entre em contato com um administrador para ativar este recurso.")

def show_config_page():
    """Exibe a página de configurações para administradores"""
    if not st.session_state.security_manager.check_permission(st.session_state.user, "admin"):
        st.error("🔒 Acesso negado. Você não tem permissão para acessar as configurações.")
        return
        
    tenant_id = st.session_state.current_tenant
    tenant = st.session_state.tenant_manager.get_tenant(tenant_id)
    tenant_config = TenantConfig(tenant_id)
    
    st.title("⚙️ Configurações")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Geral", 
        "🔌 Integrações", 
        "🤖 IA", 
        "👥 Usuários"
    ])
    
    with tab1:
        st.header("Configurações Gerais")
        
        # Informações básicas do tenant
        with st.expander("Informações da Empresa", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Nome da Empresa", value=tenant.name)
                new_domain = st.text_input("Domínio", value=tenant.domain)
                
            with col2:
                new_quota = st.number_input(
                    "Cota de Armazenamento (MB)", 
                    min_value=100, 
                    value=tenant.storage_quota_mb,
                    step=100
                )
                new_max_users = st.number_input(
                    "Máximo de Usuários", 
                    min_value=1, 
                    value=tenant.max_users,
                    step=1
                )
            
            # Exibir uso atual
            used_mb, total_mb, percentage = st.session_state.tenant_manager.check_tenant_quota(tenant_id)
            st.progress(percentage / 100)
            st.caption(f"Armazenamento usado: {used_mb} MB / {total_mb} MB ({percentage}%)")
            
            if st.button("Atualizar Informações Gerais"):
                updated = st.session_state.tenant_manager.update_tenant(
                    tenant_id,
                    name=new_name,
                    domain=new_domain,
                    storage_quota_mb=new_quota,
                    max_users=new_max_users
                )
                
                if updated:
                    st.success("Informações atualizadas com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Erro ao atualizar informações.")
        
        # Personalização visual
        with st.expander("Personalização", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                new_primary = st.color_picker("Cor Primária", value=tenant.primary_color)
                new_secondary = st.color_picker("Cor Secundária", value=tenant.secondary_color)
                
            with col2:
                new_accent = st.color_picker("Cor de Destaque", value=tenant.accent_color)
                new_logo = st.text_input("URL do Logo", value=tenant.logo_url or "")
                
            if st.button("Atualizar Aparência"):
                updated = st.session_state.tenant_manager.update_tenant(
                    tenant_id,
                    primary_color=new_primary,
                    secondary_color=new_secondary,
                    accent_color=new_accent,
                    logo_url=new_logo if new_logo else None
                )
                
                if updated:
                    st.success("Aparência atualizada com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Erro ao atualizar aparência.")
        
        # Configurações de dados
        with st.expander("Formato de Dados", expanded=False):
            date_format = tenant_config.get_config_value("data_mapping.date_format", "%Y-%m-%d")
            currency_symbol = tenant_config.get_config_value("data_mapping.currency_symbol", "R$")
            decimal_separator = tenant_config.get_config_value("data_mapping.decimal_separator", ",")
            thousands_separator = tenant_config.get_config_value("data_mapping.thousands_separator", ".")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_date_format = st.selectbox(
                    "Formato de Data",
                    ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"],
                    index=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"].index(date_format)
                )
                new_currency = st.text_input("Símbolo de Moeda", value=currency_symbol)
                
            with col2:
                new_decimal = st.selectbox(
                    "Separador Decimal",
                    [",", "."],
                    index=[",", "."].index(decimal_separator)
                )
                new_thousands = st.selectbox(
                    "Separador de Milhar",
                    [".", ",", " "],
                    index=[".", ",", " "].index(thousands_separator) if thousands_separator in [".", ",", " "] else 0
                )
            
            # Garantir que separadores são diferentes
            if new_decimal == new_thousands:
                st.warning("Os separadores decimal e de milhar devem ser diferentes.")
            
            if st.button("Atualizar Formato de Dados"):
                if new_decimal != new_thousands:
                    # Atualizar cada configuração individualmente
                    tenant_config.set_config_value("data_mapping.date_format", new_date_format)
                    tenant_config.set_config_value("data_mapping.currency_symbol", new_currency)
                    tenant_config.set_config_value("data_mapping.decimal_separator", new_decimal)
                    tenant_config.set_config_value("data_mapping.thousands_separator", new_thousands)
                    
                    st.success("Formato de dados atualizado com sucesso!")
                else:
                    st.error("Os separadores decimal e de milhar devem ser diferentes.")
                
        # Configurações de módulos
        with st.expander("Módulos", expanded=False):
            st.markdown("Selecione os módulos ativos para esta empresa:")
            
            modules = tenant.modules or []
            
            new_modules = []
            if st.checkbox("Dashboard", value="dashboard" in modules):
                new_modules.append("dashboard")
            if st.checkbox("Financeiro", value="financial" in modules):
                new_modules.append("financial")
            if st.checkbox("Comercial", value="commercial" in modules):
                new_modules.append("commercial")
            if st.checkbox("Operacional", value="operational" in modules):
                new_modules.append("operational")
            
            if st.button("Atualizar Módulos"):
                updated = st.session_state.tenant_manager.update_tenant(
                    tenant_id,
                    modules=new_modules
                )
                
                if updated:
                    st.success("Módulos atualizados com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Erro ao atualizar módulos.")
    
    with tab2:
        st.header("Integrações")
        
        # Integrações existentes
        current_integrations = tenant_config.get_config_value("integrations", {})
        
        st.subheader("Integrações Ativas")
        
        if not any(current_integrations.values()):
            st.info("Nenhuma integração configurada.")
        else:
            for integration_type, integration_id in current_integrations.items():
                if integration_id:
                    with st.expander(f"{integration_type.upper()} - {integration_id}", expanded=False):
                        st.markdown(f"**ID da Integração:** {integration_id}")
                        st.markdown("**Status:** ✅ Conectado")
                        
                        if st.button(f"Remover Integração {integration_type.upper()}", key=f"remove_{integration_type}"):
                            tenant_config.set_config_value(f"integrations.{integration_type}", None)
                            st.success(f"Integração {integration_type.upper()} removida com sucesso!")
                            st.experimental_rerun()
        
        # Adicionar nova integração
        st.subheader("Adicionar Nova Integração")
        
        col1, col2 = st.columns(2)
        
        with col1:
            integration_type = st.selectbox(
                "Tipo de Sistema",
                ["ERP", "CRM", "BI", "Outro"]
            )
            
        with col2:
            integration_system = st.selectbox(
                "Sistema",
                {
                    "ERP": ["SAP", "TOTVS", "NetSuite", "Outro"],
                    "CRM": ["Salesforce", "HubSpot", "Pipedrive", "Outro"],
                    "BI": ["Power BI", "Tableau", "Looker", "Outro"],
                    "Outro": ["API Personalizada"]
                }[integration_type]
            )
        
        # Formulário de configuração baseado no tipo selecionado
        with st.form(key="integration_form"):
            if integration_system != "Outro" and integration_system != "API Personalizada":
                col1, col2 = st.columns(2)
                
                with col1:
                    base_url = st.text_input(f"URL do {integration_system}")
                    username = st.text_input("Usuário")
                    
                with col2:
                    api_key = st.text_input("Chave de API", type="password")
                    password = st.text_input("Senha", type="password")
                
                additional_params = {}
                
                # Campos específicos por sistema
                if integration_system == "SAP":
                    client = st.text_input("Cliente SAP")
                    additional_params["client"] = client
                elif integration_system == "TOTVS":
                    company_id = st.text_input("Empresa")
                    branch_id = st.text_input("Filial")
                    additional_params["company_id"] = company_id
                    additional_params["branch_id"] = branch_id
                elif integration_system == "Salesforce":
                    security_token = st.text_input("Token de Segurança", type="password")
                    additional_params["security_token"] = security_token
            else:
                # API personalizada
                base_url = st.text_input("URL da API")
                api_key = st.text_input("Chave de API/Token", type="password")
                custom_headers = st.text_area("Cabeçalhos Personalizados (JSON)", "{}")
                
                try:
                    import json
                    headers = json.loads(custom_headers)
                    additional_params = {"custom_headers": headers}
                except:
                    st.error("Formato JSON inválido para cabeçalhos.")
                    additional_params = {}
            
            submit_button = st.form_submit_button("Testar e Salvar Integração")
            
        if submit_button:
            with st.spinner("Testando conexão..."):
                # Gerar ID para a integração
                integration_id = f"{integration_type.lower()}_{integration_system.lower().replace(' ', '_')}"
                
                # Realizar teste de conexão conforme o tipo
                success = False
                try:
                    if integration_system == "SAP":
                        success = st.session_state.integration_manager.configure_sap(
                            base_url, username, password, additional_params.get("client", "")
                        )
                    elif integration_system == "TOTVS":
                        success = st.session_state.integration_manager.configure_totvs(
                            base_url, username, password, 
                            additional_params.get("company_id", ""), 
                            additional_params.get("branch_id", "")
                        )
                    elif integration_system == "Salesforce":
                        success = st.session_state.integration_manager.configure_salesforce(
                            api_key, "", username, password, 
                            additional_params.get("security_token", "")
                        )
                    else:
                        # Integração genérica via API
                        success = st.session_state.integration_manager.connect_to_api(
                            integration_id, base_url, 
                            {"api_key": api_key, "custom_headers": additional_params.get("custom_headers", {})}
                        )
                except Exception as e:
                    st.error(f"Erro ao testar conexão: {str(e)}")
                    success = False
                
                if success:
                    # Salvar configuração no tenant
                    tenant_config.set_config_value(f"integrations.{integration_type.lower()}", integration_id)
                    st.success("Integração configurada com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Falha ao conectar. Verifique as credenciais e tente novamente.")
    
    with tab3:
        st.header("Configurações de IA")
        
        # Status atual dos recursos de IA
        ai_features = tenant.features or {}
        
        # Habilitar/desabilitar recursos
        st.subheader("Recursos de IA")
        
        ai_assistant = st.checkbox(
            "Assistente Virtual de IA", 
            value=ai_features.get("ai_assistant", False),
            help="Permite que os usuários interajam com um assistente virtual para obter insights e recomendações"
        )
        
        predictive_analysis = st.checkbox(
            "Análise Preditiva", 
            value=ai_features.get("predictive_analysis", False),
            help="Habilita previsões e detecção de tendências baseadas em dados históricos"
        )
        
        # Configurações de IA avançadas
        if predictive_analysis:
            st.subheader("Configurações de Análise Preditiva")
            
            ai_config = tenant_config.get_config_value("ai", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                prediction_horizon = st.slider(
                    "Horizonte de Previsão (meses)",
                    min_value=1,
                    max_value=24,
                    value=ai_config.get("prediction_horizon", 6),
                    help="Número de meses à frente para gerar previsões"
                )
                
                enable_recommendations = st.checkbox(
                    "Habilitar Recomendações",
                    value=ai_config.get("enable_recommendations", True),
                    help="Gerar recomendações baseadas nos dados e previsões"
                )
                
            with col2:
                confidence_threshold = st.slider(
                    "Limiar de Confiança",
                    min_value=0.5,
                    max_value=0.95,
                    value=ai_config.get("confidence_threshold", 0.7),
                    step=0.05,
                    help="Nível mínimo de confiança para exibir previsões"
                )
                
                anomaly_detection = st.checkbox(
                    "Detecção de Anomalias",
                    value=ai_config.get("anomaly_detection", True),
                    help="Identificar automaticamente valores anômalos nos dados"
                )
        
        # Botão para salvar configurações
        if st.button("Salvar Configurações de IA"):
            # Atualizar features do tenant
            new_features = ai_features.copy()
            new_features["ai_assistant"] = ai_assistant
            new_features["predictive_analysis"] = predictive_analysis
            
            updated = st.session_state.tenant_manager.update_tenant(
                tenant_id,
                features=new_features
            )
            
            # Atualizar configurações de IA se necessário
            if predictive_analysis:
                ai_settings = {
                    "prediction_horizon": prediction_horizon,
                    "enable_recommendations": enable_recommendations,
                    "confidence_threshold": confidence_threshold,
                    "anomaly_detection": anomaly_detection
                }
                
                tenant_config.set_config_value("ai", ai_settings)
            
            if updated:
                st.success("Configurações de IA atualizadas com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Erro ao atualizar configurações de IA.")
    
    with tab4:
        st.header("Gerenciamento de Usuários")
        
        # Lista de usuários existentes
        st.subheader("Usuários Ativos")
        
        # Em um sistema real, obteríamos isso do banco de dados
        # Aqui estamos usando o mock para demonstração
        users_db = st.session_state.users_db
        
        # Filtrar usuários da empresa atual
        company_users = {
            username: user_data 
            for username, user_data in users_db.items() 
            if user_data.get("company_id") == tenant.tenant_id
        }
        
        if not company_users:
            st.info("Nenhum usuário encontrado para esta empresa.")
        else:
            # Tabela de usuários
            user_data = []
            for username, data in company_users.items():
                user_data.append({
                    "ID": data.get("id", ""),
                    "Usuário": username,
                    "Nome": data.get("full_name", ""),
                    "E-mail": data.get("email", ""),
                    "Função": data.get("role", "").capitalize(),
                    "Último Login": data.get("last_login", "N/A")
                })
                
            user_df = pd.DataFrame(user_data)
            st.dataframe(user_df, use_container_width=True)
            
            # Editar usuário existente
            st.subheader("Editar Usuário")
            
            selected_user = st.selectbox(
                "Selecione um usuário para editar",
                list(company_users.keys())
            )
            
            if selected_user:
                user_data = company_users[selected_user]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_fullname = st.text_input("Nome Completo", value=user_data.get("full_name", ""))
                    new_email = st.text_input("E-mail", value=user_data.get("email", ""))
                    
                with col2:
                    new_role = st.selectbox(
                        "Função",
                        ["user", "analyst", "manager", "admin"],
                        index=["user", "analyst", "manager", "admin"].index(user_data.get("role", "user"))
                    )
                    
                    reset_password = st.checkbox("Redefinir Senha")
                    new_password = st.text_input("Nova Senha", type="password") if reset_password else None
                
                # Permissões
                st.subheader("Permissões")
                
                current_permissions = user_data.get("permissions", [])
                
                # Lista padrão de permissões possíveis
                all_permissions = [
                    "view_dashboard", "edit_dashboard",
                    "view_financial", "edit_financial",
                    "view_commercial", "edit_commercial",
                    "view_operational", "edit_operational",
                    "upload_files", "export_data"
                ]
                
                # Agrupar permissões por módulo
                permission_groups = {
                    "Dashboard": ["view_dashboard", "edit_dashboard"],
                    "Financeiro": ["view_financial", "edit_financial"],
                    "Comercial": ["view_commercial", "edit_commercial"],
                    "Operacional": ["view_operational", "edit_operational"],
                    "Geral": ["upload_files", "export_data"]
                }
                
                # Mostrar checkboxes por grupo
                new_permissions = []
                
                for group_name, permissions in permission_groups.items():
                    with st.expander(group_name, expanded=True):
                        for perm in permissions:
                            perm_name = perm.replace("_", " ").title()
                            if st.checkbox(perm_name, value=perm in current_permissions, key=f"perm_{selected_user}_{perm}"):
                                new_permissions.append(perm)
                
                if st.button("Salvar Alterações"):
                    # Em um sistema real, atualizaríamos o banco de dados
                    # Aqui estamos atualizando o mock
                    users_db[selected_user].update({
                        "full_name": new_fullname,
                        "email": new_email,
                        "role": new_role,
                        "permissions": new_permissions
                    })
                    
                    # Resetar senha se solicitado
                    if reset_password and new_password:
                        pass_hash, salt = st.session_state.security_manager._hash_password(new_password)
                        users_db[selected_user].update({
                            "password_hash": pass_hash,
                            "salt": salt
                        })
                    
                    st.success("Usuário atualizado com sucesso!")
        
        # Adicionar novo usuário
        st.subheader("Adicionar Novo Usuário")
        
        with st.form("new_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Nome de Usuário")
                fullname = st.text_input("Nome Completo")
                
            with col2:
                email = st.text_input("E-mail")
                role = st.selectbox("Função", ["user", "analyst", "manager", "admin"])
                
            password = st.text_input("Senha", type="password")
            confirm_password = st.text_input("Confirmar Senha", type="password")
            
            submit = st.form_submit_button("Adicionar Usuário")
            
            if submit:
                if not username or not password or not email or not fullname:
                    st.error("Todos os campos são obrigatórios.")
                elif password != confirm_password:
                    st.error("As senhas não coincidem.")
                elif username in users_db:
                    st.error("Nome de usuário já existe.")
                else:
                    # Validar senha
                    is_valid, message = st.session_state.security_manager.validate_password_strength(password)
                    
                    if not is_valid:
                        st.error(message)
                    else:
                        # Gerar hash da senha
                        pass_hash, salt = st.session_state.security_manager._hash_password(password)
                        
                        # Gerar ID único
                        import uuid
                        user_id = str(uuid.uuid4())[:8]
                        
                        # Criar novo usuário
                        users_db[username] = {
                            "id": user_id,
                            "password_hash": pass_hash,
                            "salt": salt,
                            "email": email,
                            "full_name": fullname,
                            "role": role,
                            "company_id": tenant.tenant_id,
                            "permissions": ["view_dashboard"],  # Permissões básicas
                            "failed_attempts": 0
                        }
                        
                        st.success(f"Usuário {username} criado com sucesso!")

def main():
    """Função principal da aplicação"""
    # Configuração da página
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Inicializar ambiente
    if not initialize_environment():
        st.error("Erro ao inicializar o ambiente da aplicação. Verifique o arquivo de log para mais detalhes.")
        st.stop()
    
    # Inicializar componentes se não existirem
    if 'security_manager' not in st.session_state:
        initialize_components()
    
    # Inicializar contexto do tenant
    if 'tenant_manager' in st.session_state:
        st.session_state.tenant_manager.init_streamlit_tenant_context()
    
    # Verificar autenticação
    if not st.session_state.security_manager.streamlit_login_form(st.session_state.users_db):
        show_landing_page()
        return
    
    # Verificar se tenant foi selecionado
    if not st.session_state.current_tenant:
        # Selecionar primeiro tenant disponível
        if st.session_state.tenant_manager.tenants:
            first_tenant = next(iter(st.session_state.tenant_manager.tenants.keys()))
            st.session_state.current_tenant = first_tenant
        else:
            st.error("Nenhuma empresa configurada. Contate o administrador.")
            st.session_state.security_manager.streamlit_logout()
            st.experimental_rerun()
            return
    
    # Aplicar tema do tenant
    tenant_id = st.session_state.current_tenant
    st.session_state.tenant_manager.apply_tenant_theme(tenant_id)
    
    # Criar sidebar de acordo com o papel do usuário
    if st.session_state.user.role == "admin":
        menu = create_admin_sidebar()
    else:
        menu = create_user_sidebar()
    
    # Renderizar página selecionada
    if menu == "Home":
        show_home_page()
    elif menu == "Dashboard":
        if st.session_state.security_manager.streamlit_require_permission("view_dashboard"):
            dashboard_page()
    elif menu == "Financeiro":
        if st.session_state.security_manager.streamlit_require_permission("view_financial"):
            financeiro_page()
    elif menu == "Comercial":
        if st.session_state.security_manager.streamlit_require_permission("view_commercial"):
            comercial_page()
    elif menu == "Operacional":
        if st.session_state.security_manager.streamlit_require_permission("view_operational"):
            operacional_page()
    elif menu == "Configurações":
        show_config_page()
    
    # Mostrar informações de versão no rodapé
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem; opacity: 0.7; font-size: 0.8rem;">
            {APP_NAME} v{VERSION} | &copy; 2025 Business Analytics Pro
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()