"""Modèles SQLAlchemy de l'observatoire de fréquentation."""

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class User(Base):
    """Utilisateur pouvant s'authentifier."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('reader', 'analyst')", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    # Le mot de passe en clair n'est jamais enregistré.
    password_hash: Mapped[str] = mapped_column(String(100))

    # "reader" : consultation ; "analyst" : accès au bilan.
    role: Mapped[str] = mapped_column(String(20))


class Frequentation(Base):
    """Nombre de visiteurs d'une médiathèque pour un mois donné."""

    __tablename__ = "frequentations"
    __table_args__ = (
        CheckConstraint("visiteurs >= 0", name="ck_frequentations_visiteurs"),
        CheckConstraint(
            "mois ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'",
            name="ck_frequentations_mois",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mediatheque: Mapped[str] = mapped_column(String(100))

    # Format AAAA-MM, par exemple "2026-01".
    mois: Mapped[str] = mapped_column(String(7))
    visiteurs: Mapped[int] = mapped_column(Integer)
