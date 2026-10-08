"""Page privée : bilan analytique renvoyé par l'API."""

import streamlit as st

from services import api_client, session


def render() -> None:
    st.title("Bilan analytique")

    if not session.est_connecte():
        st.info("Connectez-vous avec un compte analyst pour consulter le bilan.")
        return

    try:
# Le contrôle d'accès est fait par l'API : le front affiche
# simplement la réponse ou l'erreur 401/403.
        bilan = api_client.obtenir("/analytics/bilan")
    except api_client.ErreurApi as erreur:
        if erreur.status_code == 401:
            # Token expiré ou invalide : on force une nouvelle connexion.
            session.deconnecter()
            st.warning("Session invalide ou expirée : reconnectez-vous.")
        elif erreur.status_code == 403:
            st.error("Accès refusé : ce bilan est réservé au rôle analyst (403).")
        else:
            st.error(erreur.message)
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Observations", bilan["nb_observations"])
    col2.metric("Total visiteurs", bilan["total_visiteurs"])
    col3.metric("Moyenne par observation", bilan["moyenne_visiteurs"])

    st.subheader("Total par médiathèque")
    st.dataframe(
        bilan["par_mediatheque"],
        width="stretch",
        column_config={
            "mediatheque": "Médiathèque",
            "total_visiteurs": "Total visiteurs",
        },
    )
