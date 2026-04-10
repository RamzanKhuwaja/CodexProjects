"""
run_briefing_cycle.py - som_mae_financials
==========================================
Prototype runner for the new MAE brief-first workflow.

It does three things:
1. verifies the required QuickBooks files exist
2. runs extract_data.py
3. runs build_briefing_packets.py

It stops before generating .docx reports.
Codex should then present one short brief at a time on-screen, wait for Ramzan's
plain-English reply, and only generate final reports after approval.
"""

import glob
import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "current")

REQUIRED_KEYWORDS = [
    "Profit and Loss - Compare YTD",
    "Profit and Loss - Aug 2022",
    "Shareholder Advances - this fiscal year",
    "Shareholder Advances - all dates",
]

STEPS = [
    ("scripts/extract_data.py", "Extract data"),
    ("scripts/build_briefing_packets.py", "Build advisory briefing packets"),
]


def verify_source_files():
    missing = []
    print("Checking source files in data/current/")
    for keyword in REQUIRED_KEYWORDS:
        matches = (
            glob.glob(os.path.join(DATA_DIR, f"*{keyword}*.xlsx"))
            + glob.glob(os.path.join(DATA_DIR, f"*{keyword}*.csv"))
        )
        if matches:
            print(f"  OK: {os.path.basename(matches[0])}")
        else:
            print(f"  MISSING: *{keyword}* (.xlsx or .csv)")
            missing.append(keyword)

    if missing:
        print()
        print("Cannot continue until the missing QuickBooks files are added.")
        sys.exit(1)


def run_script(script_rel, label):
    print()
    print(f"=== {label} ===")
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, script_rel)],
        cwd=BASE_DIR,
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"{label} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main():
    print("MAE brief-first prototype")
    verify_source_files()

    for script_rel, label in STEPS:
        run_script(script_rel, label)

    print()
    print("Data package ready.")
    print("Next step for Codex: present 4 short MAE briefs one at a time.")
    print("Do not generate final .docx reports until Ramzan responds to the briefs.")


if __name__ == "__main__":
    main()
