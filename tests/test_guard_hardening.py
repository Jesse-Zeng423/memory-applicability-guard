from __future__ import annotations

import json
import subprocess
import sys
import unittest

from test_guard_decision import GUARD, ROOT, SCRIPT, case


def evidence(kind, decisive=True, identifier="CURRENT"):
    return {"id": identifier, "text": "Synthetic current boundary evidence", "kind": kind, "decisive": decisive}


class GuardHardeningTests(unittest.TestCase):
    def test_explicit_transfer_without_support_is_rejected(self):
        payload = case(relationship="EXPLICIT_TRANSFER", evidence=[evidence("MEMORY_SOURCE", False)])
        with self.assertRaises(GUARD.SemanticConsistencyError):
            GUARD.decide(payload)

    def test_direct_requires_decisive_applicability_or_user_statement(self):
        for kind in GUARD.EVIDENCE_KINDS:
            for decisive in (False, True):
                if kind == "MEMORY_SOURCE" and decisive:
                    continue  # Already rejected structurally by the unchanged suite.
                with self.subTest(kind=kind, decisive=decisive):
                    payload = case(evidence=[evidence(kind, decisive)])
                    if decisive and kind in {"APPLICABILITY", "USER_STATEMENT"}:
                        self.assertEqual(GUARD.decide(payload)["memory_action"], "USE")
                    else:
                        with self.assertRaises(GUARD.SemanticConsistencyError):
                            GUARD.decide(payload)

    def test_revocation_requires_permission_or_user_evidence(self):
        for kind in ("PERMISSION", "USER_STATEMENT", "APPLICABILITY"):
            payload = case(permission="REVOKED", relationship="UNKNOWN", evidence=[evidence(kind)])
            if kind in {"PERMISSION", "USER_STATEMENT"}:
                self.assertEqual(GUARD.decide(payload)["memory_action"], "IGNORE")
            else:
                with self.assertRaises(GUARD.SemanticConsistencyError):
                    GUARD.decide(payload)

    def test_supersession_requires_decisive_boundary_support(self):
        for kind in ("CURRENT_EXTERNAL", "APPLICABILITY", "USER_STATEMENT", "PERMISSION"):
            payload = case(relationship="SUPERSEDED", evidence=[evidence(kind)])
            if kind == "PERMISSION":
                with self.assertRaises(GUARD.SemanticConsistencyError):
                    GUARD.decide(payload)
            else:
                self.assertEqual(GUARD.decide(payload)["reason_code"], "SUPERSEDED")

    def test_pending_external_verification_rejects_decisive_verified_fact(self):
        payload = case(relationship="UNKNOWN", evidence_status="EXTERNAL_REQUIRED", evidence=[evidence("CURRENT_EXTERNAL")])
        with self.assertRaises(GUARD.SemanticConsistencyError):
            GUARD.decide(payload)
        payload["evidence"][0]["decisive"] = False
        self.assertEqual(GUARD.decide(payload)["guard_verdict"], "VERIFY_EXTERNAL")

    def test_consistency_reports_all_violations_after_structure(self):
        payload = case(permission="REVOKED", relationship="DIRECT", evidence=[evidence("MEMORY_SOURCE", False)])
        with self.assertRaises(GUARD.SemanticConsistencyError) as caught:
            GUARD.decide(payload)
        self.assertIn("permission=REVOKED", str(caught.exception))
        self.assertIn("relationship=DIRECT", str(caught.exception))
        payload["risk"] = "INVALID"
        with self.assertRaises(GUARD.InputValidationError) as structural:
            GUARD.decide(payload)
        self.assertNotIsInstance(structural.exception, GUARD.SemanticConsistencyError)
        self.assertEqual(structural.exception.code, "INPUT_VALIDATION_ERROR")

    def test_revoked_high_risk_retains_underlying_human_review(self):
        result = GUARD.decide(case(permission="REVOKED", risk="HIGH", proposed_memory_action="IGNORE"))
        self.assertEqual(result["guard_verdict"], "PASS")
        self.assertEqual(result["memory_action"], "IGNORE")
        self.assertIn("underlying high-risk task", result["next_step"])
        self.assertIn("human review", result["next_step"])

    def test_medium_risk_requires_decisive_confirmation_before_use(self):
        payload = case(risk="MEDIUM", evidence=[evidence("APPLICABILITY")])
        result = GUARD.decide(payload)
        self.assertEqual((result["guard_verdict"], result["reason_code"]), ("ASK_USER", "MEDIUM_RISK_CONFIRMATION_REQUIRED"))
        payload["evidence"].append(evidence("PERMISSION", False, "CONSENT"))
        self.assertEqual(GUARD.decide(payload)["memory_action"], "ASK")
        payload["evidence"][1]["decisive"] = True
        self.assertEqual(GUARD.decide(payload)["memory_action"], "USE")

    def test_conflicting_evidence_uses_distinct_reason_or_robust_action(self):
        payload = case(relationship="CONFLICTING", proposed_memory_action="ASK")
        self.assertEqual(GUARD.decide(payload)["reason_code"], "CONFLICTING_EVIDENCE")
        payload.update(robust_action_available=True, robust_action="Prepare a reusable outline")
        self.assertEqual(GUARD.decide(payload)["reason_code"], "ROBUST_ACTION_AVAILABLE")

    def test_ask_alignment_and_unknown_permission_remain_compatible(self):
        result = GUARD.decide(case(proposed_memory_action="ASK", permission="UNKNOWN"))
        self.assertEqual((result["guard_verdict"], result["memory_action"]), ("ASK_USER", "ASK"))

    def test_semantic_cli_failure_contract_from_unrelated_directory(self):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            input=json.dumps(case(relationship="EXPLICIT_TRANSFER", evidence=[evidence("MEMORY_SOURCE", False)])),
            text=True, capture_output=True, cwd=ROOT.anchor,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"], "SEMANTIC_CONSISTENCY_ERROR")
        self.assertTrue(issubclass(GUARD.SemanticConsistencyError, GUARD.InputValidationError))

    def test_all_a_to_g_scenarios_through_cli_from_root_directory(self):
        scenarios = [
            (case(relationship="EXPLICIT_TRANSFER", evidence=[evidence("MEMORY_SOURCE", False)]), "SEMANTIC_CONSISTENCY_ERROR"),
            (case(permission="REVOKED", relationship="UNKNOWN", evidence=[evidence("APPLICABILITY")]), "SEMANTIC_CONSISTENCY_ERROR"),
            (case(permission="REVOKED", risk="HIGH", proposed_memory_action="IGNORE"), "PASS"),
            (case(relationship="UNKNOWN", evidence_status="USER_RESOLVABLE", proposed_memory_action="ASK"), "ASK_USER"),
            (case(relationship="CONFLICTING"), "ASK_USER"),
            (case(risk="MEDIUM", evidence=[evidence("APPLICABILITY")]), "ASK_USER"),
            (case(permission="UNKNOWN"), "ASK_USER"),
        ]
        for payload, expected in scenarios:
            with self.subTest(expected=expected, payload=payload):
                run = subprocess.run([sys.executable, "-B", str(SCRIPT)], input=json.dumps(payload), text=True, capture_output=True, cwd=ROOT.anchor)
                if expected == "SEMANTIC_CONSISTENCY_ERROR":
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual(json.loads(run.stderr)["error"], expected)
                else:
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertEqual(json.loads(run.stdout)["guard_verdict"], expected)


if __name__ == "__main__":
    unittest.main()
