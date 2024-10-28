import streamlit as st
from src.models.openai_model import get_response

def create_chat_interface(context_type="geral"):
    """Cria interface de chat reutilizável"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 Chat Assistente")
    
    # Inicializar estado do chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0

    # Exibir histórico do chat
    for msg in st.session_state.chat_history:
        with st.sidebar.container():
            if msg["role"] == "user":
                st.sidebar.markdown("👤 **Você:**")
            else:
                st.sidebar.markdown("🤖 **Assistente:**")
            st.sidebar.markdown(msg["content"])
            st.sidebar.markdown("---")
    
    # Função para processar a mensagem
    def process_message(message):
        if message.strip():
            # Adicionar mensagem do usuário
            st.session_state.chat_history.append({"role": "user", "content": message})
            
            # Preparar contexto
            context = ""
            if len(st.session_state.chat_history) > 0:
                context = "Histórico recente:\n"
                for msg in st.session_state.chat_history[-3:]:
                    context += f"{msg['role']}: {msg['content']}\n"
            
            # Gerar prompt
            prompt = f"""
            Você é um especialista em análise {context_type}.
            Forneça uma resposta clara e objetiva.
            
            {context}
            
            Pergunta atual: {message}
            """
            
            # Spinner no conteúdo principal
            with st.spinner("Gerando resposta..."):
                response = get_response(prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Incrementar key para limpar input
            st.session_state.chat_input_key += 1
            st.rerun()

    # Input do chat com tecla Enter
    message = st.sidebar.text_input(
        "Digite sua pergunta...",
        key=f"chat_input_{st.session_state.chat_input_key}",
        on_change=lambda: process_message(st.session_state[f"chat_input_{st.session_state.chat_input_key}"])
        if st.session_state[f"chat_input_{st.session_state.chat_input_key}"] else None
    )

    # Botão de enviar (opcional, para mobile)
    if st.sidebar.button("Enviar", key=f"send_{st.session_state.chat_input_key}"):
        process_message(message)