"""
Habit CRM - Master Automated Test Runner & Regression Safety Suite
==================================================================
Runs all domain, security, navigation, streak, chart, and isolation
tests across all 12 test suites.
Usage:
    python run_all_tests.py
"""
import sys
import subprocess
import time

TEST_SUITES = [
    ("Step 6: Dates & Weekly Boundaries", "tests/test_step6_dates.py"),
    ("Step 7: Habit CRUD & Archival", "tests/test_step7_crud_archival.py"),
    ("Step 8: Habit Logs & Reflection Notes", "tests/test_step8_habit_logs.py"),
    ("Step 9: Metrics, Streaks & Analytics", "tests/test_step9_metrics_streaks.py"),
    ("Step 10: Dynamic Charts & Data Endpoints", "tests/test_step10_charts.py"),
    ("Step 11: Controls & Form Validation", "tests/test_step11_controls.py"),
    ("Step 12: Desktop Layout & Grid Structure", "tests/test_step12_ui_layout.py"),
    ("Step 13: Top Performer & Consistency Insights", "tests/test_step13_visual_elements.py"),
    ("Step 14: Responsive Breakpoints & Accessibility", "tests/test_step14_responsive_a11y.py"),
    ("Step 15: Security Hardening & Rate Limiting", "tests/test_step15_security.py"),
    ("Step 16: Cross-User Isolation & Auth Boundaries", "tests/test_step16_user_isolation.py"),
    ("Step 16: Alembic Migrations on Fresh DB", "tests/test_step16_migrations.py"),
    ("Step 17: Performance & Query Optimization", "tests/test_step17_performance.py"),
]

def main():
    print("=" * 70)
    print("          HABIT CRM — PHASE 1 MASTER AUTOMATED TEST SUITE          ")
    print("=" * 70)
    print(f"Executing {len(TEST_SUITES)} test suites...\n")

    start_total = time.time()
    results = []
    any_failed = False

    for name, script in TEST_SUITES:
        suite_start = time.time()
        print(f"--> Running: {name} ({script})...", end=" ", flush=True)
        res = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True
        )
        elapsed = round(time.time() - suite_start, 2)
        if res.returncode == 0:
            print(f"[PASS] ({elapsed}s)")
            results.append((name, script, "PASS", elapsed, ""))
        else:
            print(f"[FAIL] ({elapsed}s)")
            error_preview = (res.stderr or res.stdout)[-350:].strip()
            results.append((name, script, "FAIL", elapsed, error_preview))
            any_failed = True

    total_time = round(time.time() - start_total, 2)
    print("\n" + "=" * 70)
    print("                          TEST SUMMARY REPORT                      ")
    print("=" * 70)
    for name, script, status, elapsed, err in results:
        status_tag = f"[{status}]"
        print(f"{status_tag:8} {name:<46} ({elapsed}s)")
        if err:
            print(f"         Error: {err}\n")

    print("-" * 70)
    passed_count = sum(1 for r in results if r[2] == "PASS")
    print(f"Total Suites: {len(TEST_SUITES)} | Passed: {passed_count} | Failed: {len(TEST_SUITES) - passed_count}")
    print(f"Total Execution Time: {total_time}s")
    print("=" * 70)

    if any_failed:
        sys.exit(1)
    else:
        print("\nAll 12 test suites passed successfully! Regression coverage confirmed.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
