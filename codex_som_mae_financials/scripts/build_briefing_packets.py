"""
build_briefing_packets.py - som_mae_financials
==============================================
Reads data/extracted/run_data.json and writes a compact advisory packet for
the 4 MAE brief areas:

- marketing
- tax
- deviation
- shareholder

The packet is meant for Codex to read before presenting one short on-screen
brief at a time to Ramzan.
"""

import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_DATA_PATH = os.path.join(BASE_DIR, "data", "extracted", "run_data.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "extracted", "briefing_packets.json")


def load_run_data():
    with open(RUN_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def money(value):
    if value is None:
        return "n/a"
    if abs(value) < 0.005:
        return "$0"
    if value < 0:
        return f"-${abs(value):,.0f}"
    return f"${value:,.0f}"


def pct(value):
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def build_marketing_packet(data):
    rev = data["revenue"]
    mkt = data["marketing"]
    ftc = mkt["accounts"].get("6201.1 FTC", {}).get("current", 0.0)
    gap = mkt.get("gap_projected") or mkt.get("gap_conservative")
    obligation = mkt.get("obligation_projected") or mkt.get("obligation_conservative")

    flags = []
    if gap and gap > 0:
        flags.append(f"Marketing gap still open: {money(gap)}")
    if ftc < 10000:
        flags.append(f"FTC looks low at {money(ftc)} compared with prior year")

    return {
        "topic": "marketing",
        "title": "MAE Marketing Brief",
        "facts": [
            f"YTD tuition: {money(rev['ytd_tuition_current'])} ({pct(rev['yoy_growth_pct'])} vs prior year)",
            f"Marketing spent so far: {money(mkt['total_ytd_current'])}",
            f"Projected full-year obligation: {money(obligation)}",
        ],
        "flags": flags,
        "ask": "Should the final report push harder on the remaining marketing catch-up before July 31?",
    }


def build_tax_packet(data):
    inc = data["income"]
    tax = data["tax"]
    mkt = data["marketing"]

    apr_installment = None
    for item in tax["installments"]:
        if item["due"] == "April 30, 2026":
            apr_installment = item["amount"]
            break

    flags = []
    if apr_installment:
        flags.append(f"April 30 installment due: {money(apr_installment)}")
    if (mkt.get("gap_projected") or 0) > 0:
        flags.append("Remaining marketing spend can still reduce taxable income")
    flags.append("Class 13-a CCA expiry should stay visible in the tax explanation")

    return {
        "topic": "tax",
        "title": "MAE Tax Brief",
        "facts": [
            f"H1 pre-tax proxy: {money(inc['h1_pretax_proxy'])}",
            f"Last year's total tax: {money(tax['fy2024_25']['total_tax'])}",
            f"Installments paid YTD: {money(tax['installments_paid_ytd'])}",
        ],
        "flags": flags,
        "ask": "Should the final report emphasize the immediate cash payment first or the deduction-planning angle first?",
    }


def build_deviation_packet(data):
    exp = data["expenses"]
    handouts = exp.get("5780", {})
    insurance = exp.get("6600", {})

    flags = []
    if handouts:
        flags.append(f"Student Handouts: {pct(handouts.get('change_pct'))} vs prior year")
    if insurance:
        flags.append(f"Insurance: {pct(insurance.get('change_pct'))} vs prior year")
    flags.append("FTC should stay flagged if head-office charges still look unusually low")

    return {
        "topic": "deviation",
        "title": "MAE Deviation Brief",
        "facts": [
            "Goal: highlight unusual expense changes that need explanation before CRA or accountant review",
            f"Student Handouts current year: {money(handouts.get('current_ytd', 0.0))}",
            f"Insurance current year: {money(insurance.get('current_ytd', 0.0))}",
        ],
        "flags": flags,
        "ask": "Should the final report lean more toward CRA-risk wording or management-action wording?",
    }


def summarize_je12(transactions):
    total = 0.0
    for tx in transactions:
        if tx.get("num") == "JE-12":
            total += tx.get("amount", 0.0)
    return total


def build_shareholder_packet(data):
    sh = data["shareholder"]
    ramzan = sh["ramzan"]["closing_balance"]
    rezai = sh["rezai"]["closing_balance"]
    combined = sh["combined_closing"]

    hajj_total = 0.0
    for tx in sh["ramzan"]["transactions"]:
        memo = (tx.get("memo") or "").lower()
        if "hajj" in memo:
            hajj_total += abs(tx.get("amount", 0.0))

    je12_total = summarize_je12(sh["rezai"]["transactions"])

    flags = []
    flags.append(
        f"Current combined shareholder position: company owes shareholders {money(combined)}"
        if combined > 0
        else f"Current combined shareholder position: shareholders owe company {money(abs(combined))}"
    )
    if hajj_total > 0:
        flags.append(f"Hajj payment inside Ramzan shareholder account: {money(hajj_total)}")
    if je12_total > 0:
        flags.append(f"JE-12 credits still need documentation: {money(je12_total)}")

    return {
        "topic": "shareholder",
        "title": "MAE Shareholder Brief",
        "facts": [
            f"Ramzan closing balance: {money(ramzan)}",
            f"Rezai closing balance: {money(rezai)}",
            f"Combined closing balance: {money(combined)}",
        ],
        "flags": flags,
        "ask": "Should the final report focus more on documentation gaps or on the current balances themselves?",
    }


def main():
    data = load_run_data()

    packets = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "company": "MAE",
            "cutoff_date": data["meta"]["ytd_cutoff_date"],
        },
        "briefs": [
            build_marketing_packet(data),
            build_tax_packet(data),
            build_deviation_packet(data),
            build_shareholder_packet(data),
        ],
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(packets, f, indent=2, ensure_ascii=False)

    print(f"Saved briefing packets: {OUTPUT_PATH}")
    print("Topics prepared: marketing, tax, deviation, shareholder")


if __name__ == "__main__":
    main()
