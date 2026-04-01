import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from api.configurations.base import config
from api.exceptions.api import APIError

security = HTTPBearer()


class UserModel(BaseModel):
    id: str
    name: str
    sub: str
    iat: int
    exp: int


async def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserModel:
    try:
        payload = jwt.decode(
            credentials.credentials,
            config.signature_text,
            algorithms=["HS256"],
        )
        return UserModel(**payload)
    except jwt.PyJWTError:
        raise APIError("unauthorized")
