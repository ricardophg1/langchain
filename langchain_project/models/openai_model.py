import os
from openai import OpenAI
from langchain.prompts import PromptTemplate
import streamlit as st

def get_response(prompt: str) -> str:
    """Obtém resposta do modelo OpenAI"""
    
    # Template do prompt com contexto do projeto
    template = """Você é um assistente especializado em análise empresarial, focado em métricas financeiras, comerciais e operacionais.

    Contexto do Projeto:
    - Sistema de análise empresarial que mostra KPIs, gráficos e insights
    - Possui módulos: Financeiro, Comercial, Operacional e Dashboard
    - Trabalha com métricas como receita, novos clientes, eficiência e NPS
    - Permite análise de dados por empresa, trimestre e ano
    
    Regras de Resposta:
    1. Foque em análises e recomendações práticas relacionadas ao contexto fornecido
    2. Use dados e métricas específicas quando relevante
    3. Mantenha as respostas objetivas e profissionais
    4. Sugira ações concretas baseadas nas métricas disponíveis
    
    {input_prompt}
    
    Resposta:"""
    
    try:
        api_key = st.session_state.get('openai_api_key')
        if not api_key:
            st.error("❌ Chave da API OpenAI não encontrada!")
            st.info("Por favor, faça login novamente para recarregar a chave da API.")
            return "Erro: Chave da API OpenAI não configurada."
        
        # Cria o prompt
        prompt_template = PromptTemplate(
            input_variables=["input_prompt"],
            template=template
        )
        
        # Inicializa o cliente OpenAI
        client = OpenAI(api_key=api_key)
        
        # Formata o prompt
        formatted_prompt = prompt_template.format(input_prompt=prompt)
        
        # Gera a resposta
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em análise empresarial."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.7
        )
        
        # Retorna a resposta
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar resposta: {str(e)}")
        return f"Erro: {str(e)}"
