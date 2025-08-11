document.addEventListener("DOMContentLoaded", () => {
  const pdfUpload = document.getElementById("pdfUpload");
  const startAnalysisBtn = document.getElementById("startAnalysisBtn");
  const uploadStatus = document.getElementById("uploadStatus");
  const caseIdDisplay = document.getElementById("caseIdDisplay");
  const caseList = document.getElementById("caseList");
  const analysisResultsSection = document.getElementById(
    "analysisResultsSection"
  );
  const currentCaseIdDisplay = document.getElementById("currentCaseId");
  const resultsStatus = document.getElementById("resultsStatus");
  const bidderComparisonDiv = document.getElementById("bidderComparison");
  const textAnalysisDiv = document.getElementById("textAnalysis");
  const dropzone = document.getElementById("dropzone");
  const downloadReportBtn = document.getElementById("downloadReportBtn");

  let currentCaseId = null;

  // Function to generate a simple UUID
  function generateUUID() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
      /[xy]/g,
      function (c) {
        var r = (Math.random() * 16) | 0,
          v = c == "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      }
    );
  }

  // Function to display messages
  function showMessage(element, message, type = "info") {
    element.textContent = message;
    element.className = `status-message ${type}-message`;
  }

  // Drag & Drop support (inspired by old front)
  function setDropState(active) {
    if (dropzone) dropzone.classList.toggle("dragover", !!active);
  }
  if (dropzone) {
    ["dragenter", "dragover"].forEach((evt) =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDropState(true);
      })
    );
    ["dragleave", "dragend", "drop"].forEach((evt) =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDropState(false);
      })
    );
    dropzone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      if (dt?.files && pdfUpload) {
        const pdfs = Array.from(dt.files).filter((f) => /\.pdf$/i.test(f.name));
        const dataTransfer = new DataTransfer();
        pdfs.forEach((f) => dataTransfer.items.add(f));
        pdfUpload.files = dataTransfer.files;
        showMessage(
          uploadStatus,
          `${pdfs.length} archivo(s) listo(s) para subir.`,
          "info"
        );
      }
    });
  }

  // Function to fetch and display existing cases
  async function fetchCases() {
    try {
      const response = await fetch("/api/cases");
      const data = await response.json();
      caseList.innerHTML = ""; // Clear existing list
      if (data.cases && data.cases.length > 0) {
        data.cases.forEach((caseItem) => {
          const li = document.createElement("li");
          const link = document.createElement("a");
          link.href = "#";
          link.textContent = `ID de Caso: ${caseItem.case_id}`;
          link.onclick = (e) => {
            e.preventDefault();
            loadCaseResults(caseItem.case_id);
          };
          li.appendChild(link);
          const statusSpan = document.createElement("span");
          // Status values (completed, partially_completed, processing, empty, not_found) are internal and not translated here
          let displayStatus = caseItem.status;
          if (caseItem.status === "completed") displayStatus = "Completado";
          else if (caseItem.status === "partially_completed")
            displayStatus = "Parcialmente Completado";
          else if (caseItem.status === "processing")
            displayStatus = "Procesando";
          else if (caseItem.status === "empty") displayStatus = "Vacío";
          else if (caseItem.status === "not_found")
            displayStatus = "No Encontrado";

          statusSpan.textContent = `Estado: ${displayStatus} (${caseItem.document_count} docs)`;
          li.appendChild(statusSpan);
          caseList.appendChild(li);
        });
      } else {
        caseList.innerHTML =
          "<li>No se encontraron casos. Sube documentos para crear uno.</li>";
      }
    } catch (error) {
      console.error("Error fetching cases:", error);
      showMessage(uploadStatus, "Error al cargar casos.", "error");
    }
  }

  // Function to load and display results for a specific case
  async function loadCaseResults(caseId) {
    currentCaseId = caseId;
    currentCaseIdDisplay.textContent = caseId;
    if (analysisResultsSection) {
      analysisResultsSection.style.display = "block";
    } else {
      console.error("Error: analysisResultsSection element not found.");
    }
    bidderComparisonDiv.innerHTML = "";
    downloadReportBtn.style.display = "none";
    showMessage(resultsStatus, "Obteniendo resultados del análisis...", "info");

    try {
      const statusResponse = await fetch(`/api/cases/${caseId}/status`);
      const statusData = await statusResponse.json();

      if (
        statusData.status !== "completed" &&
        statusData.status !== "partially_completed"
      ) {
        showMessage(
          resultsStatus,
          `El caso aún está ${
            statusData.status === "processing"
              ? "procesando"
              : statusData.status
          }. Por favor, espera...`,
          "info"
        );
        // Poll for status if not completed or partially_completed
        setTimeout(() => loadCaseResults(caseId), 5000);
        return;
      }

      const comparisonResponse = await fetch(`/api/cases/${caseId}/comparison`);
      if (!comparisonResponse.ok) {
        throw new Error(`HTTP error! status: ${comparisonResponse.status}`);
      }
      const comparisonData = await comparisonResponse.json();

      displayComparisonResults(comparisonData);
      displayTextualAnalysis(comparisonData);
      showMessage(resultsStatus, "Análisis completado!", "success");
      downloadReportBtn.style.display = "block";
    } catch (error) {
      console.error("Error fetching comparison results:", error);
      showMessage(
        resultsStatus,
        `Error al cargar resultados: ${error.message}. Por favor, inténtalo de nuevo más tarde.`,
        "error"
      );
    }
  }

  // Function to display comparison data
  function displayComparisonResults(data) {
    bidderComparisonDiv.innerHTML = "";

    // Display KPIs first
    if (Object.keys(data.kpis).length > 0) {
      const kpiSection = document.createElement("div");
      kpiSection.className = "kpi-section";
      kpiSection.innerHTML = "<h3>Indicadores Clave de Rendimiento</h3>";
      for (const docId in data.kpis) {
        const kpi = data.kpis[docId];
        kpiSection.innerHTML += `
                    <p><strong>Oferente ${docId}</strong>:</p>
                    <ul>
                        <li>Puntuación Total: ${kpi.puntuacionTotal}</li>
                        <li>Ratio Puntuación/Monto: ${kpi.ratioPuntuacionMonto.toFixed(
                          2
                        )}</li>
                        <li>Alineación del Contratista: ${
                          kpi.alineacionContratista === 1
                            ? "Alineado"
                            : "No Alineado"
                        }</li>
                    </ul>
                `;
      }
      bidderComparisonDiv.appendChild(kpiSection);
    }

    data.bidders.forEach((bidder) => {
      const bidderCard = document.createElement("div");
      bidderCard.className = "bidder-card";

      let riskEvaluationHtml = "";
      for (const criterion in bidder.analysis.evaluacionRiesgos) {
        const eval = bidder.analysis.evaluacionRiesgos[criterion];
        riskEvaluationHtml += `
                    <li><strong>${criterion
                      .replace(/([A-Z])/g, " $1")
                      .replace(/^./, (str) =>
                        str.toUpperCase()
                      )}:</strong> Puntuación: ${
          eval.puntuacion
        }, Comentario: ${eval.comentario}</li>
                `;
      }

      bidderCard.innerHTML = `
                <h3>Oferente: ${
                  bidder.extraction.partes.Contratista || bidder.doc_id
                }</h3>
                <h4>Evaluación de Riesgos (Puntuación):</h4>
                <ul>${riskEvaluationHtml}</ul>
                <h4>KPIs Calculados:</h4>
                <ul>
                    <li>Puntuación Total: ${
                      bidder.analysis.kpis.puntuacionTotal
                    }</li>
                    <li>Ratio Puntuación/Monto: ${bidder.analysis.kpis.ratioPuntuacionMonto.toFixed(
                      2
                    )}</li>
                    <li>Alineación del Contratista: ${
                      bidder.analysis.kpis.alineacionContratista === 1
                        ? "Alineado"
                        : "No Alineado"
                    }</li>
                </ul>
                <h4>Resumen de Riesgos:</h4>
                <p><strong>Puntos Críticos:</strong> ${bidder.analysis.resumenRiesgos.puntosCriticos.join(
                  "; "
                )}</p>
                <p><strong>Puntos de Mejora:</strong> ${bidder.analysis.resumenRiesgos.puntosDeMejora.join(
                  "; "
                )}</p>
                <p><strong>Conclusión:</strong> ${
                  bidder.analysis.resumenRiesgos.conclusion
                }</p>
                <!-- Puedes añadir más detalles aquí si es necesario -->
            `;
      bidderComparisonDiv.appendChild(bidderCard);
    });
  }

  // Function to display a concise textual analysis
  function displayTextualAnalysis(data) {
    if (!textAnalysisDiv) return;
    const bidders = data.bidders || [];
    if (bidders.length === 0) {
      textAnalysisDiv.innerHTML =
        "<p>No hay oferentes para analizar todavía.</p>";
      return;
    }

    // Determine best score and alignment
    let best = null;
    bidders.forEach((b) => {
      const score = b.analysis?.kpis?.puntuacionTotal ?? 0;
      if (!best || score > best.score) {
        best = {
          id: b.doc_id,
          name: b.extraction?.partes?.Contratista || b.doc_id,
          score,
          ratio: b.analysis?.kpis?.ratioPuntuacionMonto ?? 0,
          aligned: b.analysis?.kpis?.alineacionContratista === 1,
        };
      }
    });

    // Build risk highlights per bidder
    const riskSummaries = bidders
      .map((b) => {
        const name = b.extraction?.partes?.Contratista || b.doc_id;
        const rr = b.analysis?.resumenRiesgos || {
          puntosCriticos: [],
          puntosDeMejora: [],
          conclusion: "",
        };
        const riesgos = (rr.puntosCriticos || []).slice(0, 3).join("; ");
        const mejoras = (rr.puntosDeMejora || []).slice(0, 2).join("; ");
        const concl = rr.conclusion || "";
        return `<p><strong>${name}:</strong> Puntuación ${
          b.analysis?.kpis?.puntuacionTotal ?? 0
        } · Ratio ${Number(b.analysis?.kpis?.ratioPuntuacionMonto ?? 0).toFixed(
          2
        )} · ${
          b.analysis?.kpis?.alineacionContratista === 1
            ? "Alineado"
            : "No alineado"
        }<br/>Riesgos: ${riesgos || "—"}<br/>Mejoras: ${
          mejoras || "—"
        }<br/>Conclusión: ${concl}</p>`;
      })
      .join("");

    const header = `<p><strong>Resumen:</strong> Se analizaron ${
      bidders.length
    } oferente(s). ${
      best
        ? `La mejor puntuación fue ${best.score} (${best.name})${
            best.aligned ? ", alineado con requisitos" : ""
          }.`
        : ""
    }</p>`;

    textAnalysisDiv.innerHTML = header + riskSummaries;
  }

  // Event listener for Start Analysis button
  startAnalysisBtn.addEventListener("click", async () => {
    const files = pdfUpload.files;
    if (files.length === 0) {
      showMessage(
        uploadStatus,
        "Por favor, selecciona al menos un archivo PDF.",
        "error"
      );
      return;
    }

    startAnalysisBtn.disabled = true;
    startAnalysisBtn.classList.add("loading-pulse");
    showMessage(uploadStatus, "Subiendo e iniciando análisis...", "info");

    currentCaseId = generateUUID(); // Generate a new case ID for this batch of uploads
    caseIdDisplay.textContent = `Procesando ID de Caso: ${currentCaseId}`;
    caseIdDisplay.style.display = "block";

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    try {
      const response = await fetch(`/api/upload/${currentCaseId}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Upload result:", result);
      showMessage(
        uploadStatus,
        `Se subieron ${files.length} documentos correctamente. Análisis iniciado en segundo plano.`,
        "success"
      );
      pdfUpload.value = ""; // Clear file input
      fetchCases(); // Refresh case list
      loadCaseResults(currentCaseId); // Start polling for results for the new case
    } catch (error) {
      console.error("Error during upload:", error);
      showMessage(
        uploadStatus,
        `Error durante la subida: ${error.message}`,
        "error"
      );
    } finally {
      startAnalysisBtn.disabled = false;
      startAnalysisBtn.classList.remove("loading-pulse");
    }
  });

  // Event listener for Download Report button
  downloadReportBtn.addEventListener("click", () => {
    if (currentCaseId) {
      window.open(`/api/cases/${currentCaseId}/report`, "_blank");
    } else {
      showMessage(
        resultsStatus,
        "No hay caso seleccionado para descargar el informe.",
        "error"
      );
    }
  });

  // Initial fetch of cases when the page loads
  fetchCases();
});
