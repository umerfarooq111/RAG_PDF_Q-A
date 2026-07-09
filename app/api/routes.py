from fastapi import APIRouter, UploadFile, File, Depends

from app.services.upload_service import UploadService
from app.services.document_service import DocumentService
from app.services.retrieval_service import RetrievalService
from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.schemas.user import UserRegister
from app.schemas.login import UserLogin

router = APIRouter(
    prefix="/api/v1",
    tags=["PDF RAG API"]
)


@router.post("/register")
def register(user: UserRegister):
    return AuthService.register(user)

@router.post("/login")
def login(user: UserLogin):
    return AuthService.login(user)

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
async def upload_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """
    Upload a PDF file to be processed.
    Only authenticated users can upload files.
    """
    return UploadService.upload_pdf(
        file=file,
        current_user=current_user
    )

@router.post("/ask")
async def ask_question(question: str, current_user: dict = Depends(get_current_user)):
    return RetrievalService.ask_question(question=question,
        current_user=current_user)


@router.get("/documents")
def get_documents(current_user: dict = Depends(get_current_user)):
    documents = DocumentService.get_all_documents()
    return {
        "documents": documents
    }


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, current_user: dict = Depends(get_current_user)):
    success = DocumentService.delete_document(document_id)
    if not success:
        return {
            "message": "Document not found."
        }
    return {
        "message": f"Document {document_id} deleted successfully."
    }


@router.delete("/clear")
def clear_database(current_user: dict = Depends(get_current_user)):
    DocumentService.clear_all_documents()
    return {
        "message": "All documents deleted successfully."
    }


