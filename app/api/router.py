from fastapi import APIRouter

from app.api.routes import upload, query, health, documents

api_router = APIRouter()


# ---------------------------
# list all documents routes
# ---------------------------
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# ---------------------------
# Health check routes
# ---------------------------
api_router.include_router(health.router,prefix="/health",tags=["Health"])

# ---------------------------
# Upload routes (PDF ingestion)
# ---------------------------
api_router.include_router(upload.router,prefix="/upload",tags=["Upload"])

# ---------------------------
# Query routes (RAG chatbot)
# ---------------------------
api_router.include_router(query.router,prefix="/ask",tags=["Query"])