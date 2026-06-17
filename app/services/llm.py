from langchain_openai import ChatOpenAI
from app.core.config import Config

_llm = None

def get_llm():
    global _llm

    if _llm is None:
        print(f'New LLM created with {Config.LLM_MODEL} ')
        _llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0,
            timeout=30,
            max_retries=2
        )
    else:
        print(f'Returning existing LLM with {Config.LLM_MODEL} ')
    return _llm