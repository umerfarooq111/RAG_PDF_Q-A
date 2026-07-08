from httpx import _status_codes
from fastapi import APIRouter, UploadFile, File

from app.services.upload_service import UploadService
from app.services.document_service import DocumentService
from app.services.retrieval_service import RetrievalService
from app.auth.auth_service import AuthService
from app.schemas.user import UserRegister

router = APIRouter(
    prefix="/api/v1",
    tags=["PDF RAG API"]
)


@router.post("/register")
def register(user: UserRegister):
    return AuthService.register(user)

@router.get("/")
def home():
    return {
        "message": "PDF RAG API is running"
    }


@router.get("/about")
def about():
    return {
        "project": "PDF Question Answering using RAG",
        "developer": "Umer Farooq"
    }

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    return UploadService.upload_pdf(file)

@router.post("/ask")
async def ask_question(question: str):
    return RetrievalService.ask_question(question)



@router.get("/documents")
def get_documents():
    documents = DocumentService.get_all_documents()
    return {
        "documents": documents
    }


@router.delete("/documents/{document_id}")
def delete_document(document_id: int):
    success = DocumentService.delete_document(document_id)
    if not success:
        return {
            "message": "Document not found."
        }
    return {
        "message": f"Document {document_id} deleted successfully."
    }


@router.delete("/clear")
def clear_database():
    DocumentService.clear_all_documents()
    return {
        "message": "All documents deleted successfully."
    }

