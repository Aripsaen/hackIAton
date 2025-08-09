import json
from worker.utils.provenance import add_provenance_to_extraction

def test_provenance_adder():
    '''
    Tests that the provenance utility correctly finds evidence and offsets.
    '''
    mock_text = "El Contratista, ACME Inc., se compromete a pagar la suma de 100.00 USD. La Forma de Pago es contra entrega."
    
    mock_extraction = {
        "fields": {
            "Contratista": "ACME Inc.",
            "MontoTotal": 100.00,
            "FormaPago": "contra entrega",
            "GarantiaCumplimiento": None # Missing field
        }
    }

    result = add_provenance_to_extraction(mock_extraction, mock_text)

    assert "provenance" in result
    assert "diagnostics" in result
    assert "missing" in result["diagnostics"]
    
    assert "GarantiaCumplimiento" in result["diagnostics"]["missing"]
    
    provenance_fields = [p["field"] for p in result["provenance"]]
    assert "Contratista" in provenance_fields
    assert "FormaPago" in provenance_fields
    assert "MontoTotal" not in provenance_fields # Not a string, can't be found directly

    # Check offsets for a known field
    p_contratista = next(p for p in result["provenance"] if p["field"] == "Contratista")
    assert p_contratista["start_char"] == 16
    assert p_contratista["end_char"] == 26
    assert "ACME Inc." in p_contratista["evidence"]
