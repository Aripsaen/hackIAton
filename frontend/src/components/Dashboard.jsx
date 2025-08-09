import { useState, useEffect } from "react";
import axios from "axios";
import "./Dashboard.css";

const API_BASE_URL = "http://localhost:8000";

function Dashboard({ cases, selectedCase, results, onCaseSelect }) {
  const [localResults, setLocalResults] = useState(null);

  useEffect(() => {
    if (results) {
      setLocalResults(results);
    }
  }, [results]);

  const handleCaseChange = (e) => {
    const caseId = e.target.value;
    if (caseId && onCaseSelect) {
      onCaseSelect(caseId);
    }
  };

  const getRiskLevel = (score) => {
    if (score >= 8) return { level: "BAJO", color: "#059669", icon: "✅" };
    if (score >= 6) return { level: "MEDIO", color: "#f59e0b", icon: "⚠️" };
    if (score >= 4) return { level: "ALTO", color: "#dc2626", icon: "🚨" };
    return { level: "CRÍTICO", color: "#991b1b", icon: "🛑" };
  };

  const getComplianceLevel = (score) => {
    if (score >= 8) return { level: "EXCELENTE", color: "#059669", icon: "🏆" };
    if (score >= 7) return { level: "BUENO", color: "#10b981", icon: "👍" };
    if (score >= 6) return { level: "REGULAR", color: "#f59e0b", icon: "📋" };
    return { level: "DEFICIENTE", color: "#dc2626", icon: "❌" };
  };

  if (!localResults && selectedCase) {
    return (
      <div className="dashboard">
        <div className="loading-state">
          <div className="processing-spinner"></div>
          <p>
            Cargando resultados para el caso: <strong>{selectedCase}</strong>
          </p>
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
          <select
            id="case-select"
            value={selectedCase || ""}
            onChange={handleCaseChange}
          >
            <option value="">Seleccione un caso...</option>
            {cases.map((caseId) => (
              <option key={caseId} value={caseId}>
                {caseId}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!localResults ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No hay resultados disponibles</h3>
          <p>
            Seleccione un caso procesado o cargue nuevos documentos para ver el
            análisis.
          </p>
        </div>
      ) : (
        <div className="results-container">
          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card documents">
              <div className="card-icon">📄</div>
              <div className="card-content">
                <h3>Documentos</h3>
                <div className="card-value">
                  {localResults.summary?.total_documents || 0}
                </div>
                <div className="card-subtitle">Analizados</div>
              </div>
            </div>

            <div className="summary-card compliance">
              <div className="card-icon">
                {
                  getComplianceLevel(localResults.summary?.avg_compliance || 0)
                    .icon
                }
              </div>
              <div className="card-content">
                <h3>Cumplimiento</h3>
                <div
                  className="card-value"
                  style={{
                    color: getComplianceLevel(
                      localResults.summary?.avg_compliance || 0
                    ).color,
                  }}
                >
                  {
                    getComplianceLevel(
                      localResults.summary?.avg_compliance || 0
                    ).level
                  }
                </div>
                <div className="card-subtitle">
                  {(localResults.summary?.avg_compliance || 0).toFixed(1)}/10
                </div>
              </div>
            </div>

            <div className="summary-card risk">
              <div className="card-icon">
                {getRiskLevel(localResults.summary?.avg_risk || 0).icon}
              </div>
              <div className="card-content">
                <h3>Nivel de Riesgo</h3>
                <div
                  className="card-value"
                  style={{
                    color: getRiskLevel(localResults.summary?.avg_risk || 0)
                      .color,
                  }}
                >
                  {getRiskLevel(localResults.summary?.avg_risk || 0).level}
                </div>
                <div className="card-subtitle">
                  {(10 - (localResults.summary?.avg_risk || 0)).toFixed(1)}/10
                </div>
              </div>
            </div>

            <div className="summary-card amount">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <h3>Monto Total</h3>
                <div className="card-value">
                  ${(localResults.summary?.total_amount || 0).toLocaleString()}
                </div>
                <div className="card-subtitle">Estimado</div>
              </div>
            </div>
          </div>

          {/* Documents Analysis */}
          <div className="documents-analysis">
            <h3>🔍 Análisis por Documento</h3>
            <div className="documents-grid">
              {localResults.documents?.map((doc, index) => (
                <div key={index} className="document-card">
                  <div className="document-header">
                    <h4>{doc.original_filename}</h4>
                    <span
                      className={`document-type ${doc.type?.toLowerCase()}`}
                    >
                      {doc.type || "DOCUMENTO"}
                    </span>
                  </div>

                  <div className="document-metrics">
                    <div className="metric">
                      <span className="metric-label">Cumplimiento:</span>
                      <div className="metric-bar">
                        <div
                          className="metric-fill compliance"
                          style={{
                            width: `${(doc.compliance_score || 0) * 10}%`,
                          }}
                        ></div>
                        <span className="metric-value">
                          {(doc.compliance_score || 0).toFixed(1)}/10
                        </span>
                      </div>
                    </div>

                    <div className="metric">
                      <span className="metric-label">Riesgo:</span>
                      <div className="metric-bar">
                        <div
                          className="metric-fill risk"
                          style={{ width: `${(doc.risk_score || 0) * 10}%` }}
                        ></div>
                        <span className="metric-value">
                          {(doc.risk_score || 0).toFixed(1)}/10
                        </span>
                      </div>
                    </div>
                  </div>

                  {doc.key_findings && doc.key_findings.length > 0 && (
                    <div className="key-findings">
                      <h5>Hallazgos Clave:</h5>
                      <ul>
                        {doc.key_findings.slice(0, 3).map((finding, i) => (
                          <li key={i}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {doc.risks && doc.risks.length > 0 && (
                    <div className="document-risks">
                      <h5>⚠️ Riesgos Detectados:</h5>
                      <ul>
                        {doc.risks.slice(0, 2).map((risk, i) => (
                          <li key={i} className="risk-item">
                            <span
                              className={`risk-severity ${risk.severity?.toLowerCase()}`}
                            >
                              {risk.severity}
                            </span>
                            {risk.description}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <h3>🔗 Acciones Rápidas</h3>
            <div className="actions-grid">
              <button
                className="action-button"
                onClick={() =>
                  window.open(localResults.report_pdf_url, "_blank")
                }
                disabled={!localResults.report_pdf_url}
              >
                📄 Ver Reporte PDF
              </button>
              <button
                className="action-button"
                onClick={() =>
                  window.open(localResults.comparison_pdf_url, "_blank")
                }
                disabled={!localResults.comparison_pdf_url}
              >
                ⚖️ Comparación Detallada
              </button>
              <button
                className="action-button"
                onClick={() =>
                  window.open(localResults.looker_dashboard_url, "_blank")
                }
                disabled={!localResults.looker_dashboard_url}
              >
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
