from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import Config
import os

EMBEDDINGS = OpenAIEmbeddings()
def load_vectorstore():
    print('load_vectorstore')
    if not os.path.exists(Config.VECTOR_STORE_PATH):
        return None
    try:
        return FAISS.load_local(
            Config.VECTOR_STORE_PATH,
            EMBEDDINGS,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f'Exception ',str(e))
        return None

def create_vectorstore(chunked_documents):
    print('create_vectorstore')
    vectorstore = FAISS.from_documents(chunked_documents, EMBEDDINGS)
    vectorstore.save_local(Config.VECTOR_STORE_PATH)
    return vectorstore


def add_to_vectorstore(vectorstore, chunked_documents):
    print('add_to_vectorstore')
    vectorstore.add_documents(chunked_documents)
    vectorstore.save_local(Config.VECTOR_STORE_PATH)
    return vectorstore

#Filter based on global retriever
#default retriever is similarity search unless otherwise specified
def get_retriever(vs, k=10, doc_id=None):
    if doc_id:
        return vs.as_retriever(search_kwargs={"k": k, "filter": {"doc_id": doc_id}})
    return vs.as_retriever(search_kwargs={"k": k})