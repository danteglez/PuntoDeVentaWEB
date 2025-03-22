import streamlit as st
from auth.login import login
from auth.register import register
from auth.logout import logout
import main

def app():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        option = st.radio("Selecciona una opción", ["Iniciar Sesión", "Registrarse"])
        if option == "Iniciar Sesión":
            login()
        else:
            register()
    else:
        st.sidebar.button("Cerrar Sesión", on_click=logout)
        main.main()

if __name__ == "__main__":
    app()