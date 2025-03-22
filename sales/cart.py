import streamlit as st
from auth.db import connect_db

CART_KEY = "carrito"

def add_to_cart(code):
    if CART_KEY not in st.session_state:
        st.session_state[CART_KEY] = []
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT nombre, venta FROM productos WHERE codigo = %s", (code,))
        product = cur.fetchone()
        cur.close()
        conn.close()
        if product:
            st.session_state[CART_KEY].append({"codigo": code, "nombre": product[0], "venta": product[1]})

def display_cart():
    st.subheader("Productos en el carrito")
    carrito = st.session_state.get(CART_KEY, [])
    if not carrito:
        st.info("No hay productos en el carrito")
        return
    total = sum(item["venta"] for item in carrito)
    for idx, item in enumerate(carrito):
        st.write(f"{idx+1}. {item['nombre']} - Precio Venta: ${item['venta']:.2f}")
    st.write(f"**Total a pagar:** ${total:.2f}")