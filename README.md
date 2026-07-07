# PDF Question-Answering System using RAG

A production-ready Retrieval-Augmented Generation (RAG) backend API for querying PDF documents. The system parses uploaded PDFs, stores their text chunks with vector embeddings in PostgreSQL (using `pgvector`), reranks retrieved context using a Cross-Encoder model, and generates final answers using Google Gemini.

---

## 🏗️ Architecture

```mermaid
graph TD
    %% Upload Flow
    subgraph Upload & Indexing Flow
        A[User Uploads PDF] --> B[PDF Parser: PyPDFLoader]
        B --> C[Text Chunking: RecursiveCharacterTextSplitter]
        C --> D[Embeddings Generator: HuggingFace BGE-Base]
        D --> E[(PostgreSQL + pgvector)]
    end

    %% Query Flow
    subgraph Query & Answer Flow
        F[User Question] --> G[Query Embedding Generator]
        G --> H[Vector Similarity Search: cosine distance]
        H --> I[(PostgreSQL: Top 20 Candidates)]
        I --> J[Reranker: Cross-Encoder ms-marco-MiniLM]
        J --> K[Top 5 Reranked Context Chunks]
        K --> L[LLM: Gemini 2.5 Flash]
        F --> L
        L --> M[Structured JSON Response]
    end
```

---

## Key Features

*   **PDF Extraction & Chunking:** Processes documents using LangChain `PyPDFLoader` and splits them intelligently with `RecursiveCharacterTextSplitter` to preserve contextual boundaries.
*   **Local Embedding Model:** Generates 768-dimensional vector embeddings using the state-of-the-art `BAAI/bge-base-en-v1.5` model.
*   **Vector Database Store:** Performs fast vector similarity search using PostgreSQL with the `pgvector` extension.
*   **Cross-Encoder Reranking:** Filters and optimizes context relevance from top 20 candidate chunks to top 5 using `cross-encoder/ms-marco-MiniLM-L6-v2`, improving retrieval precision.
*   **Gemini Q&A Engine:** Generates highly accurate answers grounded strict context constraints using the `gemini-2.5-flash` model.
*   **FastAPI REST Endpoints:** Clean API interface for uploads, list/delete documents, and context-grounded queries.

---

## Prerequisites

*   **Python:** Version `3.10` or higher.
*   **Database:** PostgreSQL `15+` with the [pgvector extension](https://github.com/pgvector/pgvector) installed.
*   **API Keys:** Active Google AI Studio API key (`GOOGLE_API_KEY`) for Gemini access.

---

## Database Setup

Before running the application, ensure your PostgreSQL database is ready and has the vector extension active. 

Run the following SQL commands to initialize the tables:

```sql
-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create documents registry table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    total_pages INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create document chunks table with 768-dim vector embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL
);

-- 4. Create an HNSW index for vector cosine similarity searches
CREATE INDEX IF NOT EXISTS document_chunks_hnsw_idx 
ON document_chunks USING hnsw (embedding vector_cosine_ops);
```

---

## Installation & Running

1.  **Clone the Repository & Navigate to Workspace:**
    ```bash
    cd RAG_PDF
    ```

2.  **Set Up Virtual Environment:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    # source .venv/bin/activate  # macOS/Linux
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory (based on `.env.example` or editing the existing `.env`):
    ```env
    GOOGLE_API_KEY="your-gemini-api-key"
    HF_TOKEN="your-huggingface-token"
    DATABASE_URL="postgresql://username:password@localhost:5432/pdf_rag_db"
    ```

5.  **Run the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will start at `http://127.0.0.1:8000`.

---

## 🔌 API Documentation

Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### Key Endpoints

#### 1. Upload PDF
*   **URL:** `/api/v1/upload`
*   **Method:** `POST`
*   **Content-Type:** `multipart/form-data`
*   **Body:** `file` (Binary PDF File)
*   **Description:** Uploads a PDF, chunks it, generates embeddings, and saves everything to PostgreSQL.

#### 2. Query RAG
*   **URL:** `/api/v1/ask`
*   **Method:** `POST`
*   **Query Params:** `question` (string)
*   **Description:** Performs vector search, reranks candidate passages, constructs context, and fetches answer from Gemini.

#### 3. List Documents
*   **URL:** `/api/v1/documents`
*   **Method:** `GET`
*   **Description:** Returns metadata of all indexed documents in the database.

#### 4. Delete Document
*   **URL:** `/api/v1/documents/{document_id}`
*   **Method:** `DELETE`
*   **Description:** Removes a specific document and its associated chunks from the store.

#### 5. Clear Database
*   **URL:** `/api/v1/clear`
*   **Method:** `DELETE`
*   **Description:** Deletes all documents and chunks from the database.
