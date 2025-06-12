import pandas as pd
import requests
import logging
from typing import Dict, Any, Optional, List, Union
import json
import os
from datetime import datetime, timedelta

class IntegrationManager:
    """
    Gerenciador de integrações com sistemas ERP e CRM populares.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.integrations = {}
        self.credentials = {}
        
    def _setup_logger(self):
        """Configura o logger para o gerenciador de integrações"""
        logger = logging.getLogger("IntegrationManager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
        
    def load_credentials(self, credentials_path: str) -> bool:
        """
        Carrega credenciais de autenticação de sistemas externos.
        
        Args:
            credentials_path: Caminho para o arquivo de credenciais (JSON)
            
        Returns:
            bool: True se carregado com sucesso, False caso contrário
        """
        try:
            with open(credentials_path, 'r') as f:
                self.credentials = json.load(f)
            self.logger.info(f"Credenciais carregadas: {len(self.credentials)} sistemas configurados")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar credenciais: {str(e)}")
            return False
            
    def configure_salesforce(self, client_id: str, client_secret: str, 
                           username: str, password: str, security_token: str) -> bool:
        """
        Configura integração com Salesforce.
        
        Args:
            client_id: ID do cliente (Consumer Key)
            client_secret: Segredo do cliente (Consumer Secret)
            username: Nome de usuário Salesforce
            password: Senha Salesforce
            security_token: Token de segurança
            
        Returns:
            bool: True se configurado com sucesso, False caso contrário
        """
        try:
            # Autenticação com Salesforce
            auth_url = "https://login.salesforce.com/services/oauth2/token"
            payload = {
                'grant_type': 'password',
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': password + security_token
            }
            
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            
            auth_data = response.json()
            
            self.integrations['salesforce'] = {
                'type': 'salesforce',
                'instance_url': auth_data['instance_url'],
                'access_token': auth_data['access_token'],
                'token_type': auth_data['token_type'],
                'expires_at': datetime.now() + timedelta(seconds=auth_data['expires_in'])
            }
            
            self.credentials['salesforce'] = {
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': '********',  # Não armazenar senha em texto plano
                'security_token': '********'  # Não armazenar token em texto plano
            }
            
            self.logger.info("Integração com Salesforce configurada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao configurar Salesforce: {str(e)}")
            return False
            
    def configure_sap(self, base_url: str, username: str, password: str, client: str) -> bool:
        """
        Configura integração com SAP.
        
        Args:
            base_url: URL base do serviço SAP OData
            username: Nome de usuário SAP
            password: Senha SAP
            client: Número do cliente SAP
            
        Returns:
            bool: True se configurado com sucesso, False caso contrário
        """
        try:
            # Teste de autenticação com SAP
            headers = {
                'x-csrf-token': 'Fetch'
            }
            
            session = requests.Session()
            session.auth = (username, password)
            session.headers.update({
                'sap-client': client
            })
            
            response = session.get(f"{base_url.rstrip('/')}/csrf-token", headers=headers)
            response.raise_for_status()
            
            csrf_token = response.headers.get('x-csrf-token')
            
            self.integrations['sap'] = {
                'type': 'sap',
                'base_url': base_url,
                'session': session,
                'csrf_token': csrf_token,
                'client': client
            }
            
            self.credentials['sap'] = {
                'base_url': base_url,
                'username': username,
                'password': '********',  # Não armazenar senha em texto plano
                'client': client
            }
            
            self.logger.info("Integração com SAP configurada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao configurar SAP: {str(e)}")
            return False
            
    def configure_totvs(self, base_url: str, username: str, password: str, 
                       company_id: str, branch_id: str) -> bool:
        """
        Configura integração com TOTVS Protheus.
        
        Args:
            base_url: URL base da API REST
            username: Nome de usuário
            password: Senha
            company_id: Código da empresa
            branch_id: Código da filial
            
        Returns:
            bool: True se configurado com sucesso, False caso contrário
        """
        try:
            # Autenticação com TOTVS Protheus
            auth_url = f"{base_url.rstrip('/')}/api/oauth2/v1/token"
            headers = {
                'Content-Type': 'application/json'
            }
            payload = {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
            
            response = requests.post(auth_url, headers=headers, json=payload)
            response.raise_for_status()
            
            auth_data = response.json()
            
            self.integrations['totvs'] = {
                'type': 'totvs',
                'base_url': base_url,
                'access_token': auth_data['access_token'],
                'token_type': auth_data['token_type'],
                'expires_at': datetime.now() + timedelta(seconds=auth_data['expires_in']),
                'company_id': company_id,
                'branch_id': branch_id
            }
            
            self.credentials['totvs'] = {
                'base_url': base_url,
                'username': username,
                'password': '********',  # Não armazenar senha em texto plano
                'company_id': company_id,
                'branch_id': branch_id
            }
            
            self.logger.info("Integração com TOTVS configurada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao configurar TOTVS: {str(e)}")
            return False
            
    def get_salesforce_data(self, object_name: str, fields: List[str] = None, 
                           filters: str = None, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtém dados do Salesforce.
        
        Args:
            object_name: Nome do objeto (Lead, Account, etc)
            fields: Lista de campos a serem retornados
            filters: Condições de filtro (WHERE)
            limit: Limite de registros
            
        Returns:
            DataFrame com os dados ou None em caso de erro
        """
        if 'salesforce' not in self.integrations:
            self.logger.error("Integração com Salesforce não configurada")
            return None
            
        try:
            integration = self.integrations['salesforce']
            
            # Verificar se o token expirou
            if datetime.now() >= integration['expires_at']:
                self.logger.info("Token do Salesforce expirado, renovando...")
                salesforce_creds = self.credentials['salesforce']
                self.configure_salesforce(
                    salesforce_creds['client_id'],
                    salesforce_creds['client_secret'],
                    salesforce_creds['username'],
                    '********',  # Senha não está armazenada em texto plano
                    '********'   # Token não está armazenado em texto plano
                )
                integration = self.integrations['salesforce']
            
            # Construir consulta SOQL
            fields_str = ", ".join(fields) if fields else "Id, Name, CreatedDate"
            query = f"SELECT {fields_str} FROM {object_name}"
            
            if filters:
                query += f" WHERE {filters}"
                
            query += f" LIMIT {limit}"
            
            # Codificar a consulta para URL
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            
            # Fazer a requisição
            url = f"{integration['instance_url']}/services/data/v52.0/query?q={encoded_query}"
            headers = {
                'Authorization': f"{integration['token_type']} {integration['access_token']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if 'records' in data:
                df = pd.DataFrame(data['records'])
                if 'attributes' in df.columns:
                    df = df.drop('attributes', axis=1)
                self.logger.info(f"Dados obtidos do Salesforce: {len(df)} registros de {object_name}")
                return df
            else:
                self.logger.warning(f"Nenhum registro encontrado para {object_name}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do Salesforce: {str(e)}")
            return None
            
    def get_sap_data(self, entity: str, filters: Dict[str, Any] = None, 
                    top: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtém dados do SAP via OData.
        
        Args:
            entity: Nome da entidade (ex: SalesOrderSet)
            filters: Dicionário com filtros
            top: Número máximo de registros
            
        Returns:
            DataFrame com os dados ou None em caso de erro
        """
        if 'sap' not in self.integrations:
            self.logger.error("Integração com SAP não configurada")
            return None
            
        try:
            integration = self.integrations['sap']
            session = integration['session']
            
            # Construir URL
            url = f"{integration['base_url'].rstrip('/')}/{entity}"
            
            params = {
                '$top': top,
                '$format': 'json'
            }
            
            # Adicionar filtros se existirem
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        filter_parts.append(f"{key} eq '{value}'")
                    else:
                        filter_parts.append(f"{key} eq {value}")
                        
                if filter_parts:
                    params['$filter'] = " and ".join(filter_parts)
            
            # Fazer a requisição
            response = session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'd' in data and 'results' in data['d']:
                df = pd.DataFrame(data['d']['results'])
                self.logger.info(f"Dados obtidos do SAP: {len(df)} registros de {entity}")
                return df
            else:
                self.logger.warning(f"Nenhum registro encontrado para {entity}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do SAP: {str(e)}")
            return None
            
    def get_totvs_data(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[pd.DataFrame]:
        """
        Obtém dados do TOTVS Protheus.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            DataFrame com os dados ou None em caso de erro
        """
        if 'totvs' not in self.integrations:
            self.logger.error("Integração com TOTVS não configurada")
            return None
            
        try:
            integration = self.integrations['totvs']
            
            # Verificar se o token expirou
            if datetime.now() >= integration['expires_at']:
                self.logger.info("Token do TOTVS expirado, renovando...")
                totvs_creds = self.credentials['totvs']
                self.configure_totvs(
                    totvs_creds['base_url'],
                    totvs_creds['username'],
                    '********',  # Senha não está armazenada em texto plano
                    totvs_creds['company_id'],
                    totvs_creds['branch_id']
                )
                integration = self.integrations['totvs']
            
            # Construir URL e parâmetros
            url = f"{integration['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
            
            headers = {
                'Authorization': f"{integration['token_type']} {integration['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Adicionar informações da empresa/filial aos parâmetros
            request_params = params.copy() if params else {}
            request_params['company'] = integration['company_id']
            request_params['branch'] = integration['branch_id']
            
            # Fazer a requisição
            response = requests.get(url, headers=headers, params=request_params)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
                self.logger.info(f"Dados obtidos do TOTVS: {len(df)} registros de {endpoint}")
                return df
            elif isinstance(data, dict) and 'items' in data:
                df = pd.DataFrame(data['items'])
                self.logger.info(f"Dados obtidos do TOTVS: {len(df)} registros de {endpoint}")
                return df
            else:
                self.logger.warning(f"Formato de dados inesperado de {endpoint}")
                return pd.DataFrame([data])
                
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do TOTVS: {str(e)}")
            return None
            
    def get_financial_data(self, source: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Obtém dados financeiros padronizados independente da fonte.
        
        Args:
            source: Fonte de dados ('salesforce', 'sap', 'totvs')
            start_date: Data inicial (formato: 'YYYY-MM-DD')
            end_date: Data final (formato: 'YYYY-MM-DD')
            
        Returns:
            DataFrame com os dados financeiros padronizados ou None em caso de erro
        """
        try:
            if source == 'salesforce':
                # Obter dados de oportunidades do Salesforce
                df = self.get_salesforce_data(
                    object_name='Opportunity',
                    fields=['Id', 'Name', 'Amount', 'CloseDate', 'StageName', 'Type'],
                    filters=f"CloseDate >= {start_date} AND CloseDate <= {end_date}",
                    limit=1000
                )
                
                if df is not None and not df.empty:
                    # Padronizar colunas
                    df = df.rename(columns={
                        'Amount': 'Receita',
                        'CloseDate': 'Data',
                        'StageName': 'Status',
                        'Type': 'Tipo'
                    })
                    df['Fonte'] = 'Salesforce'
                    
                    return df
                    
            elif source == 'sap':
                # Obter dados financeiros do SAP
                df = self.get_sap_data(
                    entity='SalesOrderSet',
                    filters={
                        'CreationDate': f"ge datetime'{start_date}T00:00:00' and le datetime'{end_date}T23:59:59'"
                    },
                    top=1000
                )
                
                if df is not None and not df.empty:
                    # Padronizar colunas
                    df = df.rename(columns={
                        'GrossAmount': 'Receita',
                        'CreationDate': 'Data',
                        'Status': 'Status'
                    })
                    df['Fonte'] = 'SAP'
                    
                    return df
                    
            elif source == 'totvs':
                # Obter dados financeiros do TOTVS
                df = self.get_totvs_data(
                    endpoint='api/financial/v1/invoices',
                    params={
                        'dateFrom': start_date,
                        'dateTo': end_date
                    }
                )
                
                if df is not None and not df.empty:
                    # Padronizar colunas
                    df = df.rename(columns={
                        'grossValue': 'Receita',
                        'issueDate': 'Data',
                        'status': 'Status'
                    })
                    df['Fonte'] = 'TOTVS'
                    
                    return df
            
            self.logger.error(f"Fonte de dados não suportada: {source}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter dados financeiros: {str(e)}")
            return None
            
    def get_sales_data(self, source: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Obtém dados de vendas padronizados independente da fonte.
        
        Args:
            source: Fonte de dados ('salesforce', 'sap', 'totvs')
            start_date: Data inicial (formato: 'YYYY-MM-DD')
            end_date: Data final (formato: 'YYYY-MM-DD')
            
        Returns:
            DataFrame com os dados de vendas padronizados ou None em caso de erro
        """
        # Implementação semelhante ao get_financial_data, adaptada para dados de vendas
        pass
        
    def get_operational_data(self, source: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Obtém dados operacionais padronizados independente da fonte.
        
        Args:
            source: Fonte de dados ('salesforce', 'sap', 'totvs')
            start_date: Data inicial (formato: 'YYYY-MM-DD')
            end_date: Data final (formato: 'YYYY-MM-DD')
            
        Returns:
            DataFrame com os dados operacionais padronizados ou None em caso de erro
        """
        try:
            if source == 'sap':
                # Obter dados de produção do SAP
                df = self.get_sap_data(
                    entity='ProductionOrderSet',
                    filters={
                        'CreationDate': f"ge datetime'{start_date}T00:00:00' and le datetime'{end_date}T23:59:59'"
                    },
                    top=1000
                )
                
                if df is not None and not df.empty:
                    # Padronizar colunas
                    df = df.rename(columns={
                        'Quantity': 'Produção',
                        'CreationDate': 'Data',
                        'Status': 'Status',
                        'Efficiency': 'Eficiência'
                    })
                    df['Fonte'] = 'SAP'
                    
                    return df
                    
            elif source == 'totvs':
                # Obter dados operacionais do TOTVS
                df = self.get_totvs_data(
                    endpoint='api/manufacturing/v1/production',
                    params={
                        'dateFrom': start_date,
                        'dateTo': end_date
                    }
                )
                
                if df is not None and not df.empty:
                    # Padronizar colunas
                    df = df.rename(columns={
                        'quantity': 'Produção',
                        'date': 'Data',
                        'status': 'Status',
                        'efficiency': 'Eficiência'
                    })
                    df['Fonte'] = 'TOTVS'
                    
                    return df
            
            self.logger.error(f"Fonte de dados não suportada para dados operacionais: {source}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter dados operacionais: {str(e)}")
            return None
            
    def save_to_cache(self, data_id: str, df: pd.DataFrame, expiry_hours: int = 24) -> bool:
        """
        Salva dados em cache para acesso mais rápido.
        
        Args:
            data_id: Identificador único dos dados
            df: DataFrame para armazenar em cache
            expiry_hours: Tempo de expiração em horas
            
        Returns:
            bool: True se salvo com sucesso, False caso contrário
        """
        try:
            cache_dir = os.path.join(os.getcwd(), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_file = os.path.join(cache_dir, f"{data_id}.pkl")
            
            # Salvar DataFrame e metadados de expiração
            metadata = {
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=expiry_hours)).isoformat(),
                'rows': len(df),
                'columns': list(df.columns)
            }
            
            # Salvar metadados separadamente
            with open(f"{cache_file}.meta", 'w') as f:
                json.dump(metadata, f)
                
            # Salvar DataFrame
            df.to_pickle(cache_file)
            
            self.logger.info(f"Dados salvos em cache: {data_id} ({len(df)} registros)")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados em cache: {str(e)}")
            return False
            
    def load_from_cache(self, data_id: str) -> Optional[pd.DataFrame]:
        """
        Carrega dados do cache se ainda forem válidos.
        
        Args:
            data_id: Identificador único dos dados
            
        Returns:
            DataFrame ou None se expirado ou não encontrado
        """
        try:
            cache_dir = os.path.join(os.getcwd(), 'cache')
            cache_file = os.path.join(cache_dir, f"{data_id}.pkl")
            meta_file = f"{cache_file}.meta"
            
            if not os.path.exists(cache_file) or not os.path.exists(meta_file):
                self.logger.info(f"Cache não encontrado para: {data_id}")
                return None
                
            # Verificar expiração
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
                
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.now() > expires_at:
                self.logger.info(f"Cache expirado para: {data_id}")
                return None
                
            # Carregar dados
            df = pd.read_pickle(cache_file)
            self.logger.info(f"Dados carregados do cache: {data_id} ({len(df)} registros)")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados do cache: {str(e)}")
            return None
