from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import func, select

from backend.config import JWT_ALGORITHM, JWT_SECRET
from backend.database import SessionLocal
from backend.models import Frequentation

BILAN = "/analytics/bilan"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_login_mauvais_mot_de_passe(client):
    # Identifiants incorrects : 401, aucun token.
    response = client.post(
        "/auth/login", json={"username": "analyst01", "password": "faux"}
    )
    assert response.status_code == 401


def test_jwt_contient_les_claims_attendus(analyst_token):
    # Le JWT est signé (pas chiffré) : ses claims sont lisibles.
    payload = jwt.decode(analyst_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "analyst01"
    assert payload["role"] == "analyst"
    assert {"iat", "exp"} <= set(payload)


def test_bilan_analyst_autorise(client, analyst_token):
    # Rôle analyst : 200 et valeurs calculées sur la base.
    response = client.get(BILAN, headers=_auth(analyst_token))
    assert response.status_code == 200
    body = response.json()

    with SessionLocal() as db:
        count, total = db.execute(
            select(func.count(Frequentation.id), func.sum(Frequentation.visiteurs))
        ).one()

    assert body["nb_observations"] == count == 24
    assert body["total_visiteurs"] == total
    assert body["moyenne_visiteurs"] == round(total / count, 2)


def test_bilan_sans_token(client):
    # Aucun en-tête Authorization : 401.
    assert client.get(BILAN).status_code == 401


def test_bilan_token_invalide(client):
    # Token falsifié : la signature est refusée, 401.
    assert client.get(BILAN, headers=_auth("pas.un.jwt")).status_code == 401


def test_bilan_token_expire(client):
    # Token correctement signé mais expiré : 401.
    passe = datetime.now(timezone.utc) - timedelta(hours=1)
    token = jwt.encode(
        {"sub": "analyst01", "role": "analyst", "iat": passe, "exp": passe},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    assert client.get(BILAN, headers=_auth(token)).status_code == 401


def test_bilan_reader_interdit(client, reader_token):
    # Authentifié mais rôle reader : 403.
    assert client.get(BILAN, headers=_auth(reader_token)).status_code == 403
