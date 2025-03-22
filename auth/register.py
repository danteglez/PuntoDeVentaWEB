import streamlit as st
from auth.db import connect_db
import psycopg2

def register():
    st.title("Registrarse")
    new_username = st.text_input("Nuevo Usuario")
    new_password = st.text_input("Nueva Contraseña", type="password")

    if st.button("Registrar"):
        if new_username and new_password:
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (new_username, new_password))
                    conn.commit()
                    st.success("Usuario registrado exitosamente. Ahora puedes iniciar sesión.")
                except psycopg2.IntegrityError:
                    conn.rollback()
                    st.error("El usuario ya existe. Intenta con otro nombre de usuario.")
                cur.close()
                conn.close()
        else:
            st.error("Por favor completa todos los campos.")