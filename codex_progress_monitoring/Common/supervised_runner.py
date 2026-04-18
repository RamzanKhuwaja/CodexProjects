from __future__ import annotations

import argparse
import importlib
import sys
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils


STATUS_CLEAR = "clear"
STATUS_WARNING_CONTINUE = "warning_continue"
STATUS_BLOCKED = "blocked"
STATUS_FAILED = "failed"


@dataclass(frozen=True)
class PipelineStep:
    order_index: int
    code: str
    slug: str
    label: str
    module_name: str
    email_capable: bool = False
    report_outlook: bool = False


@dataclass(frozen=True)
class RuntimeMode:
    name: str
    label: str
    testing: bool
    send_email: bool
    description: str


@dataclass(frozen=True)
class StepOutcome:
    step: PipelineStep
    status: str
    raw_success: bool
    output: str
    summary: str
    key_lines: tuple[str, ...]
    exception_text: str | None = None


STEP_DEFINITIONS = (
    (0, "0", "check-downloads", "Check downloaded files", "0_CheckDownloadedFiles", False, True),
    (1, "1", "check-duplicates", "Check Brightspace duplicates", "1_CheckAllDups", True, False),
    (2, "2", "generate-student-map", "Generate student map", "2_GenerateStudentMap", False, False),
    (3, "3", "attendance-missing", "Missing attendance follow-up", "3_AttendanceMissing", True, True),
    (4, "4", "struggling-students", "Struggling students", "4_StrugglingStudents", True, True),
    (45, "4_5", "principal-summary", "Principal summary", "4_5_PrincipalSummary", True, True),
    (5, "5", "remind-bs-login", "Brightspace login reminders", "5_RemindForBSLogin", True, True),
    (6, "6", "high-honours", "High honours export", "6_HighHonoursStudents", False, False),
    (7, "7", "attendance-followup", "Needs to attend more regularly", "7_NeedsToAttendMoreRegularly", False, False),
)

FLOWS = {
    "start": ("0",),
    "main": ("1", "2", "3", "4", "4_5"),
    "optional": ("5", "6", "7"),
}

MODES = {
    "silent-test": RuntimeMode(
        name="silent-test",
        label="Silent Test",
        testing=True,
        send_email=False,
        description="Use testing mode and suppress all outbound email sends.",
    ),
    "test-send": RuntimeMode(
        name="test-send",
        label="Test Send",
        testing=True,
        send_email=True,
        description="Use testing mode and send emails only to the test recipient.",
    ),
    "production": RuntimeMode(
        name="production",
        label="Production",
        testing=False,
        send_email=True,
        description="Use live recipients for teacher-facing email steps.",
    ),
}


def build_pipeline(campus: str) -> tuple[PipelineStep, ...]:
    campus = campus.upper()
    return tuple(
        PipelineStep(
            order_index=order_index,
            code=step_code,
            slug=slug,
            label=label,
            module_name=f"{campus}.{campus}_{module_suffix}",
            email_capable=email_capable,
            report_outlook=report_outlook,
        )
        for order_index, step_code, slug, label, module_suffix, email_capable, report_outlook in STEP_DEFINITIONS
    )


PIPELINES = {
    "VAU": build_pipeline("VAU"),
    "MAE": build_pipeline("MAE"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the supervised Brightspace pipeline for a single campus. "
            "Flows execute one wrapper at a time, classify the result, and stop "
            "only on blocked or failed steps."
        )
    )
    parser.add_argument("--campus", choices=sorted(PIPELINES), required=True)
    parser.add_argument("--flow", choices=sorted(FLOWS))
    parser.add_argument("--step", help="Run a single step by number or slug.")
    parser.add_argument("--mode", choices=sorted(MODES), default="silent-test")
    parser.add_argument("--list-steps", action="store_true")
    parser.add_argument("--list-modes", action="store_true")
    parser.add_argument(
        "--confirm-live-send",
        action="store_true",
        help="Required together with --mode production before real recipients can be used.",
    )
    parser.add_argument("--to-email", help="Override the test recipient address for the current run.")
    parser.add_argument("--cc-email", help="Override the campus CC address for the current run.")
    parser.add_argument("--week", type=int, help="Override THIS_WEEK_NUM for the current run only.")

    report_group = parser.add_mutually_exclusive_group()
    report_group.add_argument("--print-report", dest="print_report", action="store_true")
    report_group.add_argument("--no-print-report", dest="print_report", action="store_false")
    parser.set_defaults(print_report=True)

    args = parser.parse_args()

    if args.step and args.flow:
        parser.error("Choose either --step or --flow, not both.")
    if not args.list_steps and not args.list_modes and not args.step and not args.flow:
        parser.error("Provide --flow, --step, --list-steps, or --list-modes.")

    return args


def resolve_step(campus: str, selector: str) -> PipelineStep:
    selector = str(selector).strip().lower()
    for step in PIPELINES[campus]:
        if selector == step.code.lower() or selector == step.slug:
            return step
    available = ", ".join(f"{step.code}:{step.slug}" for step in PIPELINES[campus])
    raise ValueError(f"Unknown step '{selector}' for {campus}. Available steps: {available}")


def resolve_steps(campus: str, args: argparse.Namespace) -> tuple[PipelineStep, ...]:
    if args.step:
        return (resolve_step(campus, args.step),)
    if args.flow:
        wanted = set(FLOWS[args.flow])
        return tuple(step for step in PIPELINES[campus] if step.code in wanted)
    return ()


def validate_week_requirement(steps: tuple[PipelineStep, ...], args: argparse.Namespace) -> None:
    if not steps or args.week is not None:
        return

    needs_week = any(step.code != "0" for step in steps)
    if not needs_week:
        return

    if args.flow:
        raise ValueError(
            f"Flow '{args.flow}' requires an explicit week number. "
            "Run the start flow first, then re-run with --week <number>."
        )

    step = steps[0]
    raise ValueError(
        f"Step {step.code} ({step.slug}) requires an explicit week number. "
        "Provide --week <number>."
    )


def list_steps(campus: str) -> None:
    print(f"Supervised steps for {campus}:")
    for step in PIPELINES[campus]:
        notes = []
        if step.email_capable:
            notes.append("email-capable")
        if step.report_outlook:
            notes.append("reports Outlook status")
        if step.code != "0":
            notes.append("requires week")
        note_text = ", ".join(notes) if notes else "standard"
        print(f"  {step.code}: {step.slug:<22} {step.label} [{note_text}]")

    print()
    print("Flows:")
    for flow_name, step_numbers in FLOWS.items():
        labels = ", ".join(step_numbers)
        print(f"  {flow_name:<8} steps {labels}")


def list_modes() -> None:
    print("Runtime modes:")
    for mode in MODES.values():
        print(f"  {mode.name:<11} {mode.label}: {mode.description}")


def extract_key_lines(output: str) -> tuple[str, ...]:
    prefixes = ("ERROR:", "WARNING:", "ACTION:", "Issue:", "OK:", "INFO:")
    collected: list[str] = []
    seen: set[str] = set()

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(prefixes):
            if line not in seen:
                collected.append(line)
                seen.add(line)
        elif "Completed with duplicate findings." in line and line not in seen:
            collected.append(line)
            seen.add(line)

    return tuple(collected[:12])


def classify_step(step: PipelineStep, raw_success: bool, output: str, exception_text: str | None) -> tuple[str, str]:
    if exception_text is not None:
        return STATUS_FAILED, "Unhandled exception while executing the wrapper."

    output_lower = output.lower()
    warnings_present = "warning:" in output_lower

    if not raw_success:
        return STATUS_BLOCKED, "The wrapper reported that the step could not complete cleanly."

    if step.code == "0":
        return STATUS_CLEAR, "Downloaded files passed the expected count and format checks."

    if step.code == "1":
        if "duplicates detected" in output_lower or "duplicate findings" in output_lower:
            return STATUS_WARNING_CONTINUE, "Duplicate findings were reported, but the pipeline continues by policy."
        return STATUS_CLEAR, "No duplicate findings were reported."

    if step.code == "2":
        if warnings_present:
            return STATUS_WARNING_CONTINUE, "Student map generated successfully with warnings."
        return STATUS_CLEAR, "Student map generated successfully."

    if step.code == "3":
        if "no missing attendance" in output_lower:
            return STATUS_CLEAR, "No missing-attendance cases were found."
        return STATUS_WARNING_CONTINUE, "Missing-attendance cases were found and the step completed."

    if step.code == "4":
        if "no struggling students" in output_lower:
            return STATUS_CLEAR, "No struggling students were found."
        return STATUS_WARNING_CONTINUE, "Struggling-student cases were found and the step completed."

    if step.code == "4_5":
        if "no principal summary needed" in output_lower:
            return STATUS_CLEAR, "No principal summary email was needed."
        return STATUS_WARNING_CONTINUE, "Principal summary email step completed."

    if step.code == "5":
        if "with pending reminders" in output_lower:
            return STATUS_WARNING_CONTINUE, "Brightspace login reminders were identified and processed."
        return STATUS_CLEAR, "No Brightspace login reminders were needed."

    if step.code == "6":
        if "no high honours students" in output_lower:
            return STATUS_CLEAR, "No high-honours students were found."
        return STATUS_WARNING_CONTINUE, "High-honours students were found and exported."

    if step.code == "7":
        if "no attendance concerns" in output_lower:
            return STATUS_CLEAR, "No attendance follow-up students were found."
        return STATUS_WARNING_CONTINUE, "Attendance follow-up students were found and exported."

    return STATUS_CLEAR, "Step completed."


def execute_module(step: PipelineStep) -> tuple[bool, str, str | None]:
    buffer = StringIO()
    try:
        module = importlib.import_module(step.module_name)
        main_fn = getattr(module, "main", None)
        if not callable(main_fn):
            raise RuntimeError(f"Module '{step.module_name}' does not expose a callable main()")

        with redirect_stdout(buffer):
            raw_success = bool(main_fn())
        return raw_success, buffer.getvalue(), None
    except Exception:
        trace_text = traceback.format_exc()
        buffer.write(trace_text)
        return False, buffer.getvalue(), trace_text


def report_outlook(step: PipelineStep, mode: RuntimeMode) -> None:
    if not step.report_outlook:
        return

    is_running, message = utils.outlook_is_running()
    if step.code == "0":
        print(f"Outlook status: {message}")
        return

    if mode.send_email:
        print(f"Outlook status before this email-capable step: {message}")
    elif is_running:
        print("Outlook status: Outlook is running.")
    else:
        print("Outlook status: Outlook is not running, which is fine because email sending is disabled in this mode.")


def print_step_header(step: PipelineStep, campus: str, mode: RuntimeMode, print_report: bool, week: int) -> None:
    week_display = week if step.code != "0" else "(not used)"
    print("=" * 72)
    print(f"Step {step.code}: {step.label}")
    print(f"Campus: {campus}")
    print(f"Module: {step.module_name}")
    print(
        f"Mode: {mode.label} | testing={mode.testing} | send_email={mode.send_email} | "
        f"print_report={print_report} | week={week_display}"
    )
    print("=" * 72)


def print_step_output(output: str) -> None:
    print("--- Step Output Start ---")
    stripped = output.rstrip()
    if stripped:
        print(stripped)
    else:
        print("(no output)")
    print("--- Step Output End ---")


def print_step_footer(outcome: StepOutcome) -> None:
    print(f"Status: {outcome.status}")
    print(f"Summary: {outcome.summary}")
    if outcome.key_lines:
        print("Key lines:")
        for line in outcome.key_lines:
            print(f"  {line}")


def should_continue(status: str) -> bool:
    return status in {STATUS_CLEAR, STATUS_WARNING_CONTINUE}


def run_step(step: PipelineStep, campus: str, mode: RuntimeMode, args: argparse.Namespace) -> StepOutcome:
    requested_week = args.week if args.week is not None else utils.THIS_WEEK_NUM
    print_step_header(step, campus, mode, args.print_report, requested_week)
    report_outlook(step, mode)

    with utils.runtime_options(
        campus=campus,
        testing=mode.testing,
        send_email=mode.send_email,
        print_report=args.print_report,
        this_week_num=args.week,
        override_to_email=args.to_email,
        override_cc_email=args.cc_email,
        allow_live_email=args.confirm_live_send,
    ):
        print(f"Applied runtime: {utils.describe_runtime_state()}")
        raw_success, output, exception_text = execute_module(step)

    print_step_output(output)
    status, summary = classify_step(step, raw_success, output, exception_text)
    outcome = StepOutcome(
        step=step,
        status=status,
        raw_success=raw_success,
        output=output,
        summary=summary,
        key_lines=extract_key_lines(output),
        exception_text=exception_text,
    )
    print_step_footer(outcome)
    print()
    return outcome


def run_flow(steps: tuple[PipelineStep, ...], campus: str, mode: RuntimeMode, args: argparse.Namespace) -> int:
    completed: list[StepOutcome] = []
    for step in steps:
        outcome = run_step(step, campus, mode, args)
        completed.append(outcome)
        if not should_continue(outcome.status):
            print(f"Flow stopped after step {step.code}.")
            return 1

    warning_count = sum(1 for item in completed if item.status == STATUS_WARNING_CONTINUE)
    if warning_count:
        print(f"Flow completed with {warning_count} warning-continue step(s).")
    else:
        print("Flow completed with all steps clear.")
    return 0


def main() -> int:
    args = parse_args()
    campus = args.campus.upper()

    if args.list_steps:
        list_steps(campus)
        return 0
    if args.list_modes:
        list_modes()
        return 0

    mode = MODES[args.mode]
    steps = resolve_steps(campus, args)
    if not steps:
        raise SystemExit(1)

    try:
        validate_week_requirement(steps, args)
        return run_flow(steps, campus, mode, args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
