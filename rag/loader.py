from pathlib import Path
from langchain_core.documents import Document


def load_documents(document_path):
    
    directory = Path(document_path)
    
    if not directory.exists() :
        raise FileNotFoundError("Le dossier n'existe pas")
    
    generator = directory.glob("*.md")
    documents = []
    for doc in generator :
        c = doc.read_text(encoding="utf-8").strip()
        if not c:
            continue

        lines = c.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else doc.stem

        document = Document(page_content=c,metadata={
            "document_stem": doc.stem,
            "title": title,
            "filename":doc.name,
            "filepath":str(doc),
            "type":"markdown"
        })
        documents.append(document)
        
    return documents
