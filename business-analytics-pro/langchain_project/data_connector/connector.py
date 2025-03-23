import pandas as pd
import os
import sqlalchemy
from sqlalchemy import create_engine
import requests
from datetime import datetime
import logging
from typing import Optional, Dict, List, Any, Union

class DataConnector:
    """
    Classe responsável por conectar a plataforma a fontes de dados externas.
    Suporta conexões com bancos de dados, APIs e arquivos.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o conector de dados com configurações opcionais.
        
        Args:
            config: Dicionário com configurações de conexão
        """
        self.config = config or {}
        self.connections = {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Configura o logger para o conector"""
        logger = logging.getLogger("DataConnector")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
        
    def connect_to_database(self, connection_id: str, connection_string: str) -> bool:
        """
        Estabelece conexão com um banco de dados usando SQLAlchemy.
        
        Args:
            connection_id: Identificador único para a conexão
            connection_string: String de conexão SQLAlchemy
            
        Returns:
            bool: True se a conexão foi bem-sucedida, False caso contrário
        """
        try:
            engine = create_engine(connection_string)
            conn = engine.connect()
            self.connections[connection_id] = {
                'type': 'database',
                'engine': engine,
                'connection': conn
            }
            self.logger.info(f"Conexão com banco de dados estabelecida: {connection_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False
            
    def connect_to_api(self, connection_id: str, base_url: str, auth_params: Dict[str, Any]) -> bool:
        """
        Estabelece conexão com uma API externa.
        
        Args:
            connection_id: Identificador único para a conexão
            base_url: URL base da API
            auth_params: Parâmetros de autenticação (token, chaves, etc)
            
        Returns:
            bool: True se a conexão foi bem-sucedida, False caso contrário
        """
        try:
            # Teste de conexão com a API
            headers = {}
            if 'token' in auth_params:
                headers['Authorization'] = f"Bearer {auth_params['token']}"
            elif 'api_key' in auth_params:
                headers['X-API-Key'] = auth_params['api_key']
                
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()
            
            self.connections[connection_id] = {
                'type': 'api',
                'base_url': base_url,
                'auth_params': auth_params
            }
            self.logger.info(f"Conexão com API estabelecida: {connection_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar à API: {str(e)}")
            return False
            
    def import_from_csv(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Importa dados de um arquivo CSV.
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            DataFrame pandas ou None em caso de erro
        """
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Dados importados do CSV: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao importar CSV: {str(e)}")
            return None
            
    def import_from_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Importa dados de um arquivo Excel.
        
        Args:
            file_path: Caminho para o arquivo Excel
            sheet_name: Nome da planilha a ser importada (opcional)
            
        Returns:
            DataFrame pandas ou None em caso de erro
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            self.logger.info(f"Dados importados do Excel: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao importar Excel: {str(e)}")
            return None
            
    def query_database(self, connection_id: str, query: str) -> Optional[pd.DataFrame]:
        """
        Executa uma consulta SQL em um banco de dados conectado.
        
        Args:
            connection_id: Identificador da conexão
            query: Consulta SQL
            
        Returns:
            DataFrame pandas com o resultado ou None em caso de erro
        """
        if connection_id not in self.connections or self.connections[connection_id]['type'] != 'database':
            self.logger.error(f"Conexão de banco de dados não encontrada: {connection_id}")
            return None
            
        try:
            conn = self.connections[connection_id]['connection']
            df = pd.read_sql(query, conn)
            self.logger.info(f"Consulta executada com sucesso: {query[:50]}...")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao executar consulta: {str(e)}")
            return None
            
    def fetch_from_api(self, connection_id: str, endpoint: str, 
                       params: Optional[Dict[str, Any]] = None) -> Optional[pd.DataFrame]:
        """
        Busca dados de uma API conectada.
        
        Args:
            connection_id: Identificador da conexão
            endpoint: Endpoint específico da API
            params: Parâmetros da requisição
            
        Returns:
            DataFrame pandas com o resultado ou None em caso de erro
        """
        if connection_id not in self.connections or self.connections[connection_id]['type'] != 'api':
            self.logger.error(f"Conexão de API não encontrada: {connection_id}")
            return None
            
        try:
            base_url = self.connections[connection_id]['base_url']
            auth_params = self.connections[connection_id]['auth_params']
            
            headers = {}
            if 'token' in auth_params:
                headers['Authorization'] = f"Bearer {auth_params['token']}"
            elif 'api_key' in auth_params:
                headers['X-API-Key'] = auth_params['api_key']
                
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Tenta converter o resultado em DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'results' in data:
                df = pd.DataFrame(data['results'])
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
                
            self.logger.info(f"Dados obtidos da API: {endpoint}")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados da API: {str(e)}")
            return None
            
    def save_connection_config(self, config_path: str) -> bool:
        """
        Salva as configurações de conexão em um arquivo.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            
        Returns:
            bool: True se salvo com sucesso, False caso contrário
        """
        try:
            # Cria uma versão serializável das conexões
            serializable_connections = {}
            for conn_id, conn_data in self.connections.items():
                if conn_data['type'] == 'database':
                    serializable_connections[conn_id] = {
                        'type': 'database',
                        'connection_string': str(conn_data['engine'].url).replace('://', ':****@')  # Oculta senhas
                    }
                elif conn_data['type'] == 'api':
                    serializable_connections[conn_id] = {
                        'type': 'api',
                        'base_url': conn_data['base_url'],
                        'auth_params': {k: '****' for k in conn_data['auth_params'].keys()}  # Oculta credenciais
                    }
            
            # Salva configurações em formato JSON
            import json
            with open(config_path, 'w') as f:
                json.dump(serializable_connections, f, indent=4)
                
            self.logger.info(f"Configurações de conexão salvas em: {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
            return False
            
    def close_connections(self):
        """Fecha todas as conexões ativas"""
        for conn_id, conn_data in self.connections.items():
            try:
                if conn_data['type'] == 'database' and 'connection' in conn_data:
                    conn_data['connection'].close()
                    self.logger.info(f"Conexão fechada: {conn_id}")
            except Exception as e:
                self.logger.error(f"Erro ao fechar conexão {conn_id}: {str(e)}")
                
        self.connections = {}
        self.logger.info("Todas as conexões foram fechadas")

# Exemplos de uso:
# connector = DataConnector()
# connector.connect_to_database('mysql_prod', 'mysql://user:pass@localhost/dbname')
# df = connector.query_database('mysql_prod', 'SELECT * FROM customers LIMIT 100')
# 
# connector.connect_to_api('salesforce', 'https://api.salesforce.com/v1', {'token': 'xyz123'})
# leads_df = connector.fetch_from_api('salesforce', 'leads', {'status': 'open'})