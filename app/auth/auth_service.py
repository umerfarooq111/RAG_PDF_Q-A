from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import conn
from app.auth.password import PasswordService
from app.schemas.user import UserRegister
from app.auth.jwt_service import JWTService


class AuthService:
    @staticmethod
    def login(user: OAuth2PasswordRequestForm):

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, password_hash
                FROM users
                WHERE email = %s
                """,
                (user.username,)
            )
            # Fetch inside the with block
            db_user = cursor.fetchone()

        # User not found
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Verify password
        is_valid = PasswordService.verify_password(
            user.password,
            db_user[3]
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Create JWT
        access_token = JWTService.create_access_token(
            data={
                "sub": db_user[2],
                "user_id": db_user[0]
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or Email already exists."
                )

            # Hash password
            hashed_password = PasswordService.hash_password(user.password)

            # Insert user
            cursor.execute(
                """
                INSERT INTO users
                (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    user.username,
                    user.email,
                    hashed_password
                )
            )
            user_id = cursor.fetchone()[0]
            conn.commit()

        return {
            "id": user_id,
            "username": user.username,
            "email": user.email
        }

