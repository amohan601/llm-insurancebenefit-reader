import json
import os
from fastapi import APIRouter

router = APIRouter()

REGISTRY_PATH = "data/doc_registry.json"


@router.get("/")
def list_documents():
    print('Inside list_documents')
    if not os.path.exists(REGISTRY_PATH):
        return []

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    docs = [
        {
            "doc_id": doc_id,
            "name": data["file_name"]
        }
        for doc_id, data in registry.items()
    ]
    print(type(docs))
    print(docs)
    return docs