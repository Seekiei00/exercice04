"""Page de connexion (reader ou analyst)."""
import streamlit as st

from services import api_client, session


def _formulaire_connexion() -> None:
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


def _formulaire_inscription() -> None:

    with st.form("inscription"):
        identifiant = st.text_input("Identifiant (3 à 50 caractères)")
        mot_de_passe = st.text_input(
            "Mot de passe (8 caractères minimum)", type="password"
        )
        confirmation = st.text_input("Confirmer le mot de passe", type="password")
        soumettre = st.form_submit_button("Créer mon compte")

    if not soumettre:
        return

    if mot_de_passe != confirmation:
        st.error("Les mots de passe ne correspondent pas.")
        return

    try:
        api_client.inscription(identifiant, mot_de_passe)
    except api_client.ErreurApi as erreur:
        if erreur.status_code == 409:
            st.error("Cet identifiant est déjà utilisé.")
        elif erreur.status_code == 422:
            st.error(
                "Identifiant (lettres, chiffres, . _ -) ou mot de passe invalide."
            )
        else:
            st.error(erreur.message)
    else:
        st.success("Compte créé. Vous pouvez maintenant vous connecter.")


def render() -> None:
    st.title("Connexion")

    if session.est_connecte():
        st.success(
            f"Vous êtes connecté en tant que {st.session_state['username']} "
            f"(rôle : {st.session_state['role']})."
        )
        return

    st.subheader("Déjà un compte ?")
    _formulaire_connexion()

    st.divider()

    st.subheader("Pas encore de compte ? S'inscrire")
    _formulaire_inscription()
