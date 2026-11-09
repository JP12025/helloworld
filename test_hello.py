"""Acceptance tests for the Hello, world! exercise.

The tests run your program as a whole, exactly as a user would, then
check what it prints and try to explain what is wrong.

Run the tests from the exercise folder with:

    python test_hello.py
"""

import os
import subprocess
import sys
from pathlib import Path

EXERCISE_DIR = Path(__file__).resolve().parent
SCRIPT = "hello.py"
EXPECTED = "Hello, world!"
TIMEOUT = 5  # seconds

STEPS = [
    f"{SCRIPT} exists",
    f"{SCRIPT} runs without error",
    f"{SCRIPT} prints exactly {EXPECTED}",
]


# ---------------------------------------------------------------------------
# Running the student's program
# ---------------------------------------------------------------------------

def run_program():
    """Run the program without typing anything.

    Return (stdout, stderr, return code), or None if the program
    did not stop in time.
    """
    try:
        # sys.executable is the Python running the tests,
        # so "python" vs "python3" does not matter.
        result = subprocess.run(
            [sys.executable, SCRIPT],
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=EXERCISE_DIR,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None
    stdout = result.stdout.replace("\r\n", "\n")
    return stdout, result.stderr.strip(), result.returncode


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def show(lines):
    """Indent lines and make spaces visible (shown as '·')."""
    if not lines:
        return "    (nothing)"
    return "\n".join("    " + line.replace(" ", "·") for line in lines)


def last_lines(text, nb_lines=4):
    """Return the last lines of a text, indented."""
    lines = text.split("\n")[-nb_lines:]
    return "\n".join("    " + line for line in lines)


def point_difference(given, expected):
    """Show both texts one above the other, with a ^ under the first
    character that differs."""
    position = 0
    while (position < len(given) and position < len(expected)
           and given[position] == expected[position]):
        position += 1
    return (f"Expected: {expected.replace(' ', '·')}\n"
            f"Printed:  {given.replace(' ', '·')}\n"
            f"          {' ' * position}^ first difference here\n"
            f"(spaces are shown as ·)")


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_file():
    """Check that the script exists. Return an error message or None."""
    if (EXERCISE_DIR / SCRIPT).is_file():
        return None
    message = f"No file named {SCRIPT} in {EXERCISE_DIR}"
    candidates = []
    for path in sorted(EXERCISE_DIR.iterdir()):
        name = path.name
        if path.is_file() and name != Path(__file__).name and (
                name.endswith(".py") or name.lower().startswith("hello")):
            candidates.append(name)
    if candidates:
        message += ("\nFiles found that could be your program: "
                    + ", ".join(candidates)
                    + f"\nRename your file to exactly {SCRIPT} (lowercase, "
                    f"ending with .py).")
        if any(name.lower().startswith(SCRIPT + ".") for name in candidates):
            message += (" Your editor may have added a hidden extension "
                        "such as .txt.")
    else:
        message += ("\nCreate it in the same folder as test_hello.py, "
                    "then run the tests again from this folder.")
    return message


def has_quotes():
    """Return True if the script contains at least one quote."""
    source = (EXERCISE_DIR / SCRIPT).read_text(encoding="utf-8",
                                               errors="replace")
    return '"' in source or "'" in source


def explain_crash(stderr):
    """Explain why the program crashed."""
    message = f"Your program crashed:\n{last_lines(stderr)}"
    if "Missing parentheses" in stderr:
        message += ("\nIn Python 3, print is a function: write "
                    "print(\"...\") with parentheses.")
    elif "unterminated string" in stderr or "EOL while scanning" in stderr:
        message += ("\nA text (str) must start AND end with a quote: "
                    "check that the closing \" is there.")
    elif ("NameError" in stderr or "SyntaxError" in stderr) and (
            not has_quotes()):
        message += ("\nA text (str) must be written between quotes, "
                    "otherwise Python thinks it is a variable name: "
                    "print(\"Hello, world!\").")
    elif "NameError" in stderr:
        message += ("\nPython does not know this name: check the spelling "
                    "of print (all in lowercase).")
    elif "IndentationError" in stderr:
        message += ("\nThe line must start at the very beginning, without "
                    "any space before print.")
    elif "EOFError" in stderr:
        message += ("\nYour program waits for the user to type something "
                    "(input()), but it should only print the message.")
    elif "SyntaxError" in stderr:
        message += ("\nPython could not read your code: look at the line "
                    "shown above, the ^ points near the mistake.")
    return message


def check_runs(result):
    """Check that the program stops without error.

    Return an error message or None.
    """
    if result is None:
        return ("Your program did not stop. It should only print one "
                "message, without any loop.")
    _, stderr, return_code = result
    if return_code != 0:
        return explain_crash(stderr)
    return None


def check_output(stdout):
    """Check what the program prints. Return an error message or None."""
    if stdout == EXPECTED + "\n":
        return None
    lines = stdout.splitlines()
    printed = "Your program printed:\n" + show(lines)

    if not lines:
        return (f"Your program printed nothing. Did you call print()? "
                f"Did you save {SCRIPT} before running the tests?")
    if len(lines) > 1:
        message = "Your program should print a single line."
        if EXPECTED in lines:
            message += (f" {EXPECTED} is there: remove the other "
                        f"print() calls.")
        return f"{message}\n{printed}"

    line = lines[0]
    if line == EXPECTED:
        return ("The message must end with a newline, which print() adds "
                "by itself: don't use end=\"\".")
    if line.strip() == EXPECTED:
        return ("Nothing should be printed before or after the message "
                f"(not even spaces).\n{printed}")
    if line[1:-1] == EXPECTED and line[0] == line[-1] and line[0] in "\"'":
        return (f"The quotes are not part of the message: they only tell "
                f"Python where the text starts and ends. Write "
                f"print(\"{EXPECTED}\"), not print('\"{EXPECTED}\"').\n"
                f"{printed}")
    if line.lower() == EXPECTED.lower():
        return (f"Uppercase and lowercase letters are different: check the "
                f"capital letters.\n{point_difference(line, EXPECTED)}")
    return ("Your program should print exactly the expected message, "
            "character by character (comma, space and ! included).\n"
            f"{point_difference(line, EXPECTED)}")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(errors="replace")
    use_colors = sys.stdout.isatty() and (
        os.name != "nt" or "WT_SESSION" in os.environ)
    green = "\033[32m" if use_colors else ""
    red = "\033[31m" if use_colors else ""
    reset = "\033[0m" if use_colors else ""

    # The steps depend on each other: stop at the first failure.
    message = check_file()
    if message is None:
        result = run_program()
        message = check_runs(result)
        if message is None:
            message = check_output(result[0])
            nb_ok = 2 if message else 3
        else:
            nb_ok = 1
    else:
        nb_ok = 0

    for description in STEPS[:nb_ok]:
        print(f"{green}✔{reset} {description}")
    if nb_ok < len(STEPS):
        print(f"{red}✗{reset} {STEPS[nb_ok]}")
        print("    " + message.replace("\n", "\n    ") + "\n")
        for description in STEPS[nb_ok + 1:]:
            print(f"- {description} (not checked yet)")

    color = green if nb_ok == len(STEPS) else red
    print(f"Validated: {color}{nb_ok}/{len(STEPS)}{reset}")
    return 0 if nb_ok == len(STEPS) else 1


if __name__ == "__main__":
    sys.exit(main())
