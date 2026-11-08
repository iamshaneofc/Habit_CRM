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

    if (weeklyChart) {
        weeklyChart.destroy();
    }

    const labels = INITIAL_DAILY_DATA.map(d => d.day_name);
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

    if (categoryChart) {
        categoryChart.destroy();
    }

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

    if (buttonElement.dataset.loading === "true") return;
    buttonElement.dataset.loading = "true";

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

        // Authoritative server state sync
        if (data.completed) {
            buttonElement.classList.add("is-checked");
        } else {
            buttonElement.classList.remove("is-checked");
        }

        // Update streak display
        const streakEl = document.getElementById(`streak-${habitId}`);
        if (streakEl) {
            streakEl.textContent = `${data.current_streak}d`;
        }
        const longestEl = document.getElementById(`longest-streak-${habitId}`);
        if (longestEl && data.longest_streak !== undefined) {
            longestEl.textContent = `/${data.longest_streak}d`;
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
        refreshCategoryChart();

        showToast(data.completed ? "Habit marked complete! 🎉" : "Habit unchecked");

    } catch (err) {
        // Rollback optimistic state on error
        if (currentlyChecked) {
            buttonElement.classList.add("is-checked");
        } else {
            buttonElement.classList.remove("is-checked");
        }
        showToast("Error updating habit: " + err.message);
    } finally {
        buttonElement.dataset.loading = "false";
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
        const res = await fetch(`/api/charts/weekly-data?week_date=${encodeURIComponent(CURRENT_WEEK_DATE)}`);
        if (!res.ok) throw new Error("Weekly chart fetch failed");
        const data = await res.json();

        weeklyChart.data.labels = data.labels;
        weeklyChart.data.datasets[0].data = data.completed;
        weeklyChart.data.datasets[1].data = data.percentages;
        weeklyChart.update();
    } catch (e) {
        console.warn("API chart refresh failed, falling back to client DOM calculation:", e);
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
    }
}

async function refreshCategoryChart() {
    if (!categoryChart) return;
    try {
        const monthSelect = document.getElementById("month-select");
        const yearSelect = document.getElementById("year-select");
        const m = monthSelect ? monthSelect.value : "";
        const y = yearSelect ? yearSelect.value : "";

        const res = await fetch(`/api/charts/category-data?month=${m}&year=${y}`);
        if (!res.ok) throw new Error("Category chart fetch failed");
        const json = await res.json();

        const labels = Object.keys(json.categories);
        const data = Object.values(json.categories);
        const palette = [
            '#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b',
            '#84cc16', '#6366f1', '#ec4899', '#14b8a6', '#f97316'
        ];

        categoryChart.data.labels = labels;
        categoryChart.data.datasets[0].data = data;
        categoryChart.data.datasets[0].backgroundColor = palette.slice(0, labels.length);
        categoryChart.update();
    } catch (e) {
        console.warn("Category chart refresh error:", e);
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
// 4. Habit Modals (Add, Edit, Archive, Restore, Reset)
// ========================================================
function openHabitModal() {
    document.getElementById("modal-title").textContent = "Add New Habit";
    document.getElementById("form-habit-id").value = "";
    document.getElementById("form-habit-name").value = "";
    document.getElementById("form-habit-name").style.borderColor = "";
    document.getElementById("form-habit-category").value = "Fitness";
    document.getElementById("form-habit-icon").value = "🎯";
    document.getElementById("form-habit-color").value = "#10b981";
    document.getElementById("form-habit-target").value = "1";
    document.getElementById("form-habit-desc").value = "";
    document.getElementById("habit-modal").style.display = "flex";
    setTimeout(() => {
        const input = document.getElementById("form-habit-name");
        if (input) input.focus();
    }, 50);
}

function openEditModal(id, name, category, desc, icon, color, dailyTarget) {
    document.getElementById("modal-title").textContent = "Edit Habit";
    document.getElementById("form-habit-id").value = id;
    document.getElementById("form-habit-name").value = name;
    document.getElementById("form-habit-name").style.borderColor = "";
    document.getElementById("form-habit-category").value = category;
    document.getElementById("form-habit-icon").value = icon;
    document.getElementById("form-habit-color").value = color;
    document.getElementById("form-habit-target").value = dailyTarget || 1;
    document.getElementById("form-habit-desc").value = desc;
    document.getElementById("habit-modal").style.display = "flex";
    setTimeout(() => {
        const input = document.getElementById("form-habit-name");
        if (input) input.focus();
    }, 50);
}

function closeHabitModal() {
    document.getElementById("habit-modal").style.display = "none";
}

async function handleHabitSubmit(event) {
    event.preventDefault();
    const id = document.getElementById("form-habit-id").value;
    const nameInput = document.getElementById("form-habit-name");
    const name = nameInput.value.trim();
    const category = document.getElementById("form-habit-category").value;
    const icon = document.getElementById("form-habit-icon").value.trim() || "🎯";
    const color = document.getElementById("form-habit-color").value;
    const dailyTarget = parseInt(document.getElementById("form-habit-target").value) || 1;
    const desc = document.getElementById("form-habit-desc").value.trim();
    const saveBtn = document.getElementById("modal-save-btn");

    if (!name) {
        nameInput.focus();
        nameInput.style.borderColor = "#ef4444";
        showToast("Please enter a habit name.");
        return;
    }
    nameInput.style.borderColor = "";

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving...";
    }

    try {
        let res;
        const payload = {
            name,
            category,
            icon,
            color,
            daily_target: dailyTarget,
            description: desc
        };

        if (id) {
            // Update
            res = await fetch(`/api/habits/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            // Create
            res = await fetch("/api/habits", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Operation failed");

        closeHabitModal();
        showToast(id ? "Habit updated!" : "Habit created!");
        setTimeout(() => window.location.reload(), 300);

    } catch (err) {
        showToast("Error: " + err.message);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Habit";
        }
    }
}

async function archiveHabit(id, name) {
    if (!confirm(`Are you sure you want to archive "${name}"?\nPast logs and stats will be preserved.`)) return;

    try {
        const res = await fetch(`/api/habits/${id}/archive`, { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to archive habit");
        showToast("Habit archived (history preserved)");
        const row = document.getElementById(`habit-row-${id}`);
        if (row) row.remove();
        setTimeout(() => window.location.reload(), 400);
    } catch (err) {
        showToast("Error: " + err.message);
    }
}

async function deleteHabit(id, name) {
    archiveHabit(id, name);
}

function openManageModal() {
    document.getElementById("manage-modal").style.display = "flex";
    loadArchivedHabits();
}

function closeManageModal() {
    document.getElementById("manage-modal").style.display = "none";
}

async function loadArchivedHabits() {
    const listEl = document.getElementById("archived-habits-list");
    if (!listEl) return;
    listEl.innerHTML = '<span style="font-size: 0.8rem; color: var(--text-muted);">Loading...</span>';

    try {
        const res = await fetch("/api/habits/archived");
        const habits = await res.json();
        if (!res.ok) throw new Error("Failed to load archived habits");

        if (!habits || habits.length === 0) {
            listEl.innerHTML = '<span style="font-size: 0.8rem; color: var(--text-muted);">No archived habits.</span>';
            return;
        }

        listEl.innerHTML = habits.map(h => `
            <div class="archived-item" style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>${h.icon || '🎯'}</span>
                    <strong style="font-size: 0.85rem; color: #fff;">${h.name}</strong>
                    <span style="font-size: 0.7rem; color: var(--text-muted); background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">${h.category}</span>
                </div>
                <div style="display: flex; gap: 0.4rem;">
                    <button type="button" class="btn btn-sm btn-outline" onclick="restoreHabit(${h.id}, '${h.name}')" title="Restore to active tracker">↩️ Restore</button>
                    <button type="button" class="btn btn-sm btn-danger" onclick="deletePermanently(${h.id}, '${h.name}')" title="Permanently delete">🗑️ Delete</button>
                </div>
            </div>
        `).join("");
    } catch (err) {
        listEl.innerHTML = `<span style="font-size: 0.8rem; color: #ef4444;">Error: ${err.message}</span>`;
    }
}

async function restoreHabit(id, name) {
    try {
        const res = await fetch(`/api/habits/${id}/restore`, { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to restore habit");
        showToast(`Habit "${name}" restored!`);
        setTimeout(() => window.location.reload(), 400);
    } catch (err) {
        showToast("Error: " + err.message);
    }
}

async function deletePermanently(id, name) {
    if (!confirm(`Permanently delete "${name}"?\nWarning: This will permanently delete all historical logs for this habit.`)) return;
    try {
        const res = await fetch(`/api/habits/${id}?permanent=true`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to permanently delete");
        showToast(`Habit "${name}" deleted permanently.`);
        loadArchivedHabits();
    } catch (err) {
        showToast("Error: " + err.message);
    }
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

// ========================================================
// 6. Habit Log Reflection Notes
// ========================================================
function openNoteModal(habitId, habitName, dateStr) {
    document.getElementById("note-habit-id").value = habitId;
    document.getElementById("note-date").value = dateStr;
    document.getElementById("note-modal-title").textContent = `Note — ${habitName}`;
    document.getElementById("note-modal-subtitle").textContent = `Log reflection for ${dateStr}`;
    
    const tickBtn = document.getElementById(`tick-${habitId}-${dateStr}`);
    const existingNote = tickBtn ? (tickBtn.getAttribute("data-notes") || "") : "";
    document.getElementById("form-note-text").value = existingNote;
    document.getElementById("note-modal").style.display = "flex";
    setTimeout(() => {
        const textInput = document.getElementById("form-note-text");
        if (textInput) textInput.focus();
    }, 50);
}

function closeNoteModal() {
    document.getElementById("note-modal").style.display = "none";
}

async function handleNoteSubmit(event) {
    event.preventDefault();
    const habitId = document.getElementById("note-habit-id").value;
    const dateStr = document.getElementById("note-date").value;
    const notes = document.getElementById("form-note-text").value.trim();
    const saveBtn = document.getElementById("note-save-btn");

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving...";
    }

    try {
        const res = await fetch("/api/habits/notes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ habit_id: parseInt(habitId), date: dateStr, notes })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to save note");

        // Update UI attributes
        const tickBtn = document.getElementById(`tick-${habitId}-${dateStr}`);
        if (tickBtn) {
            tickBtn.setAttribute("data-notes", notes);
        }
        const noteBtn = document.getElementById(`note-btn-${habitId}-${dateStr}`);
        if (noteBtn) {
            if (notes) {
                noteBtn.classList.add("has-note");
                noteBtn.title = `Note: ${notes}`;
            } else {
                noteBtn.classList.remove("has-note");
                noteBtn.title = "Add reflection note";
            }
        }

        closeNoteModal();
        showToast(notes ? "Note saved! 📝" : "Note cleared.");
    } catch (err) {
        showToast("Error saving note: " + err.message);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Note";
        }
    }
}

// ========================================================
// 7. Demo Account Management
// ========================================================
async function resetDemoData() {
    const btn = document.getElementById("btn-reset-demo");
    const originalText = btn ? btn.textContent : "🔄 Reset Demo Data";
    if (btn) {
        btn.disabled = true;
        btn.textContent = "Resetting...";
    }
    try {
        const res = await fetch("/api/auth/reset-demo", { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Reset failed");
        showToast("Demo data refreshed to showcase state! ⚡");
        setTimeout(() => window.location.reload(), 700);
    } catch (err) {
        showToast("Error: " + err.message);
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }
}

// Global modal listeners: Escape key to close, click backdrop to close
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        closeHabitModal();
        closeManageModal();
        closeNoteModal();
    }
});

document.addEventListener("click", (e) => {
    if (e.target && e.target.classList.contains("modal-backdrop")) {
        e.target.style.display = "none";
    }
});


// ========================================================
// 8. FOCUS OS Visual Charts & Interactive Handlers
// ========================================================
let dailyProdChart = null;
let cumulativeChart = null;

function initFocusOSCharts() {
    initDailyProductivityChart();
    initCumulativeChart();
}

function initDailyProductivityChart() {
    const ctx = document.getElementById("dailyProductivityBarChart");
    if (!ctx) return;

    if (dailyProdChart) {
        dailyProdChart.destroy();
    }

    let labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    let values = [0, 0, 0, 0, 0, 0, 0];

    if (typeof INITIAL_DAILY_BARS !== "undefined" && Array.isArray(INITIAL_DAILY_BARS) && INITIAL_DAILY_BARS.length > 0) {
        labels = INITIAL_DAILY_BARS.map(d => d.day);
        values = INITIAL_DAILY_BARS.map(d => d.val);
    } else if (typeof INITIAL_DAILY_DATA !== "undefined" && Array.isArray(INITIAL_DAILY_DATA) && INITIAL_DAILY_DATA.length > 0) {
        labels = INITIAL_DAILY_DATA.map(d => d.day_name);
        values = INITIAL_DAILY_DATA.map(d => d.hours !== undefined ? d.hours : d.completed_count);
    }

    dailyProdChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: function(context) {
                    const chart = context.chart;
                    const {ctx, chartArea} = chart;
                    if (!chartArea) return '#10b981';
                    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    gradient.addColorStop(0, '#06b6d4');
                    gradient.addColorStop(1, '#10b981');
                    return gradient;
                },
                borderRadius: 5,
                borderSkipped: false,
                barPercentage: 0.52
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.raw}h logged`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { display: false }
                }
            }
        }
    });
}

function initCumulativeChart() {
    const ctx = document.getElementById("cumulativeProgressChart");
    if (!ctx) return;

    if (cumulativeChart) {
        cumulativeChart.destroy();
    }

    const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const rows = document.querySelectorAll(".focus-habit-row, .focus-habit-tr");
    const datasets = [];
    const defaultColors = ['#10b981', '#38bdf8', '#8b5cf6', '#f59e0b', '#84cc16', '#ec4899'];

    rows.forEach((row, rIdx) => {
        if (rIdx >= 5) return;
        const nameEl = row.querySelector(".domain-label");
        const name = nameEl ? nameEl.textContent.trim() : `Habit ${rIdx + 1}`;
        const chips = row.querySelectorAll(".hour-chip");
        let sum = 0;
        const cumData = [];
        chips.forEach(chip => {
            const hrs = parseFloat(chip.getAttribute("data-hours")) || 0;
            sum += hrs;
            cumData.push(parseFloat(sum.toFixed(1)));
        });

        const dot = row.querySelector(".domain-dot");
        const color = (dot && dot.style.backgroundColor) ? dot.style.backgroundColor : defaultColors[rIdx % defaultColors.length];

        datasets.push({
            label: name,
            data: cumData.length === 7 ? cumData : [0, 0, 0, 0, 0, 0, 0],
            borderColor: color,
            borderWidth: 2,
            tension: 0.35,
            pointRadius: 0
        });
    });

    if (datasets.length === 0) {
        datasets.push({
            label: 'No Habits',
            data: [0, 0, 0, 0, 0, 0, 0],
            borderColor: '#10b981',
            borderWidth: 2
        });
    }

    cumulativeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 9 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 9 }, stepSize: 2 }
                }
            }
        }
    });
}

function setFocusTab(btn, tab) {
    document.querySelectorAll(".focus-tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    showToast(`Switched to ${btn.textContent} view ⚡`);
}

function toggleGoalItem(el) {
    el.classList.toggle("checked");
    const circle = el.querySelector(".goal-circle");
    if (el.classList.contains("checked")) {
        circle.textContent = "✔";
        showToast("Goal marked complete!");
    } else {
        circle.textContent = "○";
    }
}

async function updateHeatmapCell(dateStr) {
    try {
        const res = await fetch("/api/analytics/heatmap?weeks=32");
        if (!res.ok) return;
        const data = await res.json();
        if (!data || !data.weeks) return;
        for (const week of data.weeks) {
            for (const cell of week) {
                if (cell.date === dateStr) {
                    const el = document.querySelector(`.gh-cell[data-date="${dateStr}"]`);
                    if (el) {
                        el.className = `gh-cell level-${cell.level}`;
                        el.setAttribute("title", cell.tooltip);
                        el.setAttribute("data-completed", cell.completed);
                        el.setAttribute("data-hours", cell.hours);
                        el.setAttribute("data-pct", cell.percentage);
                    }
                    return;
                }
            }
        }
    } catch (e) {
        console.warn("Heatmap update", e);
    }
}

async function toggleFocusCell(btn, event) {
    if (event) { openHourDropdown(btn, event); return; }
    const habitId = btn.getAttribute("data-habit-id");
    const dateStr = btn.getAttribute("data-date");
    let currentHours = parseInt(btn.getAttribute("data-hours")) || 0;
    
    // Cycle hours: 0 -> 2 -> 4 -> 6 -> 8 -> 10 -> 0 (cleanly handling any starting value)
    const sequence = [0, 2, 4, 6, 8, 10];
    let nextIdx = 1;
    let foundIdx = sequence.indexOf(currentHours);
    if (foundIdx !== -1) {
        nextIdx = (foundIdx + 1) % sequence.length;
    } else {
        nextIdx = sequence.findIndex(h => h > currentHours);
        if (nextIdx === -1) nextIdx = 0;
    }
    let newHours = sequence[nextIdx];

    btn.setAttribute("data-hours", newHours);
    const chipText = btn.querySelector(".chip-text");
    if (chipText) chipText.textContent = `${newHours}h`;

    btn.className = `hour-chip ${newHours === 0 ? 'chip-zero' : 'chip-active chip-h-' + newHours}`;

    try {
        const res = await fetch("/api/habits/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                habit_id: parseInt(habitId),
                date: dateStr,
                value: newHours
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Sync failed");

        btn.setAttribute("data-completed", data.completed ? "true" : "false");
        btn.setAttribute("data-hours", data.value);
        if (chipText) chipText.textContent = `${data.value}h`;
        btn.className = `hour-chip ${data.value === 0 ? 'chip-zero' : 'chip-active chip-h-' + data.value}`;

        const pctEl = document.getElementById("metric-week-pct");
        if (pctEl && data.overall_week_pct !== undefined) {
            pctEl.textContent = `${data.overall_week_pct}%`;
        }
        const streakEl = document.getElementById("metric-best-streak");
        if (streakEl && data.current_streak !== undefined) {
            streakEl.textContent = `${data.current_streak} Days`;
        }

        // Live update heatmap cell and cumulative chart
        updateHeatmapCell(dateStr);
        initCumulativeChart();

        showToast(newHours > 0 ? `Logged ${newHours}h for ${dateStr}!` : "Cleared day logs");
    } catch (err) {
        showToast("Sync error: " + err.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initFocusOSCharts();
});


// ========================================================
// FOCUS OS: HOUR SELECTION DROPDOWN (0 - 10h) & USER GOALS
// ========================================================
let activeHourPopover = null;

function closeHourDropdown() {
    if (activeHourPopover) {
        activeHourPopover.remove();
        activeHourPopover = null;
    }
}

document.addEventListener("click", function(e) {
    if (!e.target.closest(".hour-dropdown-popover") && !e.target.closest(".hour-chip")) {
        closeHourDropdown();
    }
});

document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") closeHourDropdown();
});

function openHourDropdown(btn, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    // Toggle close if clicking same active button
    if (activeHourPopover && activeHourPopover._targetBtn === btn) {
        closeHourDropdown();
        return;
    }
    closeHourDropdown();

    const currentHours = parseInt(btn.getAttribute("data-hours")) || 0;
    
    const popover = document.createElement("div");
    popover.className = "hour-dropdown-popover";
    popover._targetBtn = btn;
    
    // Clear / 0h option
    const zeroBtn = document.createElement("button");
    zeroBtn.type = "button";
    zeroBtn.className = "hour-opt-btn opt-zero" + (currentHours === 0 ? " opt-active" : "");
    zeroBtn.innerHTML = "<span>✕</span> Clear (0h)";
    zeroBtn.onclick = (e) => {
        e.stopPropagation();
        selectHourValue(btn, 0);
        closeHourDropdown();
    };
    popover.appendChild(zeroBtn);

    // 1h to 10h options
    for (let h = 1; h <= 10; h++) {
        const optBtn = document.createElement("button");
        optBtn.type = "button";
        optBtn.className = "hour-opt-btn" + (currentHours === h ? " opt-active" : "");
        optBtn.textContent = `${h}h`;
        optBtn.onclick = (e) => {
            e.stopPropagation();
            selectHourValue(btn, h);
            closeHourDropdown();
        };
        popover.appendChild(optBtn);
    }

    document.body.appendChild(popover);
    activeHourPopover = popover;

    // Position popover relative to button
    const rect = btn.getBoundingClientRect();
    const popHeight = 150;
    const popWidth = 168;
    
    let top = rect.bottom + window.scrollY + 4;
    let left = rect.left + window.scrollX + (rect.width / 2) - (popWidth / 2);

    if (rect.bottom + popHeight > window.innerHeight) {
        top = rect.top + window.scrollY - popHeight - 4;
    }
    if (left + popWidth > window.innerWidth - 10) {
        left = window.innerWidth - popWidth - 10;
    }
    if (left < 10) left = 10;

    popover.style.top = `${top}px`;
    popover.style.left = `${left}px`;
}

async function selectHourValue(btn, newHours) {
    const habitId = btn.getAttribute("data-habit-id");
    const dateStr = btn.getAttribute("data-date");

    btn.setAttribute("data-hours", newHours);
    const chipText = btn.querySelector(".chip-text");
    if (chipText) chipText.textContent = `${newHours}h`;

    btn.className = `hour-chip ${newHours === 0 ? 'chip-zero' : 'chip-active chip-h-' + newHours}`;

    try {
        const res = await fetch("/api/habits/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                habit_id: parseInt(habitId),
                date: dateStr,
                value: newHours
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Sync failed");

        btn.setAttribute("data-completed", data.completed ? "true" : "false");
        btn.setAttribute("data-hours", data.value);
        if (chipText) chipText.textContent = `${data.value}h`;
        btn.className = `hour-chip ${data.value === 0 ? 'chip-zero' : 'chip-active chip-h-' + data.value}`;

        const pctEl = document.getElementById("metric-week-pct");
        if (pctEl && data.overall_week_pct !== undefined) {
            pctEl.textContent = `${data.overall_week_pct}%`;
        }
        const streakEl = document.getElementById("metric-best-streak");
        if (streakEl && data.current_streak !== undefined) {
            streakEl.textContent = `${data.current_streak} Days`;
        }

        updateHeatmapCell(dateStr);
        initCumulativeChart();

        showToast(newHours > 0 ? `Logged ${newHours}h for ${dateStr}!` : `Cleared logs for ${dateStr}`);
    } catch (err) {
        showToast("Sync error: " + err.message);
    }
}

// User-Customizable 5 Goals with Emoji & Color
const DEFAULT_USER_GOALS = [
    { id: 1, emoji: "🎯", color: "#10b981", text: "Sprint 4 Delivery", checked: true },
    { id: 2, emoji: "🚀", color: "#38bdf8", text: "Deploy RAG LLM Microservice", checked: false },
    { id: 3, emoji: "📚", color: "#8b5cf6", text: "Read 50 Pages System Design", checked: false },
    { id: 4, emoji: "💪", color: "#f59e0b", text: "4x Weekly Strength Training", checked: false },
    { id: 5, emoji: "🧘", color: "#ec4899", text: "10m Daily Mindfulness & Sleep", checked: false }
];

function loadUserGoals() {
    try {
        const saved = localStorage.getItem("focus_os_user_goals_v2");
        return saved ? JSON.parse(saved) : DEFAULT_USER_GOALS;
    } catch (e) {
        return DEFAULT_USER_GOALS;
    }
}

function saveUserGoalsList(goals) {
    try {
        localStorage.setItem("focus_os_user_goals_v2", JSON.stringify(goals));
    } catch (e) {}
}

function renderUserGoals() {
    const container = document.getElementById("user-goals-list");
    if (!container) return;
    const goals = loadUserGoals();
    container.innerHTML = "";

    goals.forEach(g => {
        const row = document.createElement("div");
        row.className = "user-goal-row" + (g.checked ? " checked" : "");
        row.innerHTML = `
            <button type="button" class="goal-check-btn" onclick="toggleUserGoalCheck(${g.id})">${g.checked ? "✔" : "○"}</button>
            <span class="goal-emoji-pill" style="border-color: ${g.color}44; background: ${g.color}15;" onclick="promptEditGoalEmoji(${g.id})">${g.emoji}</span>
            <span class="goal-text" contenteditable="true" spellcheck="false" onblur="updateGoalText(${g.id}, this)">${g.text}</span>
            <input type="color" class="goal-color-picker" value="${g.color}" onchange="updateGoalColor(${g.id}, this.value)" title="Change color">
        `;
        container.appendChild(row);
    });
}

function toggleUserGoalCheck(id) {
    const goals = loadUserGoals();
    const g = goals.find(x => x.id === id);
    if (g) {
        g.checked = !g.checked;
        saveUserGoalsList(goals);
        renderUserGoals();
        showToast(g.checked ? `Completed: ${g.text} 🎯` : `Pending: ${g.text}`);
    }
}

function updateGoalText(id, el) {
    const goals = loadUserGoals();
    const g = goals.find(x => x.id === id);
    if (g) {
        g.text = el.textContent.trim() || `Goal ${id}`;
        saveUserGoalsList(goals);
        showToast("Goal saved!");
    }
}

function updateGoalColor(id, newColor) {
    const goals = loadUserGoals();
    const g = goals.find(x => x.id === id);
    if (g) {
        g.color = newColor;
        saveUserGoalsList(goals);
        renderUserGoals();
    }
}

function promptEditGoalEmoji(id) {
    const goals = loadUserGoals();
    const g = goals.find(x => x.id === id);
    if (g) {
        const nextEmojis = ["🎯", "🚀", "📚", "💪", "🧘", "⚡", "🔥", "🏆", "🧠", "💼"];
        const currIdx = nextEmojis.indexOf(g.emoji);
        g.emoji = nextEmojis[(currIdx + 1) % nextEmojis.length];
        saveUserGoalsList(goals);
        renderUserGoals();
    }
}

// ========================================================
// FOCUS OS: THEME SWITCHER (Light / Dark Mode)
// ========================================================
function initTheme() {
    const saved = localStorage.getItem('focus_os_theme') || 'dark';
    setTheme(saved, false);
}

function setTheme(theme, notify = true) {
    document.documentElement.setAttribute('data-theme', theme);
    if (document.body) {
        if (theme === 'light') {
            document.body.classList.add('theme-light');
        } else {
            document.body.classList.remove('theme-light');
        }
    }
    localStorage.setItem('focus_os_theme', theme);
    const icon = document.querySelector('.theme-icon-indicator');
    if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        btn.title = theme === 'light' ? 'Switch to Dark Mode (🌙)' : 'Switch to Light Mode (☀️)';
    }
    if (typeof initFocusOSCharts === 'function') {
        initFocusOSCharts();
    }
    if (notify && typeof showToast === 'function') {
        showToast(`Switched to ${theme === 'light' ? 'Light' : 'Dark'} Mode ${theme === 'light' ? '☀️' : '🌙'}`);
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    setTheme(current === 'dark' ? 'light' : 'dark', true);
}

// ========================================================
// FOCUS OS: EDIT WEEKLY GOALS MODAL DIALOG
// ========================================================
let activeEditingGoalIdx = 0;

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function openGoalsModal() {
    const modal = document.getElementById('goals-modal');
    if (!modal) return;
    const goals = loadUserGoals();
    const container = document.getElementById('goals-modal-inputs');
    if (container) {
        container.innerHTML = goals.map((g, idx) => `
            <div class="goal-edit-row" data-goal-id="${g.id}">
                <span class="goal-edit-idx">${idx + 1}.</span>
                <button type="button" class="goal-edit-emoji-btn" id="modal-goal-emoji-${idx}" onclick="cycleGoalModalEmoji(${idx})" title="Click to cycle emoji">${g.emoji}</button>
                <input type="text" class="goal-edit-text-input" id="modal-goal-text-${idx}" value="${escapeHtml(g.text)}" placeholder="Enter goal priority..." maxlength="80">
                <input type="color" class="goal-edit-color" id="modal-goal-color-${idx}" value="${g.color || '#10b981'}" title="Accent color">
                <label style="display:inline-flex; align-items:center; gap:4px; font-size:0.74rem; color:var(--text-muted, #94a3b8); cursor:pointer;" title="Toggle completed">
                    <input type="checkbox" id="modal-goal-chk-${idx}" ${g.checked ? 'checked' : ''}>
                    <span>Done</span>
                </label>
            </div>
        `).join('');
    }
    modal.style.display = 'flex';
}

function closeGoalsModal() {
    const modal = document.getElementById('goals-modal');
    if (modal) modal.style.display = 'none';
}

function cycleGoalModalEmoji(idx) {
    activeEditingGoalIdx = idx;
    const btn = document.getElementById(`modal-goal-emoji-${idx}`);
    if (!btn) return;
    const emojis = ["🎯", "🚀", "📚", "💪", "🧘", "⚡", "🔥", "🏆", "🧠", "💼", "💻", "📈", "🎨", "🔬"];
    const curr = btn.textContent.trim();
    const nextIdx = (emojis.indexOf(curr) + 1) % emojis.length;
    btn.textContent = emojis[nextIdx];
}

function applyPresetEmoji(emoji) {
    const btn = document.getElementById(`modal-goal-emoji-${activeEditingGoalIdx}`);
    if (btn) {
        btn.textContent = emoji;
    }
}

function handleGoalsModalSave(e) {
    if (e) e.preventDefault();
    const goals = [];
    for (let i = 0; i < 5; i++) {
        const emojiEl = document.getElementById(`modal-goal-emoji-${i}`);
        const textEl = document.getElementById(`modal-goal-text-${i}`);
        const colorEl = document.getElementById(`modal-goal-color-${i}`);
        const chkEl = document.getElementById(`modal-goal-chk-${i}`);
        goals.push({
            id: i + 1,
            emoji: emojiEl ? emojiEl.textContent.trim() : '🎯',
            text: textEl && textEl.value.trim() ? textEl.value.trim() : `Goal ${i + 1}`,
            color: colorEl ? colorEl.value : '#10b981',
            checked: chkEl ? chkEl.checked : false
        });
    }
    saveUserGoalsList(goals);
    renderUserGoals();
    closeGoalsModal();
    if (typeof showToast === 'function') {
        showToast('5 Weekly Goals saved successfully! 🎯');
    }
}

function resetGoalsModalDefaults() {
    if (!confirm('Reset all 5 weekly goals to default targets?')) return;
    saveUserGoalsList(DEFAULT_USER_GOALS);
    renderUserGoals();
    openGoalsModal();
    if (typeof showToast === 'function') {
        showToast('Goals reset to defaults.');
    }
}

// Global modal close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeGoalsModal();
    }
});

// Auto initialize theme & goals
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    renderUserGoals();
});
