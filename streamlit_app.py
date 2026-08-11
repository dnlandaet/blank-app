import streamlit as st
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Dashboard Público", layout="wide")

st.title("📊 Mi Dashboard Público")
st.write("¡Este dashboard se ejecuta 100% desde la nube!")

# Indicadores principales
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Totales", "$45,200", "+12%")
col2.metric("Nuevos Clientes", "320", "+5%")
col3.metric("Satisfacción", "98%", "+1%")

st.markdown("---")

# Gráfico de prueba
st.subheader("Rendimiento del Mes")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Ventas', 'Ingresos', 'Gastos']
)
st.line_chart(chart_data)