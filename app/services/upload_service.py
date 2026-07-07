import os
import shutil
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.database import conn
from app.services.embedding_service import EmbeddingService

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadService:
    @staticmethod
    def upload_pdf(file: UploadFile) -> dict:
        # 1. Save uploaded file to disk
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Load PDF documents
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 3. Create document record in database
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, file_path, total_pages)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (file.filename, file_path, len(documents))
            )
            document_id = cursor.fetchone()[0]
            conn.commit()

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
            for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
                cursor.execute(
                    """
                    INSERT INTO document_chunks
                    (document_id, chunk_index, page_number, content, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        document_id,
                        index,
                        chunk.metadata.get("page", 0) + 1,
                        chunk.page_content,
                        vector
                    )
                )
            conn.commit()

        return {
            "document_id": document_id,
            "filename": file.filename,
            "pages": len(documents),
            "chunks": len(chunks),
            "stored_chunks": len(chunks)
        }
