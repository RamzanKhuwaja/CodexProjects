import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "MAE"
CLASS_MAP_PATH = getattr(utils, "MAE_CLASS_MAP_FILE")


def main() -> bool:
    print(f"Entering Check on {CAMPUS}_CLASS_MAP_FILE.")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        success = utils.check_class_map(CLASS_MAP_PATH)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check_class_map failed for {CLASS_MAP_PATH}: {exc}")
        return False

    if success:
        print(f"Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    else:
        print(f"ERROR: Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
