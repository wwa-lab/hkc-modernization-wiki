"""Interactive keyboard reviewer for candidate items.

This keeps the MVP local and standard-library only. It reads candidate JSON,
lets an SME review items with arrow keys, and writes reviewed Markdown that can
be consumed by apply_reviewed_pack.py.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import textwrap
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OPTION_LABELS = {
    "A": "Accept AI Recommended Answer",
    "B": "Choose Alternative Answer",
    "C": "Provide Corrected Answer",
    "D": "Need Discussion",
    "E": "Not Applicable / Not Correct",
}


class KeyReader:
    def __enter__(self) -> "KeyReader":
        if os.name == "nt":
            return self
        import termios
        import tty
        import sys

        self._stdin = sys.stdin
        self._old_settings = termios.tcgetattr(self._stdin)
        tty.setcbreak(self._stdin.fileno())
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if os.name == "nt":
            return
        import termios

        termios.tcsetattr(self._stdin, termios.TCSADRAIN, self._old_settings)

    def read_key(self) -> str:
        if os.name == "nt":
            import msvcrt

            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                key = msvcrt.getwch()
                if key == "H":
                    return "up"
                if key == "P":
                    return "down"
            if key == "\r":
                return "enter"
            if key == "\x03":
                raise KeyboardInterrupt
            return key.lower()

        import sys

        key = sys.stdin.read(1)
        if key == "\x03":
            raise KeyboardInterrupt
        if key in ("\r", "\n"):
            return "enter"
        if key == "\x1b":
            sequence = sys.stdin.read(2)
            if sequence == "[A":
                return "up"
            if sequence == "[B":
                return "down"
        return key.lower()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def visible(value: str) -> str:
    return value.replace("`", "")


def terminal_width() -> int:
    return max(60, min(shutil.get_terminal_size((100, 24)).columns, 120))


def print_wrapped(line: str = "", indent: str = "") -> None:
    width = terminal_width()
    if not line:
        print()
        return
    if line.startswith("- "):
        wrapped = textwrap.wrap(
            line[2:],
            width=width,
            initial_indent="- ",
            subsequent_indent="  ",
            break_long_words=False,
            break_on_hyphens=False,
        )
    else:
        wrapped = textwrap.wrap(
            line,
            width=width,
            initial_indent=indent,
            subsequent_indent=indent,
            break_long_words=False,
            break_on_hyphens=False,
        )
    print("\n".join(wrapped) if wrapped else line)


def shortcut_hint(options: list[tuple[str, str]]) -> str:
    shortcuts = "/".join(key for key, _label in options)
    return f"Use Up/Down, then Enter. Shortcut keys: {shortcuts}."


def choose_from_menu(title: str, details: list[str], options: list[tuple[str, str]]) -> tuple[str, str]:
    selected = 0
    with KeyReader() as reader:
        while True:
            clear_screen()
            print(title)
            print("=" * len(title))
            print()
            for line in details:
                print_wrapped(line)
            print()
            print_wrapped(shortcut_hint(options))
            print()
            for index, (key, label) in enumerate(options):
                marker = ">" if index == selected else " "
                print_wrapped(f"{marker} {key}: {label}")
            key = reader.read_key()
            if key == "up":
                selected = (selected - 1) % len(options)
            elif key == "down":
                selected = (selected + 1) % len(options)
            elif key == "enter":
                return options[selected]
            else:
                for index, (option_key, _label) in enumerate(options):
                    if key == option_key.lower():
                        return options[index]


def prompt_text(prompt: str, default: str = "TBD") -> str:
    print()
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default


def item_details(item: dict[str, Any], index: int, total: int) -> list[str]:
    lines = [
        f"Review Item {index} of {total}",
        "",
        f"Item ID: {item['item_id']}",
        f"Type: {item['type']}",
        f"Legacy object: {visible(item['legacy_object'])}",
        "",
        "AI Recommended Answer:",
        visible(item["ai_recommended_answer"]),
        "",
        f"Why AI recommends this: {item['why_ai_recommends_this']}",
        "",
        "Evidence:",
    ]
    lines.extend(f"- {visible(evidence)}" for evidence in item["evidence"])
    lines.extend(
        [
            "",
            f"Confidence: {item['confidence']}",
            "",
            f"Question for SME: {visible(item['question_for_sme'])}",
        ]
    )
    return lines


def review_item(item: dict[str, Any], index: int, total: int) -> dict[str, str]:
    option_items = [(key, OPTION_LABELS[key]) for key in ["A", "B", "C", "D", "E"]]
    selected_option, _label = choose_from_menu(
        "SME Candidate Review",
        item_details(item, index, total),
        option_items,
    )

    selected_alternative = "TBD"
    corrected_answer = "TBD"
    if selected_option == "B":
        alternatives = [
            (str(alt_index), answer)
            for alt_index, answer in enumerate(item["alternative_answers"], start=1)
        ]
        selected_alternative, _answer = choose_from_menu(
            "Choose Alternative Answer",
            item_details(item, index, total),
            alternatives,
        )
    elif selected_option == "C":
        corrected_answer = prompt_text("Enter SME Corrected Answer", default="")
        while not corrected_answer:
            corrected_answer = prompt_text("Corrected answer is required for option C", default="")

    comment = prompt_text("SME Comment", default="TBD")
    return {
        "sme_selected_option": selected_option,
        "sme_selected_alternative": selected_alternative,
        "sme_corrected_answer": corrected_answer,
        "sme_comment": comment,
        "review_status": status_for_option(selected_option),
    }


def status_for_option(option: str) -> str:
    if option in {"A", "B", "C"}:
        return "SME Confirmed"
    if option == "D":
        return "Need Discussion"
    return "SME Reviewed"


def render_reviewed_item(index: int, item: dict[str, Any], response: dict[str, str]) -> str:
    alternatives = [
        f"  {alt_index}. {answer}"
        for alt_index, answer in enumerate(item["alternative_answers"], start=1)
    ]
    options = [f"- {key}: {OPTION_LABELS[key]}" for key in ["A", "B", "C", "D", "E"]]
    lines = [
        f"## Reviewed Item {index}",
        "",
        f"- Item ID: `{item['item_id']}`",
        f"- Type: {item['type']}",
        f"- Legacy object: `{item['legacy_object']}`",
        f"- AI Recommended Answer: {item['ai_recommended_answer']}",
        f"- Why AI recommends this: {item['why_ai_recommends_this']}",
        "- Evidence:",
        *[f"  - {evidence}" for evidence in item["evidence"]],
        f"- Confidence: {item['confidence']}",
        "- Alternative Answers:",
        *alternatives,
        f"- Question for SME: {item['question_for_sme']}",
        "",
        "### Options",
        "",
        *options,
        "",
        "### SME Response",
        "",
        f"- SME Selected Option: {response['sme_selected_option']}",
        f"- SME Selected Alternative: {response['sme_selected_alternative']}",
        f"- SME Corrected Answer: {response['sme_corrected_answer']}",
        f"- SME Comment: {response['sme_comment']}",
        f"- Review Status: {response['review_status']}",
    ]
    return "\n".join(lines)


def render_reviewed_pack(candidate_pack: dict[str, Any], responses: list[dict[str, str]]) -> str:
    candidates = candidate_pack["candidates"]
    source_ids = sorted(
        {
            source_id
            for item in candidates
            for source_id in item.get("source_material_ids", [])
        }
    )
    lines = [
        f"# Reviewed SME Pack - {candidate_pack['intake_id']}",
        "",
        "## Review Pack Metadata",
        "",
        f"- Pack ID: `SME-PACK-{candidate_pack['intake_id']}`",
        f"- Intake ID: `{candidate_pack['intake_id']}`",
        f"- Source Document References: {', '.join(f'`{source}`' for source in source_ids)}",
        f"- Created Date: {date.today().isoformat()}",
        "- Review Status: SME Reviewed",
        "",
    ]
    for index, (item, response) in enumerate(zip(candidates, responses), start=1):
        lines.append(render_reviewed_item(index, item, response))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review candidate items with keyboard selection.")
    parser.add_argument("--intake", required=True, help="Intake ID, not a file path.")
    parser.add_argument("--output", help="Optional output reviewed Markdown path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates_path = ROOT / "05-ai-factory" / "logs" / f"{args.intake}-candidates.json"
    candidate_pack = load_json(candidates_path)
    candidates = candidate_pack.get("candidates") if isinstance(candidate_pack, dict) else None
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Candidates JSON must contain a non-empty candidates list")

    responses = []
    try:
        for index, item in enumerate(candidates, start=1):
            responses.append(review_item(item, index, len(candidates)))
    except KeyboardInterrupt:
        clear_screen()
        print("Review cancelled. No reviewed pack was written.")
        return 130

    output_path = (
        Path(args.output)
        if args.output
        else ROOT / "05-ai-factory" / "reviewed" / f"{args.intake}-interactive-reviewed-pack.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_reviewed_pack(candidate_pack, responses), encoding="utf-8", newline="\n")
    clear_screen()
    print(f"Wrote reviewed pack: {output_path}")
    print("Next step:")
    print(f"py -3 05-ai-factory\\scripts\\apply_reviewed_pack.py --reviewed-pack {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
