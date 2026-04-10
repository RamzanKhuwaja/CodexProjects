"""
run_all_reports.py — som_vau_financials
========================================
Master orchestration script.  One command runs the entire pipeline.

Usage (from project root):
    python scripts/run_all_reports.py

Steps:
    1. Verify all 4 source Excel files exist in data/current/
    2. Run extract_data.py  →  data/extracted/run_data.json
    3. Print a brief data snapshot from the JSON
    4. Run generate_marketing_report.py
    5. Run generate_tax_report.py
    6. Run generate_deviation_report.py
    7. Run generate_shareholder_report.py
    8. Run validate_all.py  (skipped if the script does not yet exist)
    9. Print final completion banner
"""

import glob
import json
import os
import subprocess
import sys
from datetime import datetime

# Force UTF-8 output on Windows terminals that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_KEYWORDS = [
    "Profit and Loss - Compare YTD",
    "Profit and Loss - Aug 2022",
    "Shareholder advances - this fiscal year",
    "Shareholder Advances - all dates",
]

REPORT_SCRIPTS = [
    ("scripts/extract_data.py",                "Extract data  -->  run_data.json"),
    ("scripts/generate_marketing_report.py",   "Marketing / Advertising Report  (Task #1)"),
    ("scripts/generate_tax_report.py",         "Corporate Tax Report            (Task #2)"),
    ("scripts/generate_deviation_report.py",   "Spending Deviation Report       (Task #3)"),
    ("scripts/generate_shareholder_report.py", "Shareholder Advances Report     (Task #4)"),
]

VALIDATE_SCRIPT = "scripts/validate_all.py"
RUN_DATA_JSON   = os.path.join(BASE_DIR, "data", "extracted", "run_data.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def header(text):
    width = 62
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def run(script_rel, label):
    """Run a sub-script and stream its output to the terminal in real time."""
    header(label)
    script_abs = os.path.join(BASE_DIR, script_rel)
    result = subprocess.run(
        [sys.executable, script_abs],
        cwd=BASE_DIR,
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"\n  FAILED: {label}  (exit code {result.returncode})")
        sys.exit(result.returncode)


def fmt_currency(value):
    if value is None:
        return "n/a"
    if value < 0:
        return f"-${abs(value):,.0f}"
    return f"${value:,.0f}"


def fmt_pct(value):
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def print_data_snapshot():
    """Read run_data.json and print a brief summary."""
    if not os.path.exists(RUN_DATA_JSON):
        print("  (run_data.json not found — skipping snapshot)")
        return

    with open(RUN_DATA_JSON, "r", encoding="utf-8") as f:
        d = json.load(f)

    meta    = d.get("meta", {})
    revenue = d.get("revenue", {})
    mkt     = d.get("marketing", {})
    sh      = d.get("shareholder", {})

    cutoff  = meta.get("ytd_cutoff_date", "Unknown")
    tuit_cy = revenue.get("ytd_tuition_current", 0.0)
    tuit_py = revenue.get("ytd_tuition_prior_year", 0.0)
    yoy     = revenue.get("yoy_growth_pct")
    mkt_tot = mkt.get("total_ytd_current", 0.0)
    net_sh  = sh.get("net_current_balance")
    parent  = sh.get("parent_2900", {}).get("closing_balance")
    ramzan  = sh.get("ramzan", {}).get("closing_balance")
    farah   = sh.get("farah",  {}).get("closing_balance")

    line = "-" * 52
    print()
    print(line)
    print("  Data snapshot  (run_data.json)")
    print(line)
    print(f"  YTD cutoff:   {cutoff}")
    print(f"  Tuition CY:   {fmt_currency(tuit_cy)}")
    print(f"  Tuition PY:   {fmt_currency(tuit_py)}  ({fmt_pct(yoy)})")
    print(f"  Marketing:    {fmt_currency(mkt_tot)}")
    if net_sh is not None:
        label = "owed to corp" if net_sh < 0 else "owed by corp"
        print(f"  Shareholder:  {fmt_currency(net_sh)}  ({label}, real net)")
    if parent is not None:
        print(f"  Parent 2900:  {fmt_currency(parent)}")
    if ramzan is not None:
        print(f"  Ramzan raw:   {fmt_currency(ramzan)}")
    if farah is not None:
        print(f"  Farah raw:    {fmt_currency(farah)}")
    print(line)


# ---------------------------------------------------------------------------
# Step 1 — verify source files
# ---------------------------------------------------------------------------

def verify_source_files():
    header("Verifying source files in data/current/")
    data_dir = os.path.join(BASE_DIR, "data", "current")
    missing = []
    for keyword in REQUIRED_KEYWORDS:
        matches = (glob.glob(os.path.join(data_dir, f"*{keyword}*.xlsx")) +
                   glob.glob(os.path.join(data_dir, f"*{keyword}*.csv")))
        if matches:
            print(f"  [OK     ]  {os.path.basename(matches[0])}")
        else:
            print(f"  [MISSING]  *{keyword}* (.xlsx or .csv)")
            missing.append(keyword)

    if missing:
        print()
        print("  ERROR: The following required files are missing:")
        for kw in missing:
            print(f"    - *{kw}* (.xlsx or .csv)")
        print()
        print("  Drop the missing QuickBooks exports into data/current/ and re-run.")
        sys.exit(1)

    print()
    print("  All source files present.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    start_time = datetime.now()

    print()
    print("=" * 62)
    print("  SOM VAU FINANCIALS — FULL PIPELINE")
    print(f"  Started: {start_time.strftime('%Y-%m-%d  %H:%M:%S')}")
    print("=" * 62)

    # Step 1: verify source files
    verify_source_files()

    # Steps 2 through 7: run sub-scripts in order
    for script_rel, label in REPORT_SCRIPTS:
        run(script_rel, label)
        if "extract_data" in script_rel:
            print_data_snapshot()

    # Step 8: validate
    validate_abs = os.path.join(BASE_DIR, VALIDATE_SCRIPT)
    if os.path.exists(validate_abs):
        run(VALIDATE_SCRIPT, "Validate all reports  (validate_all.py)")
    else:
        print()
        print(f"  NOTE: {VALIDATE_SCRIPT} not found — validation step skipped.")

    # Step 9: completion banner
    end_time  = datetime.now()
    elapsed   = (end_time - start_time).seconds
    run_date  = end_time.strftime("%Y-%m-%d")

    reports_dir = os.path.join(BASE_DIR, "reports")
    docx_files  = sorted(
        f for f in os.listdir(reports_dir) if f.endswith(".docx")
    ) if os.path.isdir(reports_dir) else []

    print()
    print("=" * 62)
    print("  Reports generated:")
    for fname in docx_files:
        print(f"    reports/{fname}")
    print("=" * 62)
    print()
    width = 62
    border = "#" * width

    def banner_line(text):
        return "#  " + text.ljust(width - 5) + "  #"

    print(border)
    print(banner_line("ALL REPORTS GENERATED" + (" AND VALIDATED" if os.path.exists(validate_abs) else "")))
    print(banner_line("Reports saved in: reports/"))
    print(banner_line(f"Run date: {run_date}"))
    print(banner_line(f"Elapsed: {elapsed}s"))
    print(border)
    print()


if __name__ == "__main__":
    main()
