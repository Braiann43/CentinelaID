import requests       # para hacer llamadas HTTP a APIs externas
import hashlib        # para generar el hash SHA-1 de la contraseña
import os             # para utilizar comandos del sistema (como "clear")
from dotenv import load_dotenv   # para cargar el archivo .env con la API key 
from google import genai         # cliente oficial de la API de Gemini

load_dotenv()  # busca el archivo .env en la carpeta y carga sus variables como variables de entorno.

# Se crea UNA sola vez el "cliente" que habla con Gemini, usando la key guardada en .env
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


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
            timeout=10  # si tarda más de 10 segundos, corta y lanza un error
        )
        respuesta.raise_for_status()  # si la API devuelve un error (ej: 500), lanza una excepción

        veces_encontrada = 0
        # Recorre cada línea de la respuesta
        for linea in respuesta.text.splitlines(): # Convierte cada linea de hash en una lista de python
            hash_sufijo, cantidad = linea.split(':')  # separa sufijo y cantidad (para saber cuantas lineas hay con ese hash)
            if hash_sufijo == sufijo:      # compara el sufijo de la API con el sufijo de nuestra contraseña
                veces_encontrada = int(cantidad) # Guarda cuantas veces apareció la contraseña en filtraciones.
                break   # si lo encontró, corta el bucle (no hace falta seguir buscando)

        return veces_encontrada

    # Estos "except" se encargan de los errores específicos para que el programa no se rompa de golpe y arroje un mensaje
    except requests.exceptions.Timeout:
        print("⚠️  La API de Pwned Passwords tardó demasiado en responder. Probá de nuevo.")
        return None
    except requests.exceptions.ConnectionError:
        print("⚠️  No se pudo conectar a internet. Revisá tu conexión.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Ocurrió un error al consultar la API: {e}")
        return None


def generar_informe(veces_encontrada):
    prompt = f"""Sos un asistente de ciberseguridad que explica riesgos a personas sin conocimientos técnicos.

Te voy a pasar el resultado de una consulta a la API de Pwned Passwords:
- veces_encontrada: cantidad de veces que esta contraseña apareció en filtraciones conocidas.

Con ese dato, generá un informe breve en español con este formato:
1. Nivel de riesgo (Bajo / Poco bajo / Medio / Alto / Crítico) según la cantidad de veces encontrada.
2. Una explicación de 2-3 líneas, en lenguaje simple, de qué significa ese número (sin generar pánico innecesario).
3. Una checklist de 3 a 5 acciones concretas y priorizadas que la persona debería tomar.

No inventes información que no te di. No pidas la contraseña real. Sé claro y directo.

Datos:
veces_encontrada: {veces_encontrada}"""   # aca se inserta el número real calculado antes en la funcion de chequear_password().

    try:
        # Envía el prompt a Gemini y espera la respuesta
        respuesta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return respuesta.text   # extrae el texto de la respuesta
    except Exception as e:
        # Si falla la llamada a la IA (ej: sin cuota, sin internet), no rompe el programa, lo que hace es guardar en error en la variable e y devolver un mensaje sobre el error.
        return f"⚠️  No se pudo generar el informe con la IA. Error: {e}"


def mostrar_bienvenida():
    os.system('clear')   # limpia la terminal antes de mostrar el mensaje (en Windows sería 'cls')
    print("=" * 55)   # imprime una línea de 55 signos "=" (separador visual)
    print("   🛡️   CentinelaID — Verificador de contraseñas")
    print("=" * 55)
    print("Este programa chequea si tu contraseña apareció en")
    print("filtraciones de datos conocidas, usando la API de")
    print("Pwned Passwords (de forma segura, sin enviar tu")
    print("contraseña completa) y genera un informe con IA.")
    print("-" * 55)
    print("Escribí 'salir' en cualquier momento para terminar.")
    print("=" * 55)
    print()


def main():
    mostrar_bienvenida()

    while True:
        password = input("Ingresá una contraseña para chequear: ").strip()
        # .strip() saca espacios en blanco de sobra al principio/final

        if password.lower() == "salir":
            print("\n¡Gracias por usar CentinelaID! Cuidate en internet. 🔒")
            break   # corta el while y termina el programa

        if password == "":
            print("⚠️  No ingresaste nada. Probá de nuevo.\n")
            continue   # salta el resto del código y vuelve a preguntar

        veces = chequear_password(password)

        if veces is None:
            print("No se pudo completar el chequeo. Intentá de nuevo.\n")
            continue  # si hubo error en el chequeo, no sigue de largo y vuelve a preguntar

        print("\nGenerando informe...\n")
        informe = generar_informe(veces)
        print(informe)
        print("\n" + "-" * 55 + "\n")   # separador visual entre chequeos


if __name__ == "__main__":
    # Esto asegura que main() se ejecute solo si corrés este archivo directamente
    # (no si alguien lo importa como módulo desde otro script)
    main()