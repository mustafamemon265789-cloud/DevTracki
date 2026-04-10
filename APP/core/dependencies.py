from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.database import get_session
from app.models.user import User
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Or Expired Token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        raise exc
    user = session.get(User, user_id)
    if not user:
        raise exc
    return user
