from app.core import config
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.routes import router

app = FastAPI(
    title="PDF RAG API",
    description="Backend API for PDF Question Answering using RAG"
)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

app.include_router(router)

