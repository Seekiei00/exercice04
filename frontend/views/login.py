"""Page de connexion (reader ou analyst)."""

import streamlit as st

from services import api_client, session


def render() -> None:
    st.title("Connexion")

    if session.est_connecte():
        st.success(
            f"Vous êtes connecté en tant que {st.session_state['username']} "
            f"(rôle : {st.session_state['role']})."
        )
        return

    # st.form soumet les deux champs ensemble (pas à chaque caractère).
    with st.form("connexion"):
        identifiant = st.text_input("Identifiant")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        soumettre = st.form_submit_button("Se connecter")

    if soumettre:
        try:
            reponse = api_client.connexion(identifiant, mot_de_passe)
        except api_client.ErreurApi as erreur:
            if erreur.status_code == 401:
                st.error("Identifiant ou mot de passe incorrect.")
            else:
                st.error(erreur.message)
        else:
            # Seuls le JWT, l'identifiant et le rôle sont conservés.
            session.connecter(identifiant, reponse)
            st.rerun()
