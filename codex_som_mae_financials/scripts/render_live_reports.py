"""
render_live_reports.py - render redesigned MAE reports from a live-session payload
"""

import sys
from pathlib import Path

from live_workflow import BASE_DIR, PAYLOAD_TEMPLATE_PATH, render_report_bundle


def main():
    if len(sys.argv) > 1:
        payload_path = Path(sys.argv[1])
    else:
        payload_path = BASE_DIR / "data" / "extracted" / "live_report_payload.json"

    if not payload_path.exists():
        raise FileNotFoundError(
            f"Missing payload file: {payload_path}\n"
            f"Start from the template at: {PAYLOAD_TEMPLATE_PATH}"
        )

    outputs = render_report_bundle(payload_path)
    print("Rendered reports:")
    for path in outputs:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
