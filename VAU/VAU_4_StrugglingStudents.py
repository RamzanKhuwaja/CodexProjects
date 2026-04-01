import re
import sys
from typing import Optional

import Common.my_utils as utils

_CLASS_CODE_GRADE_PATTERN = re.compile(r"SOMp25([A-Za-z0-9]{1,2})", re.IGNORECASE)
UPPER_GRADE_MESSAGE = (
    "Please find attached the students' academic marks to date. "
    "These results provide an overview of their current progress and areas that may need further support. "
    "Angela will be reaching out to each teacher individually to discuss student performance, classroom observations, "
    "and next steps for supporting their continued growth."
)
LOWER_GRADE_MESSAGE = (
    "Please find attached the students' academic marks to date. "
    "For our lower grade students, these scores are just one indicator of their progress and should be considered "
    "alongside classroom engagement, effort, and growth over time. "
    "Angela will be in touch with each teacher to discuss student performance and next steps for supporting their development."
)

CAMPUS = "VAU"
EMAIL_COLUMNS = [
    "Org Defined ID",
    "Student Full Name",
    "Class Code",
    "Final Grade",
]


def _extract_grade_from_class_code(value: object) -> Optional[int]:
    if not isinstance(value, str):
        return None
    match = _CLASS_CODE_GRADE_PATTERN.search(value)
    if not match:
        return None
    token = match.group(1).upper()
    if not token:
        return None
    if "K" in token:
        return 0
    digits = "".join(ch for ch in token if ch.isdigit())
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def email_struggling_students_to_stakeholders(df_struggling_students) -> bool:
    if df_struggling_students is None or df_struggling_students.empty:
        return True

    missing_cols = [col for col in EMAIL_COLUMNS + ['Teacher Email', 'Teacher Full Name'] if col not in df_struggling_students.columns]
    if missing_cols:
        if hasattr(utils, 'warn_once'):
            utils.warn_once('WARNING', f"Missing columns {missing_cols} in struggling students report; email not sent")
        else:
            print(f"WARNING: Missing columns {missing_cols} in struggling students report; email not sent")
        return False

    if not utils.SEND_EMAIL:
        print('INFO: SEND_EMAIL disabled; skipping struggling student emails.')
        return True

    all_success = True
    for email in df_struggling_students['Teacher Email'].dropna().unique():
        df_teacher = df_struggling_students[df_struggling_students['Teacher Email'] == email]
        if df_teacher.empty:
            continue

        teacher_name = df_teacher['Teacher Full Name'].iloc[0]
        payload = df_teacher[EMAIL_COLUMNS].copy()

        if utils.TESTING:
            to = utils.to_email
            cc = ''
        else:
            to = email
            cc = utils.cc_email

        subject_email = 'Intervention needed for students below performance threshold'
        class_codes = df_teacher['Class Code'].dropna().astype(str)
        grade_levels = [
            grade
            for grade in (_extract_grade_from_class_code(code) for code in class_codes.unique())
            if grade is not None
        ]
        highest_grade = max(grade_levels) if grade_levels else None
        message = (
            LOWER_GRADE_MESSAGE
            if highest_grade is not None and highest_grade <= 4
            else UPPER_GRADE_MESSAGE
        )
        table_html = utils.render_html_table(
            payload,
            title='Students requiring intervention',
            subtitle='These learners currently have cumulative grades below the campus threshold.',
        )
        body_email = (
            f"Hello {teacher_name},<br><br>"
            f"{message}<br><br>"
            f"{table_html}<br><br>"
            'Ramzan Khuwaja'
        )

        if not utils.send_email(to, cc, subject_email, body_email):
            all_success = False
    return all_success


def main() -> bool:
    print(f"Entering {CAMPUS} StrugglingStudents")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        df_struggling_students = utils.FindStrugglingStudents(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindStrugglingStudents failed for {CAMPUS}: {exc}")
        return False

    if df_struggling_students is None or df_struggling_students.empty:
        print(f"No struggling students - Exiting {CAMPUS} StrugglingStudents")
        return True

    emails_ok = email_struggling_students_to_stakeholders(df_struggling_students)
    export_ok = utils.export_struggling_students_to_excel(df_struggling_students, CAMPUS)

    if not export_ok:
        print(f"ERROR: Unable to process struggling students for {CAMPUS}.")
        return False
    if not emails_ok:
        print(f"WARNING: Struggling student emails were not sent for {CAMPUS}.")

    print(f"WARNING: Found struggling students - Exiting {CAMPUS} StrugglingStudents")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
