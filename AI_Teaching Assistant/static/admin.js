// Admin dashboard logic.
// Auth is handled entirely by the browser's HTTP Basic Auth prompt
// (triggered by the 401 the server sends) - fetch() automatically reuses
// those credentials for same-origin requests once the browser has them.

const statusEl = document.getElementById("admin-status");
const table = document.getElementById("admin-table");
const tableBody = document.getElementById("admin-table-body");
const refreshBtn = document.getElementById("refresh-btn");
const hideResolvedCheckbox = document.getElementById("hide-resolved");

const modal = document.getElementById("admin-modal");
const modalClose = document.getElementById("admin-modal-close");
const modalMeta = document.getElementById("admin-modal-meta");
const modalQuestion = document.getElementById("admin-modal-question");
const modalAnswer = document.getElementById("admin-modal-answer");

let allInteractions = [];

// Reuses the same Markdown + math rendering approach as the student page.
function extractMath(text) {
  const blocks = [];
  function stash(display, latex) {
    const token = `@@MATHBLOCK${blocks.length}@@`;
    blocks.push({ display, latex: latex.trim() });
    return token;
  }
  let out = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr) => stash(true, expr));
  out = out.replace(/\$([^\$\n]+?)\$/g, (_, expr) => stash(false, expr));
  return { text: out, blocks };
}

function reinsertMath(html, blocks) {
  return html.replace(/@@MATHBLOCK(\d+)@@/g, (match, i) => {
    const block = blocks[Number(i)];
    if (!block) return match;
    try {
      return katex.renderToString(block.latex, {
        throwOnError: false,
        displayMode: block.display,
        output: "html",
      });
    } catch (err) {
      return block.display ? `$$${block.latex}$$` : `$${block.latex}$`;
    }
  });
}

function renderMarkdown(text) {
  const normalized = text
    .replace(/\\\(/g, "$")
    .replace(/\\\)/g, "$")
    .replace(/\\\[/g, "$$")
    .replace(/\\\]/g, "$$");

  if (window.marked && window.katex && window.DOMPurify) {
    const { text: protectedText, blocks } = extractMath(normalized);
    let html = marked.parse(protectedText);
    html = reinsertMath(html, blocks);
    return DOMPurify.sanitize(html, {
      ADD_TAGS: ["svg", "path", "line", "rect"],
      ADD_ATTR: ["style", "viewBox", "preserveAspectRatio", "d", "fill", "stroke", "width", "height", "xmlns"],
    });
  }
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatTimestamp(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch (_) {
    return iso;
  }
}

function truncate(text, maxLen) {
  return text.length > maxLen ? text.slice(0, maxLen).trim() + "…" : text;
}

function renderTable() {
  const hideResolved = hideResolvedCheckbox.checked;
  const rows = hideResolved
    ? allInteractions.filter((item) => !item.resolved)
    : allInteractions;

  tableBody.innerHTML = "";

  if (rows.length === 0) {
    statusEl.hidden = false;
    statusEl.textContent = allInteractions.length === 0
      ? "No questions have been asked yet."
      : "No unresolved questions.";
    table.hidden = true;
    return;
  }

  statusEl.hidden = true;
  table.hidden = false;

  for (const item of rows) {
    const tr = document.createElement("tr");
    tr.className = item.resolved ? "is-resolved" : "";

    const statusTd = document.createElement("td");
    const toggle = document.createElement("button");
    toggle.className = "status-toggle" + (item.resolved ? " status-toggle--resolved" : "");
    toggle.textContent = item.resolved ? "Resolved" : "Unresolved";
    toggle.addEventListener("click", () => toggleResolved(item));
    statusTd.appendChild(toggle);

    const regTd = document.createElement("td");
    regTd.textContent = item.registration_no;

    const questionTd = document.createElement("td");
    questionTd.className = "admin-table__question";
    questionTd.textContent = truncate(item.question, 90);

    const answerTd = document.createElement("td");
    answerTd.className = "admin-table__question";
    answerTd.textContent = truncate(item.response, 90);

    const timeTd = document.createElement("td");
    timeTd.className = "admin-table__time";
    timeTd.textContent = formatTimestamp(item.timestamp);

    tr.append(statusTd, regTd, questionTd, answerTd, timeTd);
    tr.addEventListener("click", (event) => {
      // Don't open the modal when the click was on the status button.
      if (event.target === toggle) return;
      openModal(item);
    });
    tableBody.appendChild(tr);
  }
}

async function toggleResolved(item) {
  const newValue = !item.resolved;
  try {
    const response = await fetch(`/api/admin/interactions/${item.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resolved: newValue }),
    });
    if (!response.ok) throw new Error("Update failed");
    item.resolved = newValue;
    renderTable();
  } catch (err) {
    alert("Could not update status. Please try again.");
  }
}

function openModal(item) {
  modalMeta.textContent = `${item.registration_no} — ${formatTimestamp(item.timestamp)} — model: ${item.model_used}`;
  modalQuestion.textContent = item.question;
  modalAnswer.innerHTML = renderMarkdown(item.response);
  modal.hidden = false;
}

modalClose.addEventListener("click", () => {
  modal.hidden = true;
});
modal.addEventListener("click", (event) => {
  if (event.target === modal) modal.hidden = true;
});

async function loadInteractions() {
  statusEl.hidden = false;
  statusEl.textContent = "Loading interactions…";
  table.hidden = true;

  try {
    const response = await fetch("/api/admin/interactions");
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    allInteractions = await response.json();
    renderTable();
  } catch (err) {
    statusEl.hidden = false;
    statusEl.textContent = "Could not load interactions. Please refresh.";
    table.hidden = true;
  }
}

refreshBtn.addEventListener("click", loadInteractions);
hideResolvedCheckbox.addEventListener("change", renderTable);

loadInteractions();
