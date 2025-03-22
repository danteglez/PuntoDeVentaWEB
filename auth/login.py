import streamlit as st
from auth.db import connect_db

def login():
    st.title("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if user:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Inicio de sesión exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")