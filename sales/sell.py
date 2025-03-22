import streamlit as st
from auth.db import connect_db
from sales.cart import add_to_cart, display_cart
from datetime import datetime

def registrar_venta_en_db():
    carrito = st.session_state.get("carrito", [])
    if not carrito:
        st.warning("El carrito está vacío. No se puede registrar la venta.")
        return

    conn = connect_db()
    if conn:
        cur = conn.cursor()
        for item in carrito:
            cur.execute(
                "INSERT INTO ventas (codigo_producto, nombre_producto, precio_venta, cantidad, fecha) VALUES (%s, %s, %s, %s, %s)",
                (item["codigo"], item["nombre"], item["venta"], 1, datetime.now())
            )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Venta registrada exitosamente.")
        st.session_state["carrito"] = []

def venta():
    st.subheader("Buscar Producto para Venta")
    search_query = st.text_input("Buscar producto por nombre o código:")
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT codigo, nombre, venta FROM productos WHERE nombre ILIKE %s OR codigo ILIKE %s", 
                    (f"%{search_query}%", f"%{search_query}%"))
        found_products = cur.fetchall()
        cur.close()
        conn.close()
        if found_products:
            for code, name, price in found_products:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Código:** {code} - **Nombre:** {name} - **Precio Venta:** ${price:.2f}")
                with col2:
                    if st.button("Agregar", key=code):
                        add_to_cart(code)
        else:
            st.warning("Producto no encontrado")

    display_cart()

    if st.button("Confirmar Venta"):
        registrar_venta_en_db()