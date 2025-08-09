import "./Dashboard.css";
import ExecutiveSummary from "./ExecutiveSummary"; // Import the new component

function Dashboard({ cases, selectedCase, results, onCaseSelect }) {

  const handleCaseChange = (e) => {
    const caseId = e.target.value;
    if (caseId && onCaseSelect) {
      onCaseSelect(caseId);
    }
  };

  // --- Data Transformation --- 
  // Create derived data from the new `results` prop structure
  const getSummaryData = () => {
    if (!results) return null;

    const bidders = results.comparison?.bidders || [];
    const totalDocs = results.extractions?.length || 0;
    
    const totalAmount = bidders.reduce((sum, bidder) => sum + (bidder.kpis?.monto || 0), 0);
    const avgCompliance = bidders.length > 0 
      ? bidders.reduce((sum, bidder) => sum + (bidder.kpis?.cumplimiento || 0), 0) / bidders.length
      : 0;
    const avgRisk = bidders.length > 0
      ? bidders.reduce((sum, bidder) => sum + (bidder.kpis?.riesgo || 0), 0) / bidders.length
      : 0;

    return {
      totalDocs,
      totalAmount,
      avgCompliance: avgCompliance * 10, // Scale to 0-10
      avgRisk: avgRisk * 10, // Scale to 0-10
    };
  };

  const summaryData = getSummaryData();

  const getRiskLevel = (score) => {
    if (score <= 2) return { level: "BAJO", color: "#059669", icon: "✅" };
    if (score <= 5) return { level: "MEDIO", color: "#f59e0b", icon: "⚠️" };
    if (score <= 8) return { level: "ALTO", color: "#dc2626", icon: "🚨" };
    return { level: "CRÍTICO", color: "#991b1b", icon: "🛑" };
  };

  const getComplianceLevel = (score) => {
    if (score >= 8) return { level: "EXCELENTE", color: "#059669", icon: "🏆" };
    if (score >= 7) return { level: "BUENO", color: "#10b981", icon: "👍" };
    if (score >= 6) return { level: "REGULAR", color: "#f59e0b", icon: "📋" };
    return { level: "DEFICIENTE", color: "#dc2626", icon: "❌" };
  };

  if (!results && selectedCase) {
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
          {/* New Executive Summary Component */}
          <ExecutiveSummary analysis={results.final_analysis} />

          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card documents">
              <div className="card-icon">📄</div>
              <div className="card-content">
                <h3>Documentos</h3>
                <div className="card-value">{summaryData.totalDocs}</div>
                <div className="card-subtitle">Analizados</div>
              </div>
            </div>

            <div className="summary-card compliance">
              <div className="card-icon">{getComplianceLevel(summaryData.avgCompliance).icon}</div>
              <div className="card-content">
                <h3>Cumplimiento</h3>
                <div className="card-value" style={{ color: getComplianceLevel(summaryData.avgCompliance).color }}>
                  {getComplianceLevel(summaryData.avgCompliance).level}
                </div>
                <div className="card-subtitle">Promedio {summaryData.avgCompliance.toFixed(1)}/10</div>
              </div>
            </div>

            <div className="summary-card risk">
              <div className="card-icon">{getRiskLevel(summaryData.avgRisk).icon}</div>
              <div className="card-content">
                <h3>Nivel de Riesgo</h3>
                <div className="card-value" style={{ color: getRiskLevel(summaryData.avgRisk).color }}>
                  {getRiskLevel(summaryData.avgRisk).level}
                </div>
                <div className="card-subtitle">Promedio {summaryData.avgRisk.toFixed(1)}/10</div>
              </div>
            </div>

            <div className="summary-card amount">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <h3>Monto Total</h3>
                <div className="card-value">${(summaryData.totalAmount).toLocaleString()}</div>
                <div className="card-subtitle">Agregado</div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <h3>🔗 Acciones Rápidas</h3>
            <div className="actions-grid">
              <button className="action-button" onClick={() => window.open(results.report_pdf_url, "_blank")} disabled={!results.report_pdf_url}>
                📄 Ver Reporte PDF
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