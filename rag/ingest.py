from pathlib import Path

from rag.loader import load_documents
from rag.splitter import split_documents
from rag.embed import embed_doc
from rag.repository_rag import RepositoryRag
from config import settings



DATABASE_PATH = Path(settings.database_path)
DOCUMENTS_PATH = Path(settings.documents_path)


def ingest_documents(database_path: str | Path =DATABASE_PATH , documents_path : str | Path = DOCUMENTS_PATH, chunk_size : int = 500,chunk_overlap: int = 80):
    
    documents = load_documents(documents_path)
    chunks = split_documents(documents, chunk_size, chunk_overlap)
    embeddings = embed_doc(chunks)
    repository = RepositoryRag(database_path)
    repository.initialize()
    repository.replace_chunks(chunks,embeddings)
    
    return {
        "documents_count": len(documents),
        "chunks_count": len(chunks),
        "embedding_dimension": (
            len(embeddings[0])
        ),
        "database_chunks_count": (
            repository.count_chunks()
        ),}
    
def main():
    result = ingest_documents()
    print(result)

if __name__ =="__main__":
    main()