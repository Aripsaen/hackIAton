# Licitando: Plataforma Automatizada de Análisis de Licitadores

Este proyecto es una aplicación web full-stack diseñada para automatizar el análisis y la comparación de documentos de licitadores para un hackathon.

## Características

- **Ingesta y Análisis Automatizado de PDF**: Carga sin problemas múltiples documentos PDF de licitadores a través de una interfaz web, con extracción automatizada del contenido de texto sin procesar.
- **Extracción de Datos Impulsada por LLM**: Utiliza un LLM rápido (por ejemplo, Gemini Flash) para extraer datos JSON detallados y estructurados de cada documento basándose en un esquema predefinido.
- **Análisis LLM Basado en Rúbricas**: Emplea un LLM más capaz (por ejemplo, Gemini Pro) a través de LangChain para evaluar los datos extraídos contra una rúbrica de puntuación, generando puntuaciones y retroalimentación cualitativa por documento.
- **Comparación Integral de Licitadores**: Agrega y compara datos de todos los licitadores analizados para un caso dado, calculando indicadores clave de rendimiento (KPIs) y generando una comparación única y completa.
- **Generación Automatizada de Informes**: Produce un informe PDF legible por humanos que resume todos los licitadores, sus puntuaciones y KPIs.
- **Opciones Flexibles de Almacenamiento**: Admite tanto un simulacro local basado en archivos para desarrollo como Google Cloud Storage (GCS) para entornos de producción.
- **Despliegue Contenerizado**: Empaquetado con Docker para un despliegue fácil, consistente y portátil.

## Pila Tecnológica

- **Backend**: Python 3.11, FastAPI
- **Frontend**: HTML, CSS, JavaScript (sin frameworks)
- **Orquestación de LLM**: LangChain
- **Modelos LLM**: Configurables (Google Gemini Pro/Flash, modelos OpenAI GPT compatibles a través de LangChain)
- **Análisis de PDF**: `pdfplumber`
- **Generación de Informes**: `reportlab`
- **Despliegue**: Docker

## Estructura del Proyecto

```
/
|-- app/
|   |-- __init__.py
|   |-- main.py             # Definición de la aplicación FastAPI y endpoints
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py         # Carga de configuración desde .env
|   |   |-- llm.py            # Integración de LangChain y Gemini
|   |   |-- storage.py        # Cliente GCS (real y simulado)
|   |-- services/
|   |   |-- __init__.py
|   |   |-- workflow.py       # Toda la lógica del flujo de trabajo (ingesta, extracción, análisis, etc.)
|   |-- models/
|   |   |-- __init__.py
|   |   |-- schemas.py        # Modelos Pydantic para estructuras de datos
|-- static/
|   |-- index.html          # Página principal del frontend
|   |-- style.css
|   |-- script.js
|-- .env.example            # Variables de entorno de ejemplo
|-- requirements.txt        # Dependencias de Python
|-- Dockerfile              # Definición del contenedor Docker
|-- README.md
```

## Configuración y Ejecución de la Aplicación

Esta sección proporciona instrucciones detalladas sobre cómo configurar y ejecutar la Plataforma Automatizada de Análisis de Licitadores. Puede elegir entre ejecutarla localmente para desarrollo o usar Docker para un entorno más consistente y desplegable.

### Prerrequisitos

Antes de comenzar, asegúrese de tener lo siguiente instalado en su sistema:

*   **Git**: Para clonar el repositorio.
    *   [Descargar Git](https://git-scm.com/downloads)
*   **Python 3.11+**: Para desarrollo local sin Docker.
    *   [Descargar Python](https://www.python.org/downloads/)
*   **pip**: El instalador de paquetes de Python (generalmente viene con Python).
*   **Docker Desktop**: Para construir y ejecutar la aplicación en un entorno contenerizado (recomendado tanto para desarrollo como para despliegue).
    *   [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   **Una clave API para su proveedor de LLM elegido**: Necesitará una clave API de Google (para modelos Gemini) o una clave API de OpenAI (para modelos GPT).
    *   **Clave API de Google**: [Obtener una clave API de Google](https://ai.google.dev/gemini-api/docs/get-started/python)
    *   **Clave API de OpenAI**: [Obtener una clave API de OpenAI](https://platform.openai.com/account/api-keys)

### Paso 1: Clonar el Repositorio

Abra su terminal o símbolo del sistema y ejecute el siguiente comando para clonar el proyecto en su máquina local:

```bash
git clone https://github.com/your-username/automated-bidder-analysis-platform.git
cd automated-bidder-analysis-platform
```

(Reemplace `https://github.com/your-username/automated-bidder-analysis-platform.git` con la URL real del repositorio si es diferente).

### Paso 2: Configurar Variables de Entorno

Esta aplicación utiliza variables de entorno para información sensible y configuración. Se proporciona un archivo de plantilla `.env.example`.

1.  **Copie el archivo `.env` de ejemplo:**

    ```bash
    cp .env.example .env
    ```

2.  **Edite el archivo `.env`:** Abra el archivo `.env` recién creado en un editor de texto. Debe completar los valores requeridos.

    ```env
    # Establezca en "production" para usar Google Cloud Storage, de lo contrario usa el almacenamiento simulado local.
    # Para desarrollo local, manténgalo como "development".
    ENV=development

    # Su ID de proyecto de Google Cloud (solo necesario si ENV es "production" y está usando GCS)
    # Si está ejecutando localmente con almacenamiento simulado, puede dejarlo como está.
    GCP_PROJECT_ID="su-id-de-proyecto-gcp"

    # El nombre del bucket de GCS a usar (solo necesario si ENV es "production" y está usando GCS)
    # Si está ejecutando localmente con almacenamiento simulado, puede dejarlo como está.
    GCS_BUCKET_NAME="su-nombre-de-bucket-gcs"

    # Configuración de LLM
    # Establezca el proveedor para el modelo de extracción: "gemini" u "openai"
    EXTRACTION_LLM_PROVIDER="gemini"

    # Establezca el proveedor para el modelo de análisis: "gemini" u "openai"
    ANALYSIS_LLM_PROVIDER="gemini"

    # Claves API para modelos/proveedores específicos
    # Si usa Gemini, establezca EXTRACTION_API_KEY y ANALYSIS_API_KEY con su clave API de Google.
    # Si usa OpenAI, establezca EXTRACTION_API_KEY y ANALYSIS_API_KEY con su clave API de OpenAI.
    EXTRACTION_API_KEY="su-clave-api-de-extraccion"
    ANALYSIS_API_KEY="su-clave-api-de-analisis"

    # Nombres de modelos. Estos se usarán según la configuración de LLM_PROVIDER.
    # Para Gemini:
    EXTRACTION_MODEL_NAME="gemini-1.5-flash"
    ANALYSIS_MODEL_NAME="gemini-1.5-pro"

    # Para OpenAI (descomente y configure si usa OpenAI):
    # EXTRACTION_MODEL_NAME_OPENAI="gpt-3.5-turbo"
    # ANALYSIS_MODEL_NAME_OPENAI="gpt-4o"

    # Configuración de temperatura para modelos (0.0 a 1.0)
    EXTRACTION_TEMPERATURE=0.1
    ANALYSIS_TEMPERATURE=0.2
    ```

    **Importante:**
    *   Para cada modelo (extracción y análisis), asegúrese de establecer su `_LLM_PROVIDER` (por ejemplo, `EXTRACTION_LLM_PROVIDER`) en `"gemini"` u `"openai"`.
    *   Proporcione la clave API correspondiente en `EXTRACTION_API_KEY` y `ANALYSIS_API_KEY`. Si usa Gemini, esta será su clave API de Google. Si usa OpenAI, esta será su clave API de OpenAI.
    *   Para desarrollo local, `ENV=development` es suficiente, y `GCP_PROJECT_ID` y `GCS_BUCKET_NAME` no son estrictamente necesarios ya que se utilizará el almacenamiento simulado.

### Opción A: Ejecutar Localmente (para Desarrollo)

Esta opción es adecuada para el desarrollo y las pruebas locales sin Docker. Necesitará tener Python y pip instalados.

1.  **Cree un Entorno Virtual de Python (Recomendado):**

    ```bash
    python3 -m venv venv
    ```

2.  **Active el Entorno Virtual:**

    *   **En macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **En Windows (Símbolo del sistema):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **En Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```

3.  **Instale las Dependencias de Python:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecute la Aplicación FastAPI:**

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *   La bandera `--reload` es útil para el desarrollo, ya que reinicia automáticamente el servidor cuando se detectan cambios en el código.

### Opción B: Ejecutar con Docker (Recomendado para Desarrollo y Despliegue)

Esta opción utiliza Docker para crear un entorno consistente, lo cual es ideal tanto para el desarrollo como para la preparación del despliegue.

1.  **Asegúrese de que Docker Desktop esté en ejecución:** Asegúrese de que la aplicación Docker esté abierta y en ejecución en su máquina.

2.  **Construya la Imagen de Docker:** Navegue hasta el directorio raíz del proyecto (donde se encuentra `Dockerfile`) en su terminal y ejecute:

    ```bash
    docker build -t bidder-analysis-app .
    ```
    Este comando construye una imagen de Docker llamada `bidder-analysis-app` basada en el `Dockerfile`.

3.  **Ejecute el Contenedor Docker:**

    *   **Para Desarrollo Local (con cambios de código en vivo):**

        ```bash
        docker run -p 8000:8000 -v "$(pwd)":/app --env-file .env bidder-analysis-app
        ```
        *   `-p 8000:8000`: Mapea el puerto 8000 de su máquina host al puerto 8000 dentro del contenedor.
        *   `-v "$(pwd)":/app`: **(Importante para Desarrollo)** Esto monta su directorio de proyecto local actual en el directorio `/app` dentro del contenedor. Cualquier cambio que realice en su código local se reflejará inmediatamente en el contenedor en ejecución sin necesidad de reconstruir la imagen.
        *   `--env-file .env`: Pasa las variables de entorno de su archivo `.env` al contenedor.

    *   **Para Despliegue (por ejemplo, a un servidor, sin cambios de código en vivo):**

        Para el despliegue, normalmente no necesitará el montaje de volumen, ya que el código ya se copia en la imagen durante el proceso de construcción. También podría establecer `ENV=production` en su archivo `.env` para habilitar Google Cloud Storage.

        ```bash
        docker run -p 8000:8000 --env-file .env bidder-analysis-app
        ```
        *   En un escenario de despliegue real, es probable que utilice una herramienta de orquestación más robusta (como Docker Compose, Kubernetes o un servicio específico de la nube) y gestione sus variables de entorno de forma más segura.

### Paso 3: Acceder a la Aplicación

Una vez que la aplicación esté en ejecución (ya sea localmente o a través de Docker), abra su navegador web y navegue a:

[http://localhost:8000](http://localhost:8000)

Ahora puede cargar sus archivos PDF de licitadores e iniciar el análisis.

### Limpieza (Opcional)

*   **Para detener el contenedor Docker:** Presione `Ctrl+C` en la terminal donde se está ejecutando el contenedor. Si se está ejecutando en modo separado, encuentre su ID (`docker ps`) y luego `docker stop <container_id>`.
*   **Para eliminar la imagen de Docker:** `docker rmi bidder-analysis-app`
*   **Para desactivar el entorno virtual (si se ejecuta localmente):** `deactivate`
*   **Para eliminar la carpeta del entorno virtual:** `rm -rf venv` (macOS/Linux) o `rmdir /s /q venv` (Windows)