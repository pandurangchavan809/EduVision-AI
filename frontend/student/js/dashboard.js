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

  const metricSgpa = document.getElementById("metricSgpa");
  const metricSgpaChange = document.getElementById("metricSgpaChange");
  const metricAverage = document.getElementById("metricAverage");
  const metricTwelfth = document.getElementById("metricTwelfth");
  const metricRank = document.getElementById("metricRank");
  const metricClassSize = document.getElementById("metricClassSize");
  const recentGradesList = document.getElementById("recentGradesList");
  const skillsWrap = document.getElementById("skillsWrap");
  const insightList = document.getElementById("insightList");

  function ordinal(value) {
    if (!value) return "-";
    const mod10 = value % 10;
    const mod100 = value % 100;
    if (mod10 === 1 && mod100 !== 11) return `${value}st`;
    if (mod10 === 2 && mod100 !== 12) return `${value}nd`;
    if (mod10 === 3 && mod100 !== 13) return `${value}rd`;
    return `${value}th`;
  }

  function gradeBadgeClass(grade) {
    if (grade === "A+" || grade === "A") return "bg-emerald-100 text-emerald-700";
    if (grade === "B+" || grade === "B") return "bg-blue-100 text-blue-700";
    if (grade === "C+" || grade === "C") return "bg-amber-100 text-amber-700";
    return "bg-rose-100 text-rose-700";
  }

  try {
    clearError();
    const payload = await apiGet(`/student/${encodeURIComponent(state.prn)}/dashboard`);
    setStudentHeader(payload.student);

    const metrics = payload.metrics || {};
    metricSgpa.textContent = toSgpa(metrics.current_sgpa);
    metricAverage.textContent = toPercent(metrics.average_subject_score);
    metricTwelfth.textContent = toPercent(metrics.twelfth_percentage);
    metricRank.textContent = ordinal(metrics.class_rank);
    metricClassSize.textContent = metrics.class_size
      ? `Out of ${metrics.class_size} students`
      : "Class size unavailable";

    if (metrics.sgpa_change === null || metrics.sgpa_change === undefined) {
      metricSgpaChange.textContent = "No previous semester to compare";
      metricSgpaChange.className = "mt-2 text-sm text-slate-500";
    } else if (metrics.sgpa_change >= 0) {
      metricSgpaChange.textContent = `+${metrics.sgpa_change.toFixed(2)} from previous semester`;
      metricSgpaChange.className = "mt-2 text-sm text-emerald-600";
    } else {
      metricSgpaChange.textContent = `${metrics.sgpa_change.toFixed(2)} from previous semester`;
      metricSgpaChange.className = "mt-2 text-sm text-rose-600";
    }

    const grades = payload.recent_grades || [];
    if (!grades.length) {
      recentGradesList.innerHTML = `<p class="text-sm text-slate-500">No subject records in latest semester.</p>`;
    } else {
      recentGradesList.innerHTML = grades
        .map(
          (item) => `
          <div class="flex items-center justify-between rounded-xl border border-slate-200 p-3">
            <div>
              <p class="font-semibold">${item.subject}</p>
              <p class="text-sm text-slate-500">Score: ${item.score}%</p>
            </div>
            <span class="rounded-full px-3 py-1 text-xs font-semibold ${gradeBadgeClass(item.grade)}">${item.grade}</span>
          </div>
        `
        )
        .join("");
    }

    const skills = payload.skills || [];
    if (!skills.length) {
      skillsWrap.innerHTML = `<p class="text-sm text-slate-500">No skills mapped yet.</p>`;
    } else {
      skillsWrap.innerHTML = skills
        .map(
          (skill) => `
            <span class="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">${skill}</span>
          `
        )
        .join("");
    }

    const insights = payload.insights || [];
    if (!insights.length) {
      insightList.innerHTML = `<li class="text-sm text-slate-500">No insights available.</li>`;
    } else {
      insightList.innerHTML = insights
        .map((item) => `<li class="rounded-lg bg-slate-100 px-3 py-2">${item}</li>`)
        .join("");
    }

    const chartRows = (payload.progress || []).filter((item) => item.sgpa !== null && item.sgpa !== undefined);
    const chartElement = document.getElementById("dashboardTrendChart");
    if (chartRows.length) {
      const sgpaValues = chartRows.map((item) => Number(item.sgpa));
      const minSgpa = Math.min(...sgpaValues);
      const maxSgpa = Math.max(...sgpaValues);
      const yMin = Math.max(0, Math.floor(minSgpa - 0.8));
      const yMax = Math.min(10, Math.ceil(maxSgpa + 0.8));

      new Chart(chartElement, {
        type: "line",
        data: {
          labels: chartRows.map((item) => item.semester),
          datasets: [
            {
              label: "SGPA",
              data: chartRows.map((item) => item.sgpa),
              borderColor: "#2563eb",
              backgroundColor: "rgba(37,99,235,0.1)",
              borderWidth: 3,
              pointRadius: 4,
              pointBackgroundColor: "#2563eb",
              tension: 0.3,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              min: yMin,
              max: yMax,
              ticks: { stepSize: 0.5 },
              grid: { color: "rgba(148,163,184,0.2)" },
            },
            x: {
              grid: { color: "rgba(148,163,184,0.15)" },
            },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }
  } catch (error) {
    renderError(error.message || "Failed to load dashboard data.");
  }
})();
