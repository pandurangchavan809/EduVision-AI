/* ==========================================================================
   EduVision AI - Client-side Interactive Engine & Chart Manager
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    let sgpaChartInstance = null;
    let subjectChartInstance = null;
    let currentStudentPrn = "2023AIDS001"; // Default PRN

    // Elements
    const prnSearchInput = document.getElementById("prn-search-input");
    const searchDropdown = document.getElementById("search-results-dropdown");
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    // Modal elements
    const certModal = document.getElementById("cert-modal");
    const certModalOverlay = document.getElementById("cert-modal-overlay");
    const closeCertModalBtn = document.getElementById("close-cert-modal");
    const openCertModalBtn = document.getElementById("open-cert-modal-btn");
    const certForm = document.getElementById("cert-form");

    // Initialize Default View
    loadStudentData(currentStudentPrn);
    setupTabNavigation();
    setupSearchAutoComplete();
    setupCertModal();

    // 1. Fetch & Load Student Data
    async function loadStudentData(prn) {
        try {
            const res = await fetch(`/api/student/${prn}`);
            const data = await res.json();

            if (!data.success) {
                alert(`Error: ${data.error}`);
                return;
            }

            const student = data.student;
            currentStudentPrn = student.prn;

            // Populate Student Profile Details
            document.getElementById("student-name").textContent = student.name;
            document.getElementById("student-prn").textContent = student.prn;
            document.getElementById("student-dept").textContent = student.department;
            document.getElementById("student-cgpa").textContent = student.cgpa ? student.cgpa.toFixed(2) : "N/A";
            document.getElementById("student-attendance").textContent = `${student.attendance_perc}%`;
            document.getElementById("student-hsc").textContent = `${student.hsc_perc}%`;
            document.getElementById("student-project").textContent = `${student.project_score}%`;

            // Risk status badge
            const riskBadge = document.getElementById("risk-status-badge");
            const analysis = student.ai_analysis;
            riskBadge.textContent = analysis.risk_status;
            riskBadge.className = `badge badge-${analysis.risk_color}`;

            // Predicted SGPA
            document.getElementById("predicted-sgpa").textContent = analysis.predicted_sem7_sgpa.toFixed(2);
            document.getElementById("ai-summary-text").textContent = analysis.ai_summary;

            // Strengths & Weaknesses
            const strengthsList = document.getElementById("strengths-list");
            strengthsList.innerHTML = analysis.strengths.map(s => `<li><i class="fa-solid fa-check text-emerald"></i> ${s}</li>`).join("");

            const weaknessesList = document.getElementById("weaknesses-list");
            weaknessesList.innerHTML = analysis.weaknesses.map(w => `<li><i class="fa-solid fa-triangle-exclamation text-amber"></i> ${w}</li>`).join("");

            const recommendationsList = document.getElementById("recommendations-list");
            recommendationsList.innerHTML = analysis.recommendations.map(r => `<li><i class="fa-solid fa-lightbulb text-cyan"></i> ${r}</li>`).join("");

            // Render Certifications Table
            renderCertificationsTable(student.certifications);

            // Render Charts
            renderSgpaTrendChart(student);
            renderSubjectChart(student);

        } catch (err) {
            console.error("Failed to load student data:", err);
        }
    }

    // 2. Render SGPA Trend Line Chart
    function renderSgpaTrendChart(student) {
        const ctx = document.getElementById("sgpaTrendChart").getContext("2d");

        if (sgpaChartInstance) {
            sgpaChartInstance.destroy();
        }

        const labels = ["12th Std", "Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Predicted Sem 7"];
        const dataPoints = [
            (student.hsc_perc / 10.0),
            student.sem1_sgpa,
            student.sem2_sgpa,
            student.sem3_sgpa,
            student.sem4_sgpa,
            student.sem5_sgpa,
            student.sem6_sgpa,
            student.ai_analysis.predicted_sem7_sgpa
        ];

        sgpaChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "SGPA Trajectory",
                    data: dataPoints,
                    borderColor: "#00f2fe",
                    backgroundColor: "rgba(0, 242, 254, 0.15)",
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: "#8a2be2",
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#94a3b8" } }
                },
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
                    y: { min: 4, max: 10, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
                }
            }
        });
    }

    // 3. Render Subject Performance Bar Chart
    function renderSubjectChart(student) {
        const ctx = document.getElementById("subjectChart").getContext("2d");

        if (subjectChartInstance) {
            subjectChartInstance.destroy();
        }

        const labels = ["DSA", "DBMS", "Machine Learning", "Networks"];
        const scores = [student.dsa_score, student.dbms_score, student.ml_score, student.cn_score];

        subjectChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Subject Score (%)",
                    data: scores,
                    backgroundColor: ["rgba(0, 242, 254, 0.7)", "rgba(138, 43, 226, 0.7)", "rgba(16, 185, 129, 0.7)", "rgba(245, 158, 11, 0.7)"],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
                    y: { min: 0, max: 100, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
                }
            }
        });
    }

    // 4. Render Certifications Table
    function renderCertificationsTable(certs) {
        const tbody = document.getElementById("certs-table-body");

        if (!certs || certs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No certifications uploaded yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = certs.map(c => `
            <tr>
                <td style="font-weight: 600;">${c.title}</td>
                <td style="color: var(--text-secondary);">${c.issuer}</td>
                <td style="color: var(--text-muted);">${c.issue_date || 'N/A'}</td>
                <td>
                    <span class="badge ${c.status.includes('Approved') ? 'badge-emerald' : 'badge-amber'}">
                        <i class="fa-solid ${c.status.includes('Approved') ? 'fa-check' : 'fa-clock'}"></i>
                        ${c.status}
                    </span>
                </td>
            </tr>
        `).join("");
    }

    // 5. Search Auto-complete
    function setupSearchAutoComplete() {
        let timer;
        prnSearchInput.addEventListener("input", (e) => {
            clearTimeout(timer);
            const query = e.target.value.trim();

            if (query.length < 2) {
                searchDropdown.classList.remove("active");
                return;
            }

            timer = setTimeout(async () => {
                const res = await fetch(`/api/students?q=${encodeURIComponent(query)}`);
                const data = await res.json();

                if (data.success && data.students.length > 0) {
                    searchDropdown.innerHTML = data.students.map(s => `
                        <div class="result-item" data-prn="${s.prn}">
                            <div>
                                <strong>${s.name}</strong> <small style="color: var(--cyan); font-family: var(--font-code);">(${s.prn})</small>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">${s.department}</div>
                            </div>
                            <span class="badge badge-emerald">Sem 6: ${s.sem6_sgpa}</span>
                        </div>
                    `).join("");

                    searchDropdown.classList.add("active");

                    // Handle Click on Search Item
                    document.querySelectorAll(".result-item").forEach(item => {
                        item.addEventListener("click", () => {
                            const prn = item.getAttribute("data-prn");
                            prnSearchInput.value = prn;
                            searchDropdown.classList.remove("active");
                            loadStudentData(prn);
                        });
                    });
                } else {
                    searchDropdown.innerHTML = `<div class="result-item" style="color: var(--text-muted);">No student found.</div>`;
                    searchDropdown.classList.add("active");
                }
            }, 250);
        });

        document.addEventListener("click", (e) => {
            if (!prnSearchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.classList.remove("active");
            }
        });
    }

    // 6. Tab Navigation
    function setupTabNavigation() {
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                tabBtns.forEach(b => b.classList.remove("active"));
                tabContents.forEach(c => c.style.display = "none");

                btn.classList.add("active");
                const target = btn.getAttribute("data-tab");
                const targetContent = document.getElementById(`${target}-tab`);

                if (targetContent) {
                    targetContent.style.display = "block";
                }

                if (target === "faculty") {
                    loadFacultyApprovals();
                } else if (target === "department") {
                    loadDepartmentStats();
                }
            });
        });
    }

    // 7. Load Faculty Approvals Tab
    async function loadFacultyApprovals() {
        try {
            const res = await fetch("/api/faculty/approvals");
            const data = await res.json();
            const tbody = document.getElementById("faculty-approvals-body");

            if (!data.success || data.approvals.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No pending faculty verifications.</td></tr>`;
                return;
            }

            tbody.innerHTML = data.approvals.map(item => `
                <tr>
                    <td><strong>${item.name}</strong> <small>(${item.prn})</small></td>
                    <td>${item.title}</td>
                    <td>${item.issuer}</td>
                    <td><span class="badge ${item.status.includes('Approved') ? 'badge-emerald' : 'badge-amber'}">${item.status}</span></td>
                    <td>
                        ${item.status.includes('Approved') ? '<span style="color: var(--emerald);">Approved</span>' : `
                            <button class="btn btn-primary btn-sm approve-btn" data-id="${item.id}">
                                <i class="fa-solid fa-check"></i> Approve
                            </button>
                        `}
                    </td>
                </tr>
            `).join("");

            document.querySelectorAll(".approve-btn").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const certId = btn.getAttribute("data-id");
                    await fetch("/api/faculty/approve", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ cert_id: certId, status: "Verified & Approved" })
                    });
                    loadFacultyApprovals();
                });
            });
        } catch (err) {
            console.error("Failed to load approvals:", err);
        }
    }

    // 8. Load Department Stats Tab
    async function loadDepartmentStats() {
        try {
            const res = await fetch("/api/department/stats");
            const data = await res.json();

            if (!data.success) return;

            document.getElementById("at-risk-count").textContent = data.at_risk_count;

            const grid = document.getElementById("dept-cards-grid");
            grid.innerHTML = data.departments.map(d => `
                <div class="glass-card">
                    <h3 style="color: var(--cyan); margin-bottom: 0.5rem;">${d.department}</h3>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">Total Enrolled: <strong>${d.total_students}</strong></p>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">Avg Sem 6 SGPA: <strong style="color: var(--emerald);">${d.avg_sem6_sgpa}</strong></p>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">Avg Attendance: <strong>${d.avg_attendance}%</strong></p>
                </div>
            `).join("");

            const topList = document.getElementById("top-performers-list");
            topList.innerHTML = data.top_performers.map((t, idx) => `
                <div class="metric-row">
                    <span>#${idx + 1} <strong>${t.name}</strong> (${t.department})</span>
                    <span class="badge badge-emerald">${t.sem6_sgpa} SGPA</span>
                </div>
            `).join("");

        } catch (err) {
            console.error("Failed to load dept stats:", err);
        }
    }

    // 9. Setup Certification Upload Modal
    function setupCertModal() {
        openCertModalBtn.addEventListener("click", () => certModal.classList.add("active"));
        closeCertModalBtn.addEventListener("click", () => certModal.classList.remove("active"));
        certModalOverlay.addEventListener("click", () => certModal.classList.remove("active"));

        certForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const title = document.getElementById("cert-title").value.trim();
            const issuer = document.getElementById("cert-issuer").value.trim();
            const date = document.getElementById("cert-date").value;

            if (!title || !issuer) return;

            const res = await fetch("/api/certifications", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prn: currentStudentPrn, title, issuer, issue_date: date })
            });

            const data = await res.json();
            if (data.success) {
                alert(data.message);
                certModal.classList.remove("active");
                certForm.reset();
                loadStudentData(currentStudentPrn);
            }
        });
    }
});
