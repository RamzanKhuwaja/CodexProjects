import sys

import Common.my_utils as utils

CAMPUS = "MAE"
CLASS_LIST_DIR = getattr(utils, "MAE_CLASS_LIST_DIR")


def main() -> bool:
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    print(f"Entering Check to FindDupStudentsIn {CAMPUS} BSViaClassList.")
    try:
        result = utils.FindDupStudentsInBSViaClassList(CLASS_LIST_DIR)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaClassList crashed for {CLASS_LIST_DIR}: {exc}")
        return False

    if result:
        print(f"Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")
        return True
    else:
        print(f"WARNING: Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")
        return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
