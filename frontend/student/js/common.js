(function () {
  const params = new URLSearchParams(window.location.search);
  const prnFromUrl = (params.get("prn") || "").trim().toUpperCase();
  const storedPrn = (localStorage.getItem("eduvision_prn") || "").trim().toUpperCase();
  const prn = prnFromUrl || storedPrn;
  const apiBase =
    (localStorage.getItem("eduvision_api_base") || "http://127.0.0.1:5000/api").replace(/\/$/, "");

  if (!prn) {
    window.location.href = "../index.html";
    return;
  }

  localStorage.setItem("eduvision_prn", prn);

  const page = document.body.dataset.page;
  const navItems = [
    { key: "dashboard", file: "dashboard.html" },
    { key: "progress", file: "progress.html" },
    { key: "reports", file: "reports.html" },
    { key: "improvement", file: "improvement.html" },
  ];

  navItems.forEach((item) => {
    const link = document.querySelector(`[data-nav="${item.key}"]`);
    if (!link) return;
    link.href = `${item.file}?prn=${encodeURIComponent(prn)}`;
    link.classList.remove("bg-blue-600", "text-white", "shadow-sm");
    link.classList.add("text-slate-800", "hover:bg-slate-100");

    if (item.key === page) {
      link.classList.remove("text-slate-800", "hover:bg-slate-100");
      link.classList.add("bg-blue-600", "text-white", "shadow-sm");
    }
  });

  const prnEls = document.querySelectorAll("[data-student-prn]");
  prnEls.forEach((node) => {
    node.textContent = prn;
  });

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("eduvision_prn");
      window.location.href = "../index.html";
    });
  }

  function initials(name) {
    if (!name) return "ST";
    const parts = name.split(" ").filter(Boolean);
    if (!parts.length) return "ST";
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }

  function setStudentHeader(student) {
    const name = student?.name || "Student";
    const nameEls = document.querySelectorAll("[data-student-name]");
    nameEls.forEach((node) => {
      node.textContent = name;
    });

    const initialEls = document.querySelectorAll("[data-student-initials]");
    initialEls.forEach((node) => {
      node.textContent = initials(name);
    });
  }

  async function apiGet(path) {
    const response = await fetch(`${apiBase}${path}`);
    const payload = await response.json();
    if (!response.ok) {
      let message = payload.error || "Request failed";
      if (payload.error === "Student not found") {
        const suggestionText = (payload.suggestions || [])
          .map((item) => item.prn)
          .join(", ");
        if (suggestionText) {
          message = `${message}. Try one of: ${suggestionText}`;
        }
      }
      throw new Error(message);
    }
    return payload;
  }

  function toPercent(value) {
    if (value === null || value === undefined || Number.isNaN(value)) return "-";
    return `${Number(value).toFixed(1)}%`;
  }

  function toSgpa(value) {
    if (value === null || value === undefined || Number.isNaN(value)) return "-";
    return Number(value).toFixed(2);
  }

  function renderError(message) {
    const node = document.getElementById("page-error");
    if (!node) return;
    node.innerHTML = `
      <div class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        ${message}
      </div>
    `;
  }

  function clearError() {
    const node = document.getElementById("page-error");
    if (!node) return;
    node.innerHTML = "";
  }

  function priorityPill(priority) {
    if (priority === "high") return "bg-rose-100 text-rose-700";
    if (priority === "medium") return "bg-amber-100 text-amber-700";
    return "bg-slate-100 text-slate-700";
  }

  window.EduVision = {
    state: { prn, apiBase, page },
    apiGet,
    setStudentHeader,
    toPercent,
    toSgpa,
    renderError,
    clearError,
    priorityPill,
  };
})();
