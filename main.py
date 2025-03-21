import streamlit as st
import psycopg2
import pandas as pd

# Conexión a Supabase PostgreSQL con la URL
DB_URL = "postgresql://postgres.mbidkiuthyjlvwqnsdpl:Dokiringuillas1@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
CART_KEY = "carrito"

def connect_db():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

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
                st.experimental_rerun()

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

def main():
    st.title("Punto de Venta")
    menu = ["Venta", "Ingresar Producto", "Ver Productos", "Eliminar Producto"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Venta":
        venta()
    elif choice == "Ingresar Producto":
        ingresar_producto()
    elif choice == "Ver Productos":
        ver_productos()
    elif choice == "Eliminar Producto":
        eliminar_producto()

if __name__ == "__main__":
    main()
