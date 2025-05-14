import streamlit as st
import psycopg2
import pandas as pd
import qrcode
import os
import cv2
import numpy as np
from PIL import Image
import io

DB_URL = "postgresql://postgres.mbidkiuthyjlvwqnsdpl:Dokiringuillas1@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
CART_KEY = "carrito"

def connect_db():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def generar_qr_bytes(codigo):
    qr = qrcode.make(codigo)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()

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
                if cur.fetchone():
                    st.error("El código del producto ya existe")
                else:
                    qr_bytes = generar_qr_bytes(new_code)
                    cur.execute("INSERT INTO productos (codigo, nombre, costo, venta, qr) VALUES (%s, %s, %s, %s, %s)",
                                (new_code, new_name, new_cost, new_price, psycopg2.Binary(qr_bytes)))
                    conn.commit()
                    st.success("Producto guardado exitosamente")
                    st.image(qr_bytes, caption="Código QR generado")
                cur.close()
                conn.close()

def ver_productos():
    st.title("Lista de Productos")
    conn = connect_db()
    if conn:
        df = pd.read_sql("SELECT * FROM productos", conn)
        conn.close()
        if not df.empty:
            for _, row in df.iterrows():
                with st.expander(f"{row['nombre']} (Código: {row['codigo']})"):
                    st.write(f"Costo: ${row['costo']:.2f}")
                    st.write(f"Precio de venta: ${row['venta']:.2f}")
                    if row.get("qr"):
                        qr_bytes = bytes(row["qr"])
                        st.image(qr_bytes, caption="QR del producto", width=150)
                    else:
                        st.warning("QR no disponible")
        else:
            st.warning("No hay productos disponibles")

def eliminar_producto():
    st.title("Eliminar Producto")
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT codigo, nombre FROM productos")
        productos = cur.fetchall()
        cur.close()
        conn.close()
        if not productos:
            st.warning("No hay productos para eliminar")
            return
        selected_code = st.selectbox("Seleccione un producto:", [p[0] for p in productos])
        if st.button("Eliminar Producto"):
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM productos WHERE codigo = %s", (selected_code,))
                conn.commit()
                cur.close()
                conn.close()
                st.success("Producto eliminado exitosamente")
                st.rerun()

def add_to_cart(code):
    if CART_KEY not in st.session_state:
        st.session_state[CART_KEY] = []
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT nombre, venta FROM productos WHERE codigo = %s", (code,))
        producto = cur.fetchone()
        cur.close()
        conn.close()
        if producto:
            st.session_state[CART_KEY].append({
                "codigo": code,
                "nombre": producto[0],
                "venta": producto[1]
            })
            st.success(f"Producto '{producto[0]}' agregado al carrito")

def display_cart():
    st.subheader("Carrito")
    carrito = st.session_state.get(CART_KEY, [])
    if not carrito:
        st.info("No hay productos en el carrito")
        return
    total = sum(item["venta"] for item in carrito)
    for idx, item in enumerate(carrito):
        st.write(f"{idx+1}. {item['nombre']} - ${item['venta']:.2f}")
    st.write(f"**Total:** ${total:.2f}")

def escanear_qr_desde_imagen(img):
    detector = cv2.QRCodeDetector()
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    data, bbox, _ = detector.detectAndDecode(img_cv)
    return data if data else None

def venta():
    st.subheader("Buscar Producto manualmente")
    search_query = st.text_input("Buscar por nombre o código:")
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT codigo, nombre, venta FROM productos WHERE nombre ILIKE %s OR codigo ILIKE %s",
                    (f"%{search_query}%", f"%{search_query}%"))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        for code, name, price in resultados:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Código:** {code} | **Nombre:** {name} | **Precio:** ${price:.2f}")
            with col2:
                if st.button("Agregar", key=code):
                    add_to_cart(code)

    st.markdown("---")
    st.subheader("Escanear Código QR desde Foto")
    foto = st.camera_input("Tomar o subir una imagen")

    if foto is not None:
        img = Image.open(foto)
        codigo = escanear_qr_desde_imagen(img)
        if codigo:
            st.success(f"QR detectado: {codigo}")
            add_to_cart(codigo)
        else:
            st.error("No se detectó ningún QR")

    display_cart()

def main():
    st.title("Punto de Venta")
    opciones = ["Venta", "Ingresar Producto", "Ver Productos", "Eliminar Producto"]
    seleccion = st.sidebar.selectbox("Menú", opciones)

    if seleccion == "Venta":
        venta()
    elif seleccion == "Ingresar Producto":
        ingresar_producto()
    elif seleccion == "Ver Productos":
        ver_productos()
    elif seleccion == "Eliminar Producto":
        eliminar_producto()

if __name__ == "__main__":
    main()
