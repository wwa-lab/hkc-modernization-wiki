"""Regression tests for the MVP script flow.

These tests use only the Python standard library and keep dictionary/report
writes inside a temporary directory.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "05-ai-factory" / "scripts"


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MvpFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.process_intake = load_script("process_intake")
        self.generate_review_pack = load_script("generate_review_pack")
        self.apply_reviewed_pack = load_script("apply_reviewed_pack")
        self.sample_intake = self.process_intake.load_json(
            ROOT / "05-ai-factory" / "intake" / "sample-intake.json"
        )

    def test_process_intake_builds_required_candidate_types(self) -> None:
        self.process_intake.validate_intake(self.sample_intake)
        candidate_pack = self.process_intake.build_candidates(self.sample_intake)

        self.assertEqual("HKC-INTAKE-SAMPLE-001", candidate_pack["intake_id"])
        candidates = candidate_pack["candidates"]
        self.assertEqual(4, len(candidates))
        self.assertIn("Program Review", {item["type"] for item in candidates})
        self.assertIn("Field Review", {item["type"] for item in candidates})
        self.assertTrue(any(item["confidence"] == "Low" for item in candidates))

        required_fields = {
            "item_id",
            "type",
            "legacy_object",
            "ai_recommended_answer",
            "why_ai_recommends_this",
            "evidence",
            "confidence",
            "alternative_answers",
            "question_for_sme",
            "options",
            "source_material_ids",
            "review_status",
        }
        for item in candidates:
            self.assertTrue(required_fields.issubset(item), item["item_id"])
            self.assertEqual("Pending Review", item["review_status"])

    def test_generate_review_pack_contains_required_sme_fields(self) -> None:
        candidate_pack = self.process_intake.build_candidates(self.sample_intake)
        markdown = self.generate_review_pack.render_pack(candidate_pack)

        self.assertIn("# SME Review Pack - HKC-INTAKE-SAMPLE-001", markdown)
        self.assertEqual(4, markdown.count("## Review Item "))
        for label in [
            "Item ID",
            "Type",
            "Legacy object",
            "AI Recommended Answer",
            "Why AI recommends this",
            "Evidence",
            "Confidence",
            "Alternative Answers",
            "Question for SME",
            "SME Selected Option",
            "SME Selected Alternative",
            "SME Corrected Answer",
            "SME Comment",
            "Review Status",
        ]:
            self.assertIn(f"- {label}:", markdown)
        self.assertIn("- A: Accept AI Recommended Answer", markdown)
        self.assertIn("- E: Not Applicable / Not Correct", markdown)

    def test_apply_reviewed_pack_routes_options_to_dictionaries_and_reports(self) -> None:
        reviewed_pack = ROOT / "05-ai-factory" / "reviewed" / "sample-reviewed-pack.md"
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            programs_path = temp_dir / "legacy-programs.json"
            fields_path = temp_dir / "legacy-fields.json"
            open_questions_path = temp_dir / "latest-open-question-report.md"
            review_status_path = temp_dir / "latest-review-status-report.md"
            programs_path.write_text("[]\n", encoding="utf-8")
            fields_path.write_text("[]\n", encoding="utf-8")

            self.apply_reviewed_pack.PROGRAMS_PATH = programs_path
            self.apply_reviewed_pack.FIELDS_PATH = fields_path
            self.apply_reviewed_pack.OPEN_QUESTIONS_PATH = open_questions_path
            self.apply_reviewed_pack.REVIEW_STATUS_PATH = review_status_path

            summary = self.apply_reviewed_pack.apply_reviewed_pack(reviewed_pack)

            self.assertEqual(
                {
                    "reviewed_items": 5,
                    "dictionary_updates": 3,
                    "open_questions": 1,
                    "not_applicable": 1,
                    "dry_run": False,
                },
                summary,
            )

            programs = json.loads(programs_path.read_text(encoding="utf-8"))
            fields = json.loads(fields_path.read_text(encoding="utf-8"))
            self.assertEqual(["ORDENTR"], [item["program_id"] for item in programs])
            self.assertEqual({"CUSTNO", "BILLNO"}, {item["field"] for item in fields})

            custno = next(item for item in fields if item["field"] == "CUSTNO")
            self.assertEqual("B", custno["sme_selected_option"])
            self.assertEqual("2", custno["sme_selected_alternative"])
            self.assertEqual("Ship-to customer number.", custno["description"])

            billno = next(item for item in fields if item["field"] == "BILLNO")
            self.assertEqual("C", billno["sme_selected_option"])
            self.assertIn("billing document sequence number", billno["description"])

            all_dictionary_objects = {item["legacy_object"] for item in programs + fields}
            self.assertNotIn("PRCADJ", all_dictionary_objects)
            self.assertNotIn("TMPFLAG", all_dictionary_objects)

            open_questions = open_questions_path.read_text(encoding="utf-8")
            review_status = review_status_path.read_text(encoding="utf-8")
            self.assertIn("SME-ITEM-003", open_questions)
            self.assertIn("Need Discussion", open_questions)
            self.assertIn("SME-ITEM-004", review_status)
            self.assertIn("Not Applicable / Not Correct", review_status)

            for item in programs + fields:
                self.assertEqual("SME Confirmed", item["review_status"])
                self.assertIn(item["sme_selected_option"], {"A", "B", "C"})
                self.assertEqual(
                    ["MAT-SAMPLE-001", "MAT-SAMPLE-002"],
                    item["source_material_ids"],
                )
                self.assertEqual("SME-PACK-HKC-INTAKE-SAMPLE-001", item["review_source"])
                self.assertEqual("HKC-INTAKE-SAMPLE-001", item["intake_id"])
                self.assertRegex(item["last_updated"], r"^\d{4}-\d{2}-\d{2}$")

    def test_apply_reviewed_pack_upserts_instead_of_duplicating(self) -> None:
        reviewed_pack = ROOT / "05-ai-factory" / "reviewed" / "sample-reviewed-pack.md"
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            self.apply_reviewed_pack.PROGRAMS_PATH = temp_dir / "legacy-programs.json"
            self.apply_reviewed_pack.FIELDS_PATH = temp_dir / "legacy-fields.json"
            self.apply_reviewed_pack.OPEN_QUESTIONS_PATH = temp_dir / "latest-open-question-report.md"
            self.apply_reviewed_pack.REVIEW_STATUS_PATH = temp_dir / "latest-review-status-report.md"
            self.apply_reviewed_pack.PROGRAMS_PATH.write_text("[]\n", encoding="utf-8")
            self.apply_reviewed_pack.FIELDS_PATH.write_text("[]\n", encoding="utf-8")

            self.apply_reviewed_pack.apply_reviewed_pack(reviewed_pack)
            self.apply_reviewed_pack.apply_reviewed_pack(reviewed_pack)

            programs = json.loads(self.apply_reviewed_pack.PROGRAMS_PATH.read_text(encoding="utf-8"))
            fields = json.loads(self.apply_reviewed_pack.FIELDS_PATH.read_text(encoding="utf-8"))
            self.assertEqual(1, len(programs))
            self.assertEqual(2, len(fields))

    def test_apply_reviewed_pack_dry_run_does_not_write_outputs(self) -> None:
        reviewed_pack = ROOT / "05-ai-factory" / "reviewed" / "sample-reviewed-pack.md"
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            programs_path = temp_dir / "legacy-programs.json"
            fields_path = temp_dir / "legacy-fields.json"
            open_questions_path = temp_dir / "latest-open-question-report.md"
            review_status_path = temp_dir / "latest-review-status-report.md"
            programs_path.write_text("[]\n", encoding="utf-8")
            fields_path.write_text("[]\n", encoding="utf-8")
            open_questions_path.write_text("original open questions\n", encoding="utf-8")
            review_status_path.write_text("original review status\n", encoding="utf-8")

            self.apply_reviewed_pack.PROGRAMS_PATH = programs_path
            self.apply_reviewed_pack.FIELDS_PATH = fields_path
            self.apply_reviewed_pack.OPEN_QUESTIONS_PATH = open_questions_path
            self.apply_reviewed_pack.REVIEW_STATUS_PATH = review_status_path

            summary = self.apply_reviewed_pack.apply_reviewed_pack(reviewed_pack, dry_run=True)

            self.assertTrue(summary["dry_run"])
            self.assertEqual(3, summary["dictionary_updates"])
            self.assertEqual("[]\n", programs_path.read_text(encoding="utf-8"))
            self.assertEqual("[]\n", fields_path.read_text(encoding="utf-8"))
            self.assertEqual("original open questions\n", open_questions_path.read_text(encoding="utf-8"))
            self.assertEqual("original review status\n", review_status_path.read_text(encoding="utf-8"))

    def test_backup_outputs_copies_existing_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            source_dir = temp_dir / "source"
            backup_dir = temp_dir / "backup"
            source_dir.mkdir()
            source_file = source_dir / "legacy-programs.json"
            source_file.write_text('[{"program_id": "OLD"}]\n', encoding="utf-8")

            self.apply_reviewed_pack.ROOT = temp_dir
            backups = self.apply_reviewed_pack.backup_outputs([source_file], backup_dir)

            self.assertEqual([backup_dir / "source" / "legacy-programs.json"], backups)
            self.assertEqual(
                '[{"program_id": "OLD"}]\n',
                backups[0].read_text(encoding="utf-8"),
            )

    def test_validate_repo_script_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_repo.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Result: PASSED", result.stdout)


if __name__ == "__main__":
    unittest.main()
