from fastapi import FastAPI

from app.api.routes import router as auth_router
from app.api.ai_routes import router as ai_router


app = FastAPI(title="Company Chatbot Backend")

app.include_router(auth_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health")
def health_check():
    return {"status": "OK"}
