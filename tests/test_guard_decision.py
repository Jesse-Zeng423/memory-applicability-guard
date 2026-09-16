from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "memory-applicability-guard/scripts/guard_decision.py"
SPEC = importlib.util.spec_from_file_location("guard_decision", SCRIPT)
assert SPEC and SPEC.loader
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


def case(**updates):
    value = {
        "current_task": "Choose a training option",
        "candidate_memory": "The user trained at the downtown pool",
        "proposed_memory_action": "USE",
        "permission": "ALLOWED",
        "relationship": "DIRECT",
        "evidence_status": "SUFFICIENT",
        "robust_action_available": False,
        "risk": "LOW",
        "evidence": [
            {"id": "SOURCE", "text": "Old record", "kind": "MEMORY_SOURCE", "decisive": False},
            {"id": "CURRENT", "text": "Current boundary evidence", "kind": "USER_STATEMENT", "decisive": True},
        ],
    }
    value.update(updates)
    return value


class GuardDecisionTests(unittest.TestCase):
    def assert_decision(self, payload, verdict, state, action):
        result = GUARD.decide(payload)
        self.assertEqual((result["guard_verdict"], result["memory_state"], result["memory_action"]), (verdict, state, action))

    def test_direct(self):
        self.assert_decision(case(), "PASS", "CLEAR_APPLICABLE", "USE")

    def test_explicit_transfer(self):
        self.assert_decision(case(relationship="EXPLICIT_TRANSFER", proposed_memory_action="IGNORE"), "REVISE", "CLEAR_APPLICABLE", "USE")

    def test_no_bridge(self):
        self.assert_decision(case(relationship="NO_BRIDGE"), "REVISE", "CLEAR_INAPPLICABLE", "IGNORE")

    def test_superseded(self):
        result = GUARD.decide(case(relationship="SUPERSEDED"))
        self.assertEqual(result["reason_code"], "SUPERSEDED")
        self.assertEqual([item["id"] for item in result["decisive_evidence"]], ["CURRENT"])
        self.assertEqual(result["memory_action"], "IGNORE")

    def test_permission_revoked_has_priority(self):
        result = GUARD.decide(case(permission="REVOKED", risk="HIGH", evidence_status="EXTERNAL_REQUIRED"))
        self.assertEqual(result["reason_code"], "PERMISSION_REVOKED")
        self.assertEqual(result["memory_action"], "IGNORE")

    def test_user_resolvable(self):
        self.assert_decision(case(relationship="UNKNOWN", evidence_status="USER_RESOLVABLE"), "ASK_USER", "UNCERTAIN", "ASK")

    def test_external_required(self):
        result = GUARD.decide(case(relationship="UNKNOWN", evidence_status="EXTERNAL_REQUIRED", proposed_memory_action="ASK"))
        self.assertEqual(result["guard_verdict"], "VERIFY_EXTERNAL")
        self.assertEqual(result["resolution_source"], "EXTERNAL_EVIDENCE")

    def test_robust_action(self):
        result = GUARD.decide(case(
            relationship="UNKNOWN",
            evidence_status="USER_RESOLVABLE",
            proposed_memory_action="IGNORE",
            robust_action_available=True,
            robust_action="Choose the reversible option",
        ))
        self.assertEqual(result["guard_verdict"], "PASS")
        self.assertEqual(result["reason_code"], "ROBUST_ACTION_AVAILABLE")

    def test_high_risk(self):
        self.assert_decision(case(risk="HIGH"), "ESCALATE", "UNCERTAIN", "IGNORE")

    def test_evidence_gap(self):
        self.assert_decision(case(permission="UNKNOWN", relationship="CONFLICTING", evidence_status="UNKNOWN"), "ASK_USER", "UNCERTAIN", "ASK")

    def test_invalid_enum_and_decisive_provenance(self):
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(permission="INVALID"))
        invalid = case()
        invalid["evidence"][0]["decisive"] = True
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(invalid)

    def test_repeatable_cli_output(self):
        encoded = json.dumps(case(), sort_keys=True).encode()
        command = [sys.executable, str(SCRIPT)]
        first = subprocess.run(command, input=encoded, capture_output=True, check=True).stdout
        second = subprocess.run(command, input=encoded, capture_output=True, check=True).stdout
        self.assertEqual(first, second)

    def _run_cli(self, args, payload=None, check=False):
        encoded = None if payload is None else json.dumps(payload, sort_keys=True)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=encoded,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_cli_file_and_pretty(self):
        encoded = json.dumps(case(), sort_keys=True)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            handle.write(encoded)
            path = handle.name
        self.addCleanup(lambda: Path(path).unlink(missing_ok=True))
        compact = self._run_cli(["--file", path], check=True)
        pretty = self._run_cli(["--file", path, "--pretty"], check=True)
        self.assertEqual(json.loads(compact.stdout)["guard_verdict"], "PASS")
        self.assertIn("\n", pretty.stdout)
        self.assertEqual(json.loads(pretty.stdout)["memory_action"], "USE")

    def test_cli_validate_only(self):
        result = self._run_cli(["--validate-only"], case(), check=True)
        self.assertEqual(json.loads(result.stdout), {"status": "VALID"})

    def test_cli_schema_and_version(self):
        schema = json.loads(self._run_cli(["--schema"], check=True).stdout)
        self.assertEqual(schema["title"], "Memory Applicability Guard input")
        self.assertEqual(set(schema["required"]), GUARD.REQUIRED_FIELDS)
        version = self._run_cli(["--version"], check=True)
        self.assertEqual(version.stdout.strip(), GUARD.__version__)

    def test_cli_invalid_payload_lists_issues(self):
        result = self._run_cli(["--pretty"], case(permission="INVALID"))
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stderr)
        self.assertEqual(payload["error"], "INPUT_VALIDATION_ERROR")
        self.assertTrue(any("permission must be one of" in item for item in payload["issues"]))

    def test_cli_missing_file(self):
        result = self._run_cli(["--file", str(ROOT / "tests" / "missing.json")])
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stderr)
        self.assertIn("input file not found", payload["details"])


if __name__ == "__main__":
    unittest.main()
