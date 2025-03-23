import os
from openai import OpenAI
import streamlit as st

def get_response(prompt: str) -> str:
    """Obtém resposta do modelo OpenAI"""
    try:
        api_key = st.session_state.get('openai_api_key')
        if not api_key:
            st.error("❌ Chave da API OpenAI não encontrada!")
            return None

        # Template do prompt
        system_prompt = """Você é um assistente especializado em análise empresarial, focado em métricas financeiras, comerciais e operacionais.
        - Sistema de análise empresarial que mostra KPIs, gráficos e insights
        - Possui módulos: Financeiro, Comercial, Operacional e Dashboard
        - Trabalha com métricas como receita, novos clientes, eficiência e NPS
        - Permite análise de dados por empresa, trimestre e ano
        
        Mantenha as respostas objetivas e profissionais, focando em análises práticas e recomendações baseadas em dados."""
        
        # Configura a chave da API
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Inicializa o cliente OpenAI da forma mais simples possível
        client = OpenAI()
        
        # Combina o contexto com a pergunta
        full_prompt = f"{system_prompt}\n\nPergunta: {prompt}\n\nResposta:"
        
        # Gera a resposta
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar resposta: {str(e)}")
        return None
