"""Generate a Markdown SME Review Pack from candidate JSON."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def format_list(items: list[str], prefix: str = "  -") -> list[str]:
    return [f"{prefix} {item}" for item in items]


def render_item(index: int, item: dict[str, Any]) -> str:
    alternatives = [
        f"  {alt_index}. {answer}"
        for alt_index, answer in enumerate(item["alternative_answers"], start=1)
    ]
    options = [f"- {key}: {value}" for key, value in item["options"].items()]
    lines = [
        f"## Review Item {index}",
        "",
        f"- Item ID: `{item['item_id']}`",
        f"- Type: {item['type']}",
        f"- Legacy object: `{item['legacy_object']}`",
        f"- AI Recommended Answer: {item['ai_recommended_answer']}",
        f"- Why AI recommends this: {item['why_ai_recommends_this']}",
        "- Evidence:",
        *format_list(item["evidence"]),
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
        "- SME Selected Option: Pending Review",
        "- SME Selected Alternative: TBD",
        "- SME Corrected Answer: TBD",
        "- SME Comment: TBD",
        "- Review Status: Pending Review",
    ]
    return "\n".join(lines)


def render_pack(candidate_pack: dict[str, Any]) -> str:
    candidates = candidate_pack["candidates"]
    source_ids = sorted(
        {
            source_id
            for item in candidates
            for source_id in item.get("source_material_ids", [])
        }
    )
    lines = [
        f"# SME Review Pack - {candidate_pack['intake_id']}",
        "",
        "## Review Pack Metadata",
        "",
        f"- Pack ID: `SME-PACK-{candidate_pack['intake_id']}`",
        f"- Intake ID: `{candidate_pack['intake_id']}`",
        f"- Project: {candidate_pack.get('project', 'TBD')}",
        f"- Source Document References: {', '.join(f'`{source}`' for source in source_ids)}",
        f"- Created Date: {date.today().isoformat()}",
        "- Review Status: Draft",
        "",
    ]
    for index, item in enumerate(candidates, start=1):
        lines.append(render_item(index, item))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Markdown SME Review Pack.")
    parser.add_argument("--intake", required=True, help="Intake ID, not a file path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    intake_id = args.intake
    candidates_path = ROOT / "05-ai-factory" / "logs" / f"{intake_id}-candidates.json"
    candidate_pack = load_json(candidates_path)
    if not isinstance(candidate_pack, dict) or "candidates" not in candidate_pack:
        raise ValueError("Candidates JSON must contain a candidates list")
    output_path = ROOT / "05-ai-factory" / "review-packs" / f"{intake_id}-sme-review-pack.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_pack(candidate_pack), encoding="utf-8", newline="\n")
    print(f"Read candidates: {candidates_path}")
    print(f"Wrote review pack: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
