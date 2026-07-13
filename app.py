import requests
import hashlib
import streamlit as st
from google import genai

# Configuración de la pagina 
st.set_page_config(
    page_title="CentinelaID",
    page_icon="🛡️",
    layout="centered"
)

# Conexion con Gemini
@st.cache_resource
def obtener_cliente():
    api_key = st.secrets["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)

client = obtener_cliente()


def chequear_password(password):
    try:
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefijo, sufijo = sha1[:5], sha1[5:]

        respuesta = requests.get(
            f"https://api.pwnedpasswords.com/range/{prefijo}",
            timeout=10
        )
        respuesta.raise_for_status()

        veces_encontrada = 0
        for linea in respuesta.text.splitlines():
            hash_sufijo, cantidad = linea.split(':')
            if hash_sufijo == sufijo:
                veces_encontrada = int(cantidad)
                break

        return veces_encontrada
    except requests.exceptions.Timeout:
        st.error("⚠️ La API tardó demasiado en responder. Probá de nuevo.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ No se pudo conectar a internet.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error al consultar la API: {e}")
        return None


def generar_informe(veces_encontrada):
    prompt = f"""Sos un asistente de ciberseguridad que explica riesgos a personas sin conocimientos técnicos.

Te voy a pasar el resultado de una consulta a la API de Pwned Passwords:
- veces_encontrada: cantidad de veces que esta contraseña apareció en filtraciones conocidas.

Con ese dato, generá un informe breve en español con este formato:
1. Nivel de riesgo (Bajo / Medio / Alto / Crítico) según la cantidad de veces encontrada.
2. Una explicación de 2-3 líneas, en lenguaje simple, de qué significa ese número.
3. Una checklist de 3 a 5 acciones concretas y priorizadas.

No inventes información que no te di. No pidas la contraseña real. Sé claro y directo.

Datos:
veces_encontrada: {veces_encontrada}"""

    try:
        respuesta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return respuesta.text
    except Exception as e:
        return f"⚠️ No se pudo generar el informe con la IA. Error: {e}"


def enviar_informe_email(email, veces_encontrada, informe):
    """Envía el informe al email del usuario usando un webhook de Make."""
    webhook_url = st.secrets.get("MAKE_WEBHOOK_URL", "")
    if not webhook_url:
        return False, "⚠️ El envío por email no está configurado correctamente."

    payload = {
        "email": email,
        "veces_encontrada": veces_encontrada,
        "informe": informe
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        response.raise_for_status()
        return True, "📧 ¡Informe enviado a tu correo!"
    except requests.exceptions.Timeout:
        return False, "⚠️ El servidor de email tardó demasiado. Intentá de nuevo."
    except requests.exceptions.ConnectionError:
        return False, "⚠️ No se pudo conectar con el servidor de email."
    except Exception as e:
        return False, f"⚠️ Error al enviar el email: {e}"


# INTERFAZ VISUAL #

st.title("🛡️ CentinelaID")
st.write("Verificá si tu contraseña apareció en alguna filtración de datos conocida.")

password = st.text_input(
    "Ingresá una contraseña para chequear:",
    type="password"
)

# --- Opción de enviar por email ---
enviar_por_email = st.checkbox("📧 Prefiero recibir el informe por email (en vez de verlo acá)")
email = None
if enviar_por_email:
    email = st.text_input("Ingresá tu email:")

if st.button("Chequear contraseña"):
    # Validaciones
    if password == "":
        st.warning("⚠️ Por favor ingresá una contraseña.")
    elif enviar_por_email and (not email or "@" not in email or "." not in email):
        st.warning("⚠️ Por favor ingresá un email válido.")
    else:
        # Consultar API
        with st.spinner("Consultando bases de datos de filtraciones..."):
            veces = chequear_password(password)

        if veces is not None:
            st.divider()

            # Resultado visual
            if veces == 0:
                st.success("✅ Esta contraseña no apareció en filtraciones conocidas.")
            elif veces < 100:
                st.warning(f"⚠️ Esta contraseña apareció **{veces:,}** veces en filtraciones conocidas.")
            else:
                st.error(f"🚨 Esta contraseña apareció **{veces:,}** veces en filtraciones conocidas.")

            # Generar informe con IA (se genera siempre, pero se entrega por un solo canal)
            with st.spinner("Generando informe con IA..."):
                informe = generar_informe(veces)

            if enviar_por_email and email:
                # El usuario eligió recibirlo por email: no lo mostramos en pantalla
                with st.spinner("Enviando informe por email..."):
                    exito, mensaje = enviar_informe_email(email, veces, informe)
                    if exito:
                        st.success(mensaje)
                    else:
                        st.error(mensaje)
                        st.info("No pudimos enviarlo por email, así que te lo mostramos acá:")
                        st.markdown(informe)
            else:
                # El usuario quiere verlo directamente en la app
                st.markdown(informe)