document.addEventListener('DOMContentLoaded', () => {
    const pdfUpload = document.getElementById('pdfUpload');
    const startAnalysisBtn = document.getElementById('startAnalysisBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const caseIdDisplay = document.getElementById('caseIdDisplay');
    const caseList = document.getElementById('caseList');
    const analysisResultsSection = document.getElementById('analysisResultsSection');
    const currentCaseIdDisplay = document.getElementById('currentCaseId');
    const resultsStatus = document.getElementById('resultsStatus');
    const bidderComparisonDiv = document.getElementById('bidderComparison');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    let currentCaseId = null;

    // Function to generate a simple UUID
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Function to display messages
    function showMessage(element, message, type = 'info') {
        element.textContent = message;
        element.className = `status-message ${type}-message`;
    }

    // Function to fetch and display existing cases
    async function fetchCases() {
        try {
            const response = await fetch('/api/cases');
            const data = await response.json();
            caseList.innerHTML = ''; // Clear existing list
            if (data.cases && data.cases.length > 0) {
                data.cases.forEach(caseItem => {
                    const li = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = '#';
                    link.textContent = `Case ID: ${caseItem.case_id}`; 
                    link.onclick = (e) => {
                        e.preventDefault();
                        loadCaseResults(caseItem.case_id);
                    };
                    li.appendChild(link);
                    const statusSpan = document.createElement('span');
                    statusSpan.textContent = `Status: ${caseItem.status} (${caseItem.document_count} docs)`;
                    li.appendChild(statusSpan);
                    caseList.appendChild(li);
                });
            } else {
                caseList.innerHTML = '<li>No cases found. Upload documents to create one.</li>';
            }
        } catch (error) {
            console.error('Error fetching cases:', error);
            showMessage(uploadStatus, 'Error loading cases.', 'error');
        }
    }

    // Function to load and display results for a specific case
    async function loadCaseResults(caseId) {
        currentCaseId = caseId;
        currentCaseIdDisplay.textContent = caseId;
        analysisResultsSection.style.display = 'block';
        bidderComparisonDiv.innerHTML = '';
        downloadReportBtn.style.display = 'none';
        showMessage(resultsStatus, 'Fetching analysis results...', 'info');

        try {
            const statusResponse = await fetch(`/api/cases/${caseId}/status`);
            const statusData = await statusResponse.json();

            if (statusData.status !== 'completed') {
                showMessage(resultsStatus, `Case is still ${statusData.status}. Please wait...`, 'info');
                // Poll for status if not completed
                setTimeout(() => loadCaseResults(caseId), 5000); 
                return;
            }

            const comparisonResponse = await fetch(`/api/cases/${caseId}/comparison`);
            if (!comparisonResponse.ok) {
                throw new Error(`HTTP error! status: ${comparisonResponse.status}`);
            }
            const comparisonData = await comparisonResponse.json();
            
            displayComparisonResults(comparisonData);
            showMessage(resultsStatus, 'Analysis complete!', 'success');
            downloadReportBtn.style.display = 'block';

        } catch (error) {
            console.error('Error fetching comparison results:', error);
            showMessage(resultsStatus, `Error loading results: ${error.message}. Please try again later.`, 'error');
        }
    }

    // Function to display comparison data
    function displayComparisonResults(data) {
        bidderComparisonDiv.innerHTML = '';

        // Display KPIs first
        if (Object.keys(data.kpis).length > 0) {
            const kpiSection = document.createElement('div');
            kpiSection.className = 'kpi-section';
            kpiSection.innerHTML = '<h3>Key Performance Indicators</h3>';
            for (const docId in data.kpis) {
                const kpi = data.kpis[docId];
                kpiSection.innerHTML += `<p><strong>${docId}</strong>: Score per Dollar Offered: ${kpi.score_per_dollar_offered.toFixed(4)}</p>`;
            }
            bidderComparisonDiv.appendChild(kpiSection);
        }

        data.bidders.forEach(bidder => {
            const bidderCard = document.createElement('div');
            bidderCard.className = 'bidder-card';
            bidderCard.innerHTML = `
                <h3>Bidder: ${bidder.extraction.partes.Contratista || bidder.doc_id}</h3>
                <p><strong>Object of Contract:</strong> ${bidder.extraction.contrato.ObjetoContrato}</p>
                <p><strong>Offered Amount:</strong> $${bidder.extraction.oferta.montoOfertado.valor.toLocaleString()} ${bidder.extraction.oferta.montoOfertado.moneda}</p>
                <p><strong>Total Analysis Score:</strong> ${bidder.analysis.totalPuntuacion}</p>
                <p><strong>Analysis Category:</strong> ${bidder.analysis.categoria}</p>
                <h4>Analysis Conclusion:</h4>
                <p>${bidder.analysis.conclusion}</p>
                <!-- You can add more details here as needed -->
            `;
            bidderComparisonDiv.appendChild(bidderCard);
        });
    }

    // Event listener for Start Analysis button
    startAnalysisBtn.addEventListener('click', async () => {
        const files = pdfUpload.files;
        if (files.length === 0) {
            showMessage(uploadStatus, 'Please select at least one PDF file.', 'error');
            return;
        }

        startAnalysisBtn.disabled = true;
        showMessage(uploadStatus, 'Uploading and starting analysis...', 'info');

        currentCaseId = generateUUID(); // Generate a new case ID for this batch of uploads
        caseIdDisplay.textContent = `Processing Case ID: ${currentCaseId}`; 
        caseIdDisplay.style.display = 'block';

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch(`/api/upload/${currentCaseId}`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Upload result:', result);
            showMessage(uploadStatus, `Successfully uploaded ${files.length} documents. Analysis started in background.`, 'success');
            pdfUpload.value = ''; // Clear file input
            fetchCases(); // Refresh case list
            loadCaseResults(currentCaseId); // Start polling for results for the new case

        } catch (error) {
            console.error('Error during upload:', error);
            showMessage(uploadStatus, `Upload failed: ${error.message}`, 'error');
        } finally {
            startAnalysisBtn.disabled = false;
        }
    });

    // Event listener for Download Report button
    downloadReportBtn.addEventListener('click', () => {
        if (currentCaseId) {
            window.open(`/api/cases/${currentCaseId}/report`, '_blank');
        } else {
            showMessage(resultsStatus, 'No case selected to download report.', 'error');
        }
    });

    // Initial fetch of cases when the page loads
    fetchCases();
});
