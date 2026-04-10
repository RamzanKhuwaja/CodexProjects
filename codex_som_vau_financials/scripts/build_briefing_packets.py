"""
build_briefing_packets.py - som_vau_financials
==============================================
Reads data/extracted/run_data.json and writes a compact advisory packet for
the 4 VAU brief areas:

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

    tuition = rev["ytd_tuition_current"]
    yoy = rev["yoy_growth_pct"]
    spent = mkt["total_ytd_current"]
    obligation = mkt["obligation_projected"] or mkt["obligation_ytd"]
    gap = mkt["gap_projected"] or mkt["gap_ytd"]
    ftc = mkt["accounts"].get("6201.2 FTC", {}).get("current", 0.0)

    flags = []
    if gap and gap > 0:
        flags.append(f"Marketing gap still open: {money(gap)}")
    if ftc == 0:
        flags.append("FTC is still $0 this year and may be missing or deferred")

    return {
        "topic": "marketing",
        "title": "VAU Marketing Brief",
        "facts": [
            f"YTD tuition: {money(tuition)} ({pct(yoy)} vs prior year)",
            f"Marketing spent so far: {money(spent)}",
            f"Projected full-year obligation: {money(obligation)}",
        ],
        "flags": flags,
        "ask": "Should the final report push a stronger action tone on monthly marketing catch-up?",
    }


def build_tax_packet(data):
    inc = data["income"]
    tax = data["tax"]
    mkt = data["marketing"]

    h1_pretax = inc["h1_pretax_proxy"]
    sbd_limit = tax["historical_reference"]["sbd_limit"]

    flags = []
    if h1_pretax > sbd_limit:
        flags.append(f"H1 pre-tax already exceeds SBD limit by {money(h1_pretax - sbd_limit)}")
    if (mkt.get("gap_projected") or 0) > 0:
        flags.append("Remaining marketing spend can still reduce taxable income")
    if not tax.get("installments"):
        flags.append("Installment payment status is not derived from the provided files")

    return {
        "topic": "tax",
        "title": "VAU Tax Brief",
        "facts": [
            f"H1 pre-tax proxy: {money(h1_pretax)}",
            f"SBD limit: {money(sbd_limit)}",
            f"Last year's total tax: {money(tax['historical_reference']['prior_total_tax'])}",
        ],
        "flags": flags,
        "ask": "Should the final report emphasize cash-flow planning or tax-planning first?",
    }


def build_deviation_packet(data):
    exp = data["expenses"]

    handouts = exp.get("5780", {})
    service_fee = exp.get("5711", {})
    auto = exp.get("6300_total", {})

    flags = []
    if handouts:
        flags.append(f"Student Handouts: {pct(handouts.get('change_pct'))} vs prior year")
    if service_fee.get("current_ytd", 0) > 0:
        flags.append(f"Service Fee 5711 is new this year at {money(service_fee.get('current_ytd'))}")
    if auto:
        flags.append(f"Automobile costs: {pct(auto.get('change_pct'))} vs prior year")

    return {
        "topic": "deviation",
        "title": "VAU Deviation Brief",
        "facts": [
            "Goal: highlight CRA-risk spending changes that need explanation",
            f"Service Fee 5711 current year: {money(service_fee.get('current_ytd', 0.0))}",
            f"Student Handouts current year: {money(handouts.get('current_ytd', 0.0))}",
        ],
        "flags": flags,
        "ask": "Should the final report focus more on CRA audit risk or bookkeeping cleanup?",
    }


def build_shareholder_packet(data):
    sh = data["shareholder"]
    ramzan = sh["ramzan"]["closing_balance"]
    farah = sh["farah"]["closing_balance"]
    parent = sh["parent_2900"]["closing_balance"]
    net_total = sh["net_current_balance"]

    hajj_total = 0.0
    for tx in sh["ramzan"]["transactions"]:
        memo = (tx.get("memo") or "").lower()
        if "hajj" in memo:
            hajj_total += abs(tx.get("amount", 0.0))

    flags = []
    if ramzan < 0:
        flags.append(f"Ramzan owes the corporation {money(abs(ramzan))}")
    if hajj_total > 0:
        flags.append(f"Hajj payments inside shareholder account: {money(hajj_total)}")

    return {
        "topic": "shareholder",
        "title": "VAU Shareholder Brief",
        "facts": [
            f"Real net owed to company: {money(abs(net_total))}" if net_total < 0 else f"Company owes shareholders net: {money(net_total)}",
            f"Parent 2900 offset: {money(parent)}",
            f"Raw subaccounts: Ramzan {money(ramzan)} | Farah {money(farah)}",
        ],
        "flags": flags,
        "ask": "Should the final report focus more on the real net amount owed or on cleaning up the QuickBooks presentation?",
    }


def main():
    data = load_run_data()

    packets = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "company": "VAU",
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
