"""Page publique : fréquentation paginée, accessible sans connexion."""

import streamlit as st

from services import api_client

PAGE_SIZE = 5

def render() -> None:
    st.title("Fréquentation des médiathèques")

# Streamlit réexécute le script à chaque interaction : le numéro de page est donc conservé dans la session.
    if "page_frequentations" not in st.session_state:
        st.session_state["page_frequentations"] = 1

    try:
        donnees = api_client.obtenir(
            "/frequentations",
            params={
                "page": st.session_state["page_frequentations"],
                "page_size": PAGE_SIZE,
            },
        )
    except api_client.ErreurApi as erreur:
        st.error(erreur.message)
        return

    st.dataframe(
        donnees["items"],
        width="stretch",
        column_config={
            "id": "Id",
            "mediatheque": "Médiathèque",
            "mois": "Mois",
            "visiteurs": "Visiteurs",
        },
    )
    st.caption(
        f"Page {donnees['page']} / {donnees['pages']} — "
        f"{donnees['total']} observations"
    )

    precedent, suivant = st.columns(2)
    with precedent:
        if st.button("Précédent", disabled=donnees["page"] <= 1):
            st.session_state["page_frequentations"] -= 1
            st.rerun()
    with suivant:
        if st.button("Suivant", disabled=donnees["page"] >= donnees["pages"]):
            st.session_state["page_frequentations"] += 1
            st.rerun()
