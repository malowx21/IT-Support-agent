
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # Embeddings
    embedding_model : str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # Database path
    database_path : str = "data/support.db"
    
    # Documents path
    documents_path : str = "mcp_server/knowledge"
    
    
settings = Settings()