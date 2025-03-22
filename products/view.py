import streamlit as st
import pandas as pd
from auth.db import connect_db

def ver_productos():
    st.title("Lista de Productos")
    conn = connect_db()
    if conn:
        df = pd.read_sql("SELECT * FROM productos", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("No hay productos disponibles")