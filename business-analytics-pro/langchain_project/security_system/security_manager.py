import streamlit as st
import os
import hashlib
import secrets
import jwt
import datetime
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
import json
from dataclasses import dataclass

@dataclass
class User:
    id: str
    username: str
    email: str
    full_name: str
    role: str
    company_id: str
    permissions: List[str]
    last_login: Optional[datetime.datetime] = None
    
class SecurityManager:
    """
    Gerenciador de segurança para controle de autenticação e autorização.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de segurança.
        
        Args:
            config_path: Caminho para o arquivo de configuração (opcional)
        """
        self.logger = self._setup_logger()
        self.config = self._load_config(config_path)
        self._init_jwt_secret()
        
    def _setup_logger(self):
        """Configura o logger para o gerenciador de segurança"""
        logger = logging.getLogger("SecurityManager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Carrega configurações de segurança.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            
        Returns:
            Dicionário com configurações
        """
        default_config = {
            "password_min_length": 8,
            "password_require_special": True,
            "password_require_numbers": True,
            "session_expiry_minutes": 60,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "jwt_expiry_days": 1
        }
        
        if not config_path:
            self.logger.info("Usando configurações padrão de segurança")
            return default_config
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Validar configurações
            required_keys = list(default_config.keys())
            for key in required_keys:
                if key not in config:
                    self.logger.warning(f"Configuração ausente: {key}. Usando valor padrão.")
                    config[key] = default_config[key]
                    
            self.logger.info("Configurações de segurança carregadas com sucesso")
            return config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}. Usando valores padrão.")
            return default_config
    
    def _init_jwt_secret(self):
        """Inicializa o segredo para assinatura de tokens JWT"""
        # Verificar se já existe um segredo no ambiente
        jwt_secret = os.environ.get("JWT_SECRET")
        
        if not jwt_secret:
            # Criar novo segredo e armazená-lo em um arquivo
            jwt_secret = secrets.token_hex(32)
            try:
                secret_dir = os.path.join(os.getcwd(), 'secrets')
                os.makedirs(secret_dir, exist_ok=True)
                
                with open(os.path.join(secret_dir, 'jwt_secret.key'), 'w') as f:
                    f.write(jwt_secret)
                
                # Definir no ambiente
                os.environ["JWT_SECRET"] = jwt_secret
                self.logger.info("Novo segredo JWT gerado e armazenado")
            except Exception as e:
                self.logger.error(f"Erro ao salvar segredo JWT: {str(e)}")
                # Ainda usar o segredo gerado, mesmo sem salvar
                os.environ["JWT_SECRET"] = jwt_secret
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Gera hash seguro para senha.
        
        Args:
            password: Senha em texto plano
            salt: Salt opcional (se não fornecido, um novo é gerado)
            
        Returns:
            Tupla (password_hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)
            
        # Combinar senha e salt
        password_salt = password + salt
        
        # Gerar hash usando SHA-256
        password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
        
        return password_hash, salt
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Valida a força da senha.
        
        Args:
            password: Senha a ser validada
            
        Returns:
            Tupla (válido, mensagem)
        """
        # Verificar tamanho mínimo
        if len(password) < self.config['password_min_length']:
            return False, f"A senha deve ter pelo menos {self.config['password_min_length']} caracteres"
            
        # Verificar se contém pelo menos um número
        if self.config['password_require_numbers'] and not any(c.isdigit() for c in password):
            return False, "A senha deve conter pelo menos um número"
            
        # Verificar se contém pelo menos um caractere especial
        if self.config['password_require_special']:
            special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "A senha deve conter pelo menos um caractere especial"
                
        return True, "Senha válida"
    
    def generate_token(self, user_id: str, username: str, role: str, 
                      company_id: str, extra_data: Dict[str, Any] = None) -> str:
        """
        Gera token JWT para autenticação.
        
        Args:
            user_id: ID do usuário
            username: Nome de usuário
            role: Papel/função do usuário
            company_id: ID da empresa
            extra_data: Dados extras para o payload
            
        Returns:
            Token JWT
        """
        # Calcular data de expiração
        expiry = datetime.datetime.utcnow() + datetime.timedelta(days=self.config['jwt_expiry_days'])
        
        # Preparar payload
        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "company_id": company_id,
            "exp": expiry,
            "iat": datetime.datetime.utcnow()
        }
        
        # Adicionar dados extras se fornecidos
        if extra_data:
            payload.update(extra_data)
            
        # Gerar token
        jwt_secret = os.environ.get("JWT_SECRET")
        if not jwt_secret:
            self.logger.error("Segredo JWT não encontrado")
            raise ValueError("Configuração de segurança inválida: JWT_SECRET não definido")
            
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        self.logger.info(f"Token gerado para usuário: {username}")
        return token
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Valida token JWT.
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            Tupla (válido, payload)
        """
        jwt_secret = os.environ.get("JWT_SECRET")
        if not jwt_secret:
            self.logger.error("Segredo JWT não encontrado")
            return False, None
            
        try:
            # Decodificar e validar token
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return True, payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expirado")
            return False, None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Token inválido: {str(e)}")
            return False, None
            
    def login_user(self, username: str, password: str, users_db) -> Tuple[bool, Optional[str], Optional[User]]:
        """
        Autentica um usuário.
        
        Args:
            username: Nome de usuário
            password: Senha
            users_db: Banco de dados de usuários
            
        Returns:
            Tupla (sucesso, token, user)
        """
        try:
            # Verificar se o usuário existe
            if username not in users_db:
                self.logger.warning(f"Tentativa de login com usuário inexistente: {username}")
                return False, None, None
                
            user_data = users_db[username]
            
            # Verificar bloqueio por excesso de tentativas
            if 'locked_until' in user_data:
                locked_until = datetime.datetime.fromisoformat(user_data['locked_until'])
                if datetime.datetime.now() < locked_until:
                    self.logger.warning(f"Tentativa de login em conta bloqueada: {username}")
                    return False, None, None
                else:
                    # Reset do contador de tentativas após expiração do bloqueio
                    if 'failed_attempts' in user_data:
                        user_data['failed_attempts'] = 0
            
            # Verificar senha
            stored_hash = user_data['password_hash']
            stored_salt = user_data['salt']
            
            input_hash, _ = self._hash_password(password, stored_salt)
            
            if input_hash != stored_hash:
                # Incrementar contador de tentativas falhas
                user_data['failed_attempts'] = user_data.get('failed_attempts', 0) + 1
                
                # Verificar se deve bloquear a conta
                if user_data['failed_attempts'] >= self.config['max_login_attempts']:
                    lockout_until = datetime.datetime.now() + datetime.timedelta(
                        minutes=self.config['lockout_duration_minutes']
                    )
                    user_data['locked_until'] = lockout_until.isoformat()
                    self.logger.warning(f"Conta bloqueada por excesso de tentativas: {username}")
                
                self.logger.warning(f"Tentativa de login com senha incorreta: {username}")
                return False, None, None
                
            # Reset do contador de tentativas após login bem-sucedido
            user_data['failed_attempts'] = 0
            if 'locked_until' in user_data:
                del user_data['locked_until']
                
            # Criar objeto do usuário
            user = User(
                id=user_data['id'],
                username=username,
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                company_id=user_data['company_id'],
                permissions=user_data['permissions'],
                last_login=datetime.datetime.now()
            )
            
            # Atualizar timestamp de último login
            user_data['last_login'] = user.last_login.isoformat()
            
            # Gerar token JWT
            token = self.generate_token(
                user_id=user.id,
                username=user.username,
                role=user.role,
                company_id=user.company_id,
                extra_data={"permissions": user.permissions}
            )
            
            self.logger.info(f"Login bem-sucedido: {username}")
            return True, token, user
            
        except Exception as e:
            self.logger.error(f"Erro durante login: {str(e)}")
            return False, None, None
    
    def check_permission(self, user: User, required_permission: str) -> bool:
        """
        Verifica se o usuário tem permissão específica.
        
        Args:
            user: Objeto do usuário
            required_permission: Permissão necessária
            
        Returns:
            Booleano indicando se tem permissão
        """
        # Admin tem todas as permissões
        if user.role == "admin":
            return True
            
        # Verificar na lista de permissões do usuário
        return required_permission in user.permissions
    
    def init_streamlit_auth(self):
        """
        Inicializa a autenticação no Streamlit.
        Deve ser chamado na inicialização da aplicação.
        """
        # Verificar se já existe uma sessão
        if 'user' not in st.session_state:
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.authenticated = False
    
    def streamlit_login_form(self, users_db) -> bool:
        """
        Exibe formulário de login do Streamlit e gerencia autenticação.
        
        Args:
            users_db: Banco de dados de usuários
            
        Returns:
            Booleano indicando sucesso do login
        """
        self.init_streamlit_auth()
        
        # Se já autenticado, não mostrar o formulário
        if st.session_state.authenticated:
            return True
            
        # Título e layout do formulário
        st.title("🔐 Login")
        
        # Uso de colunas para centralizar o formulário
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form"):
                username = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Por favor, preencha todos os campos.")
                        return False
                        
                    success, token, user = self.login_user(username, password, users_db)
                    
                    if success:
                        st.session_state.user = user
                        st.session_state.token = token
                        st.session_state.authenticated = True
                        st.success("Login realizado com sucesso!")
                        
                        # Placeholder para rerun automático (não ideal, mas funcional)
                        st.experimental_rerun()
                        return True
                    else:
                        if username in users_db and 'failed_attempts' in users_db[username]:
                            attempts = users_db[username]['failed_attempts']
                            remaining = self.config['max_login_attempts'] - attempts
                            
                            if remaining > 0:
                                st.error(f"Credenciais inválidas. Tentativas restantes: {remaining}")
                            else:
                                st.error("Conta bloqueada por excesso de tentativas. Tente novamente mais tarde.")
                        else:
                            st.error("Credenciais inválidas. Tente novamente.")
                        
                        return False
        
        return False
    
    def streamlit_logout(self):
        """
        Realiza logout do usuário na sessão do Streamlit.
        """
        if 'user' in st.session_state:
            del st.session_state.user
        if 'token' in st.session_state:
            del st.session_state.token
        if 'authenticated' in st.session_state:
            st.session_state.authenticated = False
            
        # Limpar outras informações de estado da sessão
        for key in list(st.session_state.keys()):
            if key not in ['user', 'token', 'authenticated']:
                del st.session_state[key]
                
        self.logger.info("Logout realizado")
    
    def streamlit_check_auth(self):
        """
        Verifica se o usuário está autenticado no Streamlit.
        Se não estiver, redireciona para a página de login.
        
        Returns:
            Booleano indicando se está autenticado
        """
        self.init_streamlit_auth()
        
        if not st.session_state.authenticated or not st.session_state.user:
            st.error("🔒 Acesso negado. Faça login para continuar.")
            return False
            
        # Verificar validade do token
        token = st.session_state.token
        is_valid, _ = self.validate_token(token)
        
        if not is_valid:
            st.error("🔒 Sessão expirada. Faça login novamente.")
            self.streamlit_logout()
            return False
            
        return True
    
    def streamlit_require_permission(self, permission: str):
        """
        Verifica se o usuário tem uma permissão específica.
        Se não tiver, exibe mensagem de erro.
        
        Args:
            permission: Permissão necessária
            
        Returns:
            Booleano indicando se tem permissão
        """
        if not self.streamlit_check_auth():
            return False
            
        user = st.session_state.user
        if not self.check_permission(user, permission):
            st.error(f"🔒 Acesso negado. Você não tem permissão para acessar esta funcionalidade.")
            return False
            
        return True

# Exemplo de banco de dados de usuários (em produção seria um banco real)
def create_mock_users_db():
    """Cria um banco de dados fictício de usuários para demonstração"""
    security = SecurityManager()
    
    users = {}
    
    # Admin
    admin_pass, admin_salt = security._hash_password("Admin@123")
    users["admin"] = {
        "id": "001",
        "password_hash": admin_pass,
        "salt": admin_salt,
        "email": "admin@empresa.com",
        "full_name": "Administrador do Sistema",
        "role": "admin",
        "company_id": "001",
        "permissions": ["all"],
        "failed_attempts": 0
    }
    
    # Gerente
    gerente_pass, gerente_salt = security._hash_password("Gerente@123")
    users["gerente"] = {
        "id": "002",
        "password_hash": gerente_pass,
        "salt": gerente_salt,
        "email": "gerente@empresa.com",
        "full_name": "Gerente Comercial",
        "role": "manager",
        "company_id": "001",
        "permissions": ["view_dashboard", "view_financial", "view_commercial", "edit_commercial", "view_operational"],
        "failed_attempts": 0
    }
    
    # Analista
    analista_pass, analista_salt = security._hash_password("Analista@123")
    users["analista"] = {
        "id": "003",
        "password_hash": analista_pass,
        "salt": analista_salt,
        "email": "analista@empresa.com",
        "full_name": "Analista Financeiro",
        "role": "analyst",
        "company_id": "001",
        "permissions": ["view_dashboard", "view_financial", "edit_financial"],
        "failed_attempts": 0
    }
    
    return users