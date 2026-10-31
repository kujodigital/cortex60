// VeriPulse × Cortex60 — 100% Cloud-Ready Interactive Controller (No Terminal Required)

const state = {
  activeTab: "news",
  coreInsights: [],
  liveNewsInsights: [],
  selectedCoreIdx: 0,

  crucibleBank: {},
  selectedModality: "matrix",
  modalityLevelIdx: { matrix: 0, sequence: 0, cryptogram: 0, spatial: 0 },
  currentProblem: null,

  mentalModels: [],
  selectedModelIdx: 0,

  srsQueue: [],
  selectedSrsIdx: 0,
};

async function loadBootstrapData() {
  try {
    const res = await fetch("/api/bootstrap");
    if (res.ok) return await res.json();
  } catch (_) {}
  const res = await fetch("./api_bootstrap.json");
  return await res.json();
}

async function initApp() {
  const data = await loadBootstrapData();
  const allInsights = data.insights || [];

  // Separate live news stories from the 6 core foundational topics
  state.liveNewsInsights = allInsights.filter((item) => String(item.id).startsWith("live_"));
  state.coreInsights = allInsights.filter((item) => !String(item.id).startsWith("live_"));
  if (!state.coreInsights.length) state.coreInsights = allInsights;

  state.crucibleBank = data.static_crucible_bank || {};
  state.currentProblem =
    (state.crucibleBank.matrix && state.crucibleBank.matrix[1]) || data.initial_crucible;
  state.mentalModels = data.mental_models || [];
  state.srsQueue = data.srs_queue || [];

  bindMainTabs();
  renderLiveNewsTab();
  renderBlock1();
  bindBlock2();
  renderBlock2();
  renderBlock3();
  bindBlock4();
  renderBlock4();
  bindBiometrics();
}

// ============================================================================
// TOP 5-TAB NAVIGATION
// ============================================================================
function bindMainTabs() {
  const tabs = ["news", "block1", "block2", "block3", "block4"];
  document.querySelectorAll(".nav-step-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      state.activeTab = target;
      document.querySelectorAll(".nav-step-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      tabs.forEach((t) => {
        const el = document.getElementById(`view-${t}`);
        if (el) el.style.display = t === target ? "block" : "none";
      });
    });
  });
}

// ============================================================================
// TAB 1: TODAY'S LIVE VERIFIED NEWS (WHAT • HOW • WHY #1 • WHY #2 • WHY #3)
// ============================================================================
function renderLiveNewsTab() {
  const container = document.getElementById("live-news-container");
  const badge = document.getElementById("news-count-badge");
  const items = state.liveNewsInsights.length ? state.liveNewsInsights : state.coreInsights.slice(0, 3);

  badge.textContent = `${items.length} Verified Briefings`;
  container.innerHTML = items
    .map(
      (story, idx) => `
      <div style="background:var(--bg-elevated); border:1.5px solid var(--border-color); border-radius:12px; padding:20px; margin-bottom:18px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
          <span class="badge">📰 STORY #${idx + 1} • ${story.domain}</span>
          ${story.trust_score ? `<span class="badge" style="color:var(--accent-success);">✅ Trust: ${story.trust_score}/100</span>` : ""}
        </div>
        <h3 style="margin:0 0 12px 0; font-size:1.2rem;">${story.title.replace("[LIVE VERIFIED] ", "")}</h3>
        <div>${story.content_html}</div>
      </div>
    `
    )
    .join("");
}

// ============================================================================
// TAB 2: BLOCK 1 — DEEP KNOWLEDGE (6 CORE DOMAINS + INSTANT RECALL QUIZ)
// ============================================================================
function renderBlock1() {
  const pillsContainer = document.getElementById("b1-domain-pills");
  pillsContainer.innerHTML = "";
  state.coreInsights.forEach((item, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `pill-btn ${idx === state.selectedCoreIdx ? "active" : ""}`;
    btn.textContent = item.domain;
    btn.addEventListener("click", () => {
      state.selectedCoreIdx = idx;
      renderBlock1();
    });
    pillsContainer.appendChild(btn);
  });

  const concept = state.coreInsights[state.selectedCoreIdx];
  if (!concept) return;

  document.getElementById("b1-concept-title").textContent = concept.title;
  document.getElementById("b1-concept-meta").textContent = `Domain: ${concept.domain} • Cross-Disciplines: ${(concept.cross_disciplines || []).join(" ↔ ")}`;
  document.getElementById("b1-article-body").innerHTML = concept.content_html;

  const qContainer = document.getElementById("b1-questions-container");
  qContainer.innerHTML = "";

  concept.questions.forEach((q, qIdx) => {
    const qBox = document.createElement("div");
    qBox.style.cssText =
      "background:var(--bg-elevated); border:1.5px solid var(--border-color); border-radius:12px; padding:16px; margin-bottom:14px;";

    const headerHtml = `
      <div style="margin-bottom:6px;"><span class="badge">🎯 ${q.tier} Question #${qIdx + 1}</span></div>
      <div style="font-weight:800; font-size:0.98rem; margin-bottom:10px;">${q.question}</div>
    `;
    qBox.innerHTML = headerHtml;

    const optsWrap = document.createElement("div");
    const revealBox = document.createElement("div");
    revealBox.className = "answer-reveal-box";
    revealBox.style.display = "none";

    q.options.forEach((optText, oIdx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice-btn";
      btn.innerHTML = `<strong>${String.fromCharCode(65 + oIdx)}.</strong> ${optText}`;
      btn.addEventListener("click", () => {
        // Highlight right and wrong options immediately
        Array.from(optsWrap.children).forEach((child, cIdx) => {
          child.classList.remove("correct", "wrong");
          if (cIdx === q.correct_index) child.classList.add("correct");
          else if (cIdx === oIdx) child.classList.add("wrong");
        });
        const isRight = oIdx === q.correct_index;
        revealBox.style.display = "block";
        revealBox.innerHTML = `
          <div><strong>${isRight ? "✅ Correct!" : "❌ Not quite — Option " + String.fromCharCode(65 + q.correct_index) + " is the right answer."}</strong></div>
          <div style="margin-top:4px;"><strong>Why:</strong> ${q.explanation}</div>
        `;
      });
      optsWrap.appendChild(btn);
    });

    qBox.appendChild(optsWrap);
    qBox.appendChild(revealBox);
    qContainer.appendChild(qBox);
  });
}

// ============================================================================
// TAB 3: BLOCK 2 — FLUID IQ LOGIC PUZZLES (100% BROWSER INTERACTIVE)
// ============================================================================
function bindBlock2() {
  document.querySelectorAll("#b2-modality-pills .pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#b2-modality-pills .pill-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.selectedModality = btn.dataset.modality;
      selectCrucibleProblem(state.selectedModality, false);
    });
  });

  document.getElementById("b2-next-problem-btn").addEventListener("click", () => {
    selectCrucibleProblem(state.selectedModality, true);
  });
}

function selectCrucibleProblem(modality, advanceLevel = false) {
  const bank = state.crucibleBank[modality] || [];
  if (advanceLevel && bank.length) {
    state.modalityLevelIdx[modality] = ((state.modalityLevelIdx[modality] || 0) + 1) % bank.length;
  }
  const idx = state.modalityLevelIdx[modality] || 0;
  if (bank[idx]) {
    state.currentProblem = bank[idx];
  }
  document.getElementById("b2-feedback").style.display = "none";
  renderBlock2();
}

function renderBlock2() {
  const p = state.currentProblem;
  if (!p) return;

  document.getElementById("b2-difficulty-badge").textContent = `Difficulty Level ${p.difficulty} / 5`;
  document.getElementById("b2-problem-type-label").textContent = p.puzzle_type_label;
  document.getElementById("b2-problem-prompt").textContent = p.prompt;

  const stim = document.getElementById("b2-visual-stimulus");
  stim.innerHTML = "";

  if (p.puzzle_type === "matrix" && p.grid_svgs) {
    const grid = document.createElement("div");
    grid.className = "matrix-grid";
    p.grid_svgs.forEach((row) => {
      row.forEach((cellSvg) => {
        const cell = document.createElement("div");
        if (cellSvg === null) {
          cell.className = "matrix-cell missing";
          cell.textContent = "?";
        } else {
          cell.className = "matrix-cell";
          cell.innerHTML = cellSvg;
        }
        grid.appendChild(cell);
      });
    });
    stim.appendChild(grid);
  } else if (p.puzzle_type === "spatial" && p.reference_svg) {
    stim.innerHTML = `
      <div style="display:flex; flex-direction:column; align-items:center; margin:12px 0;">
        <span style="font-size:0.78rem; font-weight:700; color:var(--text-secondary); margin-bottom:6px;">REFERENCE SHAPE TO ROTATE:</span>
        <div class="matrix-cell" style="width:104px; height:104px;">${p.reference_svg}</div>
      </div>
    `;
  }

  const optsContainer = document.getElementById("b2-options-container");
  optsContainer.innerHTML = "";

  if (p.options_are_svg) {
    const grid = document.createElement("div");
    grid.className = "svg-options-grid";
    p.options.forEach((svgStr, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "svg-choice-btn";
      btn.innerHTML = `<span style="font-size:0.8rem; font-weight:800;">Option ${String.fromCharCode(65 + idx)}</span>${svgStr}`;
      btn.addEventListener("click", () => revealCrucibleAnswer(idx, grid));
      grid.appendChild(btn);
    });
    optsContainer.appendChild(grid);
  } else {
    const listWrap = document.createElement("div");
    p.options.forEach((optText, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice-btn";
      btn.innerHTML = `<strong>Option ${String.fromCharCode(65 + idx)}:</strong> ${optText}`;
      btn.addEventListener("click", () => revealCrucibleAnswer(idx, listWrap));
      listWrap.appendChild(btn);
    });
    optsContainer.appendChild(listWrap);
  }
}

function revealCrucibleAnswer(chosenIdx, parentEl) {
  const p = state.currentProblem;
  const isRight = chosenIdx === p.correct_index;
  Array.from(parentEl.children).forEach((btn, idx) => {
    btn.classList.remove("correct", "wrong");
    if (idx === p.correct_index) btn.classList.add("correct");
    else if (idx === chosenIdx) btn.classList.add("wrong");
  });

  const fb = document.getElementById("b2-feedback");
  fb.style.display = "block";
  fb.innerHTML = `
    <div><strong>${isRight ? "✅ Spot On!" : "❌ Option " + String.fromCharCode(65 + p.correct_index) + " is the correct answer."}</strong></div>
    <div style="margin-top:4px;"><strong>Solution Rule:</strong> ${p.explanation}</div>
  `;
}

// ============================================================================
// TAB 4: BLOCK 3 — MENTAL MODELS (INTERACTIVE CASE STUDIES)
// ============================================================================
function renderBlock3() {
  const pills = document.getElementById("b3-model-pills");
  pills.innerHTML = "";
  state.mentalModels.forEach((m, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `pill-btn ${idx === state.selectedModelIdx ? "active" : ""}`;
    btn.textContent = m.name;
    btn.addEventListener("click", () => {
      state.selectedModelIdx = idx;
      renderBlock3();
    });
    pills.appendChild(btn);
  });

  const model = state.mentalModels[state.selectedModelIdx];
  if (!model) return;
  const cs = model.case_study;

  document.getElementById("b3-model-name").textContent = `${model.name} (${model.category})`;
  document.getElementById("b3-model-summary").textContent = model.summary;
  document.getElementById("b3-model-steps").innerHTML = model.steps.map((s) => `<div>${s}</div>`).join("");

  document.getElementById("b3-case-title").textContent = cs.title;
  document.getElementById("b3-case-scenario").textContent = cs.scenario;

  renderInteractiveQuestionBlock(
    document.getElementById("b3-fallacy-block"),
    "Step 1: Spot the Cognitive Trap / Fallacy",
    cs.fallacy_question,
    cs.fallacy_options,
    cs.fallacy_correct,
    `Correct! Identifying this trap prevents reasoning by false analogy or static assumptions.`
  );

  renderInteractiveQuestionBlock(
    document.getElementById("b3-application-block"),
    `Step 2: Apply '${model.name}' to Solve the Scenario`,
    cs.application_question,
    cs.application_options,
    cs.application_correct,
    `Optimal strategy under ${model.name}: ${model.summary}`
  );
}

function renderInteractiveQuestionBlock(container, badgeText, questionText, options, correctIdx, explanationText) {
  container.innerHTML = `
    <div style="margin-bottom:6px;"><span class="badge">${badgeText}</span></div>
    <div style="font-weight:800; font-size:0.96rem; margin-bottom:8px;">${questionText}</div>
  `;
  const optsWrap = document.createElement("div");
  const revealBox = document.createElement("div");
  revealBox.className = "answer-reveal-box";
  revealBox.style.display = "none";

  options.forEach((optText, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "choice-btn";
    btn.innerHTML = `<strong>${String.fromCharCode(65 + idx)}.</strong> ${optText}`;
    btn.addEventListener("click", () => {
      Array.from(optsWrap.children).forEach((child, cIdx) => {
        child.classList.remove("correct", "wrong");
        if (cIdx === correctIdx) child.classList.add("correct");
        else if (cIdx === idx) child.classList.add("wrong");
      });
      const isRight = idx === correctIdx;
      revealBox.style.display = "block";
      revealBox.innerHTML = `
        <div><strong>${isRight ? "✅ Correct!" : "❌ Option " + String.fromCharCode(65 + correctIdx) + " is the optimal choice."}</strong></div>
        <div style="margin-top:4px;">${explanationText}</div>
      `;
    });
    optsWrap.appendChild(btn);
  });

  container.appendChild(optsWrap);
  container.appendChild(revealBox);
}

// ============================================================================
// TAB 5: BLOCK 4 — FLASHCARDS & DAILY HEALTH CHECK-IN
// ============================================================================
function bindBlock4() {
  document.getElementById("b4-next-card-btn").addEventListener("click", () => {
    if (!state.srsQueue.length) return;
    state.selectedSrsIdx = (state.selectedSrsIdx + 1) % state.srsQueue.length;
    document.getElementById("b4-feedback").style.display = "none";
    renderBlock4();
  });
}

function renderBlock4() {
  const pills = document.getElementById("b4-queue-pills");
  pills.innerHTML = "";
  if (!state.srsQueue.length) return;

  state.srsQueue.forEach((card, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `pill-btn ${idx === state.selectedSrsIdx ? "active" : ""}`;
    btn.textContent = `${idx + 1}. ${card.domain_or_model}`;
    btn.addEventListener("click", () => {
      state.selectedSrsIdx = idx;
      document.getElementById("b4-feedback").style.display = "none";
      renderBlock4();
    });
    pills.appendChild(btn);
  });

  const card = state.srsQueue[state.selectedSrsIdx];
  document.getElementById("b4-card-source").textContent = `CARD #${state.selectedSrsIdx + 1} • ${card.domain_or_model} (${card.tier})`;
  document.getElementById("b4-card-question").textContent = card.question;

  const opts = document.getElementById("b4-card-options");
  opts.innerHTML = "";
  card.options.forEach((optText, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "choice-btn";
    btn.innerHTML = `<strong>${String.fromCharCode(65 + idx)}.</strong> ${optText}`;
    btn.addEventListener("click", () => {
      Array.from(opts.children).forEach((child, cIdx) => {
        child.classList.remove("correct", "wrong");
        if (cIdx === card.correct_index) child.classList.add("correct");
        else if (cIdx === idx) child.classList.add("wrong");
      });
      const isRight = idx === card.correct_index;
      const fb = document.getElementById("b4-feedback");
      fb.style.display = "block";
      fb.innerHTML = `
        <div><strong>${isRight ? "✅ Active Recall Verified!" : "❌ Option " + String.fromCharCode(65 + card.correct_index) + " is the correct answer."}</strong></div>
        <div style="margin-top:4px;"><strong>Explanation:</strong> ${card.explanation}</div>
      `;
    });
    opts.appendChild(btn);
  });
}

function bindBiometrics() {
  const sleepEl = document.getElementById("switch-sleep");
  const actEl = document.getElementById("switch-activity");
  const nutEl = document.getElementById("switch-nutrition");

  const updateBioScore = () => {
    const count = (sleepEl.checked ? 1 : 0) + (actEl.checked ? 1 : 0) + (nutEl.checked ? 1 : 0);
    // Past 6 days had 13/18 checks; add today's count out of 21 total
    const pct = Math.round(((13 + count) / 21) * 100);
    const badge = document.getElementById("bio-compliance-badge");
    const msg = document.getElementById("bio-status-msg");

    if (pct >= 70) {
      badge.textContent = `✅ ${pct}% Rolling 7-Day (Optimal)`;
      msg.style.color = "var(--accent-success)";
      msg.textContent = `✅ Biological Prerequisites Optimal (${pct}% ≥ 70%): Sleep, exercise, and nutrition are supporting focus and memory retention.`;
    } else {
      badge.textContent = `🚨 ${pct}% Rolling 7-Day (<70%)`;
      msg.style.color = "var(--accent-danger)";
      msg.textContent = `🚨 Biological Bottleneck Warning (${pct}% < 70%): Turn on today's switches once you complete sleep, cardio, and hydration!`;
    }
  };

  sleepEl.addEventListener("change", updateBioScore);
  actEl.addEventListener("change", updateBioScore);
  nutEl.addEventListener("change", updateBioScore);
  updateBioScore();
}

initApp();
