import streamlit as st

def create_email_button(content: str, params: dict):
    """Cria botão para envio de email
    
    Args:
        content (str): Conteúdo do email
        params (dict): Parâmetros para personalizar o email
    """
    if st.button(" Enviar por Email", use_container_width=True):
        try:
            # Aqui você pode implementar o envio real do email
            # Por enquanto, apenas simulamos o envio
            empresa = params.get('empresa', 'Empresa')
            periodo = params.get('periodo', 'Período')
            st.success(f" Relatório de {empresa} ({periodo}) enviado por email!")
            return True
        except Exception as e:
            st.error(f" Erro ao enviar email: {str(e)}")
            return False
    return False
