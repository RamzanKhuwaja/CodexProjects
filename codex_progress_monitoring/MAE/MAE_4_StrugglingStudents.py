import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "MAE"
EMAIL_COLUMNS = [
    "Org Defined ID",
    "Student Full Name",
    "Class Code",
    "Final Grade",
]


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

    k4_details = utils.build_k4_activity_details(CAMPUS, df_struggling_students)

    missing_email_rows = df_struggling_students['Teacher Email'].isna() | (
        df_struggling_students['Teacher Email'].astype(str).str.strip() == ''
    )
    missing_email_count = int(missing_email_rows.sum())
    if missing_email_count:
        if hasattr(utils, 'warn_once'):
            utils.warn_once(
                'WARNING',
                f'{missing_email_count} struggling-student rows are missing teacher email addresses and will not be emailed',
            )
        else:
            print(
                f"WARNING: {missing_email_count} struggling-student rows are missing teacher email addresses and will not be emailed"
            )

    all_success = True
    for email in df_struggling_students['Teacher Email'].dropna().unique():
        df_teacher = df_struggling_students[df_struggling_students['Teacher Email'] == email]
        if df_teacher.empty:
            continue

        teacher_name = df_teacher['Teacher Full Name'].iloc[0]
        payload = (
            df_teacher[EMAIL_COLUMNS]
            .copy()
            .drop_duplicates()
            .sort_values(['Class Code', 'Student Full Name', 'Org Defined ID'])
        )

        if utils.TESTING:
            to = utils.to_email
            cc = ''
        else:
            to = email
            cc = utils.cc_email

        print(
            f"Preparing struggling students email for {teacher_name} "
            f"({len(payload)} students) -> To: {to}; CC: {cc or '(none)'}"
        )
        subject_email = 'Students Below Performance Threshold'
        table_html = utils.render_html_table(
            payload,
            title='Students requiring intervention',
            subtitle='These learners currently have cumulative grades below the campus threshold.',
        )
        k4_html = utils.build_teacher_k4_activity_email_html(df_teacher, k4_details)
        k4_blurb = ""
        if k4_html:
            k4_blurb = (
                "For K-4 students, the activity details below show which areas are contributing most to the current grade.<br><br>"
            )
        body_email = (
            f"Hello {teacher_name},<br><br>"
            "The students below currently have cumulative grades below the campus threshold.<br><br>"
            "Please review their progress and provide any appropriate academic support or follow-up.<br><br>"
            "Lisa will follow up with teachers as needed regarding student performance and next steps.<br><br>"
            f"{table_html}<br><br>"
            f"{k4_blurb}"
            f"{k4_html}"
            "<br><br>"
            "Sincerely,<br>"
            "Ramzan Khuwaja"
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
        return False

    print(f"WARNING: Found struggling students - Exiting {CAMPUS} StrugglingStudents")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
