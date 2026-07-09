import unittest
import random
import string
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import conn

class TestAuthFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        
        # User A Details
        rand_str_a = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.username_a = f"test_a_{rand_str_a}"
        cls.email_a = f"test_a_{rand_str_a}@example.com"
        cls.password_a = "SecurePasswordA123!"
        
        # User B Details
        rand_str_b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.username_b = f"test_b_{rand_str_b}"
        cls.email_b = f"test_b_{rand_str_b}@example.com"
        cls.password_b = "SecurePasswordB123!"
        
        cls.user_a_id = None
        cls.user_b_id = None
        cls.token_a = None
        cls.token_b = None
        cls.doc_b_id = None

    @classmethod
    def tearDownClass(cls):
        # Clean up test documents and users
        try:
            with conn.cursor() as cursor:
                if cls.doc_b_id:
                    cursor.execute("DELETE FROM documents WHERE id = %s", (cls.doc_b_id,))
                cursor.execute("DELETE FROM users WHERE email IN (%s, %s)", (cls.email_a, cls.email_b))
                conn.commit()
        except Exception as e:
            print(f"Cleanup failed: {e}")

    def test_01_register_user_a_success(self):
        payload = {
            "username": self.username_a,
            "email": self.email_a,
            "password": self.password_a
        }
        response = self.client.post("/api/v1/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], self.username_a)
        self.assertEqual(data["email"], self.email_a)
        self.__class__.user_a_id = data["id"]

    def test_02_register_user_b_success(self):
        payload = {
            "username": self.username_b,
            "email": self.email_b,
            "password": self.password_b
        }
        response = self.client.post("/api/v1/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.__class__.user_b_id = data["id"]

    def test_03_register_duplicate_user_fails(self):
        payload = {
            "username": self.username_a,
            "email": self.email_a,
            "password": self.password_a
        }
        response = self.client.post("/api/v1/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Username or Email already exists.")

    def test_04_login_incorrect_credentials_fails(self):
        payload = {
            "username": self.email_a,
            "password": "wrong_password"
        }
        response = self.client.post("/api/v1/login", data=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid email or password.")

    def test_05_login_user_a_success(self):
        payload = {
            "username": self.email_a,
            "password": self.password_a
        }
        response = self.client.post("/api/v1/login", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.__class__.token_a = data["access_token"]

    def test_06_login_user_b_success(self):
        payload = {
            "username": self.email_b,
            "password": self.password_b
        }
        response = self.client.post("/api/v1/login", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.__class__.token_b = data["access_token"]

    def test_07_unauthorized_access_to_documents_fails(self):
        response = self.client.get("/api/v1/documents")
        self.assertEqual(response.status_code, 401)

    def test_08_authorized_access_to_documents_success(self):
        headers = {
            "Authorization": f"Bearer {self.token_a}"
        }
        response = self.client.get("/api/v1/documents", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("documents", response.json())

    def test_09_document_ownership_enforcement(self):
        # Insert a document belonging to User B
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, file_path, total_pages, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                ("b_doc.pdf", "/tmp/b_doc.pdf", 1, self.user_b_id)
            )
            self.__class__.doc_b_id = cursor.fetchone()[0]
            conn.commit()

        # Try to delete User B's document using User A's token
        headers_a = {
            "Authorization": f"Bearer {self.token_a}"
        }
        response = self.client.delete(f"/api/v1/documents/{self.doc_b_id}", headers=headers_a)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. You do not own this document.")

        # Try to delete a non-existent document
        response = self.client.delete("/api/v1/documents/999999", headers=headers_a)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Document not found.")

        # Delete User B's document using User B's token
        headers_b = {
            "Authorization": f"Bearer {self.token_b}"
        }
        response = self.client.delete(f"/api/v1/documents/{self.doc_b_id}", headers=headers_b)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], f"Document {self.doc_b_id} deleted successfully.")
        self.__class__.doc_b_id = None

if __name__ == "__main__":
    unittest.main()
