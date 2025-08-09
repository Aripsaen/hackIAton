import "./RubricAnalysis.css";

const getScoreColor = (score) => {
    if (score >= 4) return "#059669"; // green-700
    if (score >= 3) return "#f59e0b"; // amber-500
    return "#dc2626"; // red-600
};

function RubricAnalysis({ analysis }) {
  if (!analysis || !analysis.calificacion) {
    return <div className="rubric-container empty">Análisis de Rúbrica no disponible.</div>;
  }

  const { calificacion, totalPuntuacion, categoria, conclusion, puntosFuertes, puntosDeMejora } = analysis;

  return (
    <div className="rubric-container">
        <div className="rubric-header">
            <h3>Resultados de la Evaluación por Rúbrica</h3>
            <div className="rubric-summary-scores">
                <div className="summary-score-item">
                    <span>Puntuación Total</span>
                    <strong style={{color: getScoreColor(totalPuntuacion / 10)}}>{totalPuntuacion} / 50</strong>
                </div>
                <div className="summary-score-item">
                    <span>Categoría de Riesgo</span>
                    <strong style={{color: getScoreColor(totalPuntuacion / 10)}}>{categoria}</strong>
                </div>
            </div>
        </div>

        <div className="rubric-grid">
            {Object.entries(calificacion).map(([key, value]) => (
                <div key={key} className="rubric-item-card">
                    <div className="rubric-item-header">
                        <span className="rubric-item-title">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                        <span className="rubric-item-score" style={{ backgroundColor: getScoreColor(value.puntuacion) }}>
                            {value.puntuacion}/5
                        </span>
                    </div>
                    <p className="rubric-item-comment">{value.comentario}</p>
                </div>
            ))}
        </div>

        <div className="final-analysis-section">
            <h4>Análisis Final</h4>
            <div className="analysis-columns">
                <div className="analysis-column">
                    <h5>Puntos Fuertes</h5>
                    <ul>
                        {puntosFuertes.map((point, i) => <li key={i}>{point}</li>)}
                    </ul>
                </div>
                <div className="analysis-column">
                    <h5>Puntos de Mejora</h5>
                    <ul>
                        {puntosDeMejora.map((point, i) => <li key={i}>{point}</li>)}
                    </ul>
                </div>
            </div>
            <div className="analysis-conclusion">
                <h5>Conclusión</h5>
                <p>{conclusion}</p>
            </div>
        </div>
    </div>
  );
}

export default RubricAnalysis;
