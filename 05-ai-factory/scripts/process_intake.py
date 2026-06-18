"""Create mock SME review candidates from an intake JSON file.

This MVP intentionally does not read LAN folders or call AI services. It uses
sample intake metadata plus deterministic mock extraction to prove the flow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_INTAKE_FIELDS = [
    "intake_id",
    "project",
    "submitted_by",
    "submitted_date",
    "description",
    "materials",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def validate_intake(intake: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_INTAKE_FIELDS if not intake.get(field)]
    if missing:
        raise ValueError(f"Missing required intake field(s): {', '.join(missing)}")
    if not isinstance(intake["materials"], list) or not intake["materials"]:
        raise ValueError("intake.materials must be a non-empty list")
    for index, material in enumerate(intake["materials"], start=1):
        if not isinstance(material, dict):
            raise ValueError(f"materials[{index}] must be an object")
        for field in ["material_id", "source_path", "material_type"]:
            if not material.get(field):
                raise ValueError(f"materials[{index}] missing required field: {field}")


def material_ids(intake: dict[str, Any]) -> list[str]:
    return [material["material_id"] for material in intake["materials"]]


def build_candidates(intake: dict[str, Any]) -> dict[str, Any]:
    sources = material_ids(intake)
    return {
        "intake_id": intake["intake_id"],
        "project": intake["project"],
        "created_from": "mock extraction",
        "candidates": [
            {
                "item_id": "SME-ITEM-001",
                "type": "Program Review",
                "legacy_object": "ORDENTR",
                "ai_recommended_answer": (
                    "`ORDENTR` appears to be an order entry program used to "
                    "create or maintain customer orders."
                ),
                "why_ai_recommends_this": (
                    "The program name resembles order entry, and the mock "
                    "evidence references order header and detail file usage."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-002",
                    "Observed terms: ORDER HEADER, ORDER DETAIL, ENTRY SCREEN",
                ],
                "confidence": "Medium",
                "alternative_answers": [
                    "Order inquiry screen program.",
                    "Batch order validation program.",
                    "Order maintenance program.",
                ],
                "question_for_sme": "What is the best description of legacy program `ORDENTR`?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": "Pending Review",
            },
            {
                "item_id": "SME-ITEM-002",
                "type": "Field Review",
                "legacy_object": "CUSTNO",
                "ai_recommended_answer": (
                    "`CUSTNO` is the customer number field used to identify "
                    "the customer associated with an order or account record."
                ),
                "why_ai_recommends_this": (
                    "The field name resembles customer number, and the mock "
                    "evidence places it near customer and order records."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-001",
                    "Observed terms: CUSTOMER FILE, ORDER HEADER, CUSTNO",
                ],
                "confidence": "High",
                "alternative_answers": [
                    "Billing customer number.",
                    "Ship-to customer number.",
                    "Customer account number used only for reporting.",
                ],
                "question_for_sme": "What is the correct meaning of field `CUSTNO`?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": "Pending Review",
            },
            {
                "item_id": "SME-ITEM-003",
                "type": "Program Review",
                "legacy_object": "PRCADJ",
                "ai_recommended_answer": (
                    "`PRCADJ` may be a pricing adjustment program, but the "
                    "available mock evidence is incomplete."
                ),
                "why_ai_recommends_this": (
                    "The name suggests price adjustment, yet the mock source "
                    "does not show enough business context."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-002",
                    "Observed terms: PRICE, ADJUST, MANUAL OVERRIDE",
                ],
                "confidence": "Low",
                "alternative_answers": [
                    "Promotion adjustment program.",
                    "Manual price override screen.",
                    "Obsolete pricing batch utility.",
                ],
                "question_for_sme": "Does `PRCADJ` require a business discussion before dictionary approval?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": "Pending Review",
            },
            {
                "item_id": "SME-ITEM-004",
                "type": "Field Review",
                "legacy_object": "TMPFLAG",
                "ai_recommended_answer": (
                    "`TMPFLAG` appears to be a temporary processing flag and "
                    "may not represent stable business meaning."
                ),
                "why_ai_recommends_this": (
                    "The mock evidence only shows temporary work-file usage, "
                    "not a persistent business field."
                ),
                "evidence": [
                    "Source material: MAT-SAMPLE-001",
                    "Observed terms: WORK FILE, TEMP, TMPFLAG",
                ],
                "confidence": "Low",
                "alternative_answers": [
                    "Internal batch retry flag.",
                    "Temporary UI state flag.",
                    "Obsolete migration-only field.",
                ],
                "question_for_sme": "Should `TMPFLAG` be excluded from the approved legacy field dictionary?",
                "options": {
                    "A": "Accept AI Recommended Answer",
                    "B": "Choose Alternative Answer",
                    "C": "Provide Corrected Answer",
                    "D": "Need Discussion",
                    "E": "Not Applicable / Not Correct",
                },
                "source_material_ids": sources,
                "review_status": "Pending Review",
            },
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process intake JSON into mock candidates.")
    parser.add_argument("--intake", required=True, help="Path to intake JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    intake_path = Path(args.intake)
    intake = load_json(intake_path)
    if not isinstance(intake, dict):
        raise ValueError("Intake JSON must contain an object at the top level")
    validate_intake(intake)
    candidate_pack = build_candidates(intake)
    output_path = ROOT / "05-ai-factory" / "logs" / f"{intake['intake_id']}-candidates.json"
    write_json(output_path, candidate_pack)
    print(f"Processed intake: {intake['intake_id']}")
    print(f"Wrote candidates: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
