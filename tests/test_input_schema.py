from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "memory-applicability-guard/scripts/guard_decision.py"
SCHEMA_DIR = ROOT / "schema"
INPUT_SCHEMA_PATH = SCHEMA_DIR / "guard-input.schema.json"
OUTPUT_SCHEMA_PATH = SCHEMA_DIR / "guard-output.schema.json"
EXAMPLES_DIR = SCHEMA_DIR / "examples"
SPEC = importlib.util.spec_from_file_location("guard_decision", SCRIPT)
assert SPEC and SPEC.loader
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)

EXPECTED_EXAMPLE_RESULTS = {
    "explicit-transfer.json": ("PASS", "CLEAR_APPLICABLE", "USE", "EXPLICIT_TRANSFER"),
    "external-required.json": ("VERIFY_EXTERNAL", "UNCERTAIN", "IGNORE", "EXTERNAL_VERIFICATION_REQUIRED"),
    "high-risk.json": ("ESCALATE", "UNCERTAIN", "IGNORE", "HIGH_RISK_HUMAN_REVIEW_REQUIRED"),
    "no-bridge.json": ("REVISE", "CLEAR_INAPPLICABLE", "IGNORE", "NO_BRIDGE"),
    "permission-revoked.json": ("REVISE", "CLEAR_INAPPLICABLE", "IGNORE", "PERMISSION_REVOKED"),
    "robust-action.json": ("REVISE", "UNCERTAIN", "IGNORE", "ROBUST_ACTION_AVAILABLE"),
    "superseded-pool.json": ("REVISE", "CLEAR_INAPPLICABLE", "IGNORE", "SUPERSEDED"),
    "user-resolvable.json": ("ASK_USER", "UNCERTAIN", "ASK", "USER_RESOLVABLE_UNCERTAINTY"),
}

OUTPUT_KEYS = {
    "boundary",
    "decisive_evidence",
    "guard_verdict",
    "memory_action",
    "memory_state",
    "next_step",
    "reason_code",
    "resolution_source",
}


class InputSchemaTests(unittest.TestCase):
    def test_checked_in_schema_matches_helper(self):
        on_disk = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, GUARD.input_schema())

    def test_schema_enums_match_code_constants(self):
        schema = GUARD.input_schema()
        properties = schema["properties"]
        self.assertEqual(set(properties["permission"]["enum"]), GUARD.PERMISSIONS)
        self.assertEqual(set(properties["relationship"]["enum"]), GUARD.RELATIONSHIPS)
        self.assertEqual(set(properties["evidence_status"]["enum"]), GUARD.EVIDENCE_STATUSES)
        self.assertEqual(set(properties["risk"]["enum"]), GUARD.RISKS)
        self.assertEqual(set(properties["proposed_memory_action"]["enum"]), GUARD.MEMORY_ACTIONS)
        self.assertEqual(set(properties["evidence"]["items"]["properties"]["kind"]["enum"]), GUARD.EVIDENCE_KINDS)
        self.assertEqual(set(schema["required"]), GUARD.REQUIRED_FIELDS)

    def test_examples_satisfy_python_contract_and_expected_decisions(self):
        example_files = sorted(path.name for path in EXAMPLES_DIR.glob("*.json"))
        self.assertEqual(example_files, sorted(EXPECTED_EXAMPLE_RESULTS))
        for name in example_files:
            with self.subTest(example=name):
                payload = json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
                GUARD.validate_input(payload)
                result = GUARD.decide(payload)
                verdict, state, action, reason = EXPECTED_EXAMPLE_RESULTS[name]
                self.assertEqual(result["guard_verdict"], verdict)
                self.assertEqual(result["memory_state"], state)
                self.assertEqual(result["memory_action"], action)
                self.assertEqual(result["reason_code"], reason)
                self.assertEqual(set(result), OUTPUT_KEYS)
                self.assertEqual(result["boundary"], GUARD.BOUNDARY)

    def test_output_schema_lists_helper_fields(self):
        schema = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), OUTPUT_KEYS)
        self.assertEqual(set(schema["properties"]), OUTPUT_KEYS)
        self.assertEqual(schema["properties"]["boundary"]["const"], GUARD.BOUNDARY)


if __name__ == "__main__":
    unittest.main()
