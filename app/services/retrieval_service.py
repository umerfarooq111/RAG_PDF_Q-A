from app.db.database import conn
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


class RetrievalService:

    @staticmethod
    def retrieve_context(question: str, limit: int = 5) -> tuple[str, list[dict]]:
        # Generate embedding for the question
        question_embedding = EmbeddingService.embed_query(question)

        # Search PostgreSQL (pgvector)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT content, page_number, chunk_index
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (question_embedding, limit)
            )
            results = cursor.fetchall()

        # Build context
        context = "\n\n".join([row[0] for row in results])

        # Metadata for debugging/citations
        chunks_metadata = [
            {
                "content": row[0],
                "page_number": row[1],
                "chunk_index": row[2]
            }
            for row in results
        ]

        return context, chunks_metadata

    @staticmethod
    def ask_question(question: str):

        # Retrieve relevant chunks
        context, chunks_metadata = RetrievalService.retrieve_context(question)

        # Build prompt
        prompt = f"""
        You are a helpful AI assistant.
        Answer ONLY using the context below.
        If the answer is not present in the context, reply:
        "I don't know based on the provided document."

        Context:
        {context}

        Question:
        {question}
        """

        # Call Gemini
        response = LLMService.invoke(prompt)

        # Return API response
        return {
            "question": question,
            "retrieved_chunks": chunks_metadata,
            "answer": response.content
        }