# src/vector_store.py

from typing import Dict, List
import numpy as np

class SimpleVectorStore:
    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}
        
    def add_vector(self, key: str, vector: List[float]):
        """Adiciona um vetor ao armazenamento"""
        self.vectors[key] = vector
        
    def get_vector(self, key: str) -> List[float]:
        """Recupera um vetor do armazenamento"""
        return self.vectors.get(key, [])
    
    def similarity_search(self, query_vector: List[float], n: int = 5) -> List[str]:
        """Realiza uma busca por similaridade"""
        if not self.vectors:
            return []
        
        similarities = {}
        for key, vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            similarities[key] = similarity
            
        return sorted(similarities.keys(), key=lambda k: similarities[k], reverse=True)[:n]
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calcula a similaridade do cosseno entre dois vetores"""
        v1_arr = np.array(v1)
        v2_arr = np.array(v2)
        return np.dot(v1_arr, v2_arr) / (np.linalg.norm(v1_arr) * np.linalg.norm(v2_arr))