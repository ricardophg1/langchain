FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements/prod.txt requirements/prod.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copiar o resto dos arquivos
COPY . /app/

# Configurar variáveis de ambiente Python
ENV PYTHONPATH=/app

# Instalar o pacote em modo de desenvolvimento
RUN pip install -e .

# Expor a porta do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "langchain_project/main.py", "--server.address", "0.0.0.0"]