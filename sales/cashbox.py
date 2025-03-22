import streamlit as st
from auth.db import connect_db
from sales.cart import add_to_cart, display_cart
from datetime import datetime

CAJA_KEY = "dinero_en_caja"

def registrar_venta_en_db():
    carrito = st.session_state.get("carrito", [])
    if not carrito:
        st.warning("El carrito está vacío. No se puede registrar la venta.")
        return False, 0.0

    total = sum(item["venta"] for item in carrito)
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
        return True, total
    return False, 0.0

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
        exito, total = registrar_venta_en_db()
        if exito:
            pago = st.number_input("¿Con cuánto te pagan?", min_value=0.0, format="%.2f")
            if pago >= total:
                cambio = pago - total
                st.success(f"Cambio a entregar: ${cambio:.2f}")

                # Actualiza caja automáticamente
                if CAJA_KEY not in st.session_state:
                    st.session_state[CAJA_KEY] = 0.0
                st.session_state[CAJA_KEY] += total

                st.session_state["carrito"] = []
            else:
                st.error("El pago es menor al total. Verifica el monto.")
