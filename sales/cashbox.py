import streamlit as st
from auth.db import connect_db

def obtener_monto_caja():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT monto FROM caja ORDER BY id LIMIT 1")
        resultado = cur.fetchone()
        cur.close()
        conn.close()
        return resultado[0] if resultado else 0.0
    return 0.0

def actualizar_monto_caja(nuevo_monto):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("UPDATE caja SET monto = %s WHERE id = (SELECT id FROM caja ORDER BY id LIMIT 1)", (nuevo_monto,))
        conn.commit()
        cur.close()
        conn.close()


def caja():
    st.title("Caja - Dinero Físico")

    monto_actual = obtener_monto_caja()
    nuevo_monto = st.number_input("Dinero actual en caja:", min_value=0.0, value=monto_actual, format="%.2f")

    if st.button("Actualizar Monto en Caja"):
        actualizar_monto_caja(nuevo_monto)
        st.success("Monto actualizado correctamente.")