import requests # para hacer llamadas HTTP a APIs externas
import hashlib # para generar el hash SHA-1 de la contraseña
import os # para utilizar comandos del sistema (como "clear")
import streamlit as st
from google import genai # cliente oficial de la API de Gemini

# Configuración de la pagina (tiene que ir primero, antes de cualquier otro st.algo) ---
st.set_page_config(
    page_title="CentinelaID", # titulo de la pagina
    page_icon="🛡️",           # icono de la pagina
    layout="centered"         # centrado de la pagina (en vez de ocupar todo el ancho)
)

# Conexion con Gemini
# st.cache_resource hace que el cliente se cree UNA sola vez y se reutilice,
# en vez de recrearse cada vez que Streamlit vuelve a correr el script.
@st.cache_resource
def obtener_cliente():                     # Osea lo que hacemos con este decorador es que la funcion 
    api_key = st.secrets["GEMINI_API_KEY"] # corra una vez y las proximas veces deuelve el resultado guardado 
    return genai.Client(api_key=api_key)  # Usamos st.secrets en vez de os.environ para que la API key quede guardada en el archivo .streamlit/secrets.toml.

client = obtener_cliente()


def chequear_password(password):
    try:
        # Convierte la contraseña en un hash SHA-1 (una huella digital irreversible)
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        # Aca la cotraseña ya esta convertida en caracteres hexadecimales, por ej: ("5BAA6...") osea no se guarda ni se envía la contraseña real.

        # Divide el hash en dos partes: los primeros 5 caracteres (prefijo)
        # y el resto (sufijo). Esto es la técnica de "k-anonymity":
        # solo se manda el prefijo a la API, nunca el hash completo ni la contraseña real.
        prefijo, sufijo = sha1[:5], sha1[5:]

        # Le pide a la API TODOS los hashes que empiezan con ese prefijo
        # (te devuelve una lista larga, no un solo resultado)
        respuesta = requests.get(
            f"https://api.pwnedpasswords.com/range/{prefijo}",
            timeout=10
        )
        respuesta.raise_for_status()  # si la API devuelve un error (ej: 500), lanza una excepción

        veces_encontrada = 0
        # Recorre cada línea de la respuesta
        for linea in respuesta.text.splitlines():  # Convierte cada linea de hash en una lista de python
            hash_sufijo, cantidad = linea.split(':')  # separa sufijo y cantidad (para saber cuantas lineas hay con ese hash)
            if hash_sufijo == sufijo:  # compara el sufijo de la API con el sufijo de nuestra contraseña
                veces_encontrada = int(cantidad)  # Guarda cuantas veces apareció la contraseña en filtraciones.
                break  # si lo encontró, corta el bucle (no hace falta seguir buscando)

        return veces_encontrada
    # Estos "except" se encargan de los errores específicos para que el programa no se rompa de golpe y arroje un mensaje
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
        # Envía el prompt a Gemini y espera la respuesta
        respuesta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return respuesta.text  # extrae el texto de la respuesta
    except Exception as e:
        # Si falla la llamada a la IA (ej: sin cuota, sin internet), no rompe el programa, lo que hace es guardar en error en la variable e y devolver un mensaje sobre el error.
        return f"⚠️ No se pudo generar el informe con la IA. Error: {e}"



# INTERFAZ VISUAL (lo que ve el usuario)

st.title("🛡️ CentinelaID")
st.write("Verificá si tu contraseña apareció en alguna filtración de datos conocida.")

password = st.text_input( # crea la caja de texto 
    "Ingresá una contraseña para chequear:",
    type="password"  # esto hace que se vea con puntitos, como un campo de login real
)

if st.button("Chequear contraseña"): # dibuja un boton con el texto de "Chequear contraseña"
    if password == "":
        st.warning("⚠️ Por favor ingresá una contraseña.") # st.warning muestra un cartel de advertencia amarillo
    else:
        with st.spinner("Consultando bases de datos de filtraciones..."): #st.spinner crea un icono girando 
            veces = chequear_password(password)

        if veces is not None: # si la variable veces no es None (osea que no hubo error en la consulta a la API)
            st.divider() # dibuja una línea horizontal separadora
            
            if veces == 0:
                st.success(f"✅ Esta contraseña no apareció en filtraciones conocidas.") # Mostramos el número de forma visual, separado del texto de la IA
            elif veces < 100:
                st.warning(f"⚠️ Esta contraseña apareció **{veces:,}** veces en filtraciones conocidas.")
            else:
                st.error(f"🚨 Esta contraseña apareció **{veces:,}** veces en filtraciones conocidas.")

            with st.spinner("Generando informe con IA..."):
                informe = generar_informe(veces)

            st.markdown(informe)
            st.markdown(informe) # Esto lo que hace es renderizar el formato markdown, ya que esta pensado para la web, y se va a ver mucho mas lindo, no se van a ver los puntitos del informe.