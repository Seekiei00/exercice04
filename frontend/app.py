"""Point d'entrée Streamlit : navigation entre les pages.

Lancement : python -m streamlit run frontend/app.py
"""

import streamlit as st

from services import session
from views import login, private, public

st.set_page_config(
    page_title="Observatoire des médiathèques",
    layout="wide",
)

# Chaque page est une fonction render() définie dans views/.
pages = [
    st.Page(public.render, title="Fréquentation", url_path="frequentation", default=True),
    st.Page(login.render, title="Connexion", url_path="connexion"),
    st.Page(private.render, title="Bilan analytique", url_path="bilan"),
]

# Bandeau de session commun à toutes les pages.
with st.sidebar:
    if session.est_connecte():
        st.success(
            f"Connecté : {st.session_state['username']} "
            f"({st.session_state['role']})"
        )
        if st.button("Se déconnecter"):
            session.deconnecter()
            st.rerun()
    else:
        st.info("Non connecté")

st.navigation(pages).run()
