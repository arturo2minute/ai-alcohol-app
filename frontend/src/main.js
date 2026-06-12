import "./styles.css";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001";

const form = document.querySelector("#verify-form");
const formMessage = document.querySelector("#form-message");
const resultsBody = document.querySelector("#results-body");
const fileSummary = document.querySelector("#file-summary");
const submitButton = document.querySelector("#submit-button");
const healthStatus = document.querySelector("#health-status");
checkHealth();

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const selectedFile = formData.get("image");

  if (!(selectedFile instanceof File) || selectedFile.size === 0) {
    formMessage.textContent = "Select an image before submitting.";
    formMessage.className = "message message-error";
    return;
  }

  setSubmittingState(true);

  try {
    const response = await fetch(`${apiBaseUrl}/verify`, {
      method: "POST",
      body: formData
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Verification request failed.");
    }

    renderResults(payload);
    formMessage.textContent = payload.note;
    formMessage.className = "message message-success";
  } catch (error) {
    clearResults();
    formMessage.textContent = error.message;
    formMessage.className = "message message-error";
  } finally {
    setSubmittingState(false);
  }
});

resultsBody.addEventListener("click", (event) => {
  const warningRow = event.target.closest(".warning-row-toggle");

  if (!warningRow) {
    return;
  }

  toggleWarningRow(warningRow);
});

resultsBody.addEventListener("keydown", (event) => {
  const warningRow = event.target.closest(".warning-row-toggle");

  if (!warningRow || (event.key !== "Enter" && event.key !== " ")) {
    return;
  }

  event.preventDefault();
  toggleWarningRow(warningRow);
});

async function checkHealth() {
  try {
    const response = await fetch(`${apiBaseUrl}/health`);

    if (!response.ok) {
      throw new Error("Backend health check failed.");
    }

    const payload = await response.json();
    healthStatus.textContent = `Backend status: ${payload.status}`;
    healthStatus.className = "health health-ok";
  } catch (_error) {
    healthStatus.textContent = "Backend unreachable. Start the API on http://localhost:3001.";
    healthStatus.className = "health health-error";
  }
}

function renderResults(payload) {
  const rows = payload.results
    .map((result) => renderResultRow(result))
    .join("");

  resultsBody.innerHTML = rows;
  fileSummary.innerHTML = renderFileSummary(payload);
}

function clearResults() {
  resultsBody.innerHTML = `
    <tr>
      <td colspan="5" class="empty-state">Submit a label to see OCR-based verification results.</td>
    </tr>
  `;
  fileSummary.textContent = "";
}

function setSubmittingState(isSubmitting) {
  submitButton.disabled = isSubmitting;
  submitButton.textContent = isSubmitting ? "Submitting..." : "Run OCR verification";
}

function renderFileSummary(payload) {
  return `
    <div class="file-summary-name">${escapeHtml(payload.file.originalName)}</div>
    <div class="file-summary-counts">
      <span class="summary-pill summary-pill-match">${payload.summary.Match} match</span>
      <span class="summary-pill summary-pill-mismatch">${payload.summary.Mismatch} mismatch</span>
      <span class="summary-pill summary-pill-review">${payload.summary["Needs Review"]} needs review</span>
    </div>
  `;
}

function renderResultRow(result) {
  if (result.field === "Government Warning") {
    return `
      <tr
        class="warning-row-toggle"
        tabindex="0"
        role="button"
        aria-expanded="false"
      >
        <td data-label="Field">${escapeHtml(result.field)}</td>
        <td data-label="Expected" class="warning-summary" title="${escapeHtml(result.expectedValue || "-")}">
          <div class="warning-cell-text">${escapeHtml(result.expectedValue || "-")}</div>
        </td>
        <td data-label="Detected" class="warning-summary" title="${escapeHtml(result.detectedValue || "-")}">
          <div class="warning-cell-text">${escapeHtml(result.detectedValue || "-")}</div>
        </td>
        <td data-label="Status"><span class="badge badge-${statusClass(result.status)}">${escapeHtml(result.status)}</span></td>
        <td data-label="Notes">${escapeHtml(result.notes || "-")}</td>
      </tr>
    `;
  }

  return `
    <tr>
      <td data-label="Field">${escapeHtml(result.field)}</td>
      <td data-label="Expected">${escapeHtml(result.expectedValue || "-")}</td>
      <td data-label="Detected">${escapeHtml(result.detectedValue || "-")}</td>
      <td data-label="Status"><span class="badge badge-${statusClass(result.status)}">${escapeHtml(result.status)}</span></td>
      <td data-label="Notes">${escapeHtml(result.notes || "-")}</td>
    </tr>
  `;
}

function statusClass(status) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

function toggleWarningRow(warningRow) {
  const isExpanded = warningRow.getAttribute("aria-expanded") === "true";
  warningRow.setAttribute("aria-expanded", String(!isExpanded));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
