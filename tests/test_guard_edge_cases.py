from __future__ import annotations

import unittest

from test_guard_decision import GUARD, case


PRECEDENCE_CASES = [
    (
        "revoked_beats_high_risk_and_external",
        case(permission="REVOKED", risk="HIGH", evidence_status="EXTERNAL_REQUIRED"),
        ("REVISE", "CLEAR_INAPPLICABLE", "IGNORE", "PERMISSION_REVOKED"),
    ),
    (
        "revoked_with_matching_ignore_is_pass",
        case(permission="REVOKED", proposed_memory_action="IGNORE"),
        ("PASS", "CLEAR_INAPPLICABLE", "IGNORE", "PERMISSION_REVOKED"),
    ),
    (
        "high_risk_beats_external_and_direct_use",
        case(risk="HIGH", evidence_status="EXTERNAL_REQUIRED", relationship="DIRECT"),
        ("ESCALATE", "UNCERTAIN", "IGNORE", "HIGH_RISK_HUMAN_REVIEW_REQUIRED"),
    ),
    (
        "external_beats_no_bridge",
        case(relationship="NO_BRIDGE", evidence_status="EXTERNAL_REQUIRED"),
        ("VERIFY_EXTERNAL", "UNCERTAIN", "IGNORE", "EXTERNAL_VERIFICATION_REQUIRED"),
    ),
    (
        "no_bridge_with_matching_ignore_is_pass",
        case(relationship="NO_BRIDGE", proposed_memory_action="IGNORE"),
        ("PASS", "CLEAR_INAPPLICABLE", "IGNORE", "NO_BRIDGE"),
    ),
    (
        "superseded_beats_user_resolvable",
        case(relationship="SUPERSEDED", evidence_status="USER_RESOLVABLE"),
        ("REVISE", "CLEAR_INAPPLICABLE", "IGNORE", "SUPERSEDED"),
    ),
    (
        "direct_allowed_sufficient_use",
        case(),
        ("PASS", "CLEAR_APPLICABLE", "USE", "DIRECT"),
    ),
    (
        "explicit_transfer_revises_ignore",
        case(relationship="EXPLICIT_TRANSFER", proposed_memory_action="IGNORE"),
        ("REVISE", "CLEAR_APPLICABLE", "USE", "EXPLICIT_TRANSFER"),
    ),
    (
        "direct_does_not_use_when_permission_unknown",
        case(permission="UNKNOWN"),
        ("ASK_USER", "UNCERTAIN", "ASK", "EVIDENCE_GAP"),
    ),
    (
        "conflicting_sufficient_is_evidence_gap",
        case(relationship="CONFLICTING"),
        ("ASK_USER", "UNCERTAIN", "ASK", "EVIDENCE_GAP"),
    ),
    (
        "medium_risk_does_not_escalate",
        case(risk="MEDIUM"),
        ("PASS", "CLEAR_APPLICABLE", "USE", "DIRECT"),
    ),
    (
        "user_resolvable_without_robust_asks",
        case(relationship="UNKNOWN", evidence_status="USER_RESOLVABLE"),
        ("ASK_USER", "UNCERTAIN", "ASK", "USER_RESOLVABLE_UNCERTAINTY"),
    ),
    (
        "robust_beats_user_resolvable_and_revises_use",
        case(
            relationship="UNKNOWN",
            evidence_status="USER_RESOLVABLE",
            robust_action_available=True,
            robust_action="Choose the reversible option",
        ),
        ("REVISE", "UNCERTAIN", "IGNORE", "ROBUST_ACTION_AVAILABLE"),
    ),
    (
        "robust_with_matching_ignore_is_pass",
        case(
            relationship="UNKNOWN",
            evidence_status="UNKNOWN",
            proposed_memory_action="IGNORE",
            robust_action_available=True,
            robust_action="Choose the reversible option",
        ),
        ("PASS", "UNCERTAIN", "IGNORE", "ROBUST_ACTION_AVAILABLE"),
    ),
    (
        "ask_proposal_on_gap_still_asks",
        case(permission="UNKNOWN", relationship="CONFLICTING", evidence_status="UNKNOWN", proposed_memory_action="ASK"),
        ("ASK_USER", "UNCERTAIN", "ASK", "EVIDENCE_GAP"),
    ),
]


class GuardEdgeCaseTests(unittest.TestCase):
    def test_precedence_table(self):
        for name, payload, expected in PRECEDENCE_CASES:
            with self.subTest(name=name):
                result = GUARD.decide(payload)
                self.assertEqual(
                    (
                        result["guard_verdict"],
                        result["memory_state"],
                        result["memory_action"],
                        result["reason_code"],
                    ),
                    expected,
                )

    def test_malformed_evidence_arrays(self):
        invalid_evidence = [
            [],
            "not-a-list",
            None,
            [{"id": "SOURCE", "text": "Old record", "kind": "MEMORY_SOURCE", "decisive": False}, "tail"],
            [{"id": "ONLY", "text": "ok", "kind": "USER_STATEMENT", "decisive": True, "extra": True}],
            [{"id": "ONLY", "text": "ok", "kind": "USER_STATEMENT"}],
            [{"text": "ok", "kind": "USER_STATEMENT", "decisive": True}],
        ]
        for evidence in invalid_evidence:
            with self.subTest(evidence=evidence):
                with self.assertRaises(GUARD.InputValidationError):
                    GUARD.decide(case(evidence=evidence))

    def test_duplicate_and_blank_evidence_ids(self):
        duplicate = case(
            evidence=[
                {"id": "SAME", "text": "Old record", "kind": "MEMORY_SOURCE", "decisive": False},
                {"id": "SAME", "text": "Current boundary evidence", "kind": "USER_STATEMENT", "decisive": True},
            ]
        )
        blank = case(
            evidence=[
                {"id": "   ", "text": "Old record", "kind": "MEMORY_SOURCE", "decisive": False},
                {"id": "CURRENT", "text": "Current boundary evidence", "kind": "USER_STATEMENT", "decisive": True},
            ]
        )
        with self.assertRaises(GUARD.InputValidationError) as duplicate_error:
            GUARD.decide(duplicate)
        self.assertIn("duplicate evidence id: SAME", duplicate_error.exception.issues)
        with self.assertRaises(GUARD.InputValidationError) as blank_error:
            GUARD.decide(blank)
        self.assertTrue(any("id must be a non-empty string" in item for item in blank_error.exception.issues))

    def test_action_and_permission_conflicts(self):
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(proposed_memory_action="DELETE"))
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(permission="GRANTED"))
        revoked_use = GUARD.decide(case(permission="REVOKED", proposed_memory_action="USE"))
        self.assertEqual(revoked_use["guard_verdict"], "REVISE")
        self.assertEqual(revoked_use["memory_action"], "IGNORE")
        revoked_ask = GUARD.decide(case(permission="REVOKED", proposed_memory_action="ASK"))
        self.assertEqual(revoked_ask["guard_verdict"], "REVISE")
        self.assertEqual(revoked_ask["memory_action"], "IGNORE")

    def test_robust_action_contract(self):
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(robust_action_available=True))
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(robust_action_available=True, robust_action="   "))
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(robust_action_available=False, robust_action="Choose the reversible option"))
        allowed_null = case()
        allowed_null["robust_action"] = None
        GUARD.validate_input(allowed_null)

    def test_multi_evidence_decisive_order_and_empty_decisive(self):
        payload = case(
            evidence=[
                {"id": "SOURCE", "text": "Old record", "kind": "MEMORY_SOURCE", "decisive": False},
                {"id": "A", "text": "First current fact", "kind": "USER_STATEMENT", "decisive": True},
                {"id": "B", "text": "Second current fact", "kind": "APPLICABILITY", "decisive": True},
            ]
        )
        result = GUARD.decide(payload)
        self.assertEqual([item["id"] for item in result["decisive_evidence"]], ["A", "B"])
        none_decisive = case(
            evidence=[
                {"id": "SOURCE", "text": "Old record", "kind": "MEMORY_SOURCE", "decisive": False},
                {"id": "NOTE", "text": "Non-decisive note", "kind": "USER_STATEMENT", "decisive": False},
            ]
        )
        empty = GUARD.decide(none_decisive)
        self.assertEqual(empty["decisive_evidence"], [])
        self.assertEqual(empty["guard_verdict"], "PASS")

    def test_unknown_and_missing_fields(self):
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide("not-an-object")
        with self.assertRaises(GUARD.InputValidationError):
            GUARD.decide(case(current_task="   "))
        extra = case()
        extra["unexpected"] = True
        with self.assertRaises(GUARD.InputValidationError) as extra_error:
            GUARD.decide(extra)
        self.assertIn("unknown fields: unexpected", extra_error.exception.issues)
        missing = case()
        del missing["risk"]
        with self.assertRaises(GUARD.InputValidationError) as missing_error:
            GUARD.decide(missing)
        self.assertIn("missing fields: risk", missing_error.exception.issues)


if __name__ == "__main__":
    unittest.main()
