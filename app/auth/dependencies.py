from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_service import JWTService
from app.db.database import conn

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login"
)

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    payload = JWTService.verify_token(token)

    email = payload["sub"]

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT id,
                   username,
                   email
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return {
        "id": user[0],
        "username": user[1],
        "email": user[2]
    }