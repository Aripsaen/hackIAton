### Explicación del Código y Tecnologías (Versión 4 - Arquitectura Refactorizada)

Hola! El proyecto ha tenido una refactorización importante para reflejar un flujo de datos más lógico y potente. Aquí está la explicación final.

--- 

### 1. ¿Qué Construimos? (El Panorama General)

La aplicación web ahora funciona con una lógica de análisis más robusta:

1.  **Carga de Documentos**: El usuario sube los PDFs a través de la interfaz web.
2.  **Backend - Proceso por Documento**:
    *   **Paso 1: Extracción (LLM 1 - Gemini Flash)**: Se extrae un JSON muy detallado y anidado de cada PDF.
    *   **Paso 2: Análisis (LLM 2 - Gemini Pro)**: Inmediatamente después, cada JSON extraído se envía al modelo más potente, que lo evalúa contra una **rúbrica detallada**, generando una calificación completa (puntuaciones, comentarios, etc.) para **cada documento**.
3.  **Backend - Proceso de Consolidación**:
    *   **Paso 3: Comparación**: Una vez que todos los documentos tienen su extracción y su análisis-rúbrica, un nuevo proceso de comparación agrega los datos clave (como el monto de la oferta y la puntuación total de la rúbrica) para calcular los KPIs finales.
    *   **Paso 4: Reportes**: Se generan los reportes finales (PDF, Google Sheets).
4.  **Visualización en el Frontend**:
    *   La API ahora devuelve un único objeto (`comparison.json`) que contiene la lista de licitadores, sus KPIs finales, y anidado dentro de cada uno, su análisis de rúbrica completo.
    *   El **Dashboard** ahora es una vista detallada que muestra la **evaluación completa de la rúbrica** para cada documento.
    *   La vista de **Comparación** ahora es una tabla más simple y de alto nivel, que muestra solo los KPIs finales (monto, riesgo y cumplimiento calculados) para poder comparar las ofertas de un vistazo.

--- 

### 2. Estructura del Código y Flujo de Datos (El Cambio Clave)

El cambio más importante es el **orden del pipeline** en el `worker` y cómo fluyen los datos.

*   **Nuevo Pipeline en `worker/run.py`**:
    1.  `wf01_ingest`: Sin cambios.
    2.  `wf02_extract`: Usa el LLM 1 para obtener el JSON detallado.
    3.  `wf03_analysis`: **(Nuevo Orden)** Usa el LLM 2 para calificar el JSON del paso 2 con la rúbrica.
    4.  `wf04_compare`: **(Lógica Modificada)** Ahora recibe la información de los dos pasos anteriores para calcular los KPIs finales.
    5.  `wf05_reports`: Usa los datos del paso 4.

*   **Frontend (`frontend/components/`)**:
    *   `RubricAnalysis.jsx`: **(Nuevo)** Un componente dedicado a mostrar la compleja y detallada calificación de la rúbrica.
    *   `Dashboard.jsx`: Su rol principal ahora es mostrar el `RubricAnalysis` para cada oferta, dándole al usuario la visión más detallada.
    *   `Comparison.jsx`: Se ha simplificado para mostrar una tabla de resumen con los KPIs finales, permitiendo una comparación rápida.

*   **API (`api/`)**:
    *   `gcs.py` y `schemas.py`: Refactorizados para que la API sirva el archivo `comparison.json` como la fuente de verdad principal, ya que este ahora contiene toda la información necesaria para el frontend de forma anidada y estructurada.

Este nuevo diseño es más robusto porque el análisis de riesgo y cumplimiento se realiza a nivel de documento antes de la comparación, lo que permite que los KPIs de comparación sean mucho más ricos e informados.
