import os
from datetime import datetime, timedelta

from jose import jwt
from dotenv import load_dotenv

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