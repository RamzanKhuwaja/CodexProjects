import sys

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
        table_html = utils.render_html_table(
            payload,
            title='Students requiring intervention',
            subtitle='These learners currently have cumulative grades below the campus threshold.',
        )
        body_email = (
            f"Hello {teacher_name},<br><br>"
            'The following students currently have a cumulative grade below our threshold. '
            'Please review their progress and engage with the office team to plan next steps.<br><br>'
            f"{table_html}<br><br>"
            'Many of your students are doing well; thank you for your efforts.<br><br>'
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

    if not emails_ok or not export_ok:
        print(f"ERROR: Unable to process struggling students for {CAMPUS}.")
        return False

    print(f"WARNING: Found struggling students - Exiting {CAMPUS} StrugglingStudents")
    return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
