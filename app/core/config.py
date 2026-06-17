import os
from dotenv import load_dotenv

load_dotenv()


def get_env(k, default=None, cast=str):
    v = os.getenv(k, default)
    return cast(v) if v is not None else None


class Config:
    SERVICE_NAME = get_env("SERVICE_NAME")
    TOP_K = get_env("TOP_K", cast=int)
    CHUNK_SIZE = get_env("CHUNK_SIZE", cast=int)
    LLM_MODEL = get_env("LLM_MODEL", "gpt-4o-mini")
    VECTOR_STORE_PATH = get_env("VECTOR_STORE_PATH")
    SERVER_NAME = get_env("SERVER_NAME", "http://127.0.0.1:8000/api/v1")
    ENV = get_env("ENV", "dev")