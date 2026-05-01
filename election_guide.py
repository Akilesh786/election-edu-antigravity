"""
election_guide.py
=================
An interactive command-line tool for Election Process Education.

Features:
  - Voter eligibility check based on age and citizenship.
  - Step-by-step voter registration guide.
  - Clean, modular design with inline documentation.

Author : Election-Edu Project
Date   : 2026-05-01
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard library imports
# ─────────────────────────────────────────────────────────────────────────────
import sys
import textwrap

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
MINIMUM_VOTING_AGE = 18          # Legal voting age (years)
SEPARATOR = "─" * 60            # Visual divider for CLI output
INDENT = "  "                   # Indentation used throughout

# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def print_header(title: str) -> None:
    """Print a formatted section header to the terminal."""
    print(f"\n{SEPARATOR}")
    print(f"  🗳️  {title.upper()}")
    print(f"{SEPARATOR}")


def print_step(number: int, description: str, detail: str = "") -> None:
    """
    Print a single numbered step with an optional detail block.

    Args:
        number      : Step number (1-based).
        description : Short title of the step.
        detail      : Additional multi-line explanation (optional).
    """
    print(f"\n  Step {number}: {description}")
    if detail:
        # Wrap long lines at 70 chars and indent them neatly
        wrapped = textwrap.fill(detail, width=70,
                                initial_indent=INDENT * 2,
                                subsequent_indent=INDENT * 2)
        print(wrapped)


def prompt_yes_no(question: str) -> bool:
    """
    Prompt the user for a yes/no answer and return True for 'yes'.

    Args:
        question : The question string displayed to the user.

    Returns:
        True if the user answers 'y' or 'yes', False otherwise.
    """
    while True:
        answer = input(f"\n  {question} (yes/no): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  ⚠️  Please enter 'yes' or 'no'.")


def get_positive_integer(prompt: str) -> int:
    """
    Read a positive integer from the user, re-prompting on bad input.

    Args:
        prompt : Text displayed before the input cursor.

    Returns:
        A valid positive integer entered by the user.
    """
    while True:
        raw = input(f"\n  {prompt}: ").strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("  ⚠️  Please enter a valid positive whole number.")


# ─────────────────────────────────────────────────────────────────────────────
# Core feature 1 – Voter Eligibility Check
# ─────────────────────────────────────────────────────────────────────────────

def check_voter_eligibility(age: int, is_citizen: bool) -> tuple[bool, str]:
    """
    Determine whether a person is eligible to vote.

    Eligibility criteria:
      1. Age must be at least MINIMUM_VOTING_AGE (18 years).
      2. The person must be a citizen of the country.

    Args:
        age        : The person's age in years.
        is_citizen : True if the person holds citizenship.

    Returns:
        A tuple (eligible: bool, reason: str) where:
          - eligible is True when both criteria are met.
          - reason explains the outcome in plain language.
    """
    issues = []

    if age < MINIMUM_VOTING_AGE:
        issues.append(
            f"You must be at least {MINIMUM_VOTING_AGE} years old to vote "
            f"(you are {age})."
        )

    if not is_citizen:
        issues.append("You must be a citizen to vote.")

    if issues:
        return False, " | ".join(issues)

    return True, (
        f"You meet all eligibility requirements — you are {age} years old "
        f"and a citizen. You are eligible to vote! ✅"
    )


def run_eligibility_check() -> None:
    """
    Interactive flow: collect user input and display eligibility result.
    This function drives the voter eligibility sub-menu.
    """
    print_header("Voter Eligibility Check")

    age = get_positive_integer("Enter your age")
    is_citizen = prompt_yes_no("Are you a citizen of this country?")

    eligible, reason = check_voter_eligibility(age, is_citizen)

    print()
    if eligible:
        print(f"  ✅  ELIGIBLE: {reason}")
    else:
        print(f"  ❌  NOT ELIGIBLE: {reason}")
        print(f"\n  💡  Tip: Contact your local election authority to learn "
              f"more about the requirements in your jurisdiction.")


# ─────────────────────────────────────────────────────────────────────────────
# Core feature 2 – Voter Registration Guide
# ─────────────────────────────────────────────────────────────────────────────

# Each entry is a dict with keys: 'title' and 'detail'
REGISTRATION_STEPS = [
    {
        "title": "Confirm Your Eligibility",
        "detail": (
            "Before registering, make sure you satisfy all legal requirements: "
            "minimum age (usually 18), citizenship status, and — in some "
            "regions — residency duration. Use the eligibility checker in "
            "this tool or visit your country's official election website."
        ),
    },
    {
        "title": "Gather Required Documents",
        "detail": (
            "Commonly required documents include: a valid government-issued "
            "photo ID (passport, national ID card, or driver's licence), "
            "proof of address (utility bill, bank statement), and your "
            "Social Security / National ID number where applicable."
        ),
    },
    {
        "title": "Choose a Registration Method",
        "detail": (
            "Most countries offer multiple registration channels: "
            "(a) Online — via the official election commission website; "
            "(b) In-person — at your local election office, post office, "
            "or designated government agency; "
            "(c) By mail — download, complete, and post the official form."
        ),
    },
    {
        "title": "Complete the Registration Form",
        "detail": (
            "Fill in all required fields accurately: full legal name, "
            "date of birth, residential address, citizenship information, "
            "and contact details. Double-check every field before submitting "
            "to avoid delays or rejection."
        ),
    },
    {
        "title": "Submit Your Application",
        "detail": (
            "Submit before the official registration deadline — this is "
            "typically 15–30 days before election day, though deadlines vary "
            "by jurisdiction. Keep a copy or confirmation number for your "
            "records."
        ),
    },
    {
        "title": "Verify Your Registration",
        "detail": (
            "After submitting, check your registration status using your "
            "election authority's online portal or by calling their helpline. "
            "Confirm that your name, address, and assigned polling station "
            "are all correct."
        ),
    },
    {
        "title": "Prepare for Election Day",
        "detail": (
            "Locate your assigned polling station, find out the voting hours, "
            "and carry the required ID on election day. If you cannot vote "
            "in person, enquire about absentee / postal ballot options well "
            "in advance."
        ),
    },
]


def run_registration_guide() -> None:
    """
    Display the voter registration steps interactively.

    The user may choose to see all steps at once or advance step-by-step
    for a more guided experience.
    """
    print_header("Voter Registration Guide")

    print(
        f"\n  This guide walks you through the {len(REGISTRATION_STEPS)}-step "
        f"process of registering to vote.\n"
    )

    step_by_step = prompt_yes_no(
        "Would you like to go through each step one at a time?"
    )

    for idx, step in enumerate(REGISTRATION_STEPS, start=1):
        print_step(idx, step["title"], step["detail"])

        # In step-by-step mode, pause after each step (except the last)
        if step_by_step and idx < len(REGISTRATION_STEPS):
            input(f"\n  {INDENT}Press ENTER to continue to the next step…")

    print(f"\n  {SEPARATOR}")
    print(
        f"  🎉  You have completed the registration guide!\n"
        f"  Remember: a registered voter is an empowered citizen.\n"
        f"  {SEPARATOR}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Core feature 3 – Quick Election FAQ
# ─────────────────────────────────────────────────────────────────────────────

FAQ = {
    "1": (
        "What is the difference between a primary and a general election?",
        "A PRIMARY election is held within a political party to select its "
        "candidate(s) for the general election. A GENERAL election is the "
        "main public vote where candidates from different parties compete "
        "for an elected office."
    ),
    "2": (
        "What is an absentee / postal ballot?",
        "An absentee ballot allows registered voters to cast their vote by "
        "mail rather than appearing in person at a polling station. It is "
        "useful for voters who are travelling, ill, or otherwise unable to "
        "attend on election day."
    ),
    "3": (
        "What is a polling station?",
        "A polling station (also called a polling place) is the official "
        "location where registered voters in a particular area go to cast "
        "their ballots on election day."
    ),
    "4": (
        "What happens if I miss the voter registration deadline?",
        "You may be unable to vote in the upcoming election. Some regions "
        "offer same-day registration — check with your local election "
        "authority. Start the process early for future elections."
    ),
}


def run_faq() -> None:
    """Display a short FAQ section about elections."""
    print_header("Election FAQ")

    while True:
        print("\n  Choose a question to learn more:\n")
        for key, (question, _) in FAQ.items():
            print(f"  [{key}] {question}")
        print("  [0] Back to main menu")

        choice = input("\n  Your choice: ").strip()

        if choice == "0":
            break
        if choice in FAQ:
            _, answer = FAQ[choice]
            print(f"\n  💬  {textwrap.fill(answer, width=68, subsequent_indent='     ')}")
            input("\n  Press ENTER to return to the FAQ menu…")
        else:
            print("  ⚠️  Invalid selection. Please try again.")


# ─────────────────────────────────────────────────────────────────────────────
# Main menu & entry point
# ─────────────────────────────────────────────────────────────────────────────

MENU_OPTIONS = {
    "1": ("Check Voter Eligibility",       run_eligibility_check),
    "2": ("Voter Registration Guide",      run_registration_guide),
    "3": ("Election FAQ",                  run_faq),
    "0": ("Exit",                          None),
}


def display_main_menu() -> None:
    """Render the main menu options to the terminal."""
    print_header("Election Process Education — Main Menu")
    print(
        "\n  Welcome! This interactive tool helps you understand "
        "the electoral process.\n"
    )
    for key, (label, _) in MENU_OPTIONS.items():
        icon = "🚪" if key == "0" else "📌"
        print(f"  [{key}] {icon}  {label}")


def main() -> None:
    """
    Application entry point.

    Presents the main menu in a loop until the user exits.
    All sub-features are dispatched from here.
    """
    print(f"\n{'═' * 60}")
    print("  🗳️   ELECTION PROCESS EDUCATION TOOL   🗳️")
    print(f"{'═' * 60}")

    while True:
        display_main_menu()
        choice = input("\n  Enter your choice: ").strip()

        if choice == "0":
            print(
                "\n  Thank you for using the Election Education Tool. "
                "Remember to vote! 🗳️\n"
            )
            sys.exit(0)

        if choice in MENU_OPTIONS:
            _, action = MENU_OPTIONS[choice]
            action()          # Dispatch to the selected feature function
        else:
            print("  ⚠️  Invalid option. Please select a number from the menu.")


# ─────────────────────────────────────────────────────────────────────────────
# Script guard — only run when executed directly (not imported as a module)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
