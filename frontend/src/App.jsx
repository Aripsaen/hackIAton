import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

// Components
import DocumentUpload from "./components/DocumentUpload";
import Dashboard from "./components/Dashboard";
import Comparison from "./components/Comparison";

const API_BASE_URL = "http://localhost:8000"; // Ajustar según el entorno

function App() {
  const [currentView, setCurrentView] = useState("upload");
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [results, setResults] = useState(null);

  const fetchResults = async (caseId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/result/${caseId}`);
      setResults(response.data);
      setSelectedCase(caseId);
    } catch (error) {
      console.error("Error fetching results:", error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Procurement Analysis</h1>
        <p>Análisis Inteligente de Procesos de Licitación</p>

        <nav className="nav-tabs">
          <button
            className={currentView === "upload" ? "active" : ""}
            onClick={() => setCurrentView("upload")}
          >
            Cargar Documentos
          </button>
          <button
            className={currentView === "dashboard" ? "active" : ""}
            onClick={() => setCurrentView("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={currentView === "comparison" ? "active" : ""}
            onClick={() => setCurrentView("comparison")}
          >
            Comparación
          </button>
        </nav>
      </header>

      <main className="app-main">
        {currentView === "upload" && (
          <DocumentUpload
            onCaseCreated={(caseId) => {
              setCases((prev) => [...prev, caseId]);
              setCurrentView("dashboard");
              fetchResults(caseId);
            }}
          />
        )}

        {currentView === "dashboard" && (
          <Dashboard
            cases={cases}
            selectedCase={selectedCase}
            results={results}
            onCaseSelect={fetchResults}
          />
        )}

        {currentView === "comparison" && (
          <Comparison
            cases={cases}
            results={results}
            selectedCase={selectedCase}
          />
        )}
      </main>
    </div>
  );
}

export default App;
