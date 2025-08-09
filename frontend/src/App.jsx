import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

// Components
import DocumentUpload from "./components/DocumentUpload";
import Dashboard from "./components/Dashboard";
import Comparison from "./components/Comparison";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [currentView, setCurrentView] = useState("upload");
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchResults = async (caseId) => {
    setIsLoading(true);
    setResults(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/result/${caseId}`);
      setResults(response.data);
      setSelectedCase(caseId);
    } catch (error) {
      console.error("Error fetching results:", error);
      alert(`No se pudieron cargar los resultados para el caso ${caseId}. Es posible que aún se esté procesando o que haya fallado.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCaseCreated = (caseId) => {
    if (!cases.includes(caseId)) {
        setCases((prev) => [...prev, caseId]);
    }
    setSelectedCase(caseId);
    setCurrentView("dashboard");
    fetchResults(caseId);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Procurement Analysis</h1>
        <nav className="nav-tabs">
          <button className={currentView === "upload" ? "active" : ""} onClick={() => setCurrentView("upload")}>
            Cargar Documentos
          </button>
          <button className={currentView === "dashboard" ? "active" : ""} onClick={() => setCurrentView("dashboard")}>
            Dashboard
          </button>
          <button className={currentView === "comparison" ? "active" : ""} onClick={() => setCurrentView("comparison")}>
            Comparación
          </button>
        </nav>
      </header>

      <main className="app-main">
        {currentView === "upload" && (
          <DocumentUpload onCaseCreated={handleCaseCreated} />
        )}

        {currentView === "dashboard" && (
          <Dashboard
            cases={cases}
            selectedCase={selectedCase}
            results={results}
            onCaseSelect={fetchResults}
            isLoading={isLoading}
          />
        )}

        {currentView === "comparison" && (
          <Comparison
            results={results}
            selectedCase={selectedCase}
          />
        )}
      </main>
    </div>
  );
}

export default App;