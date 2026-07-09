import psycopg

def check():
    try:
        conn = psycopg.connect(
            host="localhost",
            dbname="pdf_rag_db",
            user="postgres",
            password="0123umer",
            port=5433
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tc.constraint_name, 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='documents';
            """)
            fks = cur.fetchall()
            print("Foreign keys in 'documents' table:")
            for fk in fks:
                print(f" - {fk[0]}: {fk[1]}({fk[2]}) -> {fk[3]}({fk[4]})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check()
