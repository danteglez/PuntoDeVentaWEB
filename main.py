import streamlit as st
import psycopg2
import pandas as pd
import qrcode
import os
from streamlit_webrtc import webrtc_streamer
import av
import cv2

DB_URL = "postgresql://postgres.mbidkiuthyjlvwqnsdpl:Dokiringuillas1@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
CART_KEY = "carrito"

def connect_db():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def generar_qr_producto(codigo):
    os.makedirs("qrs", exist_ok=True)
    qr = qrcode.make(codigo)
    qr.save(f"qrs/{codigo}.png")

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
                    cur.execute("INSERT INTO productos (codigo, nombre, costo, venta) VALUES (%s, %s, %s, %s)",
                                (new_code, new_name, new_cost, new_price))
                    conn.commit()
                    generar_qr_producto(new_code)
                    st.success("Producto guardado exitosamente")
                    st.image(f"qrs/{new_code}.png", caption="Código QR generado")
                cur.close()
                conn.close()

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

# Clase del escáner QR con OpenCV
class QRScanner:
    def __init__(self):
        self.last_result = None

    def video_frame_callback(self, frame):
        img = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            self.last_result = data
            cv2.putText(img, f"QR: {data}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def run(self):
        webrtc_streamer(key="venta_qr", video_frame_callback=self.video_frame_callback)
        if self.last_result:
            add_to_cart(self.last_result)

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
    st.subheader("Escanear Código QR")
    scanner = QRScanner()
    scanner.run()

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
