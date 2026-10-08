"""Connexion PostgreSQL avec SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import DATABASE_URL

# L'engine représente la connexion générale entre SQLAlchemy et PostgreSQL.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Fabrique une Session SQLAlchemy pour chaque requête qui en a besoin.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe de base commune aux modèles SQLAlchemy."""
    pass


def get_db():
    """Injecte une session puis la ferme après la requête."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
