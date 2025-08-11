import json
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.services.ruc_cache import get_cached_ruc, set_cached_ruc # Import cache functions

async def fetch_ruc_info(ruc: str) -> Optional[Dict[str, Any]]:
    """Fetches RUC information from webservices.ec or returns mock data."""

    # Try to get from cache first
    cached_data = get_cached_ruc(ruc)
    if cached_data:
        print(f"RUC {ruc}: Cache used.")
        return cached_data

    if settings.USE_WEBSERVICES_EC_MOCK:
        print("Using mock RUC data (API not called).")
        mock_data = {
          "data": {
            "main": [
              {
                "numeroRuc": "0992879955001",
                "razonSocial": "ACCROACHCODE S.A.",
                "estadoContribuyenteRuc": "ACTIVO",
                "actividadEconomicaPrincipal": "ACTIVIDADES DE PLANIFICACIÓN Y DISEÑO DE SISTEMAS INFORMÁTICOS QUE INTEGRAN EQUIPO Y PROGRAMAS INFORMÁTICOS Y TECNOLOGÍA DE LAS COMUNICACIONES.",
                "tipoContribuyente": "SOCIEDAD",
                "regimen": "GENERAL",
                "categoria": None,
                "obligadoLlevarContabilidad": "SI",
                "agenteRetencion": "NO",
                "contribuyenteEspecial": "NO",
                "informacionFechasContribuyente": {
                  "fechaInicioActividades": "2014-10-08 00:00:00.0",
                  "fechaCese": "",
                  "fechaReinicioActividades": "",
                  "fechaActualizacion": "2024-07-15 22:50:08.0"
                },
                "representantesLegales": [
                  {
                    "identificacion": "0924349095",
                    "nombre": "BUITRON CARRASCO GUSTAVO ENRIQUE"
                  }
                ],
                "motivoCancelacionSuspension": None,
                "contribuyenteFantasma": "NO",
                "transaccionesInexistente": "NO"
              }
            ],
            "addit": [
              {
                "nombreFantasiaComercial": "PAGOS & FACTURAS",
                "tipoEstablecimiento": "MAT",
                "direccionCompleta": "GUAYAS / GUAYAQUIL / TARQUI / VICTOR EMILIO ESTRADA 706-B Y FICUS",
                "estado": "ABIERTO",
                "numeroEstablecimiento": "001",
                "matriz": "SI"
              },
              {
                "nombreFantasiaComercial": "ACCROACHCODE",
                "tipoEstablecimiento": "OFI",
                "direccionCompleta": "GUAYAS / GUAYAQUIL / GUAYAQUIL / FICUS 706-B Y VICTOR EMILIO ESTRADA",
                "estado": "CERRADO",
                "numeroEstablecimiento": "002",
                "matriz": "NO"
              }
            ]
          }
        }
        set_cached_ruc(ruc, mock_data) # Cache mock data as well
        return mock_data

    if not settings.WEBSERVICES_EC_API_KEY:
        print("Error: WEBSERVICES_EC_API_KEY is not set. Cannot fetch real RUC data.")
        return None

    url = f"https://webservices.ec/api/ruc/{ruc}"
    headers = {
        "Authorization": f"Bearer {settings.WEBSERVICES_EC_API_KEY}",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            result_data = response.json()
            set_cached_ruc(ruc, result_data) # Cache real API data
            print(f"RUC {ruc}: API called and cached.")
            return result_data
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during RUC lookup: {e}")
        return None
