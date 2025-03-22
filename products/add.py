import streamlit as st
from auth.db import connect_db

def ingresar_producto():
    st.title("Ingresar Producto")
    new_code = st.text_input("Código del producto:")
    new_name = st.text_input("Nombre del producto:")
    new_cost = st.number_input("Costo del producto:", min_value=0.01, format="%.2f")
    new_price = st.number_input("Precio de venta del producto:", min_value=0.01, format="%.2f")

    if st.button("Guardar Producto"):
        if new_code and new_name and new_cost and new_price:
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT codigo FROM productos WHERE codigo = %s", (new_code,))
                existing_product = cur.fetchone()
                if existing_product:
                    st.error("El código del producto ya existe")
                else:
                    cur.execute("INSERT INTO productos (codigo, nombre, costo, venta) VALUES (%s, %s, %s, %s)",
                                (new_code, new_name, new_cost, new_price))
                    conn.commit()
                    st.success("Producto guardado exitosamente")
                cur.close()
                conn.close()