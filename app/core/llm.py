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
  "calificacion": {
    "cumplimientoRequisitosLegales": {
      "puntuacion": 5,
      "comentario": "El contrato cumple completamente con los requisitos legales establecidos."
    },
    "claridadYComplejidadTecnica": {
      "puntuacion": 4,
      "comentario": "Las condiciones técnicas son claras, pero algunas especificaciones adicionales podrían mejorar la claridad."
    },
    "viabilidadDelCronogramaDeEjecucion": {
      "puntuacion": 3,
      "comentario": "El cronograma es ambicioso y podría ser difícil de cumplir. Se recomienda una revisión."
    },
    "evaluacionDeRiesgosFinancierosYEconomicos": {
      "puntuacion": 5,
      "comentario": "El presupuesto está bien definido y el flujo de caja es realista."
    },
    "garantiasYPenalizaciones": {
      "puntuacion": 5,
      "comentario": "Las garantías y penalizaciones están bien estructuradas y cubren adecuadamente los riesgos."
    },
    "condicionesDePagoYAvances": {
      "puntuacion": 4,
      "comentario": "Las condiciones de pago son claras, pero los avances podrían ser más flexibles."
    },
    "capacidadesTecnicasDelContratista": {
      "puntuacion": 5,
      "comentario": "El contratista tiene la experiencia y el personal adecuado para el proyecto."
    },
    "mecanismosDeResolucionDeConflictos": {
      "puntuacion": 3,
      "comentario": "Los mecanismos de resolución de conflictos son básicos y podrían ser más detallados."
    },
    "cumplimientoConNormativasTecnicasYLegales": {
      "puntuacion": 5,
      "comentario": "El contrato cumple con todas las normativas locales e internacionales pertinentes."
    },
    "impactoYSostenibilidadDelProyecto": {
      "puntuacion": 2,
      "comentario": "No se mencionan los impactos ambientales ni la sostenibilidad del proyecto."
    }
  },
  "totalPuntuacion": 45,
  "categoria": "Riesgo Bajo",
  "analisis": {
    "puntosFuertes": [
      "Cumple con todos los requisitos legales.",
      "Condiciones técnicas detalladas y claras."
    ],
    "puntosDeMejora": [
      "Flujo de caja necesita ajustes.",
      "Falta de detalles sobre sostenibilidad ambiental."
    ]
  },
  "conclusion": "El contrato es sólido y bien estructurado. Aunque hay áreas de mejora en términos financieros y de sostenibilidad, se recomienda su aprobación con seguimiento."
}

analysis_prompt_template = ChatPromptTemplate.from_template(
    """Con base en los datos extraídos del texto en formato JSON, evalúa el contrato de obra pública utilizando la siguiente rúbrica. La calificación debe incluir una puntuación para cada uno de los criterios, y para cada criterio proporciona un comentario breve explicando la evaluación. Además, al final incluye un análisis general del contrato con los puntos fuertes, los puntos de mejora y una conclusión.

Rúbrica de Evaluación:

Cumplimiento de Requisitos Legales

Puntuación: [1-5]

Comentario: Evalúa si el contrato cumple con todos los requisitos legales, tales como la identificación de las partes involucradas (entidad contratante, contratista), RUC del contratista, legislación aplicable y mecanismos de resolución de conflictos.

Claridad y Complejidad Técnica

Puntuación: [1-5]

Comentario: Evalúa si las condiciones técnicas del contrato están claramente definidas, con detalles sobre materiales, especificaciones, maquinaria, personal requerido, etc.

Viabilidad del Cronograma de Ejecución

Puntuación: [1-5]

Comentario: Evalúa si el cronograma propuesto es realista y bien estructurado, y si los plazos asignados para las diferentes fases del proyecto son adecuados.

Evaluación de Riesgos Financieros y Económicos

Puntuación: [1-5]

Comentario: Evalúa si el presupuesto total y las partidas específicas están bien definidos, y si hay un plan de flujo de caja razonable para evitar riesgos financieros o de sobrecostos.

Garantías y Penalizaciones

Puntuación: [1-5]

Comentario: Evalúa si las garantías y penalizaciones están bien definidas y si cubren adecuadamente los riesgos, como incumplimiento o retrasos.

Condiciones de Pago y Avances

Puntuación: [1-5]

Comentario: Evalúa si las condiciones de pago son claras, justas y si los avances y pagos están bien estructurados para asegurar un flujo de trabajo adecuado.

Capacidades Técnicas del Contratista

Puntuación: [1-5]

Comentario: Evalúa si el contratista tiene la experiencia, capacidades técnicas y personal adecuado para cumplir con los requisitos del contrato.

Mecanismos de Resolución de Conflictos

Puntuación: [1-5]

Comentario: Evalúa si los mecanismos de resolución de conflictos están bien definidos, como la mediación, arbitraje o conciliación, y si son apropiados para el tipo de contrato.

Cumplimiento con Normativas Técnicas y Legales

Puntuación: [1-5]

Comentario: Evalúa si el contrato cumple con las normativas locales e internacionales pertinentes para la ejecución de la obra.

Impacto y Sostenibilidad del Proyecto

Puntuación: [1-5]

Comentario: Evalúa si el contrato tiene en cuenta la sostenibilidad del proyecto y sus posibles impactos ambientales o sociales.

Resultado Esperado:

Devuelve la puntuación obtenida en cada uno de los criterios de la rúbrica de evaluación.

Proporciona un comentario explicando cómo se ha calificado cada criterio.

Al final, incluye un análisis detallado con los puntos fuertes, los puntos de mejora y una conclusión final sobre el contrato.

JSON_SCHEMA:
{json_schema}

JSON_DATA_TO_ANALYZE:
{json_data}
"""
)

analysis_chain = analysis_prompt_template | analysis_llm
