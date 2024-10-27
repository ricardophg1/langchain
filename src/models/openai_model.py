# src/models/openai_model.py

from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

def get_response(prompt):
    try:
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Obter a chave API
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("OpenAI API key não encontrada no arquivo .env")
            return None

        # Inicializar o cliente OpenAI
        client = OpenAI(api_key=api_key)
        
        # Fazer a chamada à API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um analista especializado em análises empresariais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"Erro ao conectar com a API da OpenAI: {str(e)}")
        st.error("Por favor, verifique sua conexão com a internet e suas credenciais.")
        return None