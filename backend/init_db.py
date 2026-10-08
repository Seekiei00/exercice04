"""Initialise PostgreSQL : tables, comptes pédagogiques et 24 observations.

Lancement : python -m backend.init_db
"""

from sqlalchemy import select

# Importer les modèles les enregistre dans Base.metadata.
from backend.database import Base, SessionLocal, engine
from backend.models import Frequentation, User
from backend.security import hash_password

USERS = [
    ("analyst01", "Analyst2026!", "analyst"),
    ("reader01", "Reader2026!", "reader"),
]

MOIS = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]

# Visiteurs par médiathèque, dans l'ordre des mois ci-dessus.
# Jeu fictif mais fixe : 4 médiathèques x 6 mois = 24 observations.
VISITEURS = {
    "Médiathèque Centre": [3860, 4075, 4410, 4200, 4535, 3695],
    "Médiathèque Nord": [1930, 2040, 2205, 2100, 2270, 1850],
    "Médiathèque Sud": [1655, 1745, 1890, 1800, 1945, 1585],
    "Médiathèque des Rives": [875, 920, 1000, 950, 1025, 835],
}

OBSERVATIONS = [
    (mediatheque, mois, valeurs[index])
    for index, mois in enumerate(MOIS)
    for mediatheque, valeurs in VISITEURS.items()
]


def init_db() -> None:
    """Crée les tables puis insère les données si elles sont absentes."""

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for username, password, role in USERS:
            existing_user = db.scalar(
                select(User).where(User.username == username)
            )

            if existing_user is None:
                db.add(
                    User(
                        username=username,
                        password_hash=hash_password(password),
                        role=role,
                    )
                )

        # Les observations ne sont insérées qu'une fois : jeu stable.
        if db.scalar(select(Frequentation.id).limit(1)) is None:
            db.add_all(
                [
                    Frequentation(mediatheque=m, mois=mois, visiteurs=v)
                    for m, mois, v in OBSERVATIONS
                ]
            )

        db.commit()


if __name__ == "__main__":
    init_db()
    print(f"Base initialisée ({len(OBSERVATIONS)} observations).")
    print("analyst01 / Analyst2026!  (analyst)")
    print("reader01  / Reader2026!   (reader)")
