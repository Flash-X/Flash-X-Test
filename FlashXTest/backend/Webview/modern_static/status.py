"""
Status parsing utilities for FlashTest static generator.
"""

from pathlib import Path
from typing import List


class InvocationStatus:
    """Minimal representation of one invocation’s status on a single site."""

    def __init__(self, colour: str):
        self.colour = colour
        if colour == "green":
            self.emoji = "✅"
        elif colour == "yellow":
            self.emoji = "⚠️"
        elif colour == "red":
            self.emoji = "❌"
        else:
            raise ValueError(f"Invalid colour '{colour}'")


def classify_invocation(inv_dir: Path) -> InvocationStatus:
    """Determine colour (green/yellow/red) for *inv_dir*."""
    errors_file = inv_dir / "errors"
    log_file = inv_dir / "flash_test.log"

    # errors
    error_lines: List[str] = []
    if errors_file.exists():
        try:
            error_lines = [
                ln.strip() for ln in errors_file.read_text().splitlines() if ln.strip()
            ]
        except Exception:
            error_lines = ["<unable to read errors file>"]

    # logs
    log_errors = log_warnings = 0
    if log_file.exists():
        try:
            for line in log_file.read_text().splitlines():
                if line.startswith("ERROR:"):
                    log_errors += 1
                elif line.startswith("WARNING:"):
                    log_warnings += 1
        except Exception:
            log_errors += 1

    # determine colour
    if not error_lines and log_errors == 0:
        colour = "green"
    else:
        red_errors = 0
        for ln in error_lines:
            if (
                " failed in testing as before" in ln
                and " failed in execution" not in ln
            ):
                continue
            red_errors += 1
        if log_errors + red_errors == 0:
            colour = "yellow"
        else:
            colour = "red"

    return InvocationStatus(colour=colour)


def parse_build_status(build_dir: Path) -> tuple[InvocationStatus, str]:
    """Return (InvocationStatus, exit_msg) for a single build directory."""
    errors_file = build_dir / "errors"
    if not errors_file.exists():
        return ("yellow", "'errors' file not found")
    try:
        raw_lines = [
            ln.strip() for ln in errors_file.read_text().splitlines() if ln.strip()
        ]
    except Exception:
        return ("red", "unable to read 'errors' file")
    changed = False
    if raw_lines and raw_lines[-1] == "!":
        changed = True
        raw_lines = raw_lines[:-1]
    ints: List[int] = []
    for s in raw_lines:
        try:
            ints.append(int(s))
        except ValueError:
            return ("red", "non-numeric content in 'errors' file")
    if len(ints) < 5:
        return ("red", "unrecognised 'errors' format")
    setup_err, comp_err, exec_err, test_err, total_runs = ints[:5]
    same_test_err = ints[5] if len(ints) > 5 else 0
    colour = "green"
    msg_parts: List[str] = []
    if setup_err:
        colour = "red"
        msg_parts.append("failed in setup")
    elif comp_err:
        colour = "red"
        msg_parts.append("failed in compilation")
    else:
        if exec_err:
            colour = "red"
            msg_parts.append(f"{exec_err}/{total_runs} runs failed in execution")
        if test_err:
            if test_err == same_test_err and exec_err == 0:
                colour = "yellow"
            else:
                colour = "red"
            msg_parts.append(f"{test_err}/{total_runs} runs failed in testing")
    if colour == "green":
        msg_parts.append("all runs completed successfully")
    if same_test_err and same_test_err == test_err:
        msg_parts.append("as before")
    if changed:
        msg_parts.append("changed from previous invocation")
    return (InvocationStatus(colour), "; ".join(msg_parts))
