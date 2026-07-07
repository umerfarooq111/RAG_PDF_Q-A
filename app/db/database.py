import psycopg
from pgvector.psycopg import register_vector

conn = psycopg.connect(
    host="localhost",
    dbname="pdf_rag_db",
    user="postgres",
    password="0123umer",
    port=5433
)
register_vector(conn)
cursor = conn.cursor()