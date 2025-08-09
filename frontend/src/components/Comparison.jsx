import { useState, useEffect } from "react";
import "./Comparison.css";

function Comparison({ results, selectedCase }) {
  const [comparisonData, setComparisonData] = useState([]);
  const [sortBy, setSortBy] = useState("monto");
  const [sortOrder, setSortOrder] = useState("asc");

  useEffect(() => {
    if (results && results.comparison?.bidders && results.extractions) {
      // Combine data from comparison and extractions to get all necessary info
      const combinedData = results.comparison.bidders.map(bidder => {
        const extraction = results.extractions.find(ext => ext.doc_id === bidder.doc_id);
        return {
          ...bidder,
          ...bidder.kpis, // Flatten kpis for easier access
          original_filename: extraction?.fields?.ObjetoContrato || bidder.doc_id, // Use a relevant field or doc_id
          contractor_name: bidder.name,
        };
      });
      setComparisonData(combinedData);
    }
  }, [results]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder(field === "monto" ? "asc" : "desc");
    }
  };

  const sortedData = [...comparisonData].sort((a, b) => {
    let aValue = a[sortBy] || 0;
    let bValue = b[sortBy] || 0;

    if (sortOrder === "asc") {
      return aValue > bValue ? 1 : -1;
    }
    return aValue < bValue ? 1 : -1;
  });

  const getScoreColor = (score, isRisk = false) => {
    const effectiveScore = isRisk ? 1 - score : score;
    if (effectiveScore >= 0.8) return "#059669";
    if (effectiveScore >= 0.6) return "#f59e0b";
    return "#dc2626";
  };

  const getScoreIcon = (score, isRisk = false) => {
    const effectiveScore = isRisk ? 1 - score : score;
    if (effectiveScore >= 0.8) return "🟢";
    if (effectiveScore >= 0.6) return "🟡";
    return "🔴";
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
              : "Este caso no tiene suficientes documentos para comparar."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="comparison">
      <div className="comparison-header">
        <h2>⚖️ Comparación de Oferentes</h2>
        <p>Análisis objetivo de propuestas para el caso: <strong>{selectedCase}</strong></p>
      </div>

      <div className="comparison-table-container">
        <h3>📊 Tabla Comparativa Detallada</h3>
        <div className="table-controls">
          <span>Ordenar por:</span>
          <select value={sortBy} onChange={(e) => handleSort(e.target.value)}>
            <option value="cumplimiento">Cumplimiento</option>
            <option value="riesgo">Nivel de Riesgo</option>
            <option value="monto">Monto</option>
          </select>
          <button onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")} className="sort-toggle">
            {sortOrder === "asc" ? "↑" : "↓"}
          </button>
        </div>

        <div className="comparison-table">
          <div className="table-header">
            <div className="header-cell document">Proponente</div>
            <div className="header-cell compliance" onClick={() => handleSort("cumplimiento")}>Cumplimiento</div>
            <div className="header-cell risk" onClick={() => handleSort("riesgo")}>Riesgo</div>
            <div className="header-cell amount" onClick={() => handleSort("monto")}>Monto</div>
            <div className="header-cell flags">Alertas</div>
          </div>

          {sortedData.map((bidder, index) => {
            const isTopPerformer = index === 0;

            return (
              <div key={bidder.doc_id || index} className={`table-row ${isTopPerformer ? "top-performer" : ""}`}>
                <div className="cell document">
                  <div className="document-info">
                    <div className="document-name">
                      {bidder.name}
                      {isTopPerformer && <span className="crown">👑</span>}
                    </div>
                    <div className="contractor-name">{bidder.original_filename}</div>
                  </div>
                </div>

                <div className="cell compliance">
                  <div className="score-display">
                    <span className="score-icon">{getScoreIcon(bidder.cumplimiento)}</span>
                    <span className="score-value" style={{ color: getScoreColor(bidder.cumplimiento) }}>
                      {(bidder.cumplimiento * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="score-bar">
                    <div className="score-fill" style={{ width: `${bidder.cumplimiento * 100}%`, backgroundColor: getScoreColor(bidder.cumplimiento) }} />
                  </div>
                </div>

                <div className="cell risk">
                  <div className="score-display">
                    <span className="score-icon">{getScoreIcon(bidder.riesgo, true)}</span>
                    <span className="score-value" style={{ color: getScoreColor(bidder.riesgo, true) }}>
                      {(bidder.riesgo * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="score-bar">
                    <div className="score-fill risk-fill" style={{ width: `${bidder.riesgo * 100}%`, backgroundColor: getScoreColor(bidder.riesgo, true) }} />
                  </div>
                </div>

                <div className="cell amount">
                  <div className="amount-value">${(bidder.monto || 0).toLocaleString()}</div>
                </div>

                <div className="cell flags">
                    <div className="flags-container">
                        {bidder.flags.length > 0 ? bidder.flags.map((flag, i) => (
                            <span key={i} className="flag-pill">{flag}</span>
                        )) : <span className="no-flags">-</span>}
                    </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default Comparison;