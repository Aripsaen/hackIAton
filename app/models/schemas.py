from pydantic import BaseModel, Field, BeforeValidator, field_validator
from typing import List, Dict, Any, Optional

# --- WF-02: Extraction Schemas ---

class MonetaryValue(BaseModel):
    valor: float = 0
    moneda: str = "USD"

class TimeValue(BaseModel):
    valor: float = 0
    unidad: str = "meses"

class Recepcion(BaseModel):
    provisional: str = ""
    definitiva: str = ""

class Controversias(BaseModel):
    mecanismos: str = ""
    jurisdiccion: str = ""

class Meta(BaseModel):
    docType: str = ""
    titulo: str = ""
    fechaDoc: str = ""
    anexos: List[str] = []

class Partes(BaseModel):
    EntidadContratante: str = ""
    Contratista: str = ""
    RUC: str = ""

class Contrato(BaseModel):
    ObjetoContrato: str = ""
    MontoTotal: MonetaryValue = Field(default_factory=MonetaryValue)
    Plazo: TimeValue = Field(default_factory=TimeValue)
    FormaPago: str = ""
    recepcion: Recepcion = Field(default_factory=Recepcion)
    controversias: Controversias = Field(default_factory=Controversias)
    LegislacionAplicable: str = ""

class Garantia(BaseModel):
    tipo: str = ""
    monto: MonetaryValue = Field(default_factory=MonetaryValue)
    vigencia: str = ""
    emisor: str = ""

class Penalizaciones(BaseModel):
    multasRetraso: str = ""
    penalizacionTecnica: str = ""
    causalesTerminacion: str = ""

class Tecnico(BaseModel):
    Especificaciones: List[str] = []
    PersonalTecnicoMinimo: List[str] = []
    MaquinariaRequerida: List[str] = []

class CronogramaItem(BaseModel):
    mes: str = ""
    fase: str = ""
    actividad: str = ""
    monto: MonetaryValue = Field(default_factory=MonetaryValue)

class PresupuestoPartida(BaseModel):
    partida: str = ""
    monto: MonetaryValue = Field(default_factory=MonetaryValue)

class PresupuestoMensual(BaseModel):
    mes: str = ""
    fase: str = ""
    monto: MonetaryValue = Field(default_factory=MonetaryValue)

class FlujoCajaItem(BaseModel):
    mes: str = ""
    avanceUSD: float = 0
    amortizacionUSD: float = 0
    pagoNetoUSD: float = 0
    costoUSD: float = 0
    saldoMensualUSD: float = 0
    saldoAcumuladoUSD: float = 0

class Anticipo(BaseModel):
    porcentaje: float = 0
    monto: MonetaryValue = Field(default_factory=MonetaryValue)

class Oferta(BaseModel):
    montoOfertado: MonetaryValue = Field(default_factory=MonetaryValue)
    anticipo: Anticipo = Field(default_factory=Anticipo)
    validezDias: int = 0
    garantiaMantenimiento: float = 0

class ProvenanceItem(BaseModel):
    campo: Optional[str] = None
    evidencia: str
    start_char: int
    end_char: int

    @field_validator('evidencia', mode='before')
    @classmethod
    def convert_evidencia_to_str(cls, v: Any) -> str:
        """Converts any input to string for the evidencia field."""
        return str(v)

class Diagnostics(BaseModel):
    missing: List[str] = []
    notes: List[str] = []

class ExtractionResult(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    partes: Partes = Field(default_factory=Partes)
    contrato: Contrato = Field(default_factory=Contrato)
    garantias: List[Garantia] = []
    penalizaciones: Penalizaciones = Field(default_factory=Penalizaciones)
    tecnico: Tecnico = Field(default_factory=Tecnico)
    cronograma: List[CronogramaItem] = []
    presupuestoPartidas: List[PresupuestoPartida] = []
    presupuestoMensual: List[PresupuestoMensual] = []
    flujoCaja: List[FlujoCajaItem] = []
    oferta: Oferta = Field(default_factory=Oferta)
    ruc_info: Optional[Dict[str, Any]] = None # Added for RUC lookup data
    provenance: List[ProvenanceItem] = []
    diagnostics: Diagnostics = Field(default_factory=Diagnostics)

# --- WF-03: Analysis Schemas ---

class EvaluacionRiesgoCriterio(BaseModel):
    puntuacion: int
    comentario: str

class EvaluacionRiesgos(BaseModel):
    estadoRuc: EvaluacionRiesgoCriterio
    requisitosLegales: EvaluacionRiesgoCriterio
    viabilidadTecnica: EvaluacionRiesgoCriterio
    viabilidadCronograma: EvaluacionRiesgoCriterio
    garantiasPenalizaciones: EvaluacionRiesgoCriterio

class KpisCalculados(BaseModel):
    puntuacionTotal: int
    ratioPuntuacionMonto: float
    alineacionContratista: int

class ResumenRiesgos(BaseModel):
    puntosCriticos: List[str]
    puntosDeMejora: List[str]
    conclusion: str

class AnalysisResult(BaseModel):
    evaluacionRiesgos: EvaluacionRiesgos
    kpis: KpisCalculados
    resumenRiesgos: ResumenRiesgos

# --- WF-04: Comparison Schemas ---

class BidderSummary(BaseModel):
    doc_id: str
    file_name: str
    extraction: ExtractionResult
    analysis: AnalysisResult

class ComparisonResult(BaseModel):
    case_id: str
    bidders: List[BidderSummary]
    # Add any computed KPIs here later if needed
    kpis: Dict[str, Any] = {}

# --- API Request/Response Schemas ---

class UploadResponse(BaseModel):
    message: str
    case_id: str
    doc_id: str

class CaseSummary(BaseModel):
    case_id: str
    document_count: int
    status: str # e.g., 'processing', 'completed'

class CaseListResponse(BaseModel):
    cases: List[CaseSummary]
