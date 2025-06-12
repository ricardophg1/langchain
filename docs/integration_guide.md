# Guia de Integracao

Este guia apresenta os passos basicos para conectar a plataforma **Business Analytics AI** a sistemas externos.

## Pre-requisitos
- Python 3.9 ou superior
- Chave de API da OpenAI
- Credenciais de acesso aos sistemas que serao integrados (ERP, CRM, bancos de dados)

## Etapas Principais
1. Instale as dependencias do projeto:
   ```bash
   pip install -r requirements/prod.txt
   ```
2. Defina as variaveis de ambiente necessarias:
   ```env
   OPENAI_API_KEY=<sua_chave_aqui>
   DB_URI=<string_de_conexao>
   ```
3. Configure as fontes de dados em `config/integrations.yml`.
4. Execute a aplicacao para validar a integracao:
   ```bash
   streamlit run langchain_project/main.py
   ```

Com esses passos sua instalacao estara pronta para se comunicar com as principais ferramentas do seu negocio.
