import { useState, useRef } from "react";
import axios from "axios";
import "./DocumentUpload.css";

const API_BASE_URL = "http://localhost:8000";

function DocumentUpload({ onCaseCreated }) {
  const [caseId, setCaseId] = useState("");
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [jobStatus, setJobStatus] = useState(null);
  const fileInputRef = useRef(null);

  const handleCaseIdChange = (e) => {
    // Generate a clean case ID from input
    const cleanId = e.target.value.replace(/[^a-zA-Z0-9-_]/g, "").toLowerCase();
    setCaseId(cleanId);
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(
      (file) => file.type === "application/pdf"
    );
    setFiles(selectedFiles);
  };

  const uploadFile = async (file, index) => {
    try {
      // Step 1: Get signed URL
      const initResponse = await axios.post(`${API_BASE_URL}/upload-init`, {
        case_id: caseId,
        filename: file.name,
        content_type: file.type,
      });

      const { signed_url, gcs_path } = initResponse.data;

      // Step 2: Upload to signed URL
      await axios.put(signed_url, file, {
        headers: {
          "Content-Type": file.type,
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress((prev) => ({
            ...prev,
            [index]: progress,
          }));
        },
      });

      return { success: true, gcs_path };
    } catch (error) {
      console.error("Upload error:", error);
      return { success: false, error: error.message };
    }
  };

  const handleUpload = async () => {
    if (!caseId.trim() || files.length === 0) {
      alert("Por favor ingrese un ID de caso y seleccione archivos PDF");
      return;
    }

    setUploading(true);
    setUploadProgress({});

    try {
      // Upload all files
      const uploadPromises = files.map((file, index) =>
        uploadFile(file, index)
      );
      const results = await Promise.all(uploadPromises);

      const failedUploads = results.filter((r) => !r.success);
      if (failedUploads.length > 0) {
        alert(`${failedUploads.length} archivos fallaron al subir`);
        return;
      }

      // Start processing
      setProcessing(true);
      const processResponse = await axios.post(`${API_BASE_URL}/process`, {
        case_id: caseId,
      });

      const { job_id } = processResponse.data;

      // Poll for job status
      pollJobStatus(job_id);
    } catch (error) {
      console.error("Processing error:", error);
      alert("Error iniciando el procesamiento");
    } finally {
      setUploading(false);
    }
  };

  const pollJobStatus = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await axios.get(
          `${API_BASE_URL}/status/${jobId}`
        );
        const { status } = statusResponse.data;

        setJobStatus(status);

        if (status === "SUCCEEDED") {
          clearInterval(pollInterval);
          setProcessing(false);
          onCaseCreated(caseId);
          // Reset form
          setCaseId("");
          setFiles([]);
          setUploadProgress({});
          setJobStatus(null);
          if (fileInputRef.current) {
            fileInputRef.current.value = "";
          }
        } else if (status === "FAILED") {
          clearInterval(pollInterval);
          setProcessing(false);
          alert("El procesamiento falló. Por favor intente de nuevo.");
        }
      } catch (error) {
        console.error("Status polling error:", error);
        clearInterval(pollInterval);
        setProcessing(false);
      }
    }, 3000); // Poll every 3 seconds

    // Stop polling after 10 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (processing) {
        setProcessing(false);
        alert("El procesamiento está tomando más tiempo del esperado.");
      }
    }, 600000);
  };

  return (
    <div className="document-upload">
      <div className="upload-card">
        <h2>Cargar Documentos de Licitación</h2>
        <p>Suba pliegos, propuestas y contratos para análisis automatizado</p>

        <div className="form-group">
          <label htmlFor="caseId">ID del Caso/Licitación:</label>
          <input
            id="caseId"
            type="text"
            value={caseId}
            onChange={handleCaseIdChange}
            placeholder="ej: licitacion-obra-2024-001"
            disabled={uploading || processing}
          />
          <small>Solo letras, números, guiones y guiones bajos</small>
        </div>

        <div className="form-group">
          <label htmlFor="files">Documentos PDF:</label>
          <input
            id="files"
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            disabled={uploading || processing}
          />
          <small>
            Solo archivos PDF. Puede seleccionar múltiples archivos.
          </small>
        </div>

        {files.length > 0 && (
          <div className="file-list">
            <h3>Archivos seleccionados:</h3>
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </span>
                {uploadProgress[index] && (
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${uploadProgress[index]}%` }}
                    ></div>
                    <span className="progress-text">
                      {uploadProgress[index]}%
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={
            uploading || processing || !caseId.trim() || files.length === 0
          }
          className="upload-button"
        >
          {uploading
            ? "Subiendo..."
            : processing
            ? "Procesando..."
            : "Subir y Analizar"}
        </button>

        {processing && (
          <div className="status-info">
            <div className="processing-spinner"></div>
            <p>
              Estado: <strong>{jobStatus || "INICIANDO"}</strong>
            </p>
            <small>
              El análisis puede tomar varios minutos dependiendo del tamaño de
              los documentos...
            </small>
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentUpload;
