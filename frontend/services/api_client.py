"""Client HTTP commun à toutes les fonctionnalités Streamlit.

Le but est d'éviter de répéter requests.get(), les URLs,
le timeout et le header Authorization dans le front.
"""
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class ErreurApi(Exception):
    """Erreur simplifiée présentée aux pages Streamlit."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _api_url() -> str:
    """Retourne l'adresse de FastAPI définie dans .env."""

    return os.getenv(
        "API_URL",
        "http://127.0.0.1:8000",
    ).rstrip("/")


def _timeout() -> float:
    """Retourne le délai maximal autorisé pour un appel HTTP."""

    return float(
        os.getenv("API_TIMEOUT_SECONDS", "5")
    )


def _headers() -> dict[str, str]:
    """Ajoute automatiquement le JWT s'il existe dans la session."""

    token = st.session_state.get("access_token")

    if not token:
        return {}

# Toutes les pages bénéficient ainsi du même mécanisme JWT.
    return {
        "Authorization": f"Bearer {token}"
    }


def appeler(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
) -> dict:
    """Exécute un appel HTTP vers FastAPI.

    La gestion réseau, le timeout, le JWT et les erreurs HTTP
    sont centralisés ici plutôt que répétés dans le front.
    """

    try:
        response = requests.request(
            method=method,
            url=f"{_api_url()}{path}",
            params=params,
            json=json,
            headers=_headers(),
            timeout=_timeout(),
        )

    except requests.exceptions.Timeout as error:
        raise ErreurApi(
            "L'API n'a pas répondu dans le délai prévu."
        ) from error

    except requests.exceptions.RequestException as error:
        raise ErreurApi(
            "Impossible de joindre l'API."
        ) from error

    if response.ok:
        return response.json()

    # On transforme les erreurs HTTP en une exception unique que les pages Streamlit savent afficher simplement.
    messages = {
        401: "Session absente, invalide ou expirée.",
        403: "Votre rôle ne permet pas cet accès.",
        404: "Ressource introuvable.",
        409: "Cette ressource existe déjà.",
        422: "Paramètres invalides.",
    }

    raise ErreurApi(
        messages.get(
            response.status_code,
            f"Erreur API ({response.status_code}).",
        ),
        status_code=response.status_code,
    )


def connexion(username: str, password: str) -> dict:
    """Appelle POST /auth/login."""

    return appeler(
        "POST",
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )


def inscription(username: str, password: str) -> dict:

    return appeler(
        "POST",
        "/auth/register",
        json={
            "username": username,
            "password": password,
        },
    )


def obtenir(
    path: str,
    params: dict | None = None,
) -> dict:

    return appeler(
        "GET",
        path,
        params=params,
    )
