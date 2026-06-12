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
    .map(
      (result) => `
        <tr>
          <td>${escapeHtml(result.field)}</td>
          <td>${escapeHtml(result.expectedValue || "-")}</td>
          <td>${escapeHtml(result.detectedValue || "-")}</td>
          <td><span class="badge badge-${statusClass(result.status)}">${escapeHtml(result.status)}</span></td>
          <td>${escapeHtml(result.notes || "-")}</td>
        </tr>
      `
    )
    .join("");

  resultsBody.innerHTML = rows;
  fileSummary.textContent = `${payload.file.originalName} | ${payload.summary.Match} match, ${payload.summary.Mismatch} mismatch, ${payload.summary["Needs Review"]} needs review`;
}

function clearResults() {
  resultsBody.innerHTML = `
    <tr>
      <td colspan="5" class="empty-state">Submit a label to see placeholder verification results.</td>
    </tr>
  `;
  fileSummary.textContent = "";
}

function setSubmittingState(isSubmitting) {
  submitButton.disabled = isSubmitting;
  submitButton.textContent = isSubmitting ? "Submitting..." : "Run placeholder verification";
}

function statusClass(status) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
