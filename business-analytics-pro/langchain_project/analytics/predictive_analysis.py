import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class PredictiveAnalysis:
    """
    Classe para análise preditiva de dados empresariais.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.models = {}
        self.scalers = {}
        
    def _setup_logger(self):
        """Configura o logger para a análise preditiva"""
        logger = logging.getLogger("PredictiveAnalysis")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
        
    def forecast_time_series(self, df: pd.DataFrame, date_column: str, value_column: str, 
                             periods: int = 12, frequency: str = 'M', 
                             model_type: str = 'arima') -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Realiza previsão de série temporal.
        
        Args:
            df: DataFrame com os dados históricos
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor a ser previsto
            periods: Número de períodos para previsão
            frequency: Frequência dos dados ('D', 'W', 'M', 'Q', 'Y')
            model_type: Tipo de modelo ('arima', 'sarima')
            
        Returns:
            Tuple contendo DataFrame com os dados históricos e previsões,
            e dicionário com métricas do modelo
        """
        try:
            # Garantir que a coluna de data seja datetime
            df = df.copy()
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Ordenar por data
            df = df.sort_values(date_column)
            
            # Criar série temporal
            ts = df.set_index(date_column)[value_column]
            
            # Verificar e lidar com valores faltantes
            if ts.isnull().any():
                ts = ts.interpolate(method='linear')
            
            # Escolher e treinar modelo
            if model_type == 'arima':
                # Parâmetros simples para ARIMA (p,d,q)
                model = ARIMA(ts, order=(5, 1, 0))
                fitted_model = model.fit()
                
                # Fazer previsão
                forecast = fitted_model.forecast(steps=periods)
                forecast_index = pd.date_range(start=ts.index[-1] + pd.Timedelta(days=1), 
                                             periods=periods, freq=frequency)
                forecast_series = pd.Series(forecast, index=forecast_index)
                
                # Avaliar modelo com os últimos 20% dos dados
                train_size = int(len(ts) * 0.8)
                train, test = ts[:train_size], ts[train_size:]
                
                # Treinar modelo de avaliação
                eval_model = ARIMA(train, order=(5, 1, 0))
                eval_fitted = eval_model.fit()
                
                # Prever período de teste
                eval_forecast = eval_fitted.forecast(steps=len(test))
                
                # Calcular métricas
                mae = mean_absolute_error(test, eval_forecast)
                rmse = np.sqrt(mean_squared_error(test, eval_forecast))
                
                # Calcular erro percentual médio
                mape = np.mean(np.abs((test - eval_forecast) / test)) * 100
                
                metrics = {
                    'mae': mae,
                    'rmse': rmse,
                    'mape': mape
                }
                
                # Juntar dados históricos e previsão
                result_df = pd.DataFrame({
                    'data': pd.concat([ts.index, forecast_index]),
                    'valor': pd.concat([ts, forecast_series]),
                    'tipo': ['histórico'] * len(ts) + ['previsão'] * len(forecast)
                })
                
                self.logger.info(f"Previsão de série temporal concluída: {periods} períodos")
                return result_df, metrics
                
            else:
                self.logger.error(f"Tipo de modelo não suportado: {model_type}")
                return None, {}
                
        except Exception as e:
            self.logger.error(f"Erro na previsão de série temporal: {str(e)}")
            return None, {}
    
    def train_prediction_model(self, df: pd.DataFrame, target_column: str, 
                              feature_columns: List[str], model_id: str) -> Dict[str, float]:
        """
        Treina modelo preditivo para variável alvo com base em features.
        
        Args:
            df: DataFrame com os dados
            target_column: Nome da coluna alvo
            feature_columns: Lista de colunas de features
            model_id: Identificador único para o modelo
            
        Returns:
            Dicionário com métricas do modelo
        """
        try:
            # Preparar dados
            X = df[feature_columns].copy()
            y = df[target_column].copy()
            
            # Lidar com valores faltantes
            X = X.fillna(X.mean())
            
            # Normalizar features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Dividir em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Treinar modelo
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Avaliar modelo
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # Salvar modelo e scaler
            self.models[model_id] = model
            self.scalers[model_id] = scaler
            
            metrics = {
                'mae': mae,
                'rmse': rmse,
                'r2': r2
            }
            
            # Calcular importância de features
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            metrics['feature_importance'] = feature_importance
            
            self.logger.info(f"Modelo preditivo treinado: {model_id}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo preditivo: {str(e)}")
            return {}
    
    def predict(self, df: pd.DataFrame, model_id: str, 
               feature_columns: List[str]) -> Optional[np.ndarray]:
        """
        Faz previsões usando modelo treinado.
        
        Args:
            df: DataFrame com os dados de entrada
            model_id: Identificador do modelo
            feature_columns: Lista de colunas de features
            
        Returns:
            Array com as previsões ou None em caso de erro
        """
        try:
            if model_id not in self.models or model_id not in self.scalers:
                self.logger.error(f"Modelo não encontrado: {model_id}")
                return None
                
            # Preparar dados
            X = df[feature_columns].copy()
            X = X.fillna(X.mean())
            
            # Normalizar features
            X_scaled = self.scalers[model_id].transform(X)
            
            # Fazer previsão
            predictions = self.models[model_id].predict(X_scaled)
            
            self.logger.info(f"Previsões realizadas com modelo {model_id}: {len(predictions)} registros")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer previsões: {str(e)}")
            return None
    
    def detect_anomalies(self, df: pd.DataFrame, column: str, 
                        method: str = 'std', threshold: float = 3.0) -> pd.DataFrame:
        """
        Detecta anomalias em uma série de dados.
        
        Args:
            df: DataFrame com os dados
            column: Nome da coluna para analisar
            method: Método de detecção ('std', 'iqr')
            threshold: Limiar para considerar anomalia
            
        Returns:
            DataFrame com flag de anomalia
        """
        try:
            result_df = df.copy()
            values = result_df[column].values
            
            if method == 'std':
                # Método de desvio padrão
                mean = np.mean(values)
                std = np.std(values)
                
                # Marcar anomalias
                result_df['anomalia'] = (np.abs(values - mean) > threshold * std)
                result_df['score'] = np.abs(values - mean) / std
                
            elif method == 'iqr':
                # Método de amplitude interquartil
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                
                # Marcar anomalias
                result_df['anomalia'] = (values < lower_bound) | (values > upper_bound)
                
                # Calcular score normalizado
                distance = np.maximum(lower_bound - values, values - upper_bound)
                result_df['score'] = np.where(result_df['anomalia'], distance / iqr, 0)
                
            else:
                self.logger.error(f"Método de detecção de anomalias não suportado: {method}")
                return df
                
            # Contar anomalias
            anomaly_count = result_df['anomalia'].sum()
            self.logger.info(f"Detecção de anomalias concluída: {anomaly_count} anomalias encontradas")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de anomalias: {str(e)}")
            return df
    
    def analyze_trend(self, df: pd.DataFrame, date_column: str, 
                    value_column: str, frequency: str = 'M') -> Dict[str, Any]:
        """
        Analisa tendência em série temporal.
        
        Args:
            df: DataFrame com os dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            frequency: Frequência dos dados ('D', 'W', 'M', 'Q', 'Y')
            
        Returns:
            Dicionário com componentes de tendência e sazonalidade
        """
        try:
            # Garantir que a coluna de data seja datetime
            df = df.copy()
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Criar série temporal com frequência especificada
            ts = df.set_index(date_column)[value_column]
            ts = ts.asfreq(frequency)
            
            # Lidar com valores faltantes se necessário
            if ts.isnull().any():
                ts = ts.interpolate(method='linear')
                
            # Calcular estatísticas de tendência
            rolling_mean = ts.rolling(window=min(6, len(ts))).mean()
            
            # Calcular crescimento percentual
            total_growth = ((ts.iloc[-1] / ts.iloc[0]) - 1) * 100 if len(ts) > 1 else 0
            
            # Calcular taxa média de crescimento
            periods = len(ts) - 1
            avg_growth_rate = (np.power(ts.iloc[-1] / ts.iloc[0], 1/periods) - 1) * 100 if periods > 0 else 0
            
            # Calcular direção da tendência (últimos 3 períodos)
            recent_periods = min(3, len(ts))
            recent_trend = ts.iloc[-recent_periods:].values
            
            if len(recent_trend) >= 2:
                if recent_trend[-1] > recent_trend[0]:
                    trend_direction = "crescente"
                elif recent_trend[-1] < recent_trend[0]:
                    trend_direction = "decrescente"
                else:
                    trend_direction = "estável"
            else:
                trend_direction = "indeterminado"
                
            # Decomposição sazonal se houver dados suficientes
            seasonality = None
            if len(ts) >= 2 * int(frequency.replace('M', '12').replace('Q', '4').replace('Y', '1')):
                try:
                    decomposition = seasonal_decompose(ts, model='additive')
                    seasonality = {
                        'trend': decomposition.trend.dropna().tolist(),
                        'seasonal': decomposition.seasonal.dropna().tolist(),
                        'resid': decomposition.resid.dropna().tolist()
                    }
                except Exception as e:
                    self.logger.warning(f"Não foi possível realizar decomposição sazonal: {str(e)}")
            
            result = {
                'total_growth_pct': total_growth,
                'avg_growth_rate_pct': avg_growth_rate,
                'trend_direction': trend_direction,
                'rolling_mean': rolling_mean.dropna().tolist(),
                'seasonality': seasonality
            }
            
            self.logger.info(f"Análise de tendência concluída: {trend_direction}, crescimento total de {total_growth:.2f}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na análise de tendência: {str(e)}")
            return {}
    
    def market_basket_analysis(self, transactions: pd.DataFrame, 
                              item_column: str, transaction_column: str, 
                              min_support: float = 0.01) -> Dict[str, Any]:
        """
        Realiza análise de cesta de compras (MBA).
        
        Args:
            transactions: DataFrame com as transações
            item_column: Nome da coluna de itens
            transaction_column: Nome da coluna de ID da transação
            min_support: Suporte mínimo para regras de associação
            
        Returns:
            Dicionário com regras de associação e métricas
        """
        try:
            from mlxtend.frequent_patterns import apriori, association_rules
            from mlxtend.preprocessing import TransactionEncoder
            
            # Agrupar itens por transação
            grouped = transactions.groupby(transaction_column)[item_column].apply(list).reset_index()
            transactions_list = grouped[item_column].tolist()
            
            # Codificar transações
            te = TransactionEncoder()
            te_ary = te.fit_transform(transactions_list)
            df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
            
            # Gerar conjuntos frequentes
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
            
            # Gerar regras de associação
            rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
            
            # Converter para formato mais amigável
            results = []
            for _, row in rules.iterrows():
                antecedents = list(row['antecedents'])
                consequents = list(row['consequents'])
                
                rule_result = {
                    'antecedentes': antecedents,
                    'consequentes': consequents,
                    'suporte': row['support'],
                    'confiança': row['confidence'],
                    'lift': row['lift']
                }
                results.append(rule_result)
            
            # Ordenar por lift (mais relevantes primeiro)
            results = sorted(results, key=lambda x: x['lift'], reverse=True)
            
            # Resumo
            summary = {
                'total_rules': len(results),
                'avg_lift': rules['lift'].mean() if not rules.empty else 0,
                'top_associations': results[:10] if len(results) >= 10 else results
            }
            
            self.logger.info(f"Análise de cesta de compras concluída: {len(results)} regras encontradas")
            return {'rules': results, 'summary': summary}
            
        except ImportError:
            self.logger.error("Pacote mlxtend não instalado, necessário para análise de cesta de compras")
            return {}
        except Exception as e:
            self.logger.error(f"Erro na análise de cesta de compras: {str(e)}")
            return {}
    
    def customer_segmentation(self, df: pd.DataFrame, 
                             features: List[str], n_clusters: int = 3) -> pd.DataFrame:
        """
        Realiza segmentação de clientes utilizando clustering.
        
        Args:
            df: DataFrame com dados dos clientes
            features: Lista de features para segmentação
            n_clusters: Número de segmentos desejados
            
        Returns:
            DataFrame original com coluna de segmento adicionada
        """
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            
            # Copiar DataFrame original
            result_df = df.copy()
            
            # Selecionar features
            X = result_df[features].copy()
            
            # Lidar com valores faltantes
            X = X.fillna(X.mean())
            
            # Normalizar dados
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Aplicar K-means
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            result_df['segmento'] = kmeans.fit_predict(X_scaled)
            
            # Calcular características de cada segmento
            segment_profiles = {}
            for i in range(n_clusters):
                segment_df = result_df[result_df['segmento'] == i]
                profile = {}
                
                for feature in features:
                    profile[feature] = {
                        'media': segment_df[feature].mean(),
                        'mediana': segment_df[feature].median(),
                        'min': segment_df[feature].min(),
                        'max': segment_df[feature].max()
                    }
                
                segment_profiles[f'segmento_{i}'] = {
                    'tamanho': len(segment_df),
                    'percentual': len(segment_df) / len(result_df) * 100,
                    'perfil': profile
                }
            
            # Adicionar nomes descritivos aos segmentos
            segment_names = self._assign_segment_names(segment_profiles, features)
            
            # Mapear números para nomes
            segment_map = {i: name for i, name in enumerate(segment_names)}
            result_df['segmento_nome'] = result_df['segmento'].map(segment_map)
            
            self.logger.info(f"Segmentação de clientes concluída: {n_clusters} segmentos identificados")
            return result_df
            
        except ImportError:
            self.logger.error("Pacote sklearn não instalado, necessário para segmentação de clientes")
            return df
        except Exception as e:
            self.logger.error(f"Erro na segmentação de clientes: {str(e)}")
            return df
    
    def _assign_segment_names(self, segment_profiles: Dict[str, Dict], 
                             features: List[str]) -> List[str]:
        """
        Atribui nomes descritivos aos segmentos com base nos perfis.
        
        Args:
            segment_profiles: Dicionário com perfis de cada segmento
            features: Lista de features utilizadas
            
        Returns:
            Lista de nomes descritivos para os segmentos
        """
        # Esta é uma implementação simplificada
        # Em um caso real, a lógica seria mais complexa e adaptada ao domínio
        
        names = []
        segments = list(segment_profiles.keys())
        
        # Ordenar segmentos por tamanho (do maior para o menor)
        segments = sorted(segments, 
                         key=lambda x: segment_profiles[x]['tamanho'], 
                         reverse=True)
        
        for i, segment in enumerate(segments):
            profile = segment_profiles[segment]['perfil']
            
            # Exemplo para um caso de RFM (Recency, Frequency, Monetary)
            if 'recencia' in features and 'frequencia' in features and 'valor' in features:
                recencia = profile['recencia']['media']
                frequencia = profile['frequencia']['media']
                valor = profile['valor']['media']
                
                if frequencia > 10 and valor > 1000:
                    names.append("Clientes VIP")
                elif frequencia > 5 and valor > 500:
                    names.append("Clientes Regulares")
                elif recencia < 30:  # menos de 30 dias
                    names.append("Clientes Recentes")
                else:
                    names.append("Clientes Ocasionais")
            else:
                # Nomes genéricos se não for RFM
                names.append(f"Segmento {i+1}")
        
        return names