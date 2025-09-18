import sys

import Common.my_utils as utils

CAMPUS = "MAE"


def main() -> bool:
    print(f"Entering {CAMPUS} GenerateStudentMap")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        success = utils.GenerateStudentMap(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: GenerateStudentMap crashed for {CAMPUS}: {exc}")
        return False

    if success:
        print(f"Exiting {CAMPUS} GenerateStudentMap")
    else:
        print(f"ERROR: Exiting {CAMPUS} GenerateStudentMap")
    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
