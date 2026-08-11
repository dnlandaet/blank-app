import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Configuración inicial de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard AR - Cierre 2024 vs 2025",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análisis Comparativo de Cuentas por Cobrar (AR)")
st.markdown("Comparación de **Total Balance** y **AR Vencido** (2024 vs 2025) enfocada en los analistas **Daniel Landaeta** y **Maria Bedoya**.")

# ---------------------------------------------------------
# 1. BOTÓN DE CARGA DE DATOS (File Uploader)
# ---------------------------------------------------------
st.sidebar.header("📁 Cargar Archivo de Datos")
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo Excel (.xlsx, .xls) o CSV (Columnas A a AA)",
    type=["xlsx", "xls", "csv"]
)

@st.cache_data
def process_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    # Limpiar espacios extra en nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Convertir 'Balance as of' a fecha y extraer el año
    if 'Balance as of' in df.columns:
        df['Balance as of'] = pd.to_datetime(df['Balance as of'], errors='coerce')
        df['Año'] = df['Balance as of'].dt.year
    
    # Normalizar columna Analyst
    if 'Analyst' in df.columns:
        df['Analyst'] = df['Analyst'].astype(str).str.strip()
        
    # Columnas numéricas de interés
    numeric_columns = [
        'Credit limit', 'Annual Sales', 'Total Balance in LC',
        'To 0', 'From 1 To 30', 'From 31 To 60', 'From 61 To 90', 'From 91',
        'Total Past Due', 'To 0 Adjusted', 'From 1 To 30 Adjusted',
        'From 31 To 60 Adjusted', 'From 61 To 90 Adjusted', 'From 91 Adjusted',
        'Total Past Due Adjusted'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', '').str.replace('$', ''),
                errors='coerce'
            ).fillna(0)
            
    return df

# Carga de datos real o datos de muestra para visualización previa
if uploaded_file is not None:
    df = process_data(uploaded_file)
    st.sidebar.success("✅ ¡Datos cargados correctamente!")
else:
    st.info("👆 Por favor sube tu archivo con las columnas de A a AA usando el botón de la izquierda. Abajo se muestran datos de prueba de ejemplo:")
    
    demo_data = {
        'Customer Name': ['Cliente 1', 'Cliente 2', 'Cliente 3', 'Cliente 4', 'Cliente 5', 'Cliente 6'],
        'Total Balance in LC': [120000, 250000, 180000, 310000, 140000, 290000],
        'Total Past Due': [30000, 75000, 40000, 110000, 25000, 95000],
        'Balance as of': ['2024-12-31', '2024-12-31', '2025-12-31', '2025-12-31', '2024-12-31', '2025-12-31'],
        'Analyst': ['Daniel Landaeta', 'Maria Bedoya', 'Daniel Landaeta', 'Maria Bedoya', 'Daniel Landaeta', 'Maria Bedoya']
    }
    df = pd.DataFrame(demo_data)
    df['Balance as of'] = pd.to_datetime(df['Balance as of'])
    df['Año'] = df['Balance as of'].dt.year

# ---------------------------------------------------------
# 2. FILTROS DE INTERFAZ
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros")

analistas_disponibles = list(df['Analyst'].dropna().unique())
analistas_meta = [a for a in ['Daniel Landaeta', 'Maria Bedoya'] if a in analistas_disponibles]
default_analistas = analistas_meta if len(analistas_meta) > 0 else analistas_disponibles

selected_analysts = st.sidebar.multiselect(
    "Seleccionar Analista(s):",
    options=analistas_disponibles,
    default=default_analistas
)

anios_disponibles = sorted([int(y) for y in df['Año'].dropna().unique()])
default_years = [y for y in [2024, 2025] if y in anios_disponibles]

selected_years = st.sidebar.multiselect(
    "Seleccionar Años a Comparar:",
    options=anios_disponibles,
    default=default_years if len(default_years) > 0 else anios_disponibles
)

df_filtered = df[(df['Analyst'].isin(selected_analysts)) & (df['Año'].isin(selected_years))]

# ---------------------------------------------------------
# 3. METRICAS / KPIS COMPARATIVOS
# ---------------------------------------------------------
st.subheader("📌 Resumen General de Indicadores")

col1, col2, col3, col4 = st.columns(4)

balance_2024 = df_filtered[df_filtered['Año'] == 2024]['Total Balance in LC'].sum()
balance_2025 = df_filtered[df_filtered['Año'] == 2025]['Total Balance in LC'].sum()

ar_2024 = df_filtered[df_filtered['Año'] == 2024]['Total Past Due'].sum()
ar_2025 = df_filtered[df_filtered['Año'] == 2025]['Total Past Due'].sum()

var_balance = ((balance_2025 - balance_2024) / balance_2024 * 100) if balance_2024 > 0 else 0
var_ar = ((ar_2025 - ar_2024) / ar_2024 * 100) if ar_2024 > 0 else 0

col1.metric("Total Balance (2024)", f"${balance_2024:,.2f}")
col2.metric("Total Balance (2025)", f"${balance_2025:,.2f}", f"{var_balance:+.1f}%")

col3.metric("AR Vencido (2024)", f"${ar_2024:,.2f}")
col4.metric("AR Vencido (2025)", f"${ar_2025:,.2f}", f"{var_ar:+.1f}%", delta_color="inverse")

st.markdown("---")

# ---------------------------------------------------------
# 4. GRÁFICOS Y ANÁLISIS
# ---------------------------------------------------------
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📊 Comparación AR Vencido por Analista")
    summary = df_filtered.groupby(['Analyst', 'Año'])[['Total Balance in LC', 'Total Past Due']].sum().reset_index()
    
    fig_ar = px.bar(
        summary,
        x='Analyst',
        y='Total Past Due',
        color='Año',
        barmode='group',
        text_auto='.3s',
        title="AR Vencido (2024 vs 2025)",
        labels={'Total Past Due': 'Monto Vencido ($)', 'Analyst': 'Analista'},
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    st.plotly_chart(fig_ar, use_container_width=True)

with col_g2:
    st.subheader("📈 % AR Vencido vs Total Balance")
    summary['% Vencido'] = (summary['Total Past Due'] / summary['Total Balance in LC']) * 100
    
    fig_pct = px.bar(
        summary,
        x='Analyst',
        y='% Vencido',
        color='Año',
        barmode='group',
        text_auto='.1f',
        title="Porcentaje Vencido sobre el Total Balance",
        labels={'% Vencido': '% AR Vencido'},
        color_discrete_sequence=['#2ca02c', '#d62728']
    )
    st.plotly_chart(fig_pct, use_container_width=True)

# ---------------------------------------------------------
# 5. TABLA RESUMEN DETALLADA
# ---------------------------------------------------------
st.subheader("📋 Tabla Detallada por Analista y Año")

tabla_resumen = df_filtered.groupby(['Analyst', 'Año']).agg({
    'Total Balance in LC': 'sum',
    'Total Past Due': 'sum'
}).reset_index()

tabla_resumen['% AR Vencido'] = (tabla_resumen['Total Past Due'] / tabla_resumen['Total Balance in LC']) * 100

st.dataframe(
    tabla_resumen.style.format({
        'Total Balance in LC': '${:,.2f}',
        'Total Past Due': '${:,.2f}',
        '% AR Vencido': '{:.2f}%'
    }),
    use_container_width=True
)