from FlagEmbedding import FlagReranker


class RerankerService:

    reranker = FlagReranker(
        "BAAI/bge-reranker-v2-m3",
        use_fp16=False
    )

    @staticmethod
    def rerank(question: str, chunks_metadata: list[dict], top_k: int = 5):
        """
        Rerank retrieved chunks and return the top_k most relevant.
        """

        if not chunks_metadata:
            return []

        pairs = [
            [question, chunk["content"]]
            for chunk in chunks_metadata
        ]

        scores = RerankerService.reranker.compute_score(pairs)

        for chunk, score in zip(chunks_metadata, scores):
            chunk["score"] = score

        chunks_metadata.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return chunks_metadata[:top_k]