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
        # Generate random credentials for test run
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.username = f"test_{rand_str}"
        cls.email = f"test_{rand_str}@example.com"
        cls.password = "SecurePassword123!"

    @classmethod
    def tearDownClass(cls):
        # Clean up the test user from database
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE email = %s", (cls.email,))
                conn.commit()
        except Exception as e:
            print(f"Cleanup failed: {e}")

    def test_01_register_user_success(self):
        payload = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
        response = self.client.post("/api/v1/register", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "User registered successfully.")

    def test_02_register_duplicate_user_fails(self):
        payload = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
        response = self.client.post("/api/v1/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Username or Email already exists.")

    def test_03_login_incorrect_credentials_fails(self):
        payload = {
            "email": self.email,
            "password": "wrong_password"
        }
        response = self.client.post("/api/v1/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid email or password.")

    def test_04_login_success(self):
        payload = {
            "email": self.email,
            "password": self.password
        }
        response = self.client.post("/api/v1/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

        # Save token for subsequent tests
        self.__class__.token = data["access_token"]

    def test_05_unauthorized_access_to_documents_fails(self):
        response = self.client.get("/api/v1/documents")
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_06_authorized_access_to_documents_success(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = self.client.get("/api/v1/documents", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("documents", response.json())

if __name__ == "__main__":
    unittest.main()
