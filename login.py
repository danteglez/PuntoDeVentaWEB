import streamlit as st
import psycopg2
import main  # Importamos el archivo main.py para redirigir después del login

# Conexión a Supabase PostgreSQL con la URL
DB_URL = "postgresql://postgres.mbidkiuthyjlvwqnsdpl:Dokiringuillas1@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

def connect_db():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def setup_database():
    """Crea la tabla usuarios si no existe."""
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

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

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.rerun()

def main():
    setup_database()
    
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
        st.write(f"Bienvenido, {st.session_state['username']}")
        st.write("Redirigiendo a la página principal...")
        main.main()  # Llamamos a la función principal del archivo main.py
        
if __name__ == "__main__":
    main()
