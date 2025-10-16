const form = document.getElementById("upload-form");
const resultsDiv = document.getElementById("results");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("file");
  if (!fileInput.files.length) return;

  const fd = new FormData();
  fd.append("file", fileInput.files[0]);
  resultsDiv.innerHTML = "Processing...";

  try {
    const res = await fetch("/preview", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Upload failed");

    renderTable(data.headers, data.rows);
  } catch (err) {
    resultsDiv.textContent = err.message;
  }
});

function renderTable(headers, rows) {
  if (!headers || headers.length === 0) {
    resultsDiv.innerHTML = "<p>No data found.</p>";
    return;
  }

  const headHtml = `<tr>${headers.map(h => `<th class="resizable">${escapeHtml(h)}<span class="col-resizer" data-col="${escapeHtml(h)}"></span></th>`).join("")}</tr>`;
  const bodyHtml = rows.map(r => `<tr>${headers.map((_, i) => `<td>${escapeHtml(r[i] ?? '')}</td>`).join("")}</tr>`).join("");

  resultsDiv.innerHTML = `
    <div class="table-container">
      <div class="table-wrapper">
        <table class="results-table">
          <thead>${headHtml}</thead>
          <tbody>${bodyHtml}</tbody>
        </table>
      </div>
    </div>
  `;

  enableColumnResize();
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function enableColumnResize() {
  const table = resultsDiv.querySelector("table.results-table");
  if (!table) return;
  const headers = table.querySelectorAll("th.resizable");
  let startX = 0;
  let startWidth = 0;
  let currentTh = null;

  headers.forEach(th => {
    const resizer = th.querySelector('.col-resizer');
    if (!resizer) return;
    th.style.position = 'relative';
    resizer.addEventListener('mousedown', (e) => {
      startX = e.pageX;
      currentTh = th;
      startWidth = currentTh.offsetWidth;
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp, { once: true });
      e.preventDefault();
    });
  });

  function onMouseMove(e) {
    if (!currentTh) return;
    const delta = e.pageX - startX;
    const newWidth = Math.max(60, startWidth + delta);
    currentTh.style.width = newWidth + 'px';
  }

  function onMouseUp() {
    document.removeEventListener('mousemove', onMouseMove);
    currentTh = null;
  }
}
