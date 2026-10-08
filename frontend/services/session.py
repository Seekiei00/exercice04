"""Gestion simplifiée de la session Streamlit."""

import streamlit as st


def est_connecte() -> bool:
    """Indique si un JWT est présent dans la session courante."""
    return bool(st.session_state.get("access_token"))


def connecter(username: str, reponse: dict) -> None:
    """Mémorise le JWT et les informations utiles (pas le mot de passe)."""
    st.session_state["access_token"] = reponse["access_token"]
    st.session_state["username"] = username
    st.session_state["role"] = reponse["role"]


def deconnecter() -> None:
    """Efface les informations d'authentification de cette session."""
    for cle in ("access_token", "username", "role"):
        st.session_state.pop(cle, None)
