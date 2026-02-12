from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.auth import get_current_user
from app.services.rag import rag_pipeline
from app.core.rbac import RBAC_RULES
from app.services.logs import log_access  # ensure logs.py is inside services


router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    role = current_user["role"].lower()
    username = current_user["username"]

    # RBAC: check role exists
    if role not in RBAC_RULES:
        raise HTTPException(status_code=403, detail="Role not allowed")

    # Call RAG
    result = rag_pipeline(request.query, role)

    # Proper AI logging
    log_access(
        username=username,
        role=role,
        query=request.query,
        confidence=result["confidence"]
    )

    return {
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"],
        "role": role,
        "department": role
    }
