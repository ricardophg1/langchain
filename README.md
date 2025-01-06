# Sistema de Análise Empresarial com LangChain e OpenAI

Um sistema avançado de análise empresarial que utiliza LangChain e OpenAI para fornecer análises detalhadas e insights valiosos sobre diferentes aspectos do negócio.

## Funcionalidades

### Sistema de Autenticação

- Login seguro com usuário e senha
- Proteção de rotas e conteúdo
- Gerenciamento de sessão de usuário
- Armazenamento seguro de credenciais

### Análise Comercial

- Visualização de dados comerciais detalhados
- Gráficos interativos com Plotly
- Análise de diferentes métricas:
  - Vendas por Canal
  - Performance de Produtos
  - Análise de Clientes
  - Eficiência da Força de Vendas
  - Market Share
- Exportação de dados em CSV
- Geração de relatórios em diferentes idiomas

### Análise Financeira

- Indicadores financeiros chave
- Análise de rentabilidade
- Fluxo de caixa
- Projeções financeiras

### Dashboard

- Visão geral do negócio
- KPIs principais
- Gráficos e métricas em tempo real

### Análise Operacional

- Eficiência operacional
- Gestão de recursos
- Indicadores de produtividade

### Chat com IA

- Assistente virtual integrado
- Análises contextualizadas
- Suporte em múltiplos idiomas
- Geração de relatórios personalizados

## Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python
- **IA**: OpenAI, LangChain
- **Visualização**: Plotly
- **Análise de Dados**: Pandas, StatsModels

## Dependências

```env
streamlit==1.29.0
langchain==0.0.350
langchain-openai==0.0.2.post1
openai==1.6.1
python-dotenv==1.0.0
plotly==5.18.0
pandas==2.1.4
statsmodels==0.14.1
```

## Como Executar

1. Clone o repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd langchain
```

1. Configure o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

1. Instale as dependências

```bash
pip install -r requirements/prod.txt
```

1. Configure as variáveis de ambiente

- Crie um arquivo `.env` na raiz do projeto
- Adicione suas credenciais:

```env
OPENAI_API_KEY=sua_chave_api
APP_USERNAME=seu_usuario
APP_PASSWORD=sua_senha
```

1. Execute a aplicação

```bash
streamlit run langchain_project/main.py
```

## Segurança

- Autenticação obrigatória para acesso
- Credenciais armazenadas em variáveis de ambiente
- Proteção contra acesso não autorizado
- Sessão segura com Streamlit

## Interface

- Design responsivo
- Interface intuitiva
- Navegação simplificada
- Temas claros e escuros

## Visualizações

- Gráficos interativos
- Dashboards dinâmicos
- Exportação de dados
- Relatórios personalizados

## Suporte a Idiomas

- Português
- Inglês
- Espanhol
- Francês
- Alemão

## Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de submeter pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para questões e suporte, por favor abra uma issue no repositório.
