// ===========================================================
// Pathshala AI - frontend orchestration
// ===========================================================

const state = {
  plan: null,
  segments: [],
  currentIndex: 0,
  quizQuestions: [],
  quizIndex: 0,
  quizAnswers: [],
};

const el = (id) => document.getElementById(id);

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json();
  if (!res.ok || data.ok === false) {
    throw new Error(data.error || "Something went wrong. Please try again.");
  }
  return data;
}

// ---------------- Honest AI status ----------------
async function checkStatus() {
  const pill = el("statusPill");
  const text = el("statusText");
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.local_mode) {
      pill.className = "status-pill offline";
      text.textContent = data.has_key
        ? "AI engine offline — key found but failed to load"
        : "AI engine offline — no GROQ_API_KEY in .env";
    } else if (data.last_error) {
      pill.className = "status-pill error";
      text.innerHTML = `AI request failed: ${escapeHtml(data.last_error)} <button id="statusRetry">Recheck</button>`;
      const btn = document.getElementById("statusRetry");
      if (btn) btn.addEventListener("click", checkStatus);
    } else {
      pill.className = "status-pill live";
      text.textContent = `AI engine live (${data.model})`;
    }
  } catch (err) {
    pill.className = "status-pill error";
    text.textContent = "Could not reach the server.";
  }
}
checkStatus();

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

// ---------------- Upload ----------------
el("fileInput").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const status = el("uploadStatus");
  status.textContent = "Reading your material…";
  status.style.color = "var(--teal)";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok || data.ok === false) throw new Error(data.error || "Upload failed");
    status.textContent = `Indexed "${data.filename}" — ${data.chunks_indexed} sections ready for grounded teaching.`;
    status.style.color = "var(--teal)";
  } catch (err) {
    status.textContent = err.message;
    status.style.color = "var(--coral)";
  }
});

// ---------------- Create lesson ----------------
el("setupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = el("startBtn");
  const errBox = el("setupError");
  errBox.textContent = "";
  btn.disabled = true;
  btn.textContent = "Planning your lesson…";

  try {
    const payload = {
      topic: el("topic").value.trim(),
      level: el("level").value,
      minutes: el("minutes").value,
      language: el("language").value,
      style: el("style").value,
    };
    const data = await postJSON("/api/create_lesson", payload);
    state.plan = data.plan;
    state.segments = data.plan.segments || [];
    state.currentIndex = 0;

    el("lessonTitle").textContent = data.plan.title || payload.topic;
    el("tutorThread").innerHTML = "";
    if (data.engine === "fallback") {
      addBubble("tutor", `I'm teaching this in offline mode right now (no live AI response), so the lesson below uses a basic template rather than a fully generated one. Check the status pill at the top for why.`, "incorrect");
    }
    el("setup").classList.add("hidden");
    el("lessonStage").classList.remove("hidden");
    await loadSegment(0);
  } catch (err) {
    errBox.textContent = err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = "Start the lesson";
  }
});

// ---------------- Tutor conversation thread ----------------
function addBubble(who, html, extraClass) {
  const thread = el("tutorThread");
  const wrap = document.createElement("div");
  wrap.className = `msg ${who}${extraClass ? " " + extraClass : ""}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = who === "tutor" ? "AI" : "Me";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = html;
  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  thread.appendChild(wrap);
  thread.scrollTop = thread.scrollHeight;
  return bubble;
}

// ---------------- Segment playback ----------------
async function loadSegment(idx) {
  state.currentIndex = idx;
  const total = state.segments.length;

  el("videoLoading").classList.remove("hidden");
  el("lessonVideo").classList.add("hidden");
  el("mediaWarning").classList.add("hidden");
  el("audioFallback").classList.add("hidden");
  el("visualNote").classList.add("hidden");
  el("checkpointComposer").classList.add("hidden");
  el("nextSegmentBtn").classList.add("hidden");
  el("goToQuizBtn").classList.add("hidden");
  el("checkpointAnswer").value = "";
  el("segmentCounter").textContent = `Segment ${idx + 1} of ${total}`;
  el("progressFill").style.width = `${Math.round((idx / total) * 100)}%`;

  try {
    const data = await postJSON("/api/segment_media", { segment_index: idx });
    el("videoLoading").classList.add("hidden");

    if (data.video_url) {
      const video = el("lessonVideo");
      video.src = data.video_url;
      video.controls = true;
      video.classList.remove("hidden");
      video.play().catch(() => {
        // Autoplay was blocked - that's normal browser behaviour, not a bug.
        // The visible controls let the student press play themselves.
      });
    } else if (data.audio_url) {
      el("audioFallback").classList.remove("hidden");
      const audio = el("fallbackAudio");
      audio.src = data.audio_url;
    }

    if (data.media_warning) {
      el("mediaWarning").textContent = `⚠ ${data.media_warning}`;
      el("mediaWarning").classList.remove("hidden");
    }

    if (data.visual_type && data.visual_type !== "none") {
      el("visualTag").textContent = data.visual_type.toUpperCase();
      el("visualHintText").textContent = data.visual_hint || "";
      el("visualNote").classList.remove("hidden");
    }

    addBubble("tutor", `<strong>${escapeHtml(data.heading || "")}</strong><br>${escapeHtml(data.explanation || "")}${data.example ? `<br><br><em>Example:</em> ${escapeHtml(data.example)}` : ""}`);

    el("segmentCounter").textContent = `Segment ${data.segment_number} of ${data.total_segments}`;
    el("progressFill").style.width = `${Math.round((data.segment_number / data.total_segments) * 100)}%`;

    if (data.checkpoint_question) {
      addBubble("tutor", escapeHtml(data.checkpoint_question));
      el("checkpointComposer").classList.remove("hidden");
      el("checkpointComposer").dataset.lastSegment = data.is_last_segment ? "1" : "0";
    } else if (data.is_last_segment) {
      el("goToQuizBtn").classList.remove("hidden");
    } else {
      el("nextSegmentBtn").classList.remove("hidden");
    }
  } catch (err) {
    el("videoLoading").classList.add("hidden");
    addBubble("tutor", `⚠ Could not load this segment: ${escapeHtml(err.message)}`, "incorrect");
    const retryWrap = document.createElement("div");
    retryWrap.style.marginTop = "8px";
    const retryBtn = document.createElement("button");
    retryBtn.className = "btn-retry";
    retryBtn.textContent = "Retry this segment";
    retryBtn.addEventListener("click", () => loadSegment(idx));
    retryWrap.appendChild(retryBtn);
    el("tutorThread").appendChild(retryWrap);
  }
}

el("submitCheckpoint").addEventListener("click", async () => {
  const answer = el("checkpointAnswer").value.trim();
  if (!answer) return;
  const btn = el("submitCheckpoint");
  btn.disabled = true;
  btn.textContent = "Checking…";

  addBubble("student", escapeHtml(answer));

  try {
    const data = await postJSON("/api/checkpoint", {
      segment_index: state.currentIndex,
      answer,
    });
    addBubble(
      "tutor",
      `<strong>${data.is_correct ? "Nicely done." : "Not quite."}</strong> ${escapeHtml(data.feedback || "")}${!data.is_correct && data.re_explanation ? `<br><br>${escapeHtml(data.re_explanation)}` : ""}`,
      data.is_correct ? "correct" : "incorrect"
    );

    el("checkpointComposer").classList.add("hidden");
    el("checkpointAnswer").value = "";

    const isLast = el("checkpointComposer").dataset.lastSegment === "1";
    if (isLast) {
      el("goToQuizBtn").classList.remove("hidden");
    } else {
      el("nextSegmentBtn").classList.remove("hidden");
    }
  } catch (err) {
    addBubble("tutor", `⚠ ${escapeHtml(err.message)}`, "incorrect");
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit answer";
  }
});

el("nextSegmentBtn").addEventListener("click", () => {
  loadSegment(state.currentIndex + 1);
});

// ---------------- Follow-up questions ----------------
el("followupBtn").addEventListener("click", async () => {
  const input = el("followupInput");
  const question = input.value.trim();
  if (!question) return;
  input.value = "";

  addBubble("student", escapeHtml(question));
  const thinking = addBubble("tutor", "Thinking…");

  try {
    const data = await postJSON("/api/followup", { question });
    thinking.textContent = data.answer;
  } catch (err) {
    thinking.innerHTML = `⚠ ${escapeHtml(err.message)}`;
    thinking.parentElement.classList.add("incorrect");
  }
});
el("followupInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { e.preventDefault(); el("followupBtn").click(); }
});

// ---------------- Quiz (one question at a time) ----------------
el("goToQuizBtn").addEventListener("click", async () => {
  try {
    const res = await fetch("/api/final_quiz");
    const data = await res.json();
    if (!res.ok || data.ok === false) throw new Error(data.error || "Could not load quiz");
    state.quizQuestions = data.questions || [];
    state.quizIndex = 0;
    state.quizAnswers = state.quizQuestions.map(() => "");
    renderQuizQuestion();
    el("lessonStage").classList.add("hidden");
    el("quizStage").classList.remove("hidden");
  } catch (err) {
    addBubble("tutor", `⚠ Could not load the assessment: ${escapeHtml(err.message)}`, "incorrect");
  }
});

function renderQuizQuestion() {
  const total = state.quizQuestions.length;
  const i = state.quizIndex;
  const q = state.quizQuestions[i];

  el("quizProgressText").textContent = `Question ${i + 1} of ${total}`;
  el("quizProgressFill").style.width = `${Math.round((i / total) * 100)}%`;

  const card = el("quizCard");
  card.innerHTML = "";
  const p = document.createElement("p");
  p.className = "q";
  p.textContent = q.question;
  card.appendChild(p);

  if (q.type === "mcq" && Array.isArray(q.options) && q.options.length) {
    const wrap = document.createElement("div");
    wrap.className = "quiz-options";
    q.options.forEach((opt) => {
      const label = document.createElement("label");
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = `quizq`;
      radio.value = opt;
      radio.checked = state.quizAnswers[i] === opt;
      radio.addEventListener("change", () => { state.quizAnswers[i] = opt; });
      label.appendChild(radio);
      label.append(opt);
      wrap.appendChild(label);
    });
    card.appendChild(wrap);
  } else {
    const textarea = document.createElement("textarea");
    textarea.style.width = "100%";
    textarea.style.minHeight = "110px";
    textarea.style.background = "var(--surface-2)";
    textarea.style.border = "1px solid var(--border)";
    textarea.style.borderRadius = "9px";
    textarea.style.color = "var(--text)";
    textarea.style.padding = "12px";
    textarea.style.fontFamily = "inherit";
    textarea.placeholder = "Your answer…";
    textarea.value = state.quizAnswers[i] || "";
    textarea.addEventListener("input", () => { state.quizAnswers[i] = textarea.value; });
    card.appendChild(textarea);
  }

  el("quizPrevBtn").style.visibility = i === 0 ? "hidden" : "visible";
  const isLast = i === total - 1;
  el("quizNextBtn").classList.toggle("hidden", isLast);
  el("submitQuizBtn").classList.toggle("hidden", !isLast);
}

el("quizPrevBtn").addEventListener("click", () => {
  if (state.quizIndex > 0) { state.quizIndex--; renderQuizQuestion(); }
});
el("quizNextBtn").addEventListener("click", () => {
  if (state.quizIndex < state.quizQuestions.length - 1) { state.quizIndex++; renderQuizQuestion(); }
});

el("submitQuizBtn").addEventListener("click", async () => {
  const btn = el("submitQuizBtn");
  btn.disabled = true;
  btn.textContent = "Grading…";

  try {
    const answers = state.quizQuestions.map((q, i) => ({
      question: q.question,
      type: q.type,
      correct_answer: q.correct_answer,
      student_answer: state.quizAnswers[i] || "",
    }));

    const data = await postJSON("/api/submit_quiz", { answers });
    el("quizStage").classList.add("hidden");
    el("reportStage").classList.remove("hidden");
    renderReport(data.report);
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit assessment";
  }
});

// ---------------- Report dashboard (real charts, real data) ----------------
let scoreDonutChart = null;
let historyBarChart = null;

function renderReport(report) {
  el("reportTopic").textContent = report.topic;
  el("scoreValue").textContent = `${report.score_percent}%`;
  el("reportCounts").textContent = `${report.correct} correct out of ${report.total} questions`;

  el("strongAreas").innerHTML = (report.strong_areas || [])
    .map((s) => `<span class="tag strong">${escapeHtml(s)}</span>`).join("") || `<span class="tag strong">—</span>`;
  el("weakAreas").innerHTML = (report.weak_areas || [])
    .map((s) => `<span class="tag weak">${escapeHtml(s)}</span>`).join("") || `<span class="tag weak">—</span>`;
  el("recommendation").textContent = report.recommendation || "";

  if (typeof Chart === "undefined") {
    console.warn("Chart.js load nahi hua - charts skip, baaki report dikh raha hai.");
    return;
  }

  try {
    const style = getComputedStyle(document.body);
    const amber = style.getPropertyValue("--amber").trim() || "#f2a93b";
    const teal = style.getPropertyValue("--teal").trim() || "#35d6ab";
    const coral = style.getPropertyValue("--coral").trim() || "#ff6b5e";
    const surface3 = style.getPropertyValue("--surface-3").trim() || "#212939";

    if (scoreDonutChart) scoreDonutChart.destroy();
    scoreDonutChart = new Chart(el("scoreDonut"), {
      type: "doughnut",
      data: {
        datasets: [{
          data: [report.score_percent, 100 - report.score_percent],
          backgroundColor: [amber, surface3],
          borderWidth: 0,
        }],
      },
      options: {
        cutout: "78%",
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        animation: { duration: 600 },
      },
    });

    const history = report.history || [];
    if (historyBarChart) historyBarChart.destroy();
    historyBarChart = new Chart(el("historyChart"), {
      type: "bar",
      data: {
        labels: history.map((_, i) => `Q${i + 1}`),
        datasets: [{
          label: "Correct",
          data: history.map((h) => (h.correct ? 1 : 0)),
          backgroundColor: history.map((h) => (h.correct ? teal : coral)),
          borderRadius: 4,
          maxBarThickness: 28,
        }],
      },
      options: {
        scales: {
          y: { min: 0, max: 1, ticks: { stepSize: 1, callback: (v) => (v === 1 ? "Correct" : "Missed") }, grid: { color: "rgba(255,255,255,0.06)" } },
          x: { grid: { display: false } },
        },
        plugins: { legend: { display: false } },
      },
    });
  } catch (err) {
    console.error("Chart banane mein error aayi, par baaki report dikh raha hai:", err);
  }
}
el("restartBtn").addEventListener("click", () => location.reload());
