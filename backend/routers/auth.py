"""Authentification : vérification bcrypt puis émission d'un JWT."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import LoginRequest, RegisterRequest, TokenResponse
from backend.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    if db.scalar(select(User).where(User.username == data.username)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identifiant déjà utilisé",
        )

    db.add(
        User(
            username=data.username,
            password_hash=hash_password(data.password),
            role="reader",
        )
    )
    db.commit()

    return {"username": data.username, "role": "reader"}


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
