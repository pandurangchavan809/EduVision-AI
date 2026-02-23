(function () {
  const {
    state,
    apiGet,
    setStudentHeader,
    priorityPill,
    renderError,
    clearError,
  } = window.EduVision;

  const improvementSummary = document.getElementById("improvementSummary");
  const aiSourceTag = document.getElementById("aiSourceTag");
  const aiNotice = document.getElementById("aiNotice");
  const focusAreaGrid = document.getElementById("focusAreaGrid");
  const recommendationGrid = document.getElementById("recommendationGrid");
  const planTimeline = document.getElementById("planTimeline");
  const recommendationsStarted = document.getElementById("recommendationsStarted");
  const skillsCount = document.getElementById("skillsCount");
  const planStages = document.getElementById("planStages");
  const refreshAiBtn = document.getElementById("refreshAiBtn");

  async function loadImprovement() {
    try {
      clearError();
      const payload = await apiGet(`/student/${encodeURIComponent(state.prn)}/improvement`);
      setStudentHeader(payload.student);

      improvementSummary.textContent =
        payload.summary || "No recommendation summary available for this student.";
      aiSourceTag.textContent =
        payload.source === "gemini"
          ? "Source: Gemini API"
          : "Source: Rule-based fallback";
      aiSourceTag.className =
        payload.source === "gemini"
          ? "inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
          : "inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700";

      if (payload.ai_status === "gemini_success") {
        aiNotice.innerHTML = `
          <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            Gemini response loaded successfully from your configured API key.
          </div>
        `;
      } else {
        const message = payload.ai_error
          ? `Gemini fallback used: ${payload.ai_error}`
          : "Gemini fallback used. Configure GEMINI_API_KEY for AI-generated recommendations.";
        aiNotice.innerHTML = `
          <div class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            ${message}
          </div>
        `;
      }

      const focusAreas = payload.focus_areas || [];
      if (!focusAreas.length) {
        focusAreaGrid.innerHTML = `
          <article class="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500">
            No focus areas detected from latest semester records.
          </article>
        `;
      } else {
        focusAreaGrid.innerHTML = focusAreas
          .map(
            (focus) => `
            <article class="rounded-2xl border border-slate-200 bg-white p-5">
              <div class="mb-3 flex items-center justify-between gap-3">
                <h3 class="text-2xl font-semibold">${focus.subject}</h3>
                <span class="rounded-full px-3 py-1 text-xs font-semibold ${priorityPill(focus.priority)}">${focus.priority} priority</span>
              </div>
              <p class="text-slate-500">${focus.reason}</p>
              <div class="mt-4 flex items-center justify-between text-sm">
                <span>Current: ${focus.current_score}%</span>
                <span>Target: ${focus.target_score}%</span>
              </div>
              <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
                <div class="h-full rounded-full bg-slate-900" style="width:${focus.current_score}%"></div>
              </div>
              <p class="mt-2 text-sm text-slate-500">${focus.gap} points to goal</p>
            </article>
          `
          )
          .join("");
      }

      const recommendations = payload.recommendations || [];
      if (!recommendations.length) {
        recommendationGrid.innerHTML = `
          <article class="rounded-xl border border-slate-200 p-4 text-sm text-slate-500">
            No recommendation actions available.
          </article>
        `;
      } else {
        recommendationGrid.innerHTML = recommendations
          .map(
            (item) => `
            <article class="rounded-xl border border-slate-200 p-4">
              <div class="mb-3 flex items-start justify-between gap-3">
                <h4 class="text-xl font-semibold">${item.title}</h4>
                <span class="rounded-full px-3 py-1 text-xs font-semibold ${priorityPill(item.priority)}">${item.priority}</span>
              </div>
              <p class="text-slate-600">${item.action}</p>
              <p class="mt-3 text-sm text-slate-500">Duration: ${item.duration} | Difficulty: ${item.difficulty}</p>
            </article>
          `
          )
          .join("");
      }

      const plan = payload.six_week_plan || [];
      if (!plan.length) {
        planTimeline.innerHTML = `<p class="text-sm text-slate-500">No 6-week plan generated.</p>`;
      } else {
        planTimeline.innerHTML = plan
          .map(
            (stage, index) => `
            <article class="rounded-xl border border-slate-200 p-4">
              <div class="mb-2 flex items-center justify-between gap-3">
                <div class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">${index + 1}</div>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">${stage.week_range}</span>
              </div>
              <h4 class="text-xl font-semibold">${stage.goal}</h4>
              <ul class="mt-3 space-y-1 text-slate-600">
                ${(stage.tasks || []).map((task) => `<li>- ${task}</li>`).join("")}
              </ul>
            </article>
          `
          )
          .join("");
      }

      recommendationsStarted.textContent = payload.recommendations_started ?? recommendations.length;
      skillsCount.textContent = payload.skills_count ?? 0;
      planStages.textContent = plan.length;
    } catch (error) {
      renderError(error.message || "Failed to load improvement data.");
      aiNotice.innerHTML = "";
    }
  }

  refreshAiBtn.addEventListener("click", loadImprovement);
  loadImprovement();
})();
