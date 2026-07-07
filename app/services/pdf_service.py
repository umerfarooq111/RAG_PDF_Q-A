from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFService:

    @staticmethod
    def load_pdf(file_path: str):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents

    @staticmethod
    def split_documents(documents, chunk_size: int = 300, chunk_overlap: int = 20):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)
