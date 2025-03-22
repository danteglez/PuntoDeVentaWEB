import streamlit as st
from products.add import ingresar_producto
from products.view import ver_productos
from products.delete import eliminar_producto
from sales.sell import venta
from sales.cashbox import caja

def main():
    st.title("Punto de Venta")
    menu = ["Venta", "Ingresar Producto", "Ver Productos", "Eliminar Producto", "Caja"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Venta":
        venta()
    elif choice == "Ingresar Producto":
        ingresar_producto()
    elif choice == "Ver Productos":
        ver_productos()
    elif choice == "Eliminar Producto":
        eliminar_producto()
    elif choice == "Caja":
        caja()

if __name__ == "__main__":
    main()