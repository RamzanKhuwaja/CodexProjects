import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "VAU"
EMAIL_COLUMNS = [
    "Class Code",
    "Student Full Name",
    "Last Accessed",
    "Parent Email",
]


def email_to_remind_students(df_remind_students) -> bool:
    if df_remind_students is None or df_remind_students.empty:
        return True

    missing_cols = [col for col in EMAIL_COLUMNS + ['Teacher Email', 'Teacher Full Name'] if col not in df_remind_students.columns]
    if missing_cols:
        if hasattr(utils, 'warn_once'):
            utils.warn_once('WARNING', f"Missing columns {missing_cols} in reminder dataset; email not sent")
        else:
            print(f"WARNING: Missing columns {missing_cols} in reminder dataset; email not sent")
        return False

    if not utils.SEND_EMAIL:
        print('INFO: SEND_EMAIL disabled; skipping reminder emails.')
        return True

    missing_email_rows = df_remind_students['Teacher Email'].isna() | (
        df_remind_students['Teacher Email'].astype(str).str.strip() == ''
    )
    missing_email_count = int(missing_email_rows.sum())
    if missing_email_count:
        if hasattr(utils, 'warn_once'):
            utils.warn_once(
                'WARNING',
                f'{missing_email_count} Brightspace reminder rows are missing teacher email addresses and will not be emailed',
            )
        else:
            print(
                f"WARNING: {missing_email_count} Brightspace reminder rows are missing teacher email addresses and will not be emailed"
            )

    success = True
    for email in df_remind_students['Teacher Email'].dropna().unique():
        df_teacher = df_remind_students[df_remind_students['Teacher Email'] == email]
        if df_teacher.empty:
            continue

        teacher_name = df_teacher['Teacher Full Name'].iloc[0]
        payload = (
            df_teacher[EMAIL_COLUMNS]
            .copy()
            .drop_duplicates()
            .sort_values(['Class Code', 'Student Full Name', 'Last Accessed'])
        )

        if utils.TESTING:
            to = utils.to_email
            cc = ''
        else:
            to = email
            cc = utils.cc_email

        print(
            f"Preparing Brightspace login reminder for {teacher_name} "
            f"({len(payload)} students) -> To: {to}; CC: {cc or '(none)'}"
        )
        subject_email = 'Please remind these students to access Brightspace'
        table_html = utils.render_html_table(
            payload,
            title='Students pending Brightspace login',
            subtitle='No class access recorded in at least two weeks.',
        )
        body_email = (
            f"Hello {teacher_name},<br><br>"
            'Please review the students listed below. Our records show that they have not accessed their Brightspace class in at least two weeks.<br><br>'
            'Please remind them to log in as soon as possible so they can access class materials and so families can review report card comments in Brightspace when needed.<br><br>'
            f"{table_html}<br><br>"
            "Thank you.<br><br>"
            "Sincerely,<br>"
            "Ramzan Khuwaja"
        )

        if not utils.send_email(to, cc, subject_email, body_email):
            success = False
    return success


def main() -> bool:
    print(f"Entering {CAMPUS} RemindForBSLogin")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        df_remind_students = utils.RemindForBSLogin(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: RemindForBSLogin failed for {CAMPUS}: {exc}")
        return False

    if df_remind_students is None or df_remind_students.empty:
        print(f"Exiting {CAMPUS} RemindForBSLogin")
        return True

    emails_ok = email_to_remind_students(df_remind_students)
    export_ok = utils.export_student_reminder_to_excel(df_remind_students, CAMPUS)

    if not export_ok:
        print(f"ERROR: Unable to process reminder report for {CAMPUS}.")
        return False
    if not emails_ok:
        print(f"WARNING: Reminder emails were not sent for {CAMPUS}.")
        return False

    print(f"WARNING: Exiting {CAMPUS} RemindForBSLogin with pending reminders")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
