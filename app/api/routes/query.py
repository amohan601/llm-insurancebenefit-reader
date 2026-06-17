from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_ask_question import ask_question
from app.services.intentrouter import route_question
router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    doc_id: str | None = None
    doc_ids: list[str] | None = None


@router.post("/")
def ask(req: QueryRequest):

    if not req.question.strip():
        raise HTTPException(status_code=400)

    print(f'Original payload recieved: {str(req)}')
    result = route_question(
        question=req.question,
        doc_id=req.doc_id,
        doc_ids=req.doc_ids
    )

    return result