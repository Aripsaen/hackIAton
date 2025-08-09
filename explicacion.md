### Explicación del Código y Tecnologías (Versión 2)

Hola! Aquí tienes una explicación actualizada del proyecto, reflejando los últimos cambios.

--- 

### 1. ¿Qué Construimos? (El Panorama General)

El objetivo sigue siendo automatizar el análisis de documentos de licitaciones, pero el proceso ahora es más sofisticado y está pensado para ser el **backend de una aplicación web**.

El flujo ahora es un **proceso de dos pasos con IA**:

1.  **Subes los PDFs**: Un usuario sube uno o más PDFs para una licitación (`case_id`).
2.  **Paso 1: Extracción Rápida (Documento por Documento)**: Un "trabajador" en la nube usa un modelo de IA rápido y económico (**Gemini Flash**) para leer cada PDF y extraer la información clave en un formato estructurado (JSON). Esto se hace para cada documento individualmente.
3.  **Paso 2: Análisis Profundo (Caso Completo)**: Una vez que todos los documentos han sido procesados y comparados, se invoca a un segundo modelo de IA, más potente y con mayor capacidad de razonamiento (**Gemini Pro**). Este modelo recibe toda la información consolidada y genera un **análisis ejecutivo final** para todo el caso, incluyendo un resumen y una evaluación de riesgos.
4.  **Resultados para la Web y Dashboard**: 
    *   La API expone un endpoint (`/result/{case_id}`) que entrega **toda la información en un solo JSON**, listo para que una aplicación web (frontend) lo muestre en una página de resultados.
    *   Paralelamente, se sigue generando un reporte simple en PDF y actualizando un Google Sheet para el dashboard de Looker Studio.

--- 

### 2. Tecnologías Utilizadas (Las Piezas del Lego)

**a) FastAPI (Para la API)**

*   Su rol es el mismo, pero ahora el endpoint `GET /result/{case_id}` es más importante, ya que en lugar de devolver links de descarga, **devuelve el contenido JSON directamente**, lo cual es mucho más eficiente para un frontend.

**b) Google Cloud Run (Para ejecutar el código)**

*   Su función no cambia: el **Service** ejecuta la API y el **Job** ejecuta el worker.

**c) Vertex AI (Gemini) - El Cerebro de IA en Dos Pasos**

*   Ahora usamos dos modelos de forma estratégica:
    1.  **Gemini Flash (`VERTEX_MODEL_NAME`)**: Se usa en el paso `WF-02` para la extracción de datos. Es rápido y barato, ideal para procesar muchos documentos de forma paralela.
    2.  **Gemini Pro (`VERTEX_PRO_MODEL_NAME`)**: Se usa al final, en el paso `WF-05b`. Es el modelo "caro" y potente, que usamos solo una vez por caso para hacer el análisis inteligente y profundo.

**d) LangChain (El Orquestador de IA)**

*   **¿Qué es?**: Es una librería que ayuda a conectar y encadenar llamadas a modelos de IA de forma más sencilla.
*   **¿Cómo se usa?**: La hemos añadido para manejar la llamada final a Gemini Pro en el paso `WF-05b`. LangChain facilita la tarea de tomar múltiples fuentes de datos (el JSON de comparación y el texto de todos los documentos), formatearlos en un prompt complejo y enviárselo al modelo.

**e) GCS, Google Sheets, Looker Studio, Docker**

*   Sus roles en el proyecto no han cambiado.

--- 

### 3. Estructura del Código (El Mapa del Proyecto)

Los cambios más importantes están en el `worker`:

*   `worker/pipelines/`:
    *   `wf02_extract.py`: Sigue haciendo la extracción, pero ahora sabemos que usa el modelo "Flash".
    *   `wf05_analysis.py`: **(Nuevo)** Este es el nuevo paso en la tubería que contiene la lógica de LangChain para llamar a Gemini Pro y generar el análisis final.
    *   `run.py`: Ha sido actualizado para orquestar este nuevo paso al final del proceso.
*   `worker/prompts/`:
    *   `extraction_prompt.txt`: El prompt para la extracción de datos (usado por Gemini Flash).
    *   `analysis_prompt.txt`: **(Nuevo/Modificado)** El prompt para el análisis final del caso (usado por Gemini Pro). **Aquí es donde puedes cambiar cómo razona el analista de IA.**
*   `api/`:
    *   `schemas.py` y `gcs.py`: Han sido modificados para que el endpoint `/result/{case_id}` cargue el contenido de los JSON y los devuelva directamente en la respuesta de la API.
