(async function () {
  const {
    state,
    apiGet,
    setStudentHeader,
    toPercent,
    toSgpa,
    renderError,
    clearError,
  } = window.EduVision;

  const summaryCurrentSgpa = document.getElementById("summaryCurrentSgpa");
  const summaryOverallCgpa = document.getElementById("summaryOverallCgpa");
  const summaryRank = document.getElementById("summaryRank");
  const summaryTwelfth = document.getElementById("summaryTwelfth");
  const summarySemesters = document.getElementById("summarySemesters");
  const reportsList = document.getElementById("reportsList");
  const downloadTranscriptBtn = document.getElementById("downloadTranscriptBtn");

  let reportPayload = null;

  function gradeBadgeClass(grade) {
    if (grade === "A+" || grade === "A") return "bg-emerald-100 text-emerald-700";
    if (grade === "B+" || grade === "B") return "bg-blue-100 text-blue-700";
    if (grade === "C+" || grade === "C") return "bg-amber-100 text-amber-700";
    return "bg-rose-100 text-rose-700";
  }

  try {
    clearError();
    reportPayload = await apiGet(`/student/${encodeURIComponent(state.prn)}/reports`);
    setStudentHeader(reportPayload.student);

    const summary = reportPayload.summary || {};
    summaryCurrentSgpa.textContent = toSgpa(summary.current_sgpa);
    summaryOverallCgpa.textContent = toSgpa(summary.overall_cgpa);
    summaryTwelfth.textContent = toPercent(summary.twelfth_percentage);
    summarySemesters.textContent = summary.semesters_completed ?? "-";
    summaryRank.textContent =
      summary.class_rank && summary.class_size
        ? `${summary.class_rank}/${summary.class_size}`
        : "-";

    const reports = reportPayload.reports || [];
    if (!reports.length) {
      reportsList.innerHTML = `
        <div class="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500">
          No semester reports available.
        </div>
      `;
    } else {
      reportsList.innerHTML = reports
        .map((report) => {
          const subjectCards = (report.subjects || [])
            .map(
              (subject) => `
              <div class="rounded-xl border border-slate-200 p-4">
                <div class="mb-2 flex items-center justify-between gap-3">
                  <p class="font-semibold">${subject.subject}</p>
                  <span class="rounded-full px-3 py-1 text-xs font-semibold ${gradeBadgeClass(subject.grade)}">${subject.grade}</span>
                </div>
                <p class="text-sm text-slate-500">Score: ${subject.score}%</p>
                <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
                  <div class="h-full rounded-full bg-slate-900" style="width:${subject.score}%"></div>
                </div>
              </div>
            `
            )
            .join("");

          return `
            <article class="rounded-2xl border border-slate-200 bg-white p-5">
              <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 class="text-2xl font-semibold">${report.semester}</h3>
                  <p class="text-slate-500">SGPA: ${toSgpa(report.sgpa)}</p>
                </div>
              </div>
              <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                ${subjectCards || '<p class="text-sm text-slate-500">No subject rows for this semester.</p>'}
              </div>
            </article>
          `;
        })
        .join("");
    }
  } catch (error) {
    renderError(error.message || "Failed to load reports.");
  }

  downloadTranscriptBtn.addEventListener("click", () => {
    if (!reportPayload) return;
    const blob = new Blob([JSON.stringify(reportPayload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${state.prn}_transcript.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
})();
