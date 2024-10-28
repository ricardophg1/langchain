import streamlit as st
import os
from src.utils.email_sender import send_email

def create_email_button(content, params):
    """Componente reutilizável para botão de email e formulário"""
    # Chave única para o estado do formulário
    form_key = f"email_form_{params.get('analise', 'geral')}_{params.get('empresa', '')}"
    
    # Inicializar estado do formulário se necessário
    if form_key not in st.session_state:
        st.session_state[form_key] = {
            'show_form': False,
            'content': content
        }
    
    # Botão para mostrar/ocultar formulário
    if st.button(
        "📧 Enviar por Email",
        key=f"email_btn_{params.get('analise', 'geral')}",
        use_container_width=True
    ):
        st.session_state[form_key]['show_form'] = True
        st.session_state[form_key]['content'] = content
    
    # Mostrar formulário se ativado
    if st.session_state[form_key]['show_form']:
        with st.container():
            st.markdown("### 📧 Enviar Relatório por Email")
            
            # Email do remetente
            sender_email = os.getenv('DEFAULT_SENDER_EMAIL')
            if sender_email:
                st.info(f"Enviando de: {sender_email}")
            else:
                sender_email = st.text_input(
                    "Seu email",
                    placeholder="seu@email.com",
                    key=f"sender_{form_key}"
                )
            
            # Email do destinatário
            receiver_email = st.text_input(
                "Email do destinatário",
                placeholder="exemplo@email.com",
                key=f"receiver_{form_key}"
            )
            
            # Botão de envio que não recarrega a página
            if st.button(
                "📤 Enviar Email",
                key=f"send_{form_key}",
                use_container_width=True
            ):
                if not receiver_email:
                    st.error("Por favor, informe o email do destinatário.")
                else:
                    # Preparar email
                    subject = (f"Relatório {params.get('analise', 'Análise')} - "
                             f"{params.get('empresa', 'Empresa')} - "
                             f"{params.get('periodo', 'Período')}")
                    
                    email_content = f"""
                    Relatório Gerado via Sistema de Análise Empresarial
                    
                    {st.session_state[form_key]['content']}
                    
                    ---
                    Gerado automaticamente pelo Sistema de Análise Empresarial
                    """
                    
                    # Enviar email
                    with st.spinner("Enviando email..."):
                        if send_email(receiver_email, subject, email_content, sender_email):
                            st.success("Relatório enviado com sucesso!")
                            # Ocultar formulário após envio bem-sucedido
                            st.session_state[form_key]['show_form'] = False
                        else:
                            st.error("Falha ao enviar o email. Por favor, tente novamente.")
            
            # Botão para fechar o formulário
            if st.button(
                "❌ Cancelar",
                key=f"cancel_{form_key}",
                use_container_width=True
            ):
                st.session_state[form_key]['show_form'] = False
                st.rerun()