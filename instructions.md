### Guía Completa de Instalación y Ejecución (Desde Cero)

Esta guía te llevará paso a paso para configurar tu entorno en la nube y localmente, y para ejecutar la aplicación.

--- 
### Fase 1: Configuración Inicial de Google Cloud Platform (GCP)

**Objetivo:** Preparar tu cuenta de Google Cloud con todo lo necesario para que el proyecto funcione.

**Paso 1: Crear una Cuenta y un Proyecto en GCP**
1.  Ve a [https://cloud.google.com/](https://cloud.google.com/) y crea una cuenta. Suelen ofrecer un crédito gratuito generoso para nuevos usuarios.
2.  Una vez dentro, se te pedirá que crees un nuevo **Proyecto**. Dale un nombre (ej. `analisis-licitaciones`).
3.  Anote su **ID del Proyecto** (Project ID). Lo necesitarás para casi todo. No es el nombre, es un identificador único (ej. `analisis-licitaciones-123456`).
4.  Asegúrate de que la **Facturación (Billing)** esté activada para tu proyecto.

**Paso 2: Instalar la Herramienta de Línea de Comandos (gcloud)**
1.  Sigue las instrucciones en [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install) para instalar la `gcloud` CLI en tu sistema operativo.
2.  Abre tu terminal y ejecuta `gcloud init` para iniciar sesión con tu cuenta y seleccionar el proyecto que acabas de crear.

**Paso 3: Activar las APIs Necesarias**
1.  Los servicios de GCP que usaremos necesitan ser activados. Copia y pega este comando en tu terminal para activarlos todos de una vez:
    ```bash
    gcloud services enable cloudbuild.googleapis.com run.googleapis.com aiplatform.googleapis.com sheets.googleapis.com iam.googleapis.com storage-component.googleapis.com
    ```

**Paso 4: Crear un Bucket de Cloud Storage**
1.  Necesitamos un lugar para guardar los archivos. Ejecuta este comando, reemplazando `<tu-project-id>` con tu ID de proyecto real. El nombre del bucket debe ser único globalmente.
    ```bash
    gsutil mb gs://<tu-project-id>-procurement-bucket
    ```
2.  Anote el nombre de su bucket (ej. `gs://analisis-licitaciones-123456-procurement-bucket`).

**Paso 5: Crear una Hoja de Cálculo de Google (Google Sheet)**
1.  Ve a [https://sheets.new](https://sheets.new).
2.  Dale un nombre a la hoja, por ejemplo "Dashboard Licitaciones".
3.  En la URL de tu navegador, copia el ID de la hoja. Es la cadena larga de caracteres entre `/d/` y `/edit`. (ej. `.../d/1aBcDeFgHiJkLmNoPqRsT.../edit`)
4.  Anote este **ID de la Hoja**.

**Paso 6: Crear una Cuenta de Servicio (Service Account)**
1.  Esta es la "identidad" que usará tu aplicación para interactuar con GCP. Ve a la consola de GCP -> `IAM & Admin` -> `Service Accounts`.
2.  Haz clic en `+ CREATE SERVICE ACCOUNT`.
3.  Dale un nombre (ej. `procurement-app-runner`) y una descripción.
4.  **Conceder Permisos:** En el paso "Grant this service account access to project", añade los siguientes roles:
    *   `Cloud Run Admin`
    *   `Storage Admin`
    *   `Vertex AI User`
    *   `Service Account User`
5.  Haz clic en `Done`.
6.  **Generar una Clave:** Busca la cuenta que acabas de crear en la lista, haz clic en los tres puntos bajo "Actions" y selecciona `Manage keys`. Haz clic en `ADD KEY` -> `Create new key`. Elige **JSON** y haz clic en `CREATE`. Un archivo JSON se descargará. **Guárdalo en un lugar seguro y no lo compartas.**
7.  **Compartir la Hoja de Cálculo:** Abre el archivo JSON, copia el valor del campo `client_email`. Ve a tu Google Sheet, haz clic en `Share` y pega el email, dándole permisos de **Editor**.

--- 
### Fase 2: Configuración de tu Máquina Local

**Paso 7: Instalar Software Requerido**
1.  **Node.js y npm:** [https://nodejs.org/](https://nodejs.org/)
2.  **Python 3.11+:** [https://www.python.org/](https://www.python.org/)
3.  **Docker Desktop:** [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

**Paso 8: Autenticar para Desarrollo Local**
1.  Abre tu terminal y ejecuta este comando. Esto permite que tus scripts de Python locales usen tus credenciales de GCP para acceder a los servicios en la nube.
    ```bash
    gcloud auth application-default login
    ```

--- 
### Fase 3: Ejecutar el Proyecto Localmente

**Paso 9: Configurar el Archivo de Entorno (`.env`)**
1.  En la raíz del proyecto, copia el archivo `.env.example` y renómbralo a `.env`.
2.  Abre el archivo `.env` y rellénalo con los valores que anotaste:
    *   `PROJECT_ID`: Tu ID de proyecto de GCP.
    *   `BUCKET_NAME`: El nombre de tu bucket de GCS (sin `gs://`).
    *   `GOOGLE_SHEET_ID`: El ID de tu Google Sheet.
    *   `SERVICE_ACCOUNT_FILE`: La ruta **absoluta** en tu disco duro al archivo JSON que descargaste en el Paso 6.

**Paso 10: Ejecutar el Backend y el Frontend**
1.  **Terminal 1 (Raíz del proyecto):** Ejecuta el backend.
    
    inicia el ambiente virtual .venv
    ```bash
    source .venv/bin/activate
    ```
    ```bash
    make install
    make run-api
    ```
    Tu API ahora está corriendo en `http://localhost:8000`.

2.  **Terminal 2 (Raíz del proyecto):** Ejecuta el frontend.
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    Tu interfaz web ahora está corriendo en una dirección local (usualmente `http://localhost:5173`).

**Paso 11: Usar la Aplicación**
1.  Abre tu navegador y ve a la dirección del frontend (`http://localhost:5173`).
2.  Crea un caso, sube algunos PDFs y observa cómo se procesan.

--- 
### Fase 4: Despliegue en la Nube (Deployment)

Cuando estés listo para que el mundo vea tu aplicación:

**Paso 12: Desplegar el Backend**
1.  Asegúrate de que tu `gcloud` CLI esté apuntando al proyecto correcto (`gcloud config set project <tu-project-id>`).
2.  Ejecuta estos comandos desde la raíz del proyecto, reemplazando `<tu-sa-email>` con el email de la cuenta de servicio que creaste en el Paso 6.
    ```bash
    # Desplegar la API
    gcloud run deploy api-procurement --source . --platform managed --region us-central1 --allow-unauthenticated --service-account <tu-sa-email>

    # Desplegar el Worker
    gcloud run jobs deploy worker-procurement --source . --platform managed --region us-central1 --service-account <tu-sa-email>
    ```

**Paso 13: Desplegar el Frontend**
1.  En la carpeta `frontend/`, ejecuta `npm run build`. Esto crea una carpeta `dist/` con los archivos estáticos de tu web.
2.  Sube el contenido de la carpeta `dist/` a un servicio de hosting como **Firebase Hosting** o un **GCS Bucket configurado como sitio web**. Este es un tema avanzado, pero el primer paso es siempre construir los archivos estáticos.