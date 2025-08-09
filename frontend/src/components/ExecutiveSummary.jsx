import "./ExecutiveSummary.css";

const getRiskColor = (level) => {
  const lowerLevel = level?.toLowerCase();
  if (lowerLevel === "bajo") return "#059669";
  if (lowerLevel === "medio") return "#f59e0b";
  if (lowerLevel === "alto") return "#dc2626";
  return "#9ca3af";
};

function ExecutiveSummary({ analysis }) {
  if (!analysis || !analysis.case_summary) {
    return (
      <div className="executive-summary-card empty">
        <p>Esperando el análisis ejecutivo final del modelo Pro...</p>
      </div>
    );
  }

  const { 
    overall_risk_level,
    recommended_bidder_doc_id,
    executive_summary,
    key_risks_for_case = [],
  } = analysis.case_summary;

  return (
    <div className="executive-summary-card">
      <div className="summary-header">
        <h3>🧠 Análisis Ejecutivo (Gemini Pro)</h3>
        <div className="summary-meta">
          <div className="risk-level-badge">
            <span>Riesgo General:</span>
            <strong style={{ color: getRiskColor(overall_risk_level) }}>
              {overall_risk_level || "N/A"}
            </strong>
          </div>
          <div className="recommendation-badge">
            <span>Recomendación:</span>
            <strong>{recommended_bidder_doc_id || "N/A"}</strong>
          </div>
        </div>
      </div>

      <div className="summary-content">
        <h4>Resumen Ejecutivo:</h4>
        <p className="summary-text">{executive_summary}</p>
      </div>

      {key_risks_for_case.length > 0 && (
        <div className="summary-risks">
          <h4>Riesgos Clave para el Caso:</h4>
          <ul>
            {key_risks_for_case.map((risk, index) => (
              <li key={index} className="risk-item">
                <span 
                  className="risk-severity-dot"
                  style={{ backgroundColor: getRiskColor(risk.severity) }}
                ></span>
                <div className="risk-details">
                  <strong>{risk.risk_id}:</strong> {risk.description}
                  {risk.mitigation && <small><strong>Sugerencia:</strong> {risk.mitigation}</small>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ExecutiveSummary;
