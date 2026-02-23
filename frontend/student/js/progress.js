(async function () {
  const {
    state,
    apiGet,
    setStudentHeader,
    toSgpa,
    renderError,
    clearError,
  } = window.EduVision;

  const currentSemesterChip = document.getElementById("currentSemesterChip");
  const progressSubjects = document.getElementById("progressSubjects");
  const skillList = document.getElementById("skillList");
  const goalList = document.getElementById("goalList");

  function statusChip(status) {
    if (status === "strong") return "bg-emerald-100 text-emerald-700";
    if (status === "stable") return "bg-blue-100 text-blue-700";
    return "bg-rose-100 text-rose-700";
  }

  function goalStatusChip(status) {
    if (status === "on_track") return "bg-emerald-100 text-emerald-700";
    return "bg-amber-100 text-amber-700";
  }

  try {
    clearError();
    const payload = await apiGet(`/student/${encodeURIComponent(state.prn)}/progress`);
    setStudentHeader(payload.student);

    currentSemesterChip.textContent = payload.current_semester || "Semester -";

    const subjects = payload.subjects || [];
    if (!subjects.length) {
      progressSubjects.innerHTML = `<p class="text-sm text-slate-500">No semester subject data found for this PRN.</p>`;
    } else {
      progressSubjects.innerHTML = subjects
        .map(
          (subject) => `
          <div class="rounded-xl border border-slate-200 p-4">
            <div class="mb-2 flex items-center justify-between gap-3">
              <div>
                <p class="text-lg font-semibold">${subject.subject}</p>
                <p class="text-sm text-slate-500">Current: ${subject.score}% | Target: ${subject.target_score}%</p>
              </div>
              <span class="rounded-full px-3 py-1 text-xs font-semibold ${statusChip(subject.status)}">
                ${subject.status.replace("_", " ")}
              </span>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-slate-200">
              <div class="h-full rounded-full bg-slate-900" style="width:${subject.score}%"></div>
            </div>
          </div>
        `
        )
        .join("");
    }

    const radarData = payload.twelfth_radar || { labels: [], scores: [] };
    if (radarData.labels.length && radarData.scores.length) {
      new Chart(document.getElementById("skillsRadarChart"), {
        type: "radar",
        data: {
          labels: radarData.labels,
          datasets: [
            {
              label: "12th Marks",
              data: radarData.scores,
              borderColor: "#2563eb",
              backgroundColor: "rgba(37,99,235,0.2)",
              borderWidth: 2,
              pointBackgroundColor: "#2563eb",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              min: 0,
              max: 100,
              ticks: { stepSize: 20 },
              grid: { color: "rgba(148,163,184,0.3)" },
            },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }

    const sgpaTrend = payload.sgpa_trend || [];
    if (sgpaTrend.length) {
      const sgpaValues = sgpaTrend.map((item) => Number(item.sgpa)).filter((value) => !Number.isNaN(value));
      const minSgpa = sgpaValues.length ? Math.min(...sgpaValues) : 0;
      const maxSgpa = sgpaValues.length ? Math.max(...sgpaValues) : 10;
      const avgSgpa = sgpaValues.length
        ? sgpaValues.reduce((sum, value) => sum + value, 0) / sgpaValues.length
        : 0;

      new Chart(document.getElementById("sgpaBarChart"), {
        type: "bar",
        data: {
          labels: sgpaTrend.map((item) => item.semester),
          datasets: [
            {
              label: "SGPA",
              data: sgpaTrend.map((item) => item.sgpa),
              backgroundColor: "#2563eb",
              borderRadius: 8,
            },
            {
              type: "line",
              label: "Average SGPA",
              data: sgpaTrend.map(() => Number(avgSgpa.toFixed(2))),
              borderColor: "#0f172a",
              borderDash: [6, 5],
              borderWidth: 2,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              min: Math.max(0, Math.floor(minSgpa - 0.8)),
              max: Math.min(10, Math.ceil(maxSgpa + 0.8)),
              ticks: { stepSize: 0.5 },
              grid: { color: "rgba(148,163,184,0.25)" },
            },
            x: { grid: { display: false } },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }

    const skills = payload.skills || [];
    if (!skills.length) {
      skillList.innerHTML = `<p class="text-sm text-slate-500">No skills available for this PRN.</p>`;
    } else {
      skillList.innerHTML = skills
        .map(
          (item) => `
            <span class="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">${item}</span>
          `
        )
        .join("");
    }

    const goals = payload.goals || [];
    if (!goals.length) {
      goalList.innerHTML = `<p class="text-sm text-slate-500">No goals generated yet.</p>`;
    } else {
      goalList.innerHTML = goals
        .map(
          (goal) => `
          <div class="rounded-xl border border-slate-200 p-4">
            <div class="mb-2 flex items-start justify-between gap-3">
              <p class="font-semibold">${goal.title}</p>
              <span class="rounded-full px-3 py-1 text-xs font-semibold ${goalStatusChip(goal.status)}">${goal.status.replace("_", " ")}</span>
            </div>
            <p class="text-sm text-slate-600">Current: ${goal.current_score}% | Target: ${goal.target_score}%</p>
          </div>
        `
        )
        .join("");
    }
  } catch (error) {
    renderError(error.message || "Failed to load progress data.");
    currentSemesterChip.textContent = "Semester -";
  }
})();
