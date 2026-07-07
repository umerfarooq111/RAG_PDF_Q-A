from app.db.database import conn
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.reranker_service import RerankerService


class RetrievalService:

    @staticmethod
    def retrieve_context(question: str, limit: int = 20):
        """
        Retrieve candidate chunks from PostgreSQL.
        """

        question_embedding = EmbeddingService.embed_query(question)

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

        chunks_metadata = [

            {
                "content": row[0],
                "page_number": row[1],
                "chunk_index": row[2]
            }

            for row in results

        ]

        return chunks_metadata

    @staticmethod
    def ask_question(question: str):

        # Step 1: Retrieve Top 20 using pgvector
        chunks_metadata = RetrievalService.retrieve_context(question)

        # Step 2: Rerank and keep Top 5
        top_chunks = RerankerService.rerank(
            question,
            chunks_metadata,
            top_k=5
        )

        # Step 3: Build context for Gemini
        context = "\n\n".join(
            chunk["content"]
            for chunk in top_chunks
        )

        # Step 4: Prompt
        prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the context below.

If the answer is not present in the context, reply exactly:

"I don't know based on the provided document."

Context:
{context}

Question:
{question}
"""

        # Step 5: Generate answer
        response = LLMService.invoke(prompt)

        return {

            "question": question,

            "retrieved_chunks": top_chunks,

            "answer": response.content

        }