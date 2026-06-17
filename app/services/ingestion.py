from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vectorstore import create_vectorstore, add_to_vectorstore, load_vectorstore
from app.core.config import Config
import uuid
import os

def detect_provider(file_name: str):
    name = file_name.lower()

    if "aetna" in name:
        return "Aetna"
    elif "cigna" in name:
        return "Cigna"
    else:
        return "Unknown"

def process_pdf(filePath: str, doc_id: str, file_name: str):
    print(f'processing {doc_id} in {file_name}')
    loader = PyPDFLoader(filePath)
    documents = loader.load()
    provider = detect_provider(file_name)
    print(f'doc_id: {doc_id} for {filePath}, and doc size: {len(documents)} , provider {provider}')
    for doc in documents:
        doc.metadata.update({
            "doc_id": doc_id,
            "provider": provider,
            "file_name": file_name,
            "source": filePath,
            "url": f"{Config.SERVER_NAME}/data/raw_pdfs/{file_name}"
        })

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=50
    )

    print('starting chunking')
    chunks = splitter.split_documents(documents)

    for c in chunks:
        c.metadata["doc_id"] = doc_id
        c.metadata["file_name"] = file_name
        c.metadata["provider"] = provider

    print('starting load_vectorstore')
    vectorstore = load_vectorstore()

    if vectorstore is None:
        vectorstore = create_vectorstore(chunks)
    else:
        vectorstore = add_to_vectorstore(vectorstore, chunks)

    return {
        "chunks_added": len(chunks),
        "total_vectors": vectorstore.index.ntotal,
        "doc_id": doc_id
    }