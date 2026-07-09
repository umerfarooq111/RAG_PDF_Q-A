from jose import JWTError
import os
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()


class JWTService:

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )

    @staticmethod
    def create_access_token(data: dict):
        """
        Create a JWT access token.
        """

        to_encode = data.copy()

        expire = datetime.utcnow() + timedelta(
            minutes=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            JWTService.SECRET_KEY,
            algorithm=JWTService.ALGORITHM
        )

        return encoded_jwt
    @staticmethod
    def verify_token(token: str):

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                JWTService.SECRET_KEY,
                algorithms=[JWTService.ALGORITHM]
            )

            email = payload.get("sub")

            if email is None:
                raise credentials_exception

            return payload

        except JWTError:
            raise credentials_exception