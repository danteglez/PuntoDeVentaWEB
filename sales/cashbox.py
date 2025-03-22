import streamlit as st

ventas_simuladas = [
    {"fecha": "2025-03-22", "monto": 100.0},
    {"fecha": "2025-03-22", "monto": 55.5},
    {"fecha": "2025-03-21", "monto": 200.0}
]

def caja():
    st.title("Caja - Control de Dinero")

    total_dia = sum(venta["monto"] for venta in ventas_simuladas if venta["fecha"] == "2025-03-22")
    total_general = sum(venta["monto"] for venta in ventas_simuladas)

    st.subheader("Resumen de Ventas")
    st.write(f"Ventas del día: ${total_dia:.2f}")
    st.write(f"Ventas totales registradas: ${total_general:.2f}")

    st.subheader("Historial de Ventas")
    for venta in ventas_simuladas:
        st.write(f"Fecha: {venta['fecha']} - Monto: ${venta['monto']:.2f}")

    st.info("Este es un ejemplo. Puedes conectar esta sección con tu base de datos de ventas para que sea dinámica.")