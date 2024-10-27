import streamlit as st
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate  # Importando PromptTemplate
from pages.financeiro import dados_financeiros  # Importando a função dados_financeiros
from src.models.openai_model import get_response

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("A chave OPENAI_API_KEY não foi encontrada no arquivo .env.")

# Template para o prompt
template = '''
Você é um analista financeiro.
Escreva um relatório financeiro detalhado para a empresa "{empresa}" para o período {periodo}.
O relatório deve ser escrito em {idioma} e incluir a seguinte análise:
{analise}
{dados_financeiros}
Certifique-se de fornecer insights e conclusões para esta seção.
Formate o relatório utilizando Markdown.
'''

# Criar o template do prompt
prompt_template = PromptTemplate.from_template(template=template)

# Listas de opções
empresas = ['ACME Corp', 'Globex Corporation', 'Soylent Corp', 'Initech', 'Umbrella Corporation']
trimestres = ['Q1', 'Q2', 'Q3', 'Q4']
anos = [2021, 2022, 2023, 2024]
idiomas = ['Português', 'Inglês', 'Espanhol', 'Francês', 'Alemão']
analises = [
    "Análise do Balanço Patrimonial",
    "Análise do Fluxo de Caixa",
    "Análise de Tendências",
    "Análise de Receita e Lucro",
    "Análise de Posição de Mercado",
    "Análise de Dados Financeiros"  # Adicionando a opção de análise de dados financeiros
]

def main():
    # Interface do Streamlit
    st.title('Gerador de Relatório Financeiro:')
    empresa = st.selectbox('Selecione a empresa:', empresas)
    trimestre = st.selectbox('Selecione o trimestre:', trimestres)
    ano = st.selectbox('Selecione o ano:', anos)
    periodo = f"{trimestre} {ano}"
    idioma = st.selectbox('Selecione o idioma:', idiomas)
    analise = st.selectbox('Selecione a análise:', analises)

    if st.button('Gerar Relatório'):
        # Incluir dados financeiros se a análise selecionada for "Análise de Dados Financeiros"
        if analise == "Análise de Dados Financeiros":
            dados = dados_financeiros(empresa, periodo)  # Supondo que a função dados_financeiros recebe a empresa e o período como parâmetros
            dados_financeiros_texto = f"\n\nDados Financeiros:\n{dados}"
        else:
            dados_financeiros_texto = ""

        prompt = prompt_template.format(
            empresa=empresa,
            periodo=periodo,
            idioma=idioma,
            analise=analise,
            dados_financeiros=dados_financeiros_texto
        )
        response = get_response(prompt)
        st.subheader('Relatório Gerado:')
        st.write(response)

if __name__ == '__main__':
    main()