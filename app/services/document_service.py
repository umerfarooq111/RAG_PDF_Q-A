from app.db.database import conn

class DocumentService:
    @staticmethod
    def create_document(filename: str, file_path: str, total_pages: int) -> int:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, file_path, total_pages)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (filename, file_path, total_pages)
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
    def get_all_documents() -> list[dict]:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, uploaded_at
                FROM documents
                ORDER BY uploaded_at DESC;
            """)
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
    def delete_document(document_id: int) -> bool:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM documents
                WHERE id = %s
                RETURNING id;
                """,
                (document_id,)
            )
            deleted = cursor.fetchone()
            conn.commit()
            return deleted is not None

    @staticmethod
    def clear_all_documents():
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM documents;")
            conn.commit()
