import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "VAU"


def main() -> bool:
    print(f"Entering {CAMPUS} PrincipalSummary")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        success = utils.send_principal_struggling_summary(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Principal summary failed for {CAMPUS}: {exc}")
        return False

    if success:
        print(f"Exiting {CAMPUS} PrincipalSummary")
    else:
        print(f"ERROR: Exiting {CAMPUS} PrincipalSummary")
    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
