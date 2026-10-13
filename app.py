import streamlit as st
from supabase import create_client, Client
import urllib.parse
from datetime import datetime, date

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

st.title("💆‍♀️ Sanay Masajes - Sistema de Gestión")
st.caption("📍 Morelos 458 | 💆‍♀️ Gabinete de Masajes")

tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Pacientes y Fichas", 
    "📅 Agenda y Turnos", 
    "📝 Visitas e Historial", 
    "🎁 Gift Cards"
])

# --- TAB 1: PACIENTES Y FICHAS ---
with tab1:
    st.header("Alta de Paciente")
    with st.form("form_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre Completo *")
        telefono = col2.text_input("Teléfono (ej: 5491123456789) *")
        email = col1.text_input("Email")
        recomendado = col2.text_input("Recomendado por")
        
        dolores = st.text_area("Dolores frecuentes / Zonas a tratar")
        alergias = st.text_input("Alergias a aceites / cremas")
        contraindicaciones = st.text_input("Contraindicaciones médicas")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and telefono:
                clean_phone = "".join(filter(str.isdigit, telefono))
                supabase.table("pacientes").insert({
                    "nombre_completo": nombre,
                    "telefono": clean_phone,
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
    res_p = supabase.table("pacientes").select("*").execute()
    pacientes = res_p.data
    
    if pacientes:
        opciones_p = {p["nombre_completo"]: p for p in pacientes}
        seleccionado = st.selectbox("Seleccionar Paciente", list(opciones_p.keys()))
        p = opciones_p[seleccionado]
        
        st.subheader(f"Ficha de {p['nombre_completo']}")
        st.write(f"📞 **Teléfono:** {p['telefono']}")
        st.write(f"✉️ **Email:** {p['email'] or 'No registrado'}")
        st.write(f"🩸 **Alergias:** {p['alergias_aceites'] or 'Ninguna'}")
        st.write(f"⚠️ **Contraindicaciones:** {p['contraindicaciones'] or 'Ninguna'}")
        st.write(f"📍 **Dolores/Zonas:** {p['dolores_frecuentes'] or 'Sin especificar'}")
        if p.get('recomendado_por'):
            st.info(f"👤 Recomendado por: {p['recomendado_por']}")

# --- TAB 2: AGENDA Y TURNOS ---
with tab2:
    st.header("Agendar Nuevo Turno")
    res_p = supabase.table("pacientes").select("*").execute()
    pacientes = res_p.data
    
    if pacientes:
        opciones_p = {p["nombre_completo"]: p for p in pacientes}
        with st.form("form_turno", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            p_sel = col_t1.selectbox("Paciente", list(opciones_p.keys()))
            servicio_t = col_t2.text_input("Servicio", "Masaje Descontracturante 60 min")
            
            col_d1, col_d2 = st.columns(2)
            fecha_t = col_d1.date_input("Fecha del turno", min_value=date.today())
            hora_t = col_d2.time_input("Hora del turno")
            
            notas_t = st.text_area("Notas del turno (opcional)")
            
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
                st.success(f"Turno agendado para {p_sel} el {fecha_t.strftime('%d/%m/%Y')} a las {hora_t.strftime('%H:%M')} hs.")
                st.rerun()

        st.divider()
        st.header("📋 Próximos Turnos Agendados")
        
        # Consultar turnos con datos de pacientes
        turnos_res = supabase.table("turnos").select("*, pacientes(nombre_completo, telefono)").order("fecha", desc=False).execute()
        turnos = turnos_res.data
        
        if turnos:
            for t in turnos:
                pac_nombre = t['pacientes']['nombre_completo'] if t.get('pacientes') else 'Desconocido'
                pac_tel = t['pacientes']['telefono'] if t.get('pacientes') else ''
                fecha_f = datetime.strptime(t['fecha'], "%Y-%m-%d").strftime("%d/%m/%Y")
                hora_f = t['hora'][:5]
                
                with st.expander(f"📅 {fecha_f} {hora_f} hs - {pac_nombre} ({t['servicio']})"):
                    st.write(f"👤 **Paciente:** {pac_nombre}")
                    st.write(f"📞 **Teléfono:** {pac_tel}")
                    st.write(f"💆 **Servicio:** {t['servicio']}")
                    st.write(f"📌 **Estado:** {t['estado']}")
                    if t.get('notas'):
                        st.write(f"📝 **Notas:** {t['notas']}")
                    
                    if pac_tel:
                        msg_turn_wa = f"Hola {pac_nombre}! Te confirmamos tu turno en Sanay Masajes (Morelos 458) para el {fecha_f} a las {hora_f} hs. ¡Te esperamos!"
                        url_wa = f"https://wa.me/{pac_tel}?text={urllib.parse.quote(msg_turn_wa)}"
                        st.markdown(f"👉 [📲 Recordar Turno por WhatsApp]({url_wa})")
        else:
            st.info("No hay turnos próximos agendados.")
    else:
        st.info("Registra pacientes en la primera pestaña para agendar turnos.")

# --- TAB 3: VISITAS E HISTORIAL ---
with tab3:
    st.header("Registrar Visita Realizada")
    res_p = supabase.table("pacientes").select("*").execute()
    pacientes = res_p.data
    
    if pacientes:
        opciones_p = {p["nombre_completo"]: p for p in pacientes}
        p_nombre = st.selectbox("Paciente que asiste al gabinete", list(opciones_p.keys()), key="visita_p")
        p_data = opciones_p[p_nombre]
        
        col_v1, col_v2 = st.columns(2)
        servicio = col_v1.text_input("Servicio realizado", "Masaje Descontracturante 60 min")
        atendido_por = col_v2.text_input("Atendido por", "Sanay Masajes")
        
        notas = st.text_area("Notas de la sesión / Evolución")
        
        if st.button("Registrar Visita"):
            supabase.table("visitas").insert({
                "paciente_id": p_data["id"],
                "servicio": servicio,
                "notas_sesion": notas,
                "atendido_por": atendido_por
            }).execute()
            st.success("Visita guardada correctamente.")
            
        st.divider()
        st.header("Mensajes Rápidos")
        
        link_google = "https://g.page/r/sanay-masajes/review"
        msg_review = f"Hola {p_data['nombre_completo']}, ¿cómo te sentiste luego del masaje? En Sanay Masajes nos ayudaría mucho que nos dejes tu opinión aquí: {link_google}"
        url_review = f"https://wa.me/{p_data['telefono']}?text={urllib.parse.quote(msg_review)}"
        st.markdown(f"👉 [⭐ Solicitar Reseña en Google Maps por WhatsApp]({url_review})")

# --- TAB 4: GIFT CARDS Y VOUCHERS ---
with tab4:
    st.header("🎁 Emitir Gift Card Digital")
    
    with st.form("form_gc"):
        col_g1, col_g2 = st.columns(2)
        codigo = col_g1.text_input("Código de Gift Card", "GIFT-100")
        comprador = col_g2.text_input("Nombre de quien regala")
        
        col_g3, col_g4 = st.columns(2)
        beneficiario = col_g3.text_input("Nombre del agasajado / De")
        servicio_gc = col_g4.text_input("Servicio / Tratamiento", "Masaje Relajante 60 min")
        
        tel_destino = st.text_input("Teléfono para enviar por WhatsApp (opcional, ej: 5491123456789)")
        
        submit_gc = st.form_submit_button("Generar Gift Card")
        
    if submit_gc:
        supabase.table("gift_cards").insert({
            "codigo": codigo,
            "comprador_nombre": comprador,
            "beneficiario_nombre": beneficiario,
            "servicio": servicio_gc
        }).execute()
        st.success(f"Gift Card {codigo} guardada en la base de datos.")
        
        st.divider()
        st.subheader("🖼️ Tarjeta de Regalo Generada")
        
        # Tarjeta visual formateada en HTML/CSS
        voucher_html = f"""
        <div style="
            background: linear-gradient(135deg, #2D3748 0%, #1A202C 100%);
            border: 2px solid #CBD5E0;
            border-radius: 15px;
            padding: 25px;
            color: white;
            font-family: 'Helvetica', sans-serif;
            max-width: 500px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            margin: auto;
        ">
            <h2 style="text-align: center; color: #E2E8F0; margin-bottom: 5px;">💆‍♀️ SANAY MASAJES</h2>
            <p style="text-align: center; font-size: 13px; color: #A0AEC0; margin-top: 0;">Morelos 458 | Voucher de Regalo</p>
            <hr style="border: 0.5px solid #4A5568;">
            <p style="font-size: 18px; color: #ECC94B; text-align: center; margin: 15px 0;"><strong>{servicio_gc.upper()}</strong></p>
            <div style="font-size: 15px; margin-bottom: 8px;">🎁 <strong>Para:</strong> {beneficiario}</div>
            <div style="font-size: 15px; margin-bottom: 8px;">💝 <strong>De parte de:</strong> {comprador}</div>
            <div style="font-size: 15px; margin-bottom: 8px;">🏷️ <strong>Código:</strong> {codigo}</div>
            <hr style="border: 0.5px solid #4A5568;">
            <p style="text-align: center; font-size: 12px; color: #CBD5E0; margin-bottom: 0;">Para agendar tu turno, contáctanos mencionando tu código de Gift Card.</p>
        </div>
        """
        st.markdown(voucher_html, unsafe_allow_html=True)
        
        # Botón para enviar por WhatsApp
        msg_gc_wa = (
            f"🎁 *¡Tienes una Gift Card de Sanay Masajes!*\n\n"
            f"💆‍♀️ *Tratamiento:* {servicio_gc}\n"
            f"👤 *Para:* {beneficiario}\n"
            f"💝 *De:* {comprador}\n"
            f"🏷️ *Código:* {codigo}\n\n"
            f"📍 *Dirección:* Morelos 458\n"
            f"📲 Contáctanos para agendar tu cita."
        )
        
        if tel_destino:
            clean_tel_gc = "".join(filter(str.isdigit, tel_destino))
            url_gc_wa = f"https://wa.me/{clean_tel_gc}?text={urllib.parse.quote(msg_gc_wa)}"
            st.markdown(f"<br><a href='{url_gc_wa}' target='_blank' style='display: inline-block; padding: 12px 20px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;'>📲 Enviar Voucher de Gift Card por WhatsApp</a>", unsafe_allow_html=True)
        else:
            url_gc_wa_gen = f"https://wa.me/?text={urllib.parse.quote(msg_gc_wa)}"
            st.markdown(f"<br><a href='{url_gc_wa_gen}' target='_blank' style='display: inline-block; padding: 12px 20px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;'>📲 Compartir Voucher por WhatsApp</a>", unsafe_allow_html=True)
