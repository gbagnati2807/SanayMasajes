import streamlit as st
from supabase import create_client, Client
import urllib.parse
from datetime import datetime, date
import random
import os
import base64

st.set_page_config(
    page_title="SANAY Massage & Wellness",
    page_icon="🌸",
    layout="wide"
)

# Función para convertir la imagen a Base64
def get_image_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_image_base64("logo.png")

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
    .sanay-header {
        background: linear-gradient(135deg, #FDF2F4 0%, #F5E3E6 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #E8C5CE;
        text-align: center;
        margin-bottom: 25px;
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

# Encabezado con Logo o Texto
if logo_b64:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.image("logo.png", use_container_width=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #8C4A5C; font-size: 16px; margin-bottom: 25px;'>\"Tu bienestar también es parte del camino...\"</p>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="sanay-header">
        <h1 style="margin:0; font-size: 32px;">SANAY</h1>
        <p style="margin:0; font-weight: bold; letter-spacing: 2px; color: #733948;">MASSAGE & WELLNESS</p>
        <p class="sanay-sub">"Tu bienestar también es parte del camino..."</p>
    </div>
    """, unsafe_allow_html=True)

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
    pacientes = res_p.data
    
    if pacientes:
        opciones_p = {f"{p.get('codigo') or 'SNY'} - {p['nombre_completo']}": p for p in pacientes}
        seleccionado = st.selectbox("Seleccionar Cliente", list(opciones_p.keys()))
        p = opciones_p[seleccionado]
        
        st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #8C4A5C; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h3>👤 {p['nombre_completo']} <span style='font-size:16px; color:#8C4A5C;'>(Código: {p.get('codigo', 'N/A')})</span></h3>
            <p><strong>📱 Cel:</strong> {p['telefono']} | <strong>✉️ Mail:</strong> {p.get('email', 'N/A')} | <strong>🎂 Nacimiento:</strong> {p.get('fecha_nacimiento', 'N/A')}</p>
            <hr>
            <p><strong>🩺 Antecedentes:</strong> {p.get('antecedentes', 'N/A')}</p>
            <p><strong>💊 Medicación:</strong> {p.get('medicacion', 'N/A')}</p>
            <p><strong>🏃 Actividad:</strong> {p.get('actividad', 'N/A')}</p>
            <p><strong>🩸 Síntoma:</strong> {p.get('sintoma', 'N/A')}</p>
            <p><strong>⚠️ Patologías / Dolores:</strong> {p.get('patologias', 'N/A')}</p>
            <p><strong>🌿 Alergias:</strong> {p.get('alergias_aceites', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 2: AGENDA Y TURNOS ---
with tab2:
    st.header("Agendar Nuevo Turno")
    res_p = supabase.table("pacientes").select("*").execute()
    pacientes = res_p.data
    
    if pacientes:
        opciones_p = {p["nombre_completo"]: p for p in pacientes}
        with st.form("form_turno", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            p_sel = col_t1.selectbox("Cliente", list(opciones_p.keys()))
            servicio_t = col_t2.text_input("Servicio", "Masaje Descontracturante 60 min")
            
            col_d1, col_d2 = st.columns(2)
            fecha_t = col_d1.date_input("Fecha", min_value=date.today())
            hora_t = col_d2.time_input("Hora")
            
            notas_t = st.text_area("Observaciones del turno")
            
            if st.form_submit_button("Agendar Turno"):
                p_data = opciones_p[p_sel]
                supabase.table("turnos").insert({
                    "paciente_id": p_data["id"],
                    "fecha": fecha_t.strftime("%Y-%m-%d"),
                    "hora": hora_t.strftime("%H:%M:%S"),
                    "servicio": servicio_t,
                    "notas": notas_t,
                    "estado": "CONFIRMADO"
                }).execute()
                st.success(f"Turno agendado para {p_sel}.")
                st.rerun()

        st.divider()
        st.header("📋 Agenda de Turnos Próximos")
        turnos_res = supabase.table("turnos").select("*, pacientes(nombre_completo, telefono)").order("fecha", desc=False).execute()
        turnos = turnos_res.data
        
        if turnos:
            for t in turnos:
                pac_nombre = t['pacientes']['nombre_completo'] if t.get('pacientes') else 'Desconocido'
                pac_tel = t['pacientes']['telefono'] if t.get('pacientes') else ''
                fecha_f = datetime.strptime(t['fecha'], "%Y-%m-%d").strftime("%d/%m/%Y")
                hora_f = t['hora'][:5]
                
                with st.expander(f"📅 {fecha_f} {hora_f} hs - {pac_nombre} ({t['servicio']})"):
                    st.write(f"👤 **Cliente:** {pac_nombre}")
                    st.write(f"📞 **Cel:** {pac_tel}")
                    st.write(f"💆 **Servicio:** {t['servicio']}")
                    if pac_tel:
                        msg_turn_wa = f"Hola {pac_nombre}! Te recordamos tu turno en SANAY Massage & Wellness (Morelos 458) para el {fecha_f} a las {hora_f} hs."
                        url_wa = f"https://wa.me/{pac_tel}?text={urllib.parse.quote(msg_turn_wa)}"
                        st.markdown(f"👉 [📲 Recordar Turno por WhatsApp]({url_wa})")
        else:
            st.info("No hay turnos próximos agendados.")

# --- TAB 3: SEGUIMIENTO DE SESIONES ---
with tab3:
    st.header("Registrar Sesión y Seguimiento")
    res_p = supabase.table("pacientes").select("*").execute()
    pacientes = res_p.data
    
    if pacientes:
        opciones_p = {p["nombre_completo"]: p for p in pacientes}
        p_nombre = st.selectbox("Cliente", list(opciones_p.keys()), key="visita_p")
        p_data = opciones_p[p_nombre]
        
        col_v1, col_v2 = st.columns(2)
        fecha_s = col_v1.date_input("Fecha de Sesión", value=date.today())
        servicio_s = col_v2.text_input("Servicio", "Masaje Descontracturante 60 min")
        
        col_v3, col_v4 = st.columns(2)
        bonificacion = col_v3.text_input("Bonificación / Descuento", "Sin bonificación")
        pago = col_v4.text_input("Pago / Método", "Efectivo / Transferencia")
        
        observacion = st.text_area("Observación de la sesión")
        
        if st.button("Guardar en Ficha"):
            supabase.table("visitas").insert({
                "paciente_id": p_data["id"],
                "servicio": servicio_s,
                "notas_sesion": observacion,
                "bonificacion": bonificacion,
                "pago": pago,
                "fecha_hora": fecha_s.strftime("%Y-%m-%d")
            }).execute()
            st.success("Sesión registrada en el historial del cliente.")
            st.rerun()
            
        st.divider()
        st.subheader(f"📊 Tabla de Seguimiento de {p_nombre}")
        
        visitas_res = supabase.table("visitas").select("*").eq("paciente_id", p_data["id"]).order("fecha_hora", desc=True).execute()
        v_list = visitas_res.data
        
        if v_list:
            import pandas as pd
            tabla_data = []
            for v in v_list:
                tabla_data.append({
                    "Fecha": v.get("fecha_hora", "")[:10],
                    "Servicio": v.get("servicio", ""),
                    "Observación": v.get("notas_sesion", ""),
                    "Bonificación": v.get("bonificacion", "-"),
                    "Pago": v.get("pago", "-")
                })
            st.dataframe(pd.DataFrame(tabla_data), use_container_width=True)
        else:
            st.info("Sin sesiones registradas aún para este cliente.")

# --- TAB 4: GIFT CARDS ---
with tab4:
    st.header("🎁 Emitir Gift Card Sanay")
    
    codigo_default = f"SNY-GIFT-{random.randint(100, 999)}"
    
    with st.form("form_gc"):
        col_g1, col_g2 = st.columns(2)
        codigo = col_g1.text_input("Código de Gift Card", codigo_default)
        comprador = col_g2.text_input("Nombre de quien regala")
        
        col_g3, col_g4 = st.columns(2)
        beneficiario = col_g3.text_input("Nombre del agasajado")
        servicio_gc = col_g4.text_input("Servicio / Valor", "Masaje Relajante 60 min")
        
        tel_destino = st.text_input("Celular de envío por WhatsApp (ej: 5491123456789)")
        
        submit_gc = st.form_submit_button("Generar Voucher")
        
    if submit_gc:
        clean_tel_gc = "".join(filter(str.isdigit, tel_destino)) if tel_destino else ""
        
        supabase.table("gift_cards").insert({
            "codigo": codigo,
            "comprador_nombre": comprador,
            "beneficiario_nombre": beneficiario,
            "servicio": servicio_gc,
            "telefono_destino": clean_tel_gc
        }).execute()
        st.success(f"Gift Card {codigo} guardada.")
        
        st.divider()
        st.subheader("🌸 Voucher Estilo SANAY")
        
        if logo_b64:
            header_voucher = f'<img src="data:image/png;base64,{logo_b64}" style="max-width: 250px; margin-bottom: 10px;">'
        else:
            header_voucher = '<h2 style="margin:0; color: #5A2A38;">SANAY</h2><p style="margin:0; font-size: 11px; letter-spacing: 2px; font-weight: bold;">MASSAGE & WELLNESS</p>'
        
        voucher_html = f"""
        <div style="
            background: linear-gradient(135deg, #FDF2F4 0%, #F5E3E6 100%);
            border: 2px solid #E8C5CE;
            border-radius: 15px;
            padding: 25px;
            color: #5A2A38;
            font-family: 'Georgia', serif;
            max-width: 500px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin: auto;
            text-align: center;
        ">
            {header_voucher}
            <p style="font-style: italic; font-size: 12px; color: #8C4A5C;">"Tu bienestar también es parte del camino..."</p>
            <hr style="border: 0.5px solid #CBD5E0;">
            <p style="font-size: 18px; color: #8C4A5C; margin: 15px 0;"><strong>{servicio_gc.upper()}</strong></p>
            <p style="font-size: 14px; text-align: left;">🎁 <strong>Para:</strong> {beneficiario}</p>
            <p style="font-size: 14px; text-align: left;">💝 <strong>De parte de:</strong> {comprador}</p>
            <p style="font-size: 14px; text-align: left;">🏷️ <strong>Código:</strong> {codigo}</p>
            <hr style="border: 0.5px solid #CBD5E0;">
            <p style="font-size: 11px; color: #718096;">📍 Morelos 458 | Presenta este código para agendar tu cita.</p>
        </div>
        """
        st.markdown(voucher_html, unsafe_allow_html=True)
        
        msg_gc_wa = (
            f"🌸 *¡Tienes un Voucher de Regalo de SANAY Massage & Wellness!*\n\n"
            f"💆‍♀️ *Servicio:* {servicio_gc}\n"
            f"🎁 *Para:* {beneficiario}\n"
            f"💝 *De parte de:* {comprador}\n"
            f"🏷️ *Código:* {codigo}\n\n"
            f"📍 *Dirección:* Morelos 458\n"
            f"✨ _Tu bienestar también es parte del camino..._\n"
            f"📲 Contáctanos para agendar tu cita."
        )
        
        if clean_tel_gc:
            url_gc_wa = f"https://wa.me/{clean_tel_gc}?text={urllib.parse.quote(msg_gc_wa)}"
            st.markdown(f"<br><a href='{url_gc_wa}' target='_blank' style='display: inline-block; padding: 12px 20px; background-color: #8C4A5C; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;'>📲 Enviar Voucher por WhatsApp</a>", unsafe_allow_html=True)
