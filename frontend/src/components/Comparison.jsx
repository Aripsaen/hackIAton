import { useState, useEffect } from "react";
import "./Comparison.css";

function Comparison({ cases, results, selectedCase }) {
  const [comparisonData, setComparisonData] = useState([]);
  const [sortBy, setSortBy] = useState("compliance_score");
  const [sortOrder, setSortOrder] = useState("desc");

  useEffect(() => {
    if (results && results.documents) {
      // Filter only proposals for comparison
      const proposals = results.documents.filter(
        (doc) => doc.type && doc.type.toLowerCase().includes("propuesta")
      );

      // If no proposals, use all documents for demo purposes
      const documentsToCompare =
        proposals.length > 0 ? proposals : results.documents;

      setComparisonData(documentsToCompare);
    }
  }, [results]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  const sortedData = [...comparisonData].sort((a, b) => {
    let aValue = a[sortBy] || 0;
    let bValue = b[sortBy] || 0;

    if (sortBy === "original_filename") {
      aValue = aValue.toString();
      bValue = bValue.toString();
    }

    if (sortOrder === "asc") {
      return aValue > bValue ? 1 : -1;
    }
    return aValue < bValue ? 1 : -1;
  });

  const getScoreColor = (score) => {
    if (score >= 8) return "#059669";
    if (score >= 6) return "#f59e0b";
    if (score >= 4) return "#dc2626";
    return "#991b1b";
  };

  const getScoreIcon = (score) => {
    if (score >= 8) return "🟢";
    if (score >= 6) return "🟡";
    if (score >= 4) return "🟠";
    return "🔴";
  };

  const getBestInCategory = (field) => {
    if (comparisonData.length === 0) return null;
    return comparisonData.reduce((best, current) =>
      (current[field] || 0) > (best[field] || 0) ? current : best
    );
  };

  if (!results || comparisonData.length === 0) {
    return (
      <div className="comparison">
        <div className="empty-state">
          <div className="empty-icon">⚖️</div>
          <h3>No hay datos para comparar</h3>
          <p>
            {!selectedCase
              ? "Seleccione un caso procesado para ver la comparación entre oferentes."
              : "Este caso no tiene suficientes documentos para comparar. Asegúrese de que hay múltiples propuestas cargadas."}
          </p>
        </div>
      </div>
    );
  }

  const bestCompliance = getBestInCategory("compliance_score");
  const bestRisk = getBestInCategory("risk_score");
  const bestAmount = getBestInCategory("estimated_amount");

  return (
    <div className="comparison">
      <div className="comparison-header">
        <h2>⚖️ Comparación de Oferentes</h2>
        <p>
          Análisis objetivo de propuestas para el caso:{" "}
          <strong>{selectedCase}</strong>
        </p>
      </div>

      {/* Winners Summary */}
      <div className="winners-summary">
        <h3>🏆 Mejores en Cada Categoría</h3>
        <div className="winners-grid">
          <div className="winner-card compliance">
            <div className="winner-icon">📋</div>
            <h4>Mejor Cumplimiento</h4>
            <div className="winner-name">
              {bestCompliance?.original_filename}
            </div>
            <div className="winner-score">
              {(bestCompliance?.compliance_score || 0).toFixed(1)}/10
            </div>
          </div>

          <div className="winner-card risk">
            <div className="winner-icon">🛡️</div>
            <h4>Menor Riesgo</h4>
            <div className="winner-name">{bestRisk?.original_filename}</div>
            <div className="winner-score">
              {(bestRisk?.risk_score || 0).toFixed(1)}/10
            </div>
          </div>

          <div className="winner-card amount">
            <div className="winner-icon">💰</div>
            <h4>Mejor Oferta Económica</h4>
            <div className="winner-name">{bestAmount?.original_filename}</div>
            <div className="winner-score">
              ${(bestAmount?.estimated_amount || 0).toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="comparison-table-container">
        <h3>📊 Tabla Comparativa Detallada</h3>

        <div className="table-controls">
          <span>Ordenar por:</span>
          <select value={sortBy} onChange={(e) => handleSort(e.target.value)}>
            <option value="compliance_score">Cumplimiento</option>
            <option value="risk_score">Nivel de Riesgo</option>
            <option value="estimated_amount">Monto</option>
            <option value="original_filename">Nombre</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
            className="sort-toggle"
          >
            {sortOrder === "asc" ? "↑" : "↓"}
          </button>
        </div>

        <div className="comparison-table">
          <div className="table-header">
            <div className="header-cell document">Documento</div>
            <div
              className="header-cell compliance"
              onClick={() => handleSort("compliance_score")}
            >
              Cumplimiento
              {sortBy === "compliance_score" &&
                (sortOrder === "asc" ? " ↑" : " ↓")}
            </div>
            <div
              className="header-cell risk"
              onClick={() => handleSort("risk_score")}
            >
              Riesgo
              {sortBy === "risk_score" && (sortOrder === "asc" ? " ↑" : " ↓")}
            </div>
            <div
              className="header-cell amount"
              onClick={() => handleSort("estimated_amount")}
            >
              Monto Estimado
              {sortBy === "estimated_amount" &&
                (sortOrder === "asc" ? " ↑" : " ↓")}
            </div>
            <div className="header-cell overall">Evaluación</div>
          </div>

          {sortedData.map((doc, index) => {
            const overallScore =
              ((doc.compliance_score || 0) + (10 - (doc.risk_score || 0))) / 2;
            const isTopPerformer =
              index === 0 && sortBy !== "original_filename";

            return (
              <div
                key={doc.doc_id || index}
                className={`table-row ${isTopPerformer ? "top-performer" : ""}`}
              >
                <div className="cell document">
                  <div className="document-info">
                    <div className="document-name">
                      {doc.original_filename}
                      {isTopPerformer && <span className="crown">👑</span>}
                    </div>
                    {doc.contractor_name && (
                      <div className="contractor-name">
                        {doc.contractor_name}
                      </div>
                    )}
                  </div>
                </div>

                <div className="cell compliance">
                  <div className="score-display">
                    <span className="score-icon">
                      {getScoreIcon(doc.compliance_score || 0)}
                    </span>
                    <span
                      className="score-value"
                      style={{
                        color: getScoreColor(doc.compliance_score || 0),
                      }}
                    >
                      {(doc.compliance_score || 0).toFixed(1)}
                    </span>
                  </div>
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{
                        width: `${(doc.compliance_score || 0) * 10}%`,
                        backgroundColor: getScoreColor(
                          doc.compliance_score || 0
                        ),
                      }}
                    />
                  </div>
                </div>

                <div className="cell risk">
                  <div className="score-display">
                    <span className="score-icon">
                      {getScoreIcon(10 - (doc.risk_score || 0))}
                    </span>
                    <span
                      className="score-value"
                      style={{
                        color: getScoreColor(10 - (doc.risk_score || 0)),
                      }}
                    >
                      {(doc.risk_score || 0).toFixed(1)}
                    </span>
                  </div>
                  <div className="score-bar">
                    <div
                      className="score-fill risk-fill"
                      style={{
                        width: `${(doc.risk_score || 0) * 10}%`,
                        backgroundColor: getScoreColor(
                          10 - (doc.risk_score || 0)
                        ),
                      }}
                    />
                  </div>
                </div>

                <div className="cell amount">
                  <div className="amount-value">
                    ${(doc.estimated_amount || 0).toLocaleString()}
                  </div>
                  {doc.currency && doc.currency !== "USD" && (
                    <div className="currency">{doc.currency}</div>
                  )}
                </div>

                <div className="cell overall">
                  <div className="overall-score">
                    <div
                      className="overall-circle"
                      style={{
                        background: `conic-gradient(${getScoreColor(
                          overallScore
                        )} ${overallScore * 36}deg, #e5e7eb 0deg)`,
                      }}
                    >
                      <span className="overall-text">
                        {overallScore.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Key Insights */}
      <div className="insights-section">
        <h3>💡 Insights Clave</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>📈 Rendimiento General</h4>
            <p>
              De {comparisonData.length} propuestas analizadas,
              {" " +
                comparisonData.filter((d) => (d.compliance_score || 0) >= 7)
                  .length}{" "}
              cumplen con un nivel aceptable de requisitos.
            </p>
          </div>

          <div className="insight-card">
            <h4>⚠️ Alertas de Riesgo</h4>
            <p>
              {comparisonData.filter((d) => (d.risk_score || 0) >= 6).length}{" "}
              propuesta(s) presentan riesgos significativos que requieren
              atención especial.
            </p>
          </div>

          <div className="insight-card">
            <h4>💸 Rango de Precios</h4>
            <p>
              Variación del{" "}
              {comparisonData.length > 1
                ? Math.round(
                    ((Math.max(
                      ...comparisonData.map((d) => d.estimated_amount || 0)
                    ) -
                      Math.min(
                        ...comparisonData.map((d) => d.estimated_amount || 0)
                      )) /
                      Math.min(
                        ...comparisonData.map((d) => d.estimated_amount || 0)
                      )) *
                      100
                  )
                : 0}
              % entre la oferta más alta y más baja.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Comparison;
