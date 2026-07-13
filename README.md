# 🛡️ CentinelaID

Verificador de exposición de contraseñas en filtraciones de datos conocidas, con informe generado por IA.

## 📋 Descripción

CentinelaID permite chequear si una contraseña apareció en alguna filtración de datos pública, usando la API de **Pwned Passwords** (con el modelo de privacidad k-anonymity, por lo que la contraseña nunca se envía completa). Con ese resultado, un modelo de IA (Gemini) genera un informe en lenguaje simple con el nivel de riesgo y una checklist de acciones recomendadas.

La app tiene una interfaz web hecha con **Streamlit**, pensada para que cualquier persona pueda usarla desde un link, sin instalar nada ni tocar una terminal. Además, el usuario puede elegir cómo quiere recibir el informe: **en pantalla** o **por email** (usando una automatización armada en **Make**).

### 🌐 Demo en vivo
👉 [Probar CentinelaID](https://centinelaid-8dutjkgdqofatsuzt6rjgd.streamlit.app/)

## 🚀 Cómo ejecutarlo

### 1. Cloná el repositorio
```bash
git clone https://github.com/Braiann43/CentinelaID.git
cd CentinelaID
```

### 2. Creá un entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
```

### 3. Instalá las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurá tus credenciales
Streamlit usa un archivo `.streamlit/secrets.toml` (no un `.env`). Creá el archivo con:
```toml
GEMINI_API_KEY = "tu_api_key_de_gemini"
MAKE_WEBHOOK_URL = "https://hook.make.com/tu_webhook_id"
```
- La key de Gemini se consigue gratis en [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
- El webhook de Make se explica en la sección de abajo. Si todavía no lo configuraste, podés dejar `MAKE_WEBHOOK_URL` vacío: la app funciona igual, solo se deshabilita el envío por email.

Si lo subís a Streamlit Community Cloud, estas mismas variables se cargan en **Settings → Secrets** de la app, no hace falta el archivo local.

### 5. Ejecutá el programa
```bash
streamlit run app.py
```

## 📧 Envío del informe por email (Make)
El usuario puede tildar la opción "Prefiero recibir el informe por email" en vez de verlo en pantalla. Cuando lo hace, la app envía un POST a un **webhook de Make** con `email`, `veces_encontrada` e `informe`, y un escenario armado en Make se encarga de mandarlo por correo. Para configurarlo:

1. Crear una cuenta en [make.com](https://www.make.com) y un escenario nuevo.
2. Agregar el módulo **Webhooks → Custom webhook** como disparador y copiar la URL generada.
3. Hacer un chequeo de prueba desde la app (con el webhook ya pegado en `MAKE_WEBHOOK_URL`) para que Make detecte automáticamente la estructura del JSON (`email`, `veces_encontrada`, `informe`).
4. Agregar un módulo de **Email** (Gmail, Email genérico, etc.), usando `{{email}}` como destinatario y `{{informe}}` en el cuerpo del mensaje.
5. Activar el escenario.

## 🔧 Tecnologías usadas
- **Python** — lógica principal del programa
- **Streamlit** — interfaz web, sin necesidad de terminal
- **API de Pwned Passwords** — chequeo de filtraciones (gratuita, sin key)
- **API de Gemini (Google)** — generación del informe con IA
- **Make** — automatización del envío del informe por email
- **Prompt engineering** — diseño del prompt para informes claros y consistentes

## 🔒 Privacidad
La contraseña ingresada nunca se envía completa a ningún servidor. Se utiliza un hash SHA-1 y el modelo de k-anonymity: solo se comparten los primeros 5 caracteres del hash con la API externa.

## 🎓 Sobre este proyecto

Este proyecto fue desarrollado como Trabajo Práctico Final para el **Taller de Inteligencia Artificial**, de la **Universidad Nacional de Hurlingham (UNAHUR)**. 

La propuesta busca aplicar de forma práctica conceptos vistos durante la cursada — uso de APIs, prompt engineering e integración de modelos de lenguaje — para resolver un problema real y cotidiano: que cualquier persona, sin conocimientos técnicos, pueda saber si su contraseña está expuesta y entender qué hacer al respecto, sin depender de leer reportes técnicos difíciles de interpretar.

## 👥 Autores
- Braian Videla
- Enzo Rivadeneira