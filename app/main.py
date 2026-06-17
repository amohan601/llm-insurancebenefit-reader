from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import traceback
from app.api.router import api_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Insurance Policy RAG Chatbot",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api/v1")

print(BASE_DIR)
# Static PDFs
app.mount(
    "/data",
    StaticFiles(directory=BASE_DIR / "data"),
    name="data"
)

@app.get("/")
def root():
    return {"message": "Insurance Chatbot is running"}

@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

@app.on_event("startup")
def startup():
    print("🚀 RAG system started")