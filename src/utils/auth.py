import streamlit as st
import os
from datetime import datetime, timedelta

def init_auth_state():
    """Inicializa o estado de autenticação"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'auth_token' not in st.session_state:
        st.session_state.auth_token = None
    if 'auth_expiry' not in st.session_state:
        st.session_state.auth_expiry = None

def check_authentication():
    """Verifica se o usuário está autenticado"""
    init_auth_state()
    
    # Se já estiver autenticado, verifica a expiração
    if st.session_state.authenticated:
        if st.session_state.auth_expiry and datetime.now() < st.session_state.auth_expiry:
            return True
        else:
            # Sessão expirada
            logout_user()
            return False
    
    return False

def check_credentials(username, password):
    """Verifica as credenciais do usuário"""
    # Em um ambiente de produção, você deve usar um banco de dados
    # e hash de senhas. Este é apenas um exemplo.
    
    # Obter credenciais do arquivo .env ou variáveis de ambiente
    valid_username = os.getenv('APP_USERNAME', 'admin')
    valid_password = os.getenv('APP_PASSWORD', 'admin123')
    
    if username == valid_username and password == valid_password:
        # Autenticar usuário
        st.session_state.authenticated = True
        st.session_state.auth_token = generate_token()
        st.session_state.auth_expiry = datetime.now() + timedelta(hours=8)
        return True
    
    return False

def generate_token():
    """Gera um token de autenticação"""
    import secrets
    return secrets.token_hex(16)

def logout_user():
    """Faz logout do usuário"""
    st.session_state.authenticated = False
    st.session_state.auth_token = None
    st.session_state.auth_expiry = None

def get_current_user():
    """Retorna informações do usuário atual"""
    if st.session_state.authenticated:
        return {
            'username': os.getenv('APP_USERNAME', 'admin'),
            'last_login': st.session_state.auth_expiry - timedelta(hours=8),
            'session_expires': st.session_state.auth_expiry
        }
    return None

def require_auth(func):
    """Decorador para funções que requerem autenticação"""
    def wrapper(*args, **kwargs):
        if check_authentication():
            return func(*args, **kwargs)
        else:
            st.warning("Por favor, faça login para continuar.")
            return None
    return wrapper