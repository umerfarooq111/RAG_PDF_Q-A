from sentence_transformers import CrossEncoder


class RerankerService:

    # Load once when the application starts
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    @staticmethod
    def rerank(question: str, chunks_metadata: list[dict], top_k: int = 5):
        """
        Rerank retrieved chunks and return the top_k most relevant.
        """

        if not chunks_metadata:
            return []

        # Create (query, passage) pairs
        pairs = [
            (question, chunk["content"])
            for chunk in chunks_metadata
        ]

        # Predict relevance scores
        scores = RerankerService.reranker.predict(pairs)

        # Attach score to each chunk
        for chunk, score in zip(chunks_metadata, scores):
            chunk["score"] = float(score)

        # Sort by score (highest first)
        chunks_metadata.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # Return top-k
        return chunks_metadata[:top_k]