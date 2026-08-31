from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from config import settings

# lru_cache on l'utilise avec les fonctions couteuses ainsi lorsqu'on appelle la fonction avec les memes args python donne le resultat en cache sans réexecuter la fonction
# on l'utilise ici avec les modeles d'embeddings qui prennement bcp de temps pour se charger 


@lru_cache(maxsize=1)
def get_embed_model():
    return HuggingFaceEmbeddings(model_name = settings.embedding_model, encode_kwargs ={"normalize_embeddings":True})


def embed_doc(documents):
    if not documents :
        return []
    
    # Le titre redonne son contexte à chaque chunk, y compris lorsqu'il
    # provient du milieu d'un document et ne contient plus le titre Markdown.
    texts = [
        (
            f"Titre : {doc.metadata.get('title', '')}\n\n"
            f"{doc.page_content}"
        )
        for doc in documents
    ]
    
    model = get_embed_model()
    
    embed_docs = model.embed_documents(texts=texts)
    
    return embed_docs

    
def embed_query(query):
    
    if not query.strip():
        raise ValueError("La requete ne peut pas etre vide ")
    
    model = get_embed_model()
    
    return model.embed_query(query)
