/**
 * Habit CRM - Frontend Interaction & Visualization Script
 */

let weeklyChart = null;
let categoryChart = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    initWeeklyChart();
    initCategoryChart();
});

// ========================================================
// 1. Chart.js Visualizations
// ========================================================
function initWeeklyChart() {
    const ctx = document.getElementById("weeklyTrendsChart");
    if (!ctx || !INITIAL_DAILY_DATA) return;

    const labels = INITIAL_DAILY_DATA.map(d => `${d.day_name} (${d.day_name === 'Sun' ? 'Sun' : d.day_name})`);
    const completedCounts = INITIAL_DAILY_DATA.map(d => d.completed_count);
    const percentages = INITIAL_DAILY_DATA.map(d => d.percentage);

    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    type: 'bar',
                    label: 'Habits Completed',
                    data: completedCounts,
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: '#10b981',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    order: 2
                },
                {
                    type: 'line',
                    label: 'Completion %',
                    data: percentages,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 2,
                    tension: 0.35,
                    fill: false,
                    yAxisID: 'y1',
                    order: 1,
                    pointBackgroundColor: '#06b6d4',
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: '#111827',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                },
                y: {
                    beginAtZero: true,
                    max: 10,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { stepSize: 2, color: '#94a3b8' },
                    title: { display: true, text: 'Completed Count', color: '#64748b' }
                },
                y1: {
                    beginAtZero: true,
                    max: 100,
                    position: 'right',
                    grid: { display: false },
                    ticks: { callback: v => `${v}%`, color: '#06b6d4' }
                }
            }
        }
    });
}

function initCategoryChart() {
    const ctx = document.getElementById("categoryDonutChart");
    if (!ctx || !INITIAL_CATEGORY_DATA) return;

    const labels = Object.keys(INITIAL_CATEGORY_DATA);
    const data = Object.values(INITIAL_CATEGORY_DATA);

    const palette = [
        '#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b',
        '#84cc16', '#6366f1', '#ec4899', '#14b8a6', '#f97316'
    ];

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: palette.slice(0, labels.length),
                borderColor: '#111827',
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 12,
                        font: { family: 'Inter', size: 11 },
                        boxWidth: 12
                    }
                },
                tooltip: {
                    backgroundColor: '#111827',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1',
                    padding: 8
                }
            },
            cutout: '68%'
        }
    });
}

// ========================================================
// 2. Interactive Tick / Toggle Handler
// ========================================================
async function toggleHabit(buttonElement) {
    if (buttonElement.disabled || buttonElement.classList.contains("is-future-btn")) {
        showToast("Future dates cannot be marked complete.");
        return;
    }

    const habitId = buttonElement.getAttribute("data-habit-id");
    const dateStr = buttonElement.getAttribute("data-date");

    // Optimistic UI state toggle
    const currentlyChecked = buttonElement.classList.contains("is-checked");
    const newChecked = !currentlyChecked;
    
    if (newChecked) {
        buttonElement.classList.add("is-checked");
    } else {
        buttonElement.classList.remove("is-checked");
    }

    try {
        const response = await fetch("/api/habits/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ habit_id: parseInt(habitId), date: dateStr })
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.detail || "Failed to toggle");
        }

        // Update streak display
        const streakEl = document.getElementById(`streak-${habitId}`);
        if (streakEl) {
            streakEl.textContent = `${data.current_streak}d`;
        }

        // Update row progress
        updateRowProgress(habitId);

        // Update global week progress
        const weekPctEl = document.getElementById("metric-week-pct");
        const weekBarEl = document.getElementById("metric-week-bar");
        if (weekPctEl) weekPctEl.textContent = `${data.overall_week_pct}%`;
        if (weekBarEl) weekBarEl.style.width = `${data.overall_week_pct}%`;

        // Update Chart data asynchronously
        refreshWeeklyChart();

        showToast(newChecked ? "Habit marked complete! 🎉" : "Habit unchecked");

    } catch (err) {
        // Rollback optimistic state on error
        if (currentlyChecked) {
            buttonElement.classList.add("is-checked");
        } else {
            buttonElement.classList.remove("is-checked");
        }
        showToast("Error updating habit: " + err.message);
    }
}

function updateRowProgress(habitId) {
    const row = document.getElementById(`habit-row-${habitId}`);
    if (!row) return;

    const checkedBtns = row.querySelectorAll(".tick-btn.is-checked");
    const count = checkedBtns.length;
    const pct = Math.round((count / 7) * 100);

    const bar = document.getElementById(`row-bar-${habitId}`);
    const textCount = document.getElementById(`row-count-${habitId}`);
    const textWrap = document.getElementById(`row-text-${habitId}`);

    if (bar) bar.style.width = `${pct}%`;
    if (textCount) textCount.textContent = count;
    if (textWrap) textWrap.innerHTML = `<strong>${count}</strong>/7 (${pct}%)`;
}

async function refreshWeeklyChart() {
    if (!weeklyChart) return;
    try {
        const res = await fetch(`/?week_date=${CURRENT_WEEK_DATE}&format=json`);
        // Recalculate directly from DOM tick buttons for instantaneous chart sync
        const dayCounts = [0, 0, 0, 0, 0, 0, 0];
        const rows = document.querySelectorAll(".habit-row");
        const totalHabits = rows.length || 1;

        rows.forEach(r => {
            const btns = r.querySelectorAll(".tick-btn");
            btns.forEach((btn, idx) => {
                if (btn.classList.contains("is-checked") && idx < 7) {
                    dayCounts[idx]++;
                }
            });
        });

        weeklyChart.data.datasets[0].data = dayCounts;
        weeklyChart.data.datasets[1].data = dayCounts.map(c => Math.round((c / totalHabits) * 100));
        weeklyChart.update();
    } catch (e) {
        console.error("Chart refresh error:", e);
    }
}

// ========================================================
// 3. Month & Week Filters
// ========================================================
function onDateFilterChange() {
    const monthSelect = document.getElementById("month-select");
    const yearSelect = document.getElementById("year-select");
    const monthNum = monthSelect ? monthSelect.value : (new Date().getMonth() + 1);
    const yearNum = yearSelect ? yearSelect.value : (new Date().getFullYear());
    window.location.href = `/?month=${monthNum}&year=${yearNum}`;
}

function onMonthChange(monthNum) {
    onDateFilterChange();
}

// ========================================================
// 4. Habit Modals (Add, Edit, Delete, Reset)
// ========================================================
function openHabitModal() {
    document.getElementById("modal-title").textContent = "Add New Habit";
    document.getElementById("form-habit-id").value = "";
    document.getElementById("form-habit-name").value = "";
    document.getElementById("form-habit-category").value = "Fitness";
    document.getElementById("form-habit-icon").value = "🎯";
    document.getElementById("form-habit-color").value = "#10b981";
    document.getElementById("form-habit-desc").value = "";
    document.getElementById("habit-modal").style.display = "flex";
}

function openEditModal(id, name, category, desc, icon, color) {
    document.getElementById("modal-title").textContent = "Edit Habit";
    document.getElementById("form-habit-id").value = id;
    document.getElementById("form-habit-name").value = name;
    document.getElementById("form-habit-category").value = category;
    document.getElementById("form-habit-icon").value = icon;
    document.getElementById("form-habit-color").value = color;
    document.getElementById("form-habit-desc").value = desc;
    document.getElementById("habit-modal").style.display = "flex";
}

function closeHabitModal() {
    document.getElementById("habit-modal").style.display = "none";
}

async function handleHabitSubmit(event) {
    event.preventDefault();
    const id = document.getElementById("form-habit-id").value;
    const name = document.getElementById("form-habit-name").value.trim();
    const category = document.getElementById("form-habit-category").value;
    const icon = document.getElementById("form-habit-icon").value.trim() || "🎯";
    const color = document.getElementById("form-habit-color").value;
    const desc = document.getElementById("form-habit-desc").value.trim();

    if (!name) return;

    try {
        let res;
        if (id) {
            // Update
            res = await fetch(`/api/habits/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, category, icon, color, description: desc })
            });
        } else {
            // Create
            res = await fetch("/api/habits", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, category, icon, color, description: desc })
            });
        }

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Operation failed");

        closeHabitModal();
        showToast(id ? "Habit updated!" : "Habit created!");
        setTimeout(() => window.location.reload(), 400);

    } catch (err) {
        showToast("Error: " + err.message);
    }
}

async function deleteHabit(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
        const res = await fetch(`/api/habits/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Delete failed");
        showToast("Habit deleted");
        const row = document.getElementById(`habit-row-${id}`);
        if (row) row.remove();
        setTimeout(() => window.location.reload(), 400);
    } catch (err) {
        showToast("Error deleting habit");
    }
}

function openManageModal() {
    document.getElementById("manage-modal").style.display = "flex";
}

function closeManageModal() {
    document.getElementById("manage-modal").style.display = "none";
}

async function resetDefaultHabits() {
    if (!confirm("This will reset all habits to the 10 default habits. Continue?")) return;
    try {
        const res = await fetch("/api/habits/reset-defaults", { method: "POST" });
        if (!res.ok) throw new Error("Reset failed");
        showToast("Reset to 10 default habits!");
        closeManageModal();
        setTimeout(() => window.location.reload(), 500);
    } catch (e) {
        showToast("Failed to reset habits");
    }
}

// ========================================================
// 5. Toast System
// ========================================================
let toastTimer = null;
function showToast(message) {
    const toast = document.getElementById("toast");
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2400);
}
