"""Authentification : vérification bcrypt puis émission d'un JWT."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import LoginRequest, TokenResponse
from backend.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Retourne un JWT (sub, role, iat, exp) si les identifiants sont valides."""

    user = db.scalar(select(User).where(User.username == data.username))

    # Même réponse que l'utilisateur existe ou non.
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.username, user.role),
        role=user.role,
    )
