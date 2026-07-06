# 🛡️ CentinelaID

Verificador de exposición de contraseñas en filtraciones de datos conocidas, con informe generado por IA.

## 📋 Descripción

CentinelaID permite chequear si una contraseña apareció en alguna filtración de datos pública, usando la API de **Pwned Passwords** (con el modelo de privacidad k-anonymity, por lo que la contraseña nunca se envía completa). Con ese resultado, un modelo de IA (Gemini) genera un informe en lenguaje simple con el nivel de riesgo y una checklist de acciones recomendadas.

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

### 4. Configurá tu API key
Copiá el archivo de ejemplo y completá con tu propia key:
```bash
cp .env.example .env
```
Editá `.env` y reemplazá `tu_api_key_aca` por tu key real de Gemini (se consigue gratis en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).

### 5. Ejecutá el programa
```bash
python centinela.py
```

## 🔧 Tecnologías usadas
- **Python** — lógica principal del programa
- **API de Pwned Passwords** — chequeo de filtraciones (gratuita, sin key)
- **API de Gemini (Google)** — generación del informe con IA
- **Prompt engineering** — diseño del prompt para informes claros y consistentes

## 🔒 Privacidad
La contraseña ingresada nunca se envía completa a ningún servidor. Se utiliza un hash SHA-1 y el modelo de k-anonymity: solo se comparten los primeros 5 caracteres del hash con la API externa.

## 🎓 Sobre este proyecto

Este proyecto fue desarrollado como Trabajo Práctico Final para el **Taller de Inteligencia Artificial**, de la **Universidad Nacional de Hurlingham (UNAHUR)**. 

La propuesta busca aplicar de forma práctica conceptos vistos durante la cursada — uso de APIs, prompt engineering e integración de modelos de lenguaje — para resolver un problema real y cotidiano: que cualquier persona, sin conocimientos técnicos, pueda saber si su contraseña está expuesta y entender qué hacer al respecto, sin depender de leer reportes técnicos difíciles de interpretar.

## 👥 Autores
- Braian Videla
- Enzo Rivadeneira