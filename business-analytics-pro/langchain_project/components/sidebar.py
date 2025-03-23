import streamlit as st
from langchain_project.utils.auth import logout_user
from langchain_project.components.file_importer import file_importer

def create_authenticated_sidebar():
    """Cria a sidebar para usuários autenticados"""
    with st.sidebar:
        # Informações do usuário
        st.info(f"👤 Usuário: {st.session_state.username}")
        if st.button("📤 Logout"):
            logout_user()
            st.rerun()
        
        # Menu de navegação
        st.markdown("---")
        st.markdown("### 📌 Navegação")
        menu = st.selectbox(
            "Escolha uma página",
            ["Home", "Dashboard", "Financeiro", "Comercial", "Operacional"]
        )
        
        # Importador de arquivos
        st.markdown("---")
        st.markdown("### 📁 Importar Arquivos")
        file_importer()
        
        return menu

def create_report_history():
    """Cria a seção de histórico de relatórios"""
    with st.sidebar:
        st.markdown("---")
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
