from langchain_huggingface import HuggingFaceEmbeddings

_embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

class EmbeddingService:
    @staticmethod
    def embed_documents(texts: list[str]) -> list[list[float]]:
        return _embeddings.embed_documents(texts)
    
    @staticmethod
    def embed_query(text: str) -> list[float]:
        return _embeddings.embed_query(text)
