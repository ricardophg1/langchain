import streamlit as st
import os
from dotenv import load_dotenv

def check_credentials(username: str, password: str) -> bool:
    """Verifica as credenciais do usuário"""
    load_dotenv()
    
    # Carrega as credenciais do arquivo .env
    valid_username = os.getenv("APP_USERNAME")
    valid_password = os.getenv("APP_PASSWORD")
    
    # Verifica se as credenciais foram carregadas
    if not valid_username or not valid_password:
        st.error("Erro: Credenciais não encontradas no arquivo .env")
        return False
    
    # Verifica se as credenciais são válidas
    is_valid = (username == valid_username and password == valid_password)
    
    # Se as credenciais forem válidas, inicializa a sessão
    if is_valid:
        initialize_session(username)
    
    return is_valid

def check_authentication():
    """Verifica se o usuário está autenticado"""
    return st.session_state.get("authenticated", False)

def initialize_session(username: str):
    """Inicializa a sessão do usuário"""
    st.session_state.authenticated = True
    st.session_state.username = username
    
    # Carrega a chave da API OpenAI
    load_dotenv()
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")

def logout_user():
    """Faz logout do usuário e limpa a sessão"""
    # Lista de chaves a serem limpas
    keys_to_clear = [
        "authenticated",
        "username",
        "openai_api_key",
        "messages",
        "chat_history",
        "selected_params",
        "history"
    ]
    
    # Limpa cada chave da sessão
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
