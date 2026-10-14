import streamlit as st
from supabase import create_client, Client
import urllib.parse
from datetime import datetime, date
import random

st.set_page_config(
    page_title="SANAY Massage & Wellness",
    page_icon="🌸",
    layout="wide"
)

# URL RAW directa de tu GitHub
LOGO_URL = "https://github.com/gbagnati2807/SanayMasajes/blob/main/Logo.jpeg?raw=true"

# Estilo personalizado basado en la plantilla de SANAY
st.markdown("""
<style>
    .stApp {
        background-color: #FAF5F5;
    }
    h1, h2, h3 {
        color: #5A2A38 !important;
        font-family: 'Georgia', serif;
    }
    .sanay-sub {
        font-style: italic;
        color: #8C4A5C;
        font-size: 15px;
    }
    .stButton>button {
        background-color: #8C4A5C !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Conexión a Supabase usando Secrets
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ENCABEZADO CON LOGO
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    st.image(LOGO_URL, use_container_width=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #8C4A5C; font-size: 16px; margin-bottom: 25px;'>\"Tu bienestar también es parte del camino...\"</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Ficha del Cliente", 
    "📅 Agenda y Turnos", 
    "📝 Seguimiento de Sesiones", 
    "🎁 Gift Cards"
])

# --- TAB 1: FICHA DEL CLIENTE ---
with tab1:
    st.header("Alta de Ficha de Cliente")
    
    code_gen = f"SNY-{random.randint(100, 999)}"
    
    with st.form("form_paciente", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        nombre = col_c1.text_input("Nombre y Apellido *")
        telefono = col_c2.text_input("Cel / WhatsApp *")
        
        col_c3, col_c4, col_c5 = st.columns(3)
        fecha_nac = col_c3.date_input("Fecha de Nacimiento", value=date(1990, 1, 1))
        codigo = col_c4.text_input("Código de Cliente", code_gen)
        email = col_c5.text_input("Mail")
        
        st.subheader("Información Clínica / Salud")
        col_s1, col_s2 = st.columns(2)
        antecedentes = col_s1.text_area("Antecedentes")
        medicacion = col_s2.text_area("Medicación")
        
        col_s3, col_s4 = st.columns(2)
        actividad = col_s3.text_input("Actividad (física / laboral)")
        sintoma = col_s4.text_input("Síntoma principal")
        
        patologias = st.text_area("Patologías / Dolores habituales")
        alergias = st.text_input("Alergias a aceites / cremas")
        contraindicaciones = st.text_input("Contraindicaciones")
        
        if st.form_submit_button("Guardar Ficha"):
            if nombre and telefono:
                clean_phone = "".join(filter(str.isdigit, telefono))
                supabase.table("pacientes").insert({
                    "nombre_completo": nombre,
                    "telefono": clean_phone,
                    "email": email,
                    "codigo": codigo,
                    "fecha_nacimiento": fecha_nac.strftime("%Y-%m-%d"),
                    "antecedentes": antecedentes,
                    "medicacion": medicacion,
                    "actividad": actividad,
                    "sintoma": sintoma,
                    "patologias": patologias,
                    "alergias_aceites": alergias,
                    "contraindicaciones": contraindicaciones
                }).execute()
                st.success(f"Ficha de {nombre} guardada con éxito.")
                st.rerun()
            else:
                st.error("Nombre y Celular son obligatorios.")

    st.divider()
    st.header("Buscar Ficha de Cliente")
    res_p = supabase.table("pacientes").select("*").execute()
