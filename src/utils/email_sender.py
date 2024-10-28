import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import os

def send_email(receiver_email, subject, content, sender_email=None):
    """Envia email com o relatório"""
    try:
        # Configurações do email
        smtp_server = "smtp.gmail.com"  # Ajuste conforme seu servidor de email
        smtp_port = 587
        
        # Usar email padrão se não fornecido
        sender_email = sender_email or os.getenv('DEFAULT_SENDER_EMAIL')
        sender_password = os.getenv('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            st.error("Configurações de email não encontradas.")
            return False
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        # Adicionar corpo do email
        msg.attach(MIMEText(content, 'markdown'))
        
        # Conectar ao servidor e enviar
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao enviar email: {str(e)}")
        return False