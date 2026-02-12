from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
import sqlite3

from app.core.database import DB_PATH
from app.models.models import verify_password
from app.services.auth import create_access_token, get_current_user
from app.core.rbac import rbac_required
from app.services.rag import rag_pipeline
from app.services.logs import log_access  # adjust if logs.py exists elsewhere

from pydantic import BaseModel


router = APIRouter()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, password, role FROM users WHERE username=?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_username, db_password, role = user

    if not verify_password(password, db_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": db_username,
        "role": role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user


# --------- FINAL RBAC ENDPOINT ---------

@router.get("/secure-search")
def secure_search(
    department: str = Query(..., description="finance, hr, engineering, marketing, general"),
    current_user: dict = Depends(get_current_user)
):
    role = current_user["role"]
    username = current_user["username"]

    # RBAC CHECK
    rbac_required(department)(current_user)

    # LOG
    log_access(username, role, f"/secure-search?department={department}", confidence=1.0)

    return {
        "requested_department": department,
        "access_granted_for_role": role,
        "data": f"Confidential {department} data"
    }
