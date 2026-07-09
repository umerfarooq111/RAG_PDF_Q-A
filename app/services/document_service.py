from app.db.database import conn
from fastapi import HTTPException, status

class DocumentService:
    @staticmethod
    def create_document(filename: str, file_path: str, total_pages: int, user_id: int) -> int:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, file_path, total_pages, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (filename, file_path, total_pages, user_id)
            )
            document_id = cursor.fetchone()[0]
            conn.commit()
            return document_id

    @staticmethod
    def create_chunks(document_id: int, chunks: list, vectors: list[list[float]]):
        with conn.cursor() as cursor:
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

    @staticmethod
    def get_all_documents(user_id: int) -> list[dict]:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, uploaded_at
                FROM documents
                WHERE user_id = %s
                ORDER BY uploaded_at DESC;
            """, (user_id,))
            documents = cursor.fetchall()
            return [
                {
                    "id": doc[0],
                    "filename": doc[1],
                    "uploaded_at": doc[2]
                }
                for doc in documents
            ]

    @staticmethod
    def delete_document(document_id: int, user_id: int) -> bool:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id
                FROM documents
                WHERE id = %s
                """,
                (document_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found."
                )
            if row[0] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You do not own this document."
                )
            
            cursor.execute(
                """
                DELETE FROM documents
                WHERE id = %s
                """,
                (document_id,)
            )
            conn.commit()
            return True

    @staticmethod
    def clear_all_documents(user_id: int):
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM documents
                WHERE user_id = %s
                """,
                (user_id,)
            )
            conn.commit()

