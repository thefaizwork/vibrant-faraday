// Multi-Agent Web Design Dashboard Client
let currentRunState = null;
let currentCodeType = "html";
let currentCodeCache = { html: "", css: "", js: "", react: "", backend: "" };

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initViewportControls();
  initFormHandler();
  initCodeTabs();
  initCopyButton();
  loadRecentRuns();
});

function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      const target = btn.getAttribute("data-tab");
      const targetContent = document.getElementById(`tab-${target}`);
      if (targetContent) targetContent.classList.add("active");
    });
  });
}

function initViewportControls() {
  const viewBtns = document.querySelectorAll(".view-btn[data-width]");
  const frame = document.getElementById("preview-frame");
  viewBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      viewBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      frame.style.width = btn.getAttribute("data-width");
    });
  });
}

function initCodeTabs() {
  const codeTabs = document.querySelectorAll(".code-tab-btn");
  codeTabs.forEach(btn => {
    btn.addEventListener("click", () => {
      codeTabs.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentCodeType = btn.getAttribute("data-code");
      renderCode();
    });
  });
}

function initCopyButton() {
  const copyBtn = document.getElementById("copy-code-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const codeContent = document.getElementById("code-content");
      if (codeContent && codeContent.textContent) {
        navigator.clipboard.writeText(codeContent.textContent).then(() => {
          const original = copyBtn.textContent;
          copyBtn.textContent = "✅ Copied!";
          setTimeout(() => { copyBtn.textContent = original; }, 2000);
        });
      }
    });
  }
}

function initFormHandler() {
  const form = document.getElementById("generate-form");
  const genBtn = document.getElementById("generate-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = document.getElementById("prompt-input").value.trim();
    const mode = document.getElementById("mode-select").value;
    const framework = document.getElementById("framework-select") ? document.getElementById("framework-select").value : "vanilla_gsap_lenis";
    const animation = document.getElementById("animation-select") ? document.getElementById("animation-select").value : "gsap_lenis";
    const maxIters = parseInt(document.getElementById("max-iters").value, 10);
    const qualityThresh = parseFloat(document.getElementById("quality-thresh").value);

    const ablated = [];
    document.querySelectorAll(".ablate-chk:checked").forEach(chk => {
      ablated.push(chk.value);
    });

    genBtn.disabled = true;
    genBtn.innerHTML = `<span>⏳ Running Multi-Agent Loop...</span>`;
    updateStatus("in_progress", "Generating...");

    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt,
          system_mode: mode,
          framework: framework,
          animation_stack: animation,
          ablated_agents: ablated,
          max_iterations: maxIters,
          quality_threshold: qualityThresh
        })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}: ${await resp.text()}`);
      }

      const data = await resp.json();
      await loadRunState(data.run_id);
      loadRecentRuns();
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
      updateStatus("failed", "Error");
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = `<span>🚀 Launch Multi-Agent Loop</span>`;
    }
  });
}

async function loadRunState(runId) {
  try {
    const resp = await fetch(`/api/run/${runId}`);
    if (!resp.ok) return;
    currentRunState = await resp.json();
    renderRunState();
  } catch (e) {
    console.error("Error loading run state:", e);
  }
}

function renderRunState() {
  if (!currentRunState) return;

  document.getElementById("current-run-id").textContent = currentRunState.run_id;
  updateStatus(currentRunState.status, currentRunState.status);

  // Metrics quickbar
  const ev = currentRunState.evaluation || {};
  document.getElementById("metric-composite").textContent = ev.composite_score !== undefined ? ev.composite_score.toFixed(1) : "--";
  document.getElementById("metric-aesthetic").textContent = ev.aesthetic_score !== undefined && ev.aesthetic_score !== null ? ev.aesthetic_score.toFixed(1) : "--";
  document.getElementById("metric-accessibility").textContent = ev.accessibility_score !== undefined && ev.accessibility_score !== null ? ev.accessibility_score.toFixed(1) : "--";
  document.getElementById("metric-usability").textContent = ev.usability_score !== undefined && ev.usability_score !== null ? ev.usability_score.toFixed(1) : "--";
  document.getElementById("metric-ethics").textContent = ev.ethics_score !== undefined && ev.ethics_score !== null ? ev.ethics_score.toFixed(1) : "--";
  document.getElementById("metric-originality").textContent = ev.originality_score !== undefined && ev.originality_score !== null ? ev.originality_score.toFixed(1) : "--";

  // Build Iteration Selector
  const iterContainer = document.getElementById("iteration-selector");
  iterContainer.innerHTML = "";

  const finalBtn = document.createElement("button");
  finalBtn.className = "iter-btn active";
  finalBtn.textContent = `Final (v${currentRunState.current_iteration})`;
  finalBtn.onclick = () => setPreviewIteration("final");
  iterContainer.appendChild(finalBtn);

  (currentRunState.history || []).forEach((it, idx) => {
    const btn = document.createElement("button");
    btn.className = "iter-btn";
    btn.textContent = `Iter ${it.iteration_number}`;
    btn.onclick = () => setPreviewIteration(it.iteration_number);
    iterContainer.appendChild(btn);
  });

  setPreviewIteration("final");
  renderCritiques();
  renderPlan();
}

function setPreviewIteration(target) {
  if (!currentRunState) return;

  const frame = document.getElementById("preview-frame");
  const popout = document.getElementById("popout-link");
  const previewUrl = `/api/preview/${currentRunState.run_id}/${target}`;
  frame.src = previewUrl;
  popout.href = previewUrl;

  // Fetch website code
  const itNum = target === "final" ? null : target;
  const url = itNum ? `/api/run/${currentRunState.run_id}/website?iteration=${itNum}` : `/api/run/${currentRunState.run_id}/website`;
  fetch(url)
    .then(r => r.json())
    .then(data => {
      currentCodeCache.html = data.html || "";
      currentCodeCache.css = data.css || "";
      currentCodeCache.js = data.javascript || "";
      currentCodeCache.react = data.react_code || "// React code generated in full Next.js project";
      currentCodeCache.backend = data.backend_schema || "// Backend schema & API integration contract";
      renderCode();
    });
}

function renderCode() {
  const codeContent = document.getElementById("code-content");
  if (currentCodeType === "html") {
    codeContent.textContent = currentCodeCache.html || "<!-- No HTML available -->";
  } else if (currentCodeType === "css") {
    codeContent.textContent = currentCodeCache.css || "/* No CSS available */";
  } else if (currentCodeType === "js") {
    codeContent.textContent = currentCodeCache.js || "// No JS available";
  } else if (currentCodeType === "react") {
    codeContent.textContent = currentCodeCache.react || "// No React TSX available";
  } else if (currentCodeType === "backend") {
    codeContent.textContent = currentCodeCache.backend || "// No Backend schema available";
  }
}

function renderCritiques() {
  const container = document.getElementById("critiques-container");
  container.innerHTML = "";

  const results = currentRunState.agent_results || {};
  if (Object.keys(results).length === 0) {
    container.innerHTML = `<div class="empty-state">No specialist critiques available for this mode.</div>`;
    return;
  }

  for (const [agentName, crit] of Object.entries(results)) {
    const card = document.createElement("div");
    card.className = "critique-card";

    const issues = crit.issues || crit.wcag_issues || crit.dark_patterns_detected || [];
    const recs = crit.recommendations || [];

    card.innerHTML = `
      <div class="critique-header">
        <span class="critique-title">${formatAgentName(agentName)}</span>
        <span class="critique-score">${crit.score !== undefined ? crit.score.toFixed(1) : '--'}/10</span>
      </div>
      <div style="font-size:0.8rem; font-weight:600; color:var(--accent-amber); margin-bottom:0.3rem;">Issues Identified (${issues.length}):</div>
      <ul class="critique-list">
        ${issues.length > 0 ? issues.map(i => `<li>${i}</li>`).join("") : "<li>None &mdash; Exceeds benchmark standards.</li>"}
      </ul>
      <div style="font-size:0.8rem; font-weight:600; color:var(--accent-green); margin-bottom:0.3rem;">Recommendations:</div>
      <ul class="critique-list">
        ${recs.length > 0 ? recs.map(r => `<li>${r}</li>`).join("") : "<li>Maintain current structure.</li>"}
      </ul>
    `;
    container.appendChild(card);
  }
}

function renderPlan() {
  const container = document.getElementById("plan-container");
  const agg = currentRunState.aggregate_feedback;
  const history = currentRunState.history || [];
  const latestRefinement = history.length > 0 ? history[history.length - 1].refinement : null;

  if (!agg) {
    container.innerHTML = `<div class="empty-state">No aggregation plan recorded.</div>`;
    return;
  }

  container.innerHTML = `
    <div class="card" style="margin-bottom:1rem;">
      <h3 style="color:var(--accent-cyan); font-size:1rem; margin-bottom:0.5rem;">🎯 Refinement Strategy</h3>
      <p style="font-size:0.88rem; color:var(--text-main); margin-bottom:1rem;">${agg.refinement_strategy || 'Iterative quality improvement.'}</p>
      
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
        <div>
          <h4 style="color:var(--accent-amber); font-size:0.85rem; margin-bottom:0.4rem;">Priority Items (${(agg.priority_issues || []).length})</h4>
          <ul class="critique-list">
            ${(agg.priority_issues || []).map(p => `<li>${p}</li>`).join("")}
          </ul>
        </div>
        <div>
          <h4 style="color:var(--accent-green); font-size:0.85rem; margin-bottom:0.4rem;">Preserve Directives</h4>
          <ul class="critique-list">
            ${(agg.preserve || []).map(p => `<li>${p}</li>`).join("")}
          </ul>
        </div>
      </div>
    </div>

    ${latestRefinement ? `
    <div class="card">
      <h3 style="color:var(--primary); font-size:1rem; margin-bottom:0.5rem;">🔧 Refinement Change Log</h3>
      <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">${latestRefinement.change_summary}</p>
      <div style="display:flex; flex-direction:column; gap:0.5rem;">
        ${(latestRefinement.issue_mappings || []).map(m => `
          <div style="background:var(--bg-dark); padding:0.6rem; border-radius:6px; border:1px solid var(--border-color); font-size:0.82rem;">
            <div style="font-weight:600; color:var(--accent-amber); margin-bottom:0.2rem;">Issue: ${m.issue}</div>
            <div style="color:var(--text-main);">Action: ${m.action_taken}</div>
            <div style="color:var(--text-muted); font-size:0.75rem; margin-top:0.2rem;">Modified: ${m.files_modified.join(', ')}</div>
          </div>
        `).join("")}
      </div>
    </div>
    ` : ''}
  `;
}

async function loadRecentRuns() {
  try {
    const resp = await fetch("/api/runs?limit=10");
    if (!resp.ok) return;
    const runs = await resp.json();
    const list = document.getElementById("runs-list");
    if (runs.length === 0) {
      list.innerHTML = `<div class="empty-state">No historical runs yet.</div>`;
      return;
    }
    list.innerHTML = "";
    runs.forEach(r => {
      const item = document.createElement("div");
      item.className = "run-item";
      item.onclick = () => loadRunState(r.run_id);
      item.innerHTML = `
        <div class="run-item-top">
          <span>${r.run_id}</span>
          <span style="color:var(--accent-cyan);">${r.composite_score !== null ? r.composite_score.toFixed(1) : '--'}</span>
        </div>
        <div class="run-item-mode">${r.system_mode} &bull; iters: ${r.current_iteration}</div>
      `;
      list.appendChild(item);
    });
  } catch (e) {
    console.error("Error loading recent runs:", e);
  }
}

function updateStatus(status, label) {
  const badge = document.getElementById("run-status-badge");
  badge.className = `run-status-badge ${status}`;
  badge.textContent = label;
}

function formatAgentName(name) {
  return name.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}
