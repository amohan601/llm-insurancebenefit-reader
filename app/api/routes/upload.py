import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion import process_pdf

router = APIRouter()

UPLOAD_DIR = "data/raw_pdfs"
REGISTRY_PATH = "data/doc_registry.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_doc_registry(doc_id, file_name):
    registry = {}

    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            registry = json.load(f)

    registry[doc_id] = {
        "file_name": file_name,
        "path": f"{UPLOAD_DIR}/{file_name}"
    }

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs allowed")

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = process_pdf(file_path, doc_id, file.filename)

    # Save registry
    save_doc_registry(doc_id, file.filename)

    return {
        "message": "Uploaded successfully",
        "doc_id": doc_id,
        "file": file.filename,
        "chunks": result["chunks_added"],
        "vectors": result["total_vectors"]
    }