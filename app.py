import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página (Ancho completo para que luzca en proyector)
st.set_page_config(page_title="Simulador de Producción", page_icon="🏭", layout="wide")

# Título y encabezado ejecutivo
st.title("🏭 Simulador Inteligente de Producción y Materia Prima")
st.markdown("Ingresa la cantidad a fabricar en el panel izquierdo para calcular insumos, tiempos y costos en tiempo real.")
st.divider()

# ==========================================
# 1. BASE DE DATOS INTERNA (Edita tus datos aquí)
# ==========================================
# Datos por CADA UNIDAD producida
datos_internos = [
    {"Material": "Materia Prima A (Acero/Tela)", "Unidad": "kg", "Consumo_Unitario": 2.5, "Costo_Unitario": 12.00, "Stock_Actual": 500},
    {"Material": "Materia Prima B (Resina/Hilo)", "Unidad": "litros", "Consumo_Unitario": 0.8, "Costo_Unitario": 8.50, "Stock_Actual": 120},
    {"Material": "Componente C (Tornillería/Botones)", "Unidad": "unidades", "Consumo_Unitario": 6.0, "Costo_Unitario": 0.35, "Stock_Actual": 1500},
    {"Material": "Empaque y Etiquetado", "Unidad": "unidades", "Consumo_Unitario": 1.0, "Costo_Unitario": 1.20, "Stock_Actual": 300},
]

# Tiempos por CADA UNIDAD producida (en minutos)
tiempo_preparacion_min = 2.0
tiempo_ensamblaje_min = 5.5
tiempo_control_calidad_min = 1.5
costo_hora_hombre = 15.00  # Costo operativo por hora

df_base = pd.DataFrame(datos_internos)

# ==========================================
# 2. PANEL LATERAL DE CONTROL (Input)
# ==========================================
st.sidebar.header("⚙️ Parámetros de Simulación")
cantidad = st.sidebar.number_input("Cantidad de unidades a producir:", min_value=1, max_value=10000, value=100, step=10)
turnos_dia = st.sidebar.slider("Horas laborales por día:", min_value=4, max_value=24, value=8)

st.sidebar.info("💡 **Tip para la presentación:** Cambia la cantidad en vivo para demostrar cómo el sistema recalcula alertas de inventario al instante.")

# ==========================================
# 3. MOTOR DE CÁLCULO
# ==========================================
df_calc = df_base.copy()
df_calc["Cantidad_Requerida"] = df_calc["Consumo_Unitario"] * cantidad
df_calc["Costo_Total_Material"] = df_calc["Cantidad_Requerida"] * df_calc["Costo_Unitario"]
df_calc["Balance_Stock"] = df_calc["Stock_Actual"] - df_calc["Cantidad_Requerida"]
df_calc["Estado"] = df_calc["Balance_Stock"].apply(lambda x: "✅ Disponible" if x >= 0 else "⚠️ Faltante")

# Cálculos de tiempo y costos globales
tiempo_total_min = (tiempo_preparacion_min + tiempo_ensamblaje_min + tiempo_control_calidad_min) * cantidad
tiempo_total_horas = tiempo_total_min / 60
dias_produccion = tiempo_total_horas / turnos_dia

costo_total_materiales = df_calc["Costo_Total_Material"].sum()
costo_mano_obra = tiempo_total_horas * costo_hora_hombre
costo_total_proyecto = costo_total_materiales + costo_mano_obra

# ==========================================
# 4. INTERFAZ VISUAL Y RESULTADOS
# ==========================================

# Fila 1: Tarjetas de Indicadores Clave (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Producción Solicitada", f"{cantidad:,} uds")
col2.metric("⏱️ Tiempo Total Estimado", f"{tiempo_total_horas:,.1f} hrs", f"{dias_produccion:,.1f} días laborales")
col3.metric("🧱 Costo Materia Prima", f"${costo_total_materiales:,.2f}")
col4.metric("💰 Costo Total Proyecto", f"${costo_total_proyecto:,.2f}", f"Incluye ${costo_mano_obra:,.2f} mano de obra")

st.divider()

# Fila 2: Tabla detallada y Alertas
col_izq, col_der = st.columns([1.4, 1])

with col_izq:
    st.subheader("📋 Desglose de Materia Prima e Inventario")
    
    # Mostrar alerta si falta algún material
    faltantes = df_calc[df_calc["Balance_Stock"] < 0]
    if not faltantes.empty:
        st.error(f"🚨 **Alerta de Inventario:** No hay suficiente stock para cubrir {len(faltantes)} material(es). Revisa la columna 'Estado'.")
    else:
        st.success("✅ **Inventario Óptimo:** Tienes stock suficiente para cubrir toda la orden de producción.")

    # Formatear tabla para que se vea limpia
    tabla_mostrar = df_calc[["Material", "Cantidad_Requerida", "Unidad", "Stock_Actual", "Costo_Total_Material", "Estado"]]
    st.dataframe(
        tabla_mostrar.style.format({
            "Cantidad_Requerida": "{:,.2f}",
            "Stock_Actual": "{:,.2f}",
            "Costo_Total_Material": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

with col_der:
    st.subheader("📊 Distribución de Costos")
    fig = px.pie(
        df_calc, 
        values="Costo_Total_Material", 
        names="Material", 
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
    st.plotly_chart(fig, use_container_width=True)
