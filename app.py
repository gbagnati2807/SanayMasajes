import streamlit as st
from supabase import create_client, Client
import urllib.parse

st.set_page_config(
    page_title="Sanay Masajes",
    page_icon="💆‍♀️",
    layout="wide"
)

# Conexión a Supabase usando Secrets
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.title("💆‍♀️ Sanay Masajes - Gestión")

tab1, tab2, tab3 = st.tabs(["👤 Pacientes y Fichas", "📅 Visitas y WhatsApp", "🎁 Gift Cards"])

# --- TAB 1: PACIENTES Y FICHAS ---
with tab1:
    st.header("Alta de Paciente")
    with st.form("form_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo *")
        telefono = col2.text_input("Teléfono (con código de país, ej: 549...) *")
        email = col1.text_input("Email")
        recomendado = col2.text_input("Recomendado por")
        
        dolores = st.text_area("Dolores frecuentes / Zonas a tratar")
        alergias = st.text_input("Alergias a aceites / cremas")
        contraindicaciones = st.text_input("Contraindicaciones médicas")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and telefono:
                supabase.table("pacientes").insert({
                    "nombre_completo": nombre,
                    "telefono": telefono,
                    "email": email,
                    "recomendado_por": recomendado,
                    "dolores_frecuentes": dolores,
                    "alergias_aceites": alergias,
                    "contraindicaciones": contraindicaciones
                }).execute()
                st.success(f"Paciente {nombre} guardado correctamente.")
                st.rerun()
            else:
                st.error("Nombre y Teléfono son obligatorios.")

    st.divider()
    st.header("Buscar Ficha de Paciente")
    res = supabase.table("pacientes").select("*").execute()
    pacientes = res.data
    
    if pacientes:
        opciones = {p["nombre_completo"]: p for p in pacientes}
        seleccionado = st.selectbox("Seleccionar Paciente", list(opciones.keys()))
        p = opciones[seleccionado]
        
        st.subheader(f"Ficha de {p['nombre_completo']}")
        st.write(f"📞 **Teléfono:** {p['telefono']}")
        st.write(f"✉️ **Email:** {p['email'] or 'No registrado'}")
        st.write(f"🩸 **Alergias:** {p['alergias_aceites'] or 'Ninguna'}")
        st.write(f"⚠️ **Contraindicaciones:** {p['contraindicaciones'] or 'Ninguna'}")
        st.write(f"📍 **Dolores/Zonas:** {p['dolores_frecuentes'] or 'Sin especificar'}")
        if p.get('recomendado_por'):
            st.info(f"👤 Recomendado por: {p['recomendado_por']}")

# --- TAB 2: VISITAS Y WHATSAPP ---
with tab2:
    st.header("Registrar Visita")
    res = supabase.table("pacientes").select("*").execute()
    pacientes = res.data
    
    if pacientes:
        opciones = {p["nombre_completo"]: p for p in pacientes}
        p_nombre = st.selectbox("Paciente atendido", list(opciones.keys()), key="visita_p")
        p_data = opciones[p_nombre]
        
        servicio = st.text_input("Servicio realizado", "Masaje Descontracturante 60 min")
        notas = st.text_area("Notas de la sesión / Evolución")
        
        if st.button("Registrar Visita"):
            supabase.table("visitas").insert({
                "paciente_id": p_data["id"],
                "servicio": servicio,
                "notas_sesion": notas
            }).execute()
            st.success("Visita guardada en el historial.")
            
        st.divider()
        st.header("Mensajes Rápidos de WhatsApp")
        
        # Mensaje Recordatorio
        msg_turno = f"Hola {p_data['nombre_completo']}! Te recordamos tu turno de masaje en Sanay Masajes (Morelos 458)."
        url_turno = f"https://wa.me/{p_data['telefono']}?text={urllib.parse.quote(msg_turno)}"
        st.markdown(f"👉 [📲 Enviar Recordatorio de Turno]({url_turno})")
        
        # Mensaje Reseña Google
        link_google = "https://g.page/r/sanay-masajes/review"
        msg_review = f"Hola {p_data['nombre_completo']}, ¿cómo te sentiste luego del masaje? Nos ayudaría mucho que nos dejes una opinión aquí: {link_google}"
        url_review = f"https://wa.me/{p_data['telefono']}?text={urllib.parse.quote(msg_review)}"
        st.markdown(f"👉 [⭐ Solicitar Reseña en Google Maps]({url_review})")

# --- TAB 3: GIFT CARDS ---
with tab3:
    st.header("Crear Gift Card")
    with st.form("form_gc", clear_on_submit=True):
        codigo = st.text_input("Código de Gift Card", "GIFT-100")
        comprador = st.text_input("Nombre de quien regala")
        beneficiario = st.text_input("Nombre del agasajado")
        servicio_gc = st.text_input("Servicio / Valor", "Masaje Relajante 60 min")
        
        if st.form_submit_button("Guardar Gift Card"):
            supabase.table("gift_cards").insert({
                "codigo": codigo,
                "comprador_nombre": comprador,
                "beneficiario_nombre": beneficiario,
                "servicio": servicio_gc
            }).execute()
            st.success(f"Gift Card {codigo} creada exitosamente.")
