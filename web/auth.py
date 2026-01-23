from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.config import settings

security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials) -> bool:
    if (
        credentials.username == settings.ADMIN_USERNAME
        and credentials.password == settings.ADMIN_PASSWORD
    ):
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )
