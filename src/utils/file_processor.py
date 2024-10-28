# src/utils/file_processor.py

import pandas as pd
import json
import streamlit as st
from io import StringIO

def normalize_json_data(data):
    """Normaliza dados JSON complexos em um formato tabular"""
    if isinstance(data, list):
        # Se for uma lista de dicionários, converte diretamente
        return pd.json_normalize(data)
    elif isinstance(data, dict):
        # Se for um dicionário único, coloca em uma lista
        return pd.json_normalize([data])
    else:
        raise ValueError("Formato JSON não suportado")

def read_file(uploaded_file):
    """Lê diferentes tipos de arquivos e retorna um DataFrame"""
    if uploaded_file is None:
        return None
    
    try:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type == 'csv':
            return pd.read_csv(uploaded_file)
        elif file_type == 'json':
            # Ler o conteúdo do arquivo JSON
            content = uploaded_file.getvalue().decode('utf-8')
            json_data = json.loads(content)
            
            try:
                # Tentar normalizar os dados JSON
                df = normalize_json_data(json_data)
                
                # Se o DataFrame estiver vazio ou tiver estrutura inválida
                if df.empty or len(df.columns) == 0:
                    raise ValueError("Estrutura JSON inválida para conversão")
                
                return df
            
            except Exception as json_error:
                st.error(f"Erro ao processar JSON: {str(json_error)}")
                st.info("Por favor, verifique se o arquivo JSON está no formato adequado:")
                st.code("""
                # Formato esperado:
                [
                    {
                        "campo1": "valor1",
                        "campo2": "valor2"
                    },
                    {
                        "campo1": "valor3",
                        "campo2": "valor4"
                    }
                ]
                # ou
                {
                    "campo1": "valor1",
                    "campo2": "valor2"
                }
                """)
                return None
                
        elif file_type == 'txt':
            content = StringIO(uploaded_file.getvalue().decode("utf-8"))
            return pd.read_csv(content, sep='\t')
        else:
            st.error(f"Formato de arquivo não suportado: {file_type}")
            return None
            
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {str(e)}")
        return None

def preview_data(df):
    """Gera uma visualização prévia dos dados de forma segura"""
    if df is None:
        return None
    
    try:
        # Limitar o número de linhas e colunas para preview
        max_rows = 5
        max_cols = 10
        
        preview_df = df.head(max_rows)
        
        # Se houver muitas colunas, mostrar apenas as primeiras
        if len(preview_df.columns) > max_cols:
            preview_df = preview_df.iloc[:, :max_cols]
            st.info(f"Mostrando apenas as primeiras {max_cols} colunas de {len(df.columns)} no total.")
        
        # Converter tipos complexos para string
        for col in preview_df.columns:
            if preview_df[col].dtype == 'object':
                preview_df[col] = preview_df[col].astype(str)
        
        return preview_df
    
    except Exception as e:
        st.error(f"Erro ao gerar preview: {str(e)}")
        return None

def analyze_data(df):
    """Analisa os dados importados e sugere área apropriada"""
    if df is None:
        return None
    
    try:
        columns = set(str(col).lower() for col in df.columns)
        
        # Palavras-chave para cada área
        financial_keywords = {'receita', 'custo', 'lucro', 'despesa', 'revenue', 'cost', 'profit', 'expense', 'ebitda'}
        commercial_keywords = {'venda', 'cliente', 'produto', 'sales', 'customer', 'product', 'nps', 'marketing'}
        operational_keywords = {'produção', 'estoque', 'qualidade', 'production', 'stock', 'quality', 'maintenance'}
        
        # Contagem de palavras-chave encontradas
        financial_count = len(columns.intersection(financial_keywords))
        commercial_count = len(columns.intersection(commercial_keywords))
        operational_count = len(columns.intersection(operational_keywords))
        
        # Retorna a área com mais palavras-chave encontradas
        counts = {
            'Financeiro': financial_count,
            'Comercial': commercial_count,
            'Operacional': operational_count
        }
        
        suggested_area = max(counts, key=counts.get)
        return suggested_area if max(counts.values()) > 0 else 'Financeiro'  # Default para Financeiro
        
    except Exception:
        return 'Financeiro'  # Em caso de erro, retorna área padrão