from app.db.database import conn
from app.auth.password import PasswordService
from app.schemas.user import UserRegister


class AuthService:

    @staticmethod
    def register(user: UserRegister):

        with conn.cursor() as cursor:

            # Check username/email
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE username=%s OR email=%s
                """,
                (user.username, user.email)
            )

            existing = cursor.fetchone()

            if existing:
                return {
                    "message": "Username or Email already exists."
                }

            # Hash password
            hashed_password = PasswordService.hash_password(user.password)

            # Insert user
            cursor.execute(
                """
                INSERT INTO users
                (username,email,password_hash)
                VALUES (%s,%s,%s)
                """,
                (
                    user.username,
                    user.email,
                    hashed_password
                )
            )

            conn.commit()

        return {
            "message": "User registered successfully."
        }