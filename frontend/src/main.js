import "./styles.css";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001";
const defaultBatchStatusMessage =
  "Batch mode is available. Select an image folder and a manifest JSON file.";
const emptyResultsMessage = "Submit a label to see OCR-based verification results.";
const requiredManifestFields = ["brandName", "classType", "alcoholContent", "netContents"];

const form = document.querySelector("#verify-form");
const formMessage = document.querySelector("#form-message");
const resultsBody = document.querySelector("#results-body");
const fileSummary = document.querySelector("#file-summary");
const submitButton = document.querySelector("#submit-button");
const healthStatus = document.querySelector("#health-status");
const batchUploadToggle = document.querySelector("#batch-upload-toggle");
const singleUploadFields = document.querySelector("#single-upload-fields");
const batchUploadFields = document.querySelector("#batch-upload-fields");
const modeDescription = document.querySelector("#mode-description");
const imageInput = document.querySelector("#image");
const imageDirectoryInput = document.querySelector("#image-directory");
const manifestFileInput = document.querySelector("#manifest-file");
const batchStatus = document.querySelector("#batch-status");
const resultsNav = document.querySelector("#results-nav");
const previousResultButton = document.querySelector("#previous-result-button");
const nextResultButton = document.querySelector("#next-result-button");
const resultsPosition = document.querySelector("#results-position");

let renderedResults = [];
let currentResultIndex = -1;

checkHealth();
syncUploadMode();

batchUploadToggle.addEventListener("change", () => {
  syncUploadMode();
  formMessage.textContent = "";
  formMessage.className = "message";
});

imageDirectoryInput.addEventListener("change", () => {
  handleBatchSelectionChange();
});

manifestFileInput.addEventListener("change", () => {
  handleBatchSelectionChange();
});

previousResultButton.addEventListener("click", () => {
  if (currentResultIndex <= 0) {
    return;
  }

  currentResultIndex -= 1;
  renderCurrentResultItem();
});

nextResultButton.addEventListener("click", () => {
  if (currentResultIndex >= renderedResults.length - 1) {
    return;
  }

  currentResultIndex += 1;
  renderCurrentResultItem();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (getUploadMode() === "batch") {
    await handleBatchSubmit();
    return;
  }

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

    const payload = await readJsonResponse(response);

    if (!response.ok) {
      throw new Error(payload?.error || "Verification request failed.");
    }

    if (!payload || !Array.isArray(payload.results) || !payload.summary || !payload.file) {
      throw new Error("The verification service returned an unexpected response.");
    }

    setRenderedResults([createVerifiedResultItem({ payload })]);
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

async function handleBatchSubmit() {
  const selectedManifest = getSelectedManifestFile();
  const selectedImages = Array.from(imageDirectoryInput.files || []);

  formMessage.textContent = "";
  formMessage.className = "message";

  if (selectedImages.length === 0) {
    const message = "Select an image folder before running batch verification.";
    appendBatchStatus(message);
    formMessage.textContent = message;
    formMessage.className = "message message-error";
    return;
  }

  if (!selectedManifest) {
    const message = "Select a manifest JSON file before running batch verification.";
    appendBatchStatus(message);
    formMessage.textContent = message;
    formMessage.className = "message message-error";
    return;
  }

  clearResults();
  setSubmittingState(true);
  setBatchStatus(["Reading manifest file..."]);

  try {
    const manifest = await parseBatchManifest(selectedManifest);
    const validatedEntries = validateManifestEntries(manifest.entries);
    const fileMap = buildSelectedFileMap(selectedImages);
    const resolvedEntries = resolveBatchEntries(validatedEntries, fileMap);
    const matchedCount = resolvedEntries.filter((entry) => entry.imageFile).length;
    const missingCount = resolvedEntries.length - matchedCount;

    appendBatchStatus(`Found ${validatedEntries.length} label${pluralSuffix(validatedEntries.length)} in the manifest.`);
    appendBatchStatus(`Matched ${matchedCount} image${pluralSuffix(matchedCount)} from the selected folder.`);

    if (missingCount > 0) {
      appendBatchStatus(`${missingCount} file${pluralSuffix(missingCount)} listed in the manifest ${missingCount === 1 ? "was" : "were"} not found.`);
    }

    const batchResults = await runBatchVerification(resolvedEntries);
    const issueCount = batchResults.filter((item) => item.kind !== "verified").length;

    setRenderedResults(batchResults);
    appendBatchStatus("Batch review is complete.");
    formMessage.textContent =
      issueCount > 0
        ? "Batch review is complete. Some labels still need attention."
        : "Batch review is complete.";
    formMessage.className = "message message-success";
  } catch (error) {
    clearResults();
    appendBatchStatus(error.message);
    formMessage.textContent = error.message;
    formMessage.className = "message message-error";
  } finally {
    setSubmittingState(false);
  }
}

function handleBatchSelectionChange() {
  if (getUploadMode() !== "batch") {
    return;
  }

  const hadResults = renderedResults.length > 0;

  if (hadResults) {
    clearResults();
  }

  const statusLines = buildBatchSelectionStatusLines();

  if (hadResults) {
    statusLines.push("Previous batch results were cleared because the selected files changed.");
  }

  setBatchStatus(statusLines);
  formMessage.textContent = "";
  formMessage.className = "message";
}

function buildBatchSelectionStatusLines() {
  const statusLines = [];
  const selectedImages = Array.from(imageDirectoryInput.files || []);
  const selectedManifest = getSelectedManifestFile();

  if (selectedImages.length > 0) {
    statusLines.push(`Selected folder contains ${selectedImages.length} file${pluralSuffix(selectedImages.length)}.`);
  }

  if (selectedManifest) {
    statusLines.push(`Selected manifest: ${selectedManifest.name}`);
  }

  return statusLines.length > 0 ? statusLines : [defaultBatchStatusMessage];
}

function getSelectedManifestFile() {
  return manifestFileInput.files?.[0] || null;
}

async function parseBatchManifest(file) {
  let parsedManifest;

  try {
    const manifestText = await file.text();
    parsedManifest = JSON.parse(manifestText);
  } catch (_error) {
    throw new Error("The manifest file could not be read. Please choose a valid JSON file.");
  }

  if (!parsedManifest || typeof parsedManifest !== "object" || Array.isArray(parsedManifest)) {
    throw new Error("The manifest file must contain a JSON object.");
  }

  if (parsedManifest.manifestVersion !== 1) {
    throw new Error('The manifest must include "manifestVersion": 1.');
  }

  if (!Array.isArray(parsedManifest.entries) || parsedManifest.entries.length === 0) {
    throw new Error('The manifest must include a non-empty "entries" list.');
  }

  return parsedManifest;
}

function validateManifestEntries(entries) {
  const validatedEntries = [];
  const seenFilePaths = new Set();

  entries.forEach((entry, index) => {
    const entryNumber = index + 1;

    if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
      throw new Error(`Entry ${entryNumber} must be an object.`);
    }

    const filePath = normalizeManifestPath(entry.file);

    if (!filePath) {
      throw new Error(`Entry ${entryNumber} is missing "file".`);
    }

    if (seenFilePaths.has(filePath)) {
      throw new Error(`The manifest lists "${filePath}" more than once.`);
    }

    const fields = entry.fields;

    if (!fields || typeof fields !== "object" || Array.isArray(fields)) {
      throw new Error(`Entry ${entryNumber} is missing "fields".`);
    }

    const normalizedFields = {};

    requiredManifestFields.forEach((fieldName) => {
      const fieldValue = fields[fieldName];

      if (typeof fieldValue !== "string" || fieldValue.trim() === "") {
        throw new Error(`Entry ${entryNumber} is missing "fields.${fieldName}".`);
      }

      normalizedFields[fieldName] = fieldValue.trim();
    });

    seenFilePaths.add(filePath);
    validatedEntries.push({
      submissionId: normalizeOptionalText(entry.submissionId),
      displayName: normalizeOptionalText(entry.displayName),
      filePath,
      fields: normalizedFields
    });
  });

  return validatedEntries;
}

function buildSelectedFileMap(files) {
  const fileMap = new Map();

  files.forEach((file) => {
    if (!(file instanceof File) || file.size === 0) {
      return;
    }

    const relativePath = getSelectedFolderRelativePath(file);

    if (!relativePath) {
      return;
    }

    fileMap.set(relativePath, file);
  });

  return fileMap;
}

function getSelectedFolderRelativePath(file) {
  const rawPath =
    typeof file.webkitRelativePath === "string" && file.webkitRelativePath
      ? file.webkitRelativePath
      : file.name;
  const normalizedPath = normalizeManifestPath(rawPath);

  if (!normalizedPath) {
    return "";
  }

  const firstSlashIndex = normalizedPath.indexOf("/");
  return firstSlashIndex === -1 ? normalizedPath : normalizedPath.slice(firstSlashIndex + 1);
}

function resolveBatchEntries(entries, fileMap) {
  return entries.map((entry) => {
    const imageFile = fileMap.get(entry.filePath) || null;

    if (imageFile) {
      return {
        ...entry,
        imageFile,
        errorMessage: ""
      };
    }

    return {
      ...entry,
      imageFile: null,
      errorMessage: `The manifest lists "${entry.filePath}", but that file was not found in the selected folder.`
    };
  });
}

async function runBatchVerification(resolvedEntries) {
  const batchResults = [];

  for (let index = 0; index < resolvedEntries.length; index += 1) {
    const entry = resolvedEntries[index];
    appendBatchStatus(`Checking label ${index + 1} of ${resolvedEntries.length}: ${entry.filePath}`);

    if (!entry.imageFile) {
      batchResults.push(createMissingFileResultItem(entry));
      appendBatchStatus(`File not found: ${entry.filePath}`);
      continue;
    }

    try {
      const payload = await verifyBatchEntry(entry);
      batchResults.push(createVerifiedResultItem({ ...entry, payload }));
    } catch (error) {
      batchResults.push(createRequestErrorResultItem(entry, error.message));
      appendBatchStatus(`Could not verify ${entry.filePath}. ${error.message}`);
    }
  }

  return batchResults;
}

async function verifyBatchEntry(entry) {
  const formData = new FormData();
  formData.append("image", entry.imageFile, entry.imageFile.name);
  formData.append("brandName", entry.fields.brandName);
  formData.append("classType", entry.fields.classType);
  formData.append("alcoholContent", entry.fields.alcoholContent);
  formData.append("netContents", entry.fields.netContents);

  let response;

  try {
    response = await fetch(`${apiBaseUrl}/verify`, {
      method: "POST",
      body: formData
    });
  } catch (_error) {
    throw new Error("The verification service could not be reached. Check that the backend is running.");
  }

  const payload = await readJsonResponse(response);

  if (!response.ok) {
    throw new Error(payload?.error || "The verification request failed.");
  }

  if (!payload || !Array.isArray(payload.results) || !payload.summary || !payload.file) {
    throw new Error("The verification service returned an unexpected response.");
  }

  return payload;
}

async function readJsonResponse(response) {
  try {
    return await response.json();
  } catch (_error) {
    return null;
  }
}

function clearResults() {
  renderedResults = [];
  currentResultIndex = -1;
  resultsBody.innerHTML = `
    <tr>
      <td colspan="5" class="empty-state">${emptyResultsMessage}</td>
    </tr>
  `;
  fileSummary.textContent = "";
  updateResultsNavigation();
}

function setSubmittingState(isSubmitting) {
  submitButton.disabled = isSubmitting;

  if (!isSubmitting) {
    submitButton.textContent = "Run OCR verification";
    return;
  }

  submitButton.textContent = getUploadMode() === "batch" ? "Running batch review..." : "Submitting...";
}

function getUploadMode() {
  return batchUploadToggle.checked ? "batch" : "single";
}

function syncUploadMode() {
  const uploadMode = getUploadMode();
  const isBatchMode = uploadMode === "batch";

  singleUploadFields.hidden = isBatchMode;
  singleUploadFields.classList.toggle("mode-panel-hidden", isBatchMode);
  batchUploadFields.hidden = !isBatchMode;
  batchUploadFields.classList.toggle("mode-panel-hidden", !isBatchMode);
  resultsNav.hidden = !isBatchMode;
  resultsNav.classList.toggle("results-nav-hidden", !isBatchMode);
  imageInput.required = !isBatchMode;

  clearResults();

  if (isBatchMode) {
    modeDescription.textContent = "Select a folder of label images and one manifest JSON file for sequential review.";
    setBatchStatus(buildBatchSelectionStatusLines());
    return;
  }

  modeDescription.textContent = "Upload one label image and enter the expected values manually.";
}

function setRenderedResults(results) {
  renderedResults = results;
  currentResultIndex = results.length > 0 ? 0 : -1;
  renderCurrentResultItem();
}

function renderCurrentResultItem() {
  if (currentResultIndex < 0 || currentResultIndex >= renderedResults.length) {
    clearResults();
    return;
  }

  renderResultItem(renderedResults[currentResultIndex]);
  updateResultsNavigation();
}

function renderResultItem(resultItem) {
  if (resultItem.kind === "verified") {
    renderVerifiedResultItem(resultItem);
    return;
  }

  renderBatchIssueResultItem(resultItem);
}

function renderVerifiedResultItem(resultItem) {
  const rows = resultItem.payload.results.map((result) => renderResultRow(result)).join("");

  resultsBody.innerHTML = rows;
  fileSummary.innerHTML = renderVerifiedSummary(resultItem);
}

function renderBatchIssueResultItem(resultItem) {
  const resultStatus = resultItem.kind === "missing-file" ? "Mismatch" : "Needs Review";
  const resultNotes = resultItem.errorMessage || "This label could not be verified.";

  resultsBody.innerHTML = renderResultRow({
    field: "Batch Status",
    expectedValue: resultItem.filePath || "-",
    detectedValue: "-",
    status: resultStatus,
    notes: resultNotes
  });
  fileSummary.innerHTML = renderBatchIssueSummary(resultItem);
}

function updateResultsNavigation() {
  if (renderedResults.length === 0) {
    previousResultButton.disabled = true;
    nextResultButton.disabled = true;
    resultsPosition.textContent = "No results loaded";
    return;
  }

  previousResultButton.disabled = currentResultIndex <= 0;
  nextResultButton.disabled = currentResultIndex >= renderedResults.length - 1;
  resultsPosition.textContent = `Result ${currentResultIndex + 1} of ${renderedResults.length}`;
}

function renderVerifiedSummary(resultItem) {
  const { payload } = resultItem;
  const summary = payload.summary || {};
  const title = resultItem.displayName || payload.file.originalName;
  const detailLines = [];

  if (resultItem.submissionId) {
    detailLines.push(`Submission ID: ${resultItem.submissionId}`);
  }

  if (resultItem.filePath) {
    detailLines.push(`File: ${resultItem.filePath}`);
  }

  return `
    <div class="file-summary-name">${escapeHtml(title)}</div>
    ${renderSummaryDetails(detailLines)}
    <div class="file-summary-counts">
      <span class="summary-pill summary-pill-match">${summary.Match || 0} match</span>
      <span class="summary-pill summary-pill-mismatch">${summary.Mismatch || 0} mismatch</span>
      <span class="summary-pill summary-pill-review">${summary["Needs Review"] || 0} needs review</span>
    </div>
  `;
}

function renderBatchIssueSummary(resultItem) {
  const title = resultItem.displayName || resultItem.filePath || "Batch item";
  const detailLines = [];
  const errorLabel = resultItem.kind === "missing-file" ? "Missing file" : "Request error";

  if (resultItem.submissionId) {
    detailLines.push(`Submission ID: ${resultItem.submissionId}`);
  }

  if (resultItem.filePath) {
    detailLines.push(`File: ${resultItem.filePath}`);
  }

  return `
    <div class="file-summary-name">${escapeHtml(title)}</div>
    ${renderSummaryDetails(detailLines)}
    <div class="file-summary-counts">
      <span class="summary-pill summary-pill-error">${escapeHtml(errorLabel)}</span>
    </div>
    <div class="summary-note">${escapeHtml(resultItem.errorMessage || "This label could not be verified.")}</div>
  `;
}

function renderSummaryDetails(detailLines) {
  if (detailLines.length === 0) {
    return "";
  }

  return `
    <div class="file-summary-meta">
      ${detailLines.map((detailLine) => `<div class="summary-detail">${escapeHtml(detailLine)}</div>`).join("")}
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

function createVerifiedResultItem({
  submissionId = "",
  displayName = "",
  filePath = "",
  payload
}) {
  return {
    kind: "verified",
    submissionId,
    displayName,
    filePath,
    payload,
    errorMessage: ""
  };
}

function createMissingFileResultItem(entry) {
  return {
    kind: "missing-file",
    submissionId: entry.submissionId,
    displayName: entry.displayName,
    filePath: entry.filePath,
    payload: null,
    errorMessage: entry.errorMessage
  };
}

function createRequestErrorResultItem(entry, errorMessage) {
  return {
    kind: "request-error",
    submissionId: entry.submissionId,
    displayName: entry.displayName,
    filePath: entry.filePath,
    payload: null,
    errorMessage
  };
}

function setBatchStatus(lines) {
  batchStatus.value = lines.filter(Boolean).join("\n");
}

function appendBatchStatus(line) {
  if (!line) {
    return;
  }

  batchStatus.value = batchStatus.value ? `${batchStatus.value}\n${line}` : line;
  batchStatus.scrollTop = batchStatus.scrollHeight;
}

function normalizeManifestPath(value) {
  if (typeof value !== "string") {
    return "";
  }

  return value.trim().replaceAll("\\", "/");
}

function normalizeOptionalText(value) {
  return typeof value === "string" ? value.trim() : "";
}

function pluralSuffix(count) {
  return count === 1 ? "" : "s";
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
