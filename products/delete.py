import streamlit as st
from auth.db import connect_db

def eliminar_producto():
    st.title("Eliminar Producto")
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT codigo, nombre FROM productos")
        productos = cur.fetchall()
        product_codes = {p[0]: p[1] for p in productos}
        cur.close()
        conn.close()

        if not product_codes:
            st.warning("No hay productos disponibles para eliminar")
            return

        selected_code = st.selectbox("Seleccione un producto para eliminar:", list(product_codes.keys()))
        if st.button("Eliminar Producto"):
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM productos WHERE codigo = %s", (selected_code,))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"Producto '{product_codes[selected_code]}' eliminado exitosamente")
                st.rerun()