from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents,chunk_size,chunk_overlap):
    
    if chunk_size <=0 :
        raise ValueError("chunk_size doit etre supérieur à 0")
    if chunk_overlap<0:
        raise ValueError("chunk_overlap doit etre positif")
    
    if chunk_size <= chunk_overlap :
        raise ValueError("chunk_overlap doit etre inferieur à chunk_size")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,separators=["\n\n", "\n", ".", " ",""])
    chunks = splitter.split_documents(documents)
    
    counters: dict[str, int] = {}

    for chunk in chunks:
        document_id = chunk.metadata[
            "document_stem"
        ]

        chunk_index = counters.get(
            document_id,
            0,
        )

        chunk.metadata["chunk_index"] =  chunk_index
    

        counters[document_id] = chunk_index + 1 

    return chunks
    