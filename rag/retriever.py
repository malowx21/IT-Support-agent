import numpy as np 

from pathlib import Path
from config import settings

from rag.embed import embed_query
from rag.repository_rag import RepositoryRag


DATABASE_PATH =Path(settings.database_path)

def cosine_similarity(a, b):
    if len(a)!= len(b):
        raise ValueError("Les deux vecteurs doivent avoir la meme dimension")
    a, b = np.array(a),np.array(b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def retrieve_docs(query:str,limit:int=3, minimum_score: float = 0.0, database_path: str| Path =  DATABASE_PATH):
    
    if not query.strip():
        raise ValueError("La requete ne peut pas etre vide")
    
    if limit <= 0:
        raise ValueError("Limit ne peut etre negatif")
    
    if not -1 <= minimum_score<= 1 :
        raise ValueError("minimum_score doit etre entre 1 et -1")
    
    
    query_embed = embed_query(query)
    
    
    repository = RepositoryRag(database_path)
    repository.initialize()
    
    chunks = repository.get_all_chunks()
    
    results = []
    
    for chunk in chunks:
        embed_doc = chunk["embedding"]
        if len(query_embed)!=len(embed_doc):
            raise ValueError("Les deux vecteurs d'embedding doivent avoir la meme dimension")
        score = cosine_similarity(embed_doc,query_embed)
        
        if score < minimum_score :
            continue
        
        results.append({
            "id": chunk['id'],
            "document_id":chunk["document_id"],
            "content" : chunk["content"],
            "metadata": chunk['metadata'],
            "score": score
        })
        
    results.sort(key=lambda result: result["score"], reverse=True)
        
    return results[:limit]