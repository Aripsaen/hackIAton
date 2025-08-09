import "./Dashboard.css";
import RubricAnalysis from "./RubricAnalysis"; // Import the new component

function Dashboard({ cases, selectedCase, results, onCaseSelect, isLoading }) {

  const handleCaseChange = (e) => {
    const caseId = e.target.value;
    if (caseId && onCaseSelect) {
      onCaseSelect(caseId);
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard">
        <div className="loading-state">
          <div className="processing-spinner"></div>
          <p>Cargando resultados para el caso: <strong>{selectedCase}</strong></p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>📊 Dashboard de Análisis</h2>
        <div className="case-selector">
          <label htmlFor="case-select">Caso:</label>
          <select id="case-select" value={selectedCase || ""} onChange={handleCaseChange}>
            <option value="">Seleccione un caso...</option>
            {cases.map((caseId) => (
              <option key={caseId} value={caseId}>{caseId}</option>
            ))}
          </select>
        </div>
      </div>

      {!results ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No hay resultados disponibles</h3>
          <p>Seleccione un caso procesado o cargue nuevos documentos para ver el análisis.</p>
        </div>
      ) : (
        <div className="results-container">
          {/* The comparison object now contains bidders, and each bidder has their analysis */}
          {results.comparison?.bidders?.map(bidder => (
            <RubricAnalysis key={bidder.doc_id} analysis={bidder.analysis} />
          ))}

          <div className="quick-actions">
            <h3>🔗 Acciones Rápidas</h3>
            <div className="actions-grid">
              <button className="action-button" onClick={() => window.open(results.report_pdf_url, "_blank")} disabled={!results.report_pdf_url}>
                📄 Ver Reporte PDF General
              </button>
              <button className="action-button" onClick={() => window.open(results.sheet_url, "_blank")} disabled={!results.sheet_url}>
                📊 Dashboard Looker
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
