from langchain_huggingface import HuggingFaceEmbeddings

_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

class EmbeddingService:
    @staticmethod
    def embed_documents(texts: list[str]) -> list[list[float]]:
        return _embeddings.embed_documents(texts)
    
    @staticmethod
    def embed_query(text: str) -> list[float]:
        return _embeddings.embed_query(text)
