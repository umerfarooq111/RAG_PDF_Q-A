import os
import shutil
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.embedding_service import EmbeddingService
from app.services.document_service import DocumentService

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadService:
    @staticmethod
    def upload_pdf(file: UploadFile, current_user: dict) -> dict:
        # 1. Save uploaded file to disk
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Load PDF documents
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 3. Create document record in database
        document_id = DocumentService.create_document(
            filename=file.filename,
            file_path=file_path,
            total_pages=len(documents),
            user_id=current_user["id"]
        )

        # 4. Split document into text chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)

        # 5. Generate embeddings for the chunks
        vectors = EmbeddingService.embed_documents(
            [chunk.page_content for chunk in chunks]
        )

        # 6. Save document chunks and embeddings to database
        DocumentService.create_chunks(document_id, chunks, vectors)

        return {
            "document_id": document_id,
            "filename": file.filename,
            "pages": len(documents),
            "chunks": len(chunks),
            "stored_chunks": len(chunks)
        }

