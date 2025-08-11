from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from app.core.config import settings
import json

# Initialize LLM based on configuration
# Initialize Extraction LLM based on configuration
if settings.EXTRACTION_LLM_PROVIDER == "gemini":
    from langchain_google_genai import ChatGoogleGenerativeAI
    extraction_llm = ChatGoogleGenerativeAI(
        model=settings.EXTRACTION_MODEL_NAME,
        temperature=settings.EXTRACTION_TEMPERATURE,
        google_api_key=settings.EXTRACTION_API_KEY
    )
elif settings.EXTRACTION_LLM_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    openai_extraction_model = os.getenv("EXTRACTION_MODEL_NAME_OPENAI", "gpt-3.5-turbo")
    extraction_llm = ChatOpenAI(
        model=openai_extraction_model,
        temperature=settings.EXTRACTION_TEMPERATURE,
        openai_api_key=settings.EXTRACTION_API_KEY
    )
else:
    raise ValueError("Unsupported EXTRACTION_LLM_PROVIDER. Please set EXTRACTION_LLM_PROVIDER to 'gemini' or 'openai' in your .env file.")

# Initialize Analysis LLM based on configuration
if settings.ANALYSIS_LLM_PROVIDER == "gemini":
    from langchain_google_genai import ChatGoogleGenerativeAI
    analysis_llm = ChatGoogleGenerativeAI(
        model=settings.ANALYSIS_MODEL_NAME,
        temperature=settings.ANALYSIS_TEMPERATURE,
        google_api_key=settings.ANALYSIS_API_KEY
    )
elif settings.ANALYSIS_LLM_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    openai_analysis_model = os.getenv("ANALYSIS_MODEL_NAME_OPENAI", "gpt-4o")
    analysis_llm = ChatOpenAI(
        model=openai_analysis_model,
        temperature=settings.ANALYSIS_TEMPERATURE,
        openai_api_key=settings.ANALYSIS_API_KEY
    )
else:
    raise ValueError("Unsupported ANALYSIS_LLM_PROVIDER. Please set ANALYSIS_LLM_PROVIDER to 'gemini' or 'openai' in your .env file.")

# --- WF-02: Extraction Prompt and Schema ---

extraction_json_schema = {
  "meta": {
    "docType": "",
    "titulo": "",
    "fechaDoc": "",
    "anexos": []
  },
  "partes": {
    "EntidadContratante": "",
    "Contratista": "",
    "RUC": ""
  },
  "contrato": {
    "ObjetoContrato": "",
    "MontoTotal": {"valor": 0, "moneda": "USD"},
    "Plazo": {"valor": 0, "unidad": "meses"},
    "FormaPago": "",
    "Recepcion": {"provisional": "", "definitiva": ""},
    "Controversias": {"mecanismos": "", "jurisdiccion": ""},
    "LegislacionAplicable": ""
  },
  "garantias": [
    {"tipo":"", "monto":{"valor":0,"moneda":"USD"}, "vigencia":"", "emisor":""}
  ],
  "penalizaciones": {
    "multasRetraso": "",
    "penalizacionTecnica": "",
    "causalesTerminacion": ""
  },
  "tecnico": {
    "Especificaciones": [],
    "PersonalTecnicoMinimo": [],
    "MaquinariaRequerida": []
  },
  "cronograma": [
    {"mes":"", "fase":"", "actividad":"", "monto":{"valor":0,"moneda":"USD"}}
  ],
  "presupuestoPartidas": [
    {"partida":"", "monto":{"valor":0,"moneda":"USD"}}
  ],
  "presupuestoMensual": [
    {"mes":"", "fase":"", "monto":{"valor":0,"moneda":"USD"}}
  ],
  "flujoCaja": [
    {"mes":"", "avanceUSD":0, "amortizacionUSD":0, "pagoNetoUSD":0, "costoUSD":0, "saldoMensualUSD":0, "saldoAcumuladoUSD":0}
  ],
  "oferta": {
    "montoOfertado": {"valor":0, "moneda":"USD"},
    "anticipo": {"porcentaje":0, "monto":{"valor":0,"moneda":"USD"}},
    "validezDias": 0,
    "garantiaMantenimiento": 0
  },
  "provenance": [],
  "diagnostics": {
    "missing": [],
    "notes": []
  }
}

extraction_prompt_template = ChatPromptTemplate.from_template(
    """Actúa como un extractor de datos de documentos estructurados (contratos, licitaciones, propuestas). Tu objetivo es analizar un texto y devolver un JSON con la información extraída, respetando estrictamente la estructura y las reglas de extracción.

Entrada:
Recibirás un único string de texto. Los offsets (start_char y end_char) deben ser índices de carácter relativos a ese string.

Reglas de Extracción:
Números y Moneda: Devuelve los valores numéricos, no como strings. La moneda por defecto es “USD” si no se especifica otra.
Porcentajes: Convierte porcentajes a números (ej. "5%" debe ser 5).
Trazabilidad (provenance):
Para cada campo no vacío en el JSON, debes incluir una entrada en el array provenance.
La entrada debe contener la ruta JSON del campo (campo), el texto exacto que coincide con la evidencia (evidencia), y los índices de inicio y fin del carácter en el texto original (start_char, end_char).
No incluyas entradas duplicadas en provenance.
Campos Faltantes (diagnostics.missing):
Si un campo del JSON no tiene una evidencia literal en el texto, deja su valor por defecto ("", [], 0).
Agrega la ruta JSON de este campo en el array diagnostics.missing para indicar que no se encontró información.
Tablas y Mapeos Específicos:
cronograma: Mapea los montos de la tabla presupuestoMensual a la tabla cronograma.
Usa el mes como clave de mapeo (ej. "2 - 3" coincide con "2 - 3"). Normaliza los guiones y espacios para la comparación.
Si el mes no coincide, intenta mapear por la fase (insensible a mayúsculas/minúsculas).
Si no se puede mapear, el monto debe ser 0 y el campo cronograma.[índice].monto debe reportarse como faltante en diagnostics.missing.
flujoCaja: Extrae todas las filas de la tabla si existe.
contrato.FormaPago: Busca frases como "Forma de pago", "avances mensuales", "pagos por hitos", etc. Si no se encuentra, deja "" y añádelo a diagnostics.missing.
meta.fechaDoc: Busca fechas en encabezados o actas (ACTA N.º... Fecha:). Si no hay, deja "" y añádelo a diagnostics.missing.

Estructura de la Salida:
Tu respuesta debe ser un único JSON con la estructura definida a continuación. No agregues texto adicional ni explicaciones.

JSON_SCHEMA:
{json_schema}

TEXTO_A_ANALIZAR:
{text}
"""
)

extraction_chain = extraction_prompt_template | extraction_llm

# --- WF-03: Analysis Prompt and Schema ---

analysis_json_schema = {
  "evaluacionRiesgos": {
    "estadoRuc": {
      "puntuacion": 100,
      "comentario": "El estado del RUC del contratista es 'ACTIVO', lo cual es un requisito fundamental."
    },
    "requisitosLegales": {
      "puntuacion": 50,
      "comentario": "El contrato identifica claramente a las partes, el RUC, la legislación aplicable y los mecanismos de resolución de conflictos."
    },
    "viabilidadTecnica": {
      "puntuacion": 50,
      "comentario": "Las especificaciones técnicas, personal y maquinaria requerida están bien detalladas, lo que minimiza el riesgo técnico."
    },
    "viabilidadCronograma": {
      "puntuacion": 50,
      "comentario": "El cronograma de 12 meses parece razonable para la magnitud del proyecto."
    },
    "garantiasPenalizaciones": {
      "puntuacion": 0,
      "comentario": "Aunque se definen garantías, no se especifica si cubren todos los riesgos potenciales del contrato. Las penalizaciones por retraso (0.1% diario) son estándar, pero la 'penalización técnica' es vaga y requiere mayor definición."
    }
  },
  "kpis": {
    "puntuacionTotal": 250,
    "ratioPuntuacionMonto": 12.5,
    "alineacionContratista": 0
  },
  "resumenRiesgos": {
    "puntosCriticos": [
      "La actividad económica del RUC no coincide con el objeto del contrato."
    ],
    "puntosDeMejora": [
      "Se requiere más detalle en las garantías y penalizaciones para cubrir todos los escenarios de riesgo."
    ],
    "conclusion": "La oferta presenta un riesgo crítico debido a la inconsistencia entre la actividad económica del contratista y el objeto del contrato. Esto es un factor de descalificación inmediato. Se recomienda rechazar la oferta a menos que el contratista pueda demostrar una experiencia sustancial y relevante en proyectos similares."
  }
}

analysis_prompt_template = ChatPromptTemplate.from_template(
    """Actúa como un analista experto en contratos. Tu tarea es evaluar una oferta de obra pública basándote en un JSON de datos extraídos y en la información del RUC del contratista. No solo identifiques los riesgos, sino que también calcules KPIs específicos para cuantificar el valor de la oferta.

Entrada:
Recibirás un único JSON que contiene:
1. La información extraída del contrato.
2. Un objeto anidado `ruc_info` con los datos del RUC del contratista.

Rúbrica de Evaluación y Cálculo de KPIs:
1.  **Estado y Actividad del RUC:**
    * **Puntuación:** Otorga 0 puntos si el `estadoContribuyenteRuc` no es "ACTIVO" o si la `actividadEconomicaPrincipal` no es coherente con el `ObjetoContrato`. Otorga 100 puntos si ambos son correctos.
    * **Comentario:** Explica la razón de la puntuación (si es 0, especifica si es por el estado o la actividad).
2.  **Cumplimiento de Requisitos Legales:**
    * **Puntuación:** Otorga 50 puntos si el contrato cumple con la identificación de partes, RUC, legislación y mecanismos de controversias. Otorga 0 si falta alguno.
    * **Comentario:** Detalla cualquier requisito legal faltante.
3.  **Viabilidad Técnica:**
    * **Puntuación:** Otorga 50 puntos si las especificaciones, personal y maquinaria son detalladas y adecuadas. Otorga 0 si son vagas.
    * **Comentario:** Describe la claridad de la información técnica.
4.  **Viabilidad del Cronograma:**
    * **Puntuación:** Otorga 50 puntos si el cronograma es realista. Otorga 0 si es demasiado ambicioso o desestructurado.
    * **Comentario:** Evalúa la coherencia del cronograma.
5.  **Garantías y Penalizaciones:**
    * **Puntuación:** Otorga 50 puntos si las cláusulas son claras y proporcionales. Otorga 0 si son débiles o vagas.
    * **Comentario:** Menciona si las cláusulas cubren todos los riesgos potenciales.

**Cálculo de KPIs:**
Una vez obtenidas las puntuaciones, calcula los siguientes KPIs:

1.  **Puntuación Total:** Suma las puntuaciones de todos los criterios (RUC + Requisitos Legales + Viabilidad Técnica + Viabilidad del Cronograma + Garantías). La puntuación máxima es 300.
2.  **Ratio de Puntuación vs. Monto Ofertado:**
    * **Fórmula:** `(Puntuación Total / Monto Total Ofertado) * 1,000,000`
    * **Objetivo:** Este KPI normaliza el valor de la oferta, permitiendo comparar ofertas de distintos montos. Un valor más alto indica una mejor oferta por cada millón de USD.
3.  **Alineación del Contratista:**
    * **Fórmula:** `0` si la actividad del RUC no coincide con el contrato; `1` si sí coincide.
    * **Objetivo:** Este es un indicador binario de riesgo crítico.

**Estructura de la Salida:**
Tu respuesta debe ser un único JSON con la siguiente estructura. No agregues texto adicional ni explicaciones fuera del JSON.

JSON_SCHEMA:
{json_schema}

JSON_DATA_TO_ANALYZE:
{json_data}
"""
)

analysis_chain = analysis_prompt_template | analysis_llm
