import pandas as pd
import json
import os
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
import datetime
from dataclasses import dataclass, asdict
import streamlit as st

@dataclass
class TenantConfig:
    """Configuração de um tenant (cliente) na plataforma"""
    tenant_id: str
    name: str
    domain: str
    created_at: datetime.datetime
    logo_url: Optional[str] = None
    primary_color: str = "#4A6BDF"
    secondary_color: str = "#E5E9F6"
    accent_color: str = "#FF725C"
    modules: List[str] = None
    storage_quota_mb: int = 1000
    max_users: int = 10
    features: Dict[str, bool] = None
    custom_settings: Dict[str, Any] = None
    config_path: Optional[str] = None
    
    def __post_init__(self):
        if self.modules is None:
            self.modules = ["dashboard", "financial", "commercial"]
        if self.features is None:
            self.features = {
                "ai_assistant": True,
                "data_export": True,
                "api_access": False,
                "predictive_analysis": False
            }
        if self.custom_settings is None:
            self.custom_settings = {}
        if self.config_path is None:
            self.config_path = os.path.join(os.getcwd(), 'data', 'tenants', self.tenant_id, 'config.json')
        self.logger = logging.getLogger(f"TenantConfig-{self.tenant_id}")

    def save_config(self) -> bool:
        """Salva as configurações do tenant."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(asdict(self), f, indent=4, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
            return False

    def get_config_value(self, path: str, default: Any = None) -> Any:
        """Obtém um valor específico da configuração."""
        try:
            current = asdict(self)
            for key in path.split('.'):
                current = current.get(key, default)
            return current
        except Exception:
            return default

    def set_config_value(self, path: str, value: Any) -> bool:
        """Define um valor específico na configuração."""
        try:
            keys = path.split('.')
            current = self.custom_settings
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Erro ao definir configuração: {e}")
            return False

    def format_currency(self, value: float) -> str:
        """Formata um valor monetário de acordo com as configurações do tenant."""
        try:
            locale = self.custom_settings.get('locale', 'pt_BR')
            currency = self.custom_settings.get('currency', 'R$')
            return f"{currency} {value:,.2f}"
        except Exception:
            return f"R$ {value:,.2f}"

class TenantManager:
    """
    Gerenciador de tenants (multi-tenancy) para a plataforma.
    Responsável por isolar dados e configurações entre diferentes clientes.
    """
    
    def __init__(self, tenants_path: Optional[str] = None):
        """
        Inicializa o gerenciador de tenants.
        
        Args:
            tenants_path: Caminho para o arquivo de configuração dos tenants
        """
        self.logger = self._setup_logger()
        self.tenants_path = tenants_path or os.path.join(os.getcwd(), 'config', 'tenants.json')
        self.tenants = self._load_tenants()
        
    def _setup_logger(self):
        """Configura o logger para o gerenciador de tenants"""
        logger = logging.getLogger("TenantManager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
        
    def _load_tenants(self) -> Dict[str, TenantConfig]:
        """
        Carrega as configurações dos tenants do arquivo.
        
        Returns:
            Dicionário com configurações de tenants
        """
        try:
            if not os.path.exists(self.tenants_path):
                # Criar diretório se não existir
                os.makedirs(os.path.dirname(self.tenants_path), exist_ok=True)
                
                # Criar arquivo de exemplo
                self._create_example_tenants()
                
            with open(self.tenants_path, 'r') as f:
                tenants_data = json.load(f)
                
            # Converter de dicionário para objetos TenantConfig
            tenants = {}
            for tenant_id, data in tenants_data.items():
                # Converter string de data para objeto datetime
                if 'created_at' in data and isinstance(data['created_at'], str):
                    data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
                else:
                    data['created_at'] = datetime.datetime.now()
                    
                tenants[tenant_id] = TenantConfig(tenant_id=tenant_id, **data)
                
            self.logger.info(f"Carregados {len(tenants)} tenants")
            return tenants
        except Exception as e:
            self.logger.error(f"Erro ao carregar tenants: {str(e)}")
            return {}
    
    def _create_example_tenants(self):
        """Cria arquivo de exemplo com tenants de demonstração"""
        example_tenants = {
            "acme": {
                "name": "ACME Corporation",
                "domain": "acme.com",
                "created_at": datetime.datetime.now().isoformat(),
                "logo_url": "/images/acme_logo.png",
                "primary_color": "#3366FF",
                "modules": ["dashboard", "financial", "commercial", "operational"],
                "features": {
                    "ai_assistant": True,
                    "data_export": True,
                    "api_access": True,
                    "predictive_analysis": True
                },
                "storage_quota_mb": 5000,
                "max_users": 25
            },
            "globex": {
                "name": "Globex Corporation",
                "domain": "globex.com",
                "created_at": datetime.datetime.now().isoformat(),
                "logo_url": "/images/globex_logo.png",
                "primary_color": "#22AA99",
                "modules": ["dashboard", "financial", "commercial"],
                "features": {
                    "ai_assistant": True,
                    "data_export": True,
                    "api_access": False,
                    "predictive_analysis": False
                },
                "storage_quota_mb": 2000,
                "max_users": 10
            },
            "initech": {
                "name": "Initech",
                "domain": "initech.com",
                "created_at": datetime.datetime.now().isoformat(),
                "logo_url": "/images/initech_logo.png",
                "primary_color": "#FF6600",
                "modules": ["dashboard", "financial"],
                "features": {
                    "ai_assistant": False,
                    "data_export": True,
                    "api_access": False,
                    "predictive_analysis": False
                },
                "storage_quota_mb": 1000,
                "max_users": 5
            }
        }
        
        try:
            with open(self.tenants_path, 'w') as f:
                json.dump(example_tenants, f, indent=4, default=str)
                
            self.logger.info("Arquivo de exemplo de tenants criado")
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo de exemplo: {str(e)}")
    
    def save_tenants(self) -> bool:
        """
        Salva as configurações dos tenants no arquivo.
        
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            # Converter de objetos para dicionário
            tenants_dict = {}
            for tenant_id, tenant in self.tenants.items():
                # Converter para dicionário
                tenant_dict = asdict(tenant)
                # Converter datetime para string
                tenant_dict['created_at'] = tenant_dict['created_at'].isoformat()
                tenants_dict[tenant_id] = tenant_dict
                
            with open(self.tenants_path, 'w') as f:
                json.dump(tenants_dict, f, indent=4)
                
            self.logger.info(f"Configurações salvas: {len(self.tenants)} tenants")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
            return False
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """
        Obtém configuração de um tenant específico.
        
        Args:
            tenant_id: ID do tenant
            
        Returns:
            Configuração do tenant ou None se não encontrado
        """
        return self.tenants.get(tenant_id)
    
    def create_tenant(self, name: str, domain: str, modules: List[str] = None,
                     features: Dict[str, bool] = None) -> Optional[TenantConfig]:
        """
        Cria um novo tenant.
        
        Args:
            name: Nome da empresa/tenant
            domain: Domínio associado
            modules: Lista de módulos ativos
            features: Dicionário de recursos habilitados
            
        Returns:
            Configuração do tenant criado ou None em caso de erro
        """
        try:
            # Gerar ID baseado no nome
            tenant_id = name.lower().replace(' ', '_')
            
            # Verificar se já existe
            if tenant_id in self.tenants:
                self.logger.warning(f"Tenant já existe: {tenant_id}")
                return None
                
            # Criar configuração padrão
            tenant_config = TenantConfig(
                tenant_id=tenant_id,
                name=name,
                domain=domain,
                created_at=datetime.datetime.now(),
                modules=modules,
                features=features
            )
            
            # Adicionar ao dicionário
            self.tenants[tenant_id] = tenant_config
            
            # Salvar alterações
            self.save_tenants()
            
            # Criar diretórios de dados para o tenant
            self._create_tenant_directories(tenant_id)
            
            self.logger.info(f"Novo tenant criado: {tenant_id}")
            return tenant_config
        except Exception as e:
            self.logger.error(f"Erro ao criar tenant: {str(e)}")
            return None
    
    def _create_tenant_directories(self, tenant_id: str):
        """
        Cria diretórios necessários para um novo tenant.
        
        Args:
            tenant_id: ID do tenant
        """
        try:
            # Diretório base para dados do tenant
            tenant_dir = os.path.join(os.getcwd(), 'data', 'tenants', tenant_id)
            
            # Criar diretórios para diferentes tipos de dados
            directories = [
                tenant_dir,
                os.path.join(tenant_dir, 'uploads'),
                os.path.join(tenant_dir, 'reports'),
                os.path.join(tenant_dir, 'exports'),
                os.path.join(tenant_dir, 'models')
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                
            self.logger.info(f"Diretórios criados para tenant: {tenant_id}")
        except Exception as e:
            self.logger.error(f"Erro ao criar diretórios para tenant {tenant_id}: {str(e)}")
    
    def update_tenant(self, tenant_id: str, **kwargs) -> bool:
        """
        Atualiza configurações de um tenant.
        
        Args:
            tenant_id: ID do tenant
            **kwargs: Atributos a serem atualizados
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            if tenant_id not in self.tenants:
                self.logger.warning(f"Tenant não encontrado: {tenant_id}")
                return False
                
            tenant = self.tenants[tenant_id]
            
            # Atualizar atributos
            for key, value in kwargs.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)
                    
            # Salvar alterações
            self.save_tenants()
            
            self.logger.info(f"Tenant atualizado: {tenant_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao atualizar tenant {tenant_id}: {str(e)}")
            return False
    
    def delete_tenant(self, tenant_id: str, delete_data: bool = False) -> bool:
        """
        Remove um tenant.
        
        Args:
            tenant_id: ID do tenant
            delete_data: Se True, também exclui os dados associados
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            if tenant_id not in self.tenants:
                self.logger.warning(f"Tenant não encontrado: {tenant_id}")
                return False
                
            # Remover do dicionário
            del self.tenants[tenant_id]
            
            # Salvar alterações
            self.save_tenants()
            
            # Opcionalmente remover dados
            if delete_data:
                tenant_dir = os.path.join(os.getcwd(), 'data', 'tenants', tenant_id)
                if os.path.exists(tenant_dir):
                    import shutil
                    shutil.rmtree(tenant_dir)
                    self.logger.info(f"Dados do tenant excluídos: {tenant_id}")
            
            self.logger.info(f"Tenant removido: {tenant_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao remover tenant {tenant_id}: {str(e)}")
            return False
    
    def get_tenant_data_path(self, tenant_id: str, data_type: str = None) -> str:
        """
        Retorna o caminho para armazenamento de dados de um tenant.
        
        Args:
            tenant_id: ID do tenant
            data_type: Tipo de dados (uploads, reports, exports, models)
            
        Returns:
            Caminho completo para o diretório
        """
        base_dir = os.path.join(os.getcwd(), 'data', 'tenants', tenant_id)
        
        if data_type:
            return os.path.join(base_dir, data_type)
        return base_dir
    
    def check_tenant_quota(self, tenant_id: str) -> Tuple[int, int, float]:
        """
        Verifica o uso atual de armazenamento de um tenant.
        
        Args:
            tenant_id: ID do tenant
            
        Returns:
            Tupla (usado_mb, total_mb, percentual)
        """
        try:
            tenant = self.get_tenant(tenant_id)
            if not tenant:
                return 0, 0, 0
                
            # Obter tamanho total do diretório do tenant
            tenant_dir = self.get_tenant_data_path(tenant_id)
            used_bytes = 0
            
            if os.path.exists(tenant_dir):
                for dirpath, _, filenames in os.walk(tenant_dir):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        used_bytes += os.path.getsize(file_path)
            
            # Converter para MB
            used_mb = used_bytes / (1024 * 1024)
            total_mb = tenant.storage_quota_mb
            percentage = (used_mb / total_mb) * 100 if total_mb > 0 else 0
            
            return round(used_mb, 2), total_mb, round(percentage, 2)
        except Exception as e:
            self.logger.error(f"Erro ao verificar quota do tenant {tenant_id}: {str(e)}")
            return 0, 0, 0
    
    def apply_tenant_theme(self, tenant_id: str):
        """
        Aplica o tema visual do tenant na interface do Streamlit.
        
        Args:
            tenant_id: ID do tenant
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return
            
        # Definir as cores personalizadas via CSS
        css = f"""
        <style>
            :root {{
                --primary-color: {tenant.primary_color};
                --secondary-color: {tenant.secondary_color};
                --accent-color: {tenant.accent_color};
            }}
            
            .stApp {{
                background-color: var(--secondary-color);
            }}
            
            .stButton>button {{
                background-color: var(--primary-color);
                color: white;
            }}
            
            .stButton>button:hover {{
                background-color: var(--accent-color);
            }}
            
            h1, h2, h3 {{
                color: var(--primary-color);
            }}
            
            .stSidebar {{
                background-color: white;
            }}
        </style>
        """
        
        # Injetar CSS customizado
        st.markdown(css, unsafe_allow_html=True)
        
        # Adicionar logo se disponível
        if tenant.logo_url:
            st.sidebar.image(tenant.logo_url, width=200)
        
        # Definir título da página
        st.set_page_config(
            page_title=f"{tenant.name} - Analytics",
            page_icon="📊",
            layout="wide"
        )
    
    def init_streamlit_tenant_context(self):
        """
        Inicializa o contexto do tenant no Streamlit.
        Deve ser chamado na inicialização da aplicação.
        """
        if 'current_tenant' not in st.session_state:
            st.session_state.current_tenant = None
    
    def select_tenant_ui(self):
        """
        Exibe interface para seleção de tenant no Streamlit.
        Deve ser usado quando um usuário admin precisa trocar de tenant.
        """
        self.init_streamlit_tenant_context()
        
        st.sidebar.markdown("### 🏢 Selecionar Empresa")
        
        tenant_options = [(tenant_id, tenant.name) for tenant_id, tenant in self.tenants.items()]
        tenant_ids = [t[0] for t in tenant_options]
        tenant_names = [t[1] for t in tenant_options]
        
        # Índice do tenant atual selecionado
        current_index = 0
        if st.session_state.current_tenant in tenant_ids:
            current_index = tenant_ids.index(st.session_state.current_tenant)
            
        selected_index = st.sidebar.selectbox(
            "Empresa:",
            range(len(tenant_options)),
            format_func=lambda i: tenant_names[i],
            index=current_index
        )
        
        selected_tenant_id = tenant_ids[selected_index]
        
        # Atualizar tenant selecionado na sessão
        if st.session_state.current_tenant != selected_tenant_id:
            st.session_state.current_tenant = selected_tenant_id
            st.experimental_rerun()
            
        return selected_tenant_id
    
    def show_tenant_info_ui(self):
        """
        Exibe informações sobre o tenant atual no Streamlit.
        """
        if not st.session_state.current_tenant:
            return
            
        tenant = self.get_tenant(st.session_state.current_tenant)
        if not tenant:
            return
            
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### ℹ️ Informações da Empresa")
        st.sidebar.markdown(f"**Empresa:** {tenant.name}")
        
        # Mostrar uso de armazenamento
        used_mb, total_mb, percentage = self.check_tenant_quota(tenant.tenant_id)
        st.sidebar.progress(percentage / 100)
        st.sidebar.caption(f"Armazenamento: {used_mb} MB / {total_mb} MB ({percentage}%)")
        
        # Mostrar recursos disponíveis
        st.sidebar.markdown("**Recursos ativos:**")
        for feature, enabled in tenant.features.items():
            icon = "✅" if enabled else "❌"
            feature_name = feature.replace("_", " ").title()
            st.sidebar.markdown(f"{icon} {feature_name}")