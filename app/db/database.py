import psycopg
from pgvector.psycopg import register_vector
from app.core.config import DATABASE_URL

conn = psycopg.connect(DATABASE_URL)
register_vector(conn)