import streamlit as st
from langchain_project.models.openai_model import get_response

def create_chat_interface(context_type: str = "geral"):
    """Cria interface de chat interativa
    
    Args:
        context_type (str): Tipo de contexto do chat (comercial, financeiro, etc.)
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.markdown(f"💬 Chat - Contexto: {context_type.title()}")
    
    # Exibe mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Campo de entrada do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Adiciona mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gera resposta com contexto
        with st.chat_message("assistant"):
            prompt_with_context = f"Contexto: Análise {context_type}\n\nPergunta: {prompt}"
            response = get_response(prompt_with_context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
