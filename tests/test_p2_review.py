from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("p2_review", ROOT / "scripts/p2_review.py")
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"eval_id": "synthetic-1", "current_query": "Plan a meeting",
                      "query_context": "test", "query_date": "2026-09-29",
                      "task_risk": "low", "pack_version": "synthetic-test",
                      "available_actions": [], "candidate_memories": [
                          {"memory_id": "m1", "content": "An old preference"}],
                      "interaction_history": [], "applicability_boundary_metadata": []}]
        self.fingerprint = "test-fingerprint"
        self.bundle = REVIEW.blank_bundle(self.rows, self.fingerprint)

    def reviewed(self):
        entry = self.bundle["cases"][0]
        entry["targets"].update(permission="UNKNOWN", relationship="UNKNOWN",
                                evidence_status="UNKNOWN", risk="LOW",
                                robust_action_available=False, robust_action=None,
                                decisive_evidence_ids=[], memory_action="ASK")
        entry["evidence_kinds"] = {"m1": "MEMORY_SOURCE"}
        entry["review"] = {"status": "REVIEWED", "reviewer": "Synthetic test reviewer",
                           "reviewed_at": "2026-09-29T12:00:00Z"}
        return entry

    def result(self, require=False):
        return REVIEW.validate_bundle(self.bundle, self.rows, self.fingerprint, require)

    def test_blank_draft_passes_but_cannot_unlock_execution(self):
        result = self.result()
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["execution_ready"])
        self.assertEqual(self.result(True)["status"], "FAIL")

    def test_complete_review_is_contract_ready_only(self):
        self.reviewed()
        self.assertTrue(self.result(True)["execution_ready"])
        self.assertIn("not independently authenticated", self.result()["boundary"])

    def test_protocol_fingerprint_and_case_coverage_are_mandatory(self):
        original = copy.deepcopy(self.bundle)
        for field in ("source_sha256", "protocol_version"):
            self.bundle = copy.deepcopy(original)
            self.bundle[field] = "wrong"
            self.assertEqual(self.result()["status"], "FAIL")
        self.bundle = copy.deepcopy(original)
        self.bundle["cases"] *= 2
        self.assertEqual(self.result()["status"], "FAIL")
        self.bundle["cases"] = []
        self.assertEqual(self.result()["status"], "FAIL")

    def test_drafts_reject_malformed_values_and_untraceable_ids(self):
        entry = self.bundle["cases"][0]
        for field, value in (("permission", []), ("risk", "INVALID"),
                             ("robust_action_available", 1), ("decisive_evidence_ids", ["missing"])):
            entry["targets"][field] = value
            self.assertEqual(self.result()["status"], "FAIL", field)
            entry["targets"][field] = None
        entry["review"]["status"] = []
        self.assertEqual(self.result()["status"], "FAIL")

    def test_review_needs_named_reviewer_and_timezone_timestamp(self):
        entry = self.reviewed()
        for timestamp in ("yesterday", "2026-09-29T12:00:00", None):
            entry["review"]["reviewed_at"] = timestamp
            self.assertEqual(self.result(True)["status"], "FAIL")
        entry["review"]["reviewed_at"] = "2026-09-29T12:00:00Z"
        entry["review"]["reviewer"] = " "
        self.assertEqual(self.result(True)["status"], "FAIL")

    def test_review_rejects_unsupported_claim_and_wrong_expected_action(self):
        entry = self.reviewed()
        entry["targets"].update(permission="ALLOWED", relationship="DIRECT", evidence_status="SUFFICIENT", memory_action="USE")
        self.assertEqual(self.result(True)["status"], "FAIL")
        entry["evidence_kinds"]["m1"] = "APPLICABILITY"
        entry["targets"]["decisive_evidence_ids"] = ["m1"]
        self.assertEqual(self.result(True)["status"], "PASS")
        entry["targets"]["memory_action"] = "IGNORE"
        self.assertEqual(self.result(True)["status"], "FAIL")

    def test_duplicate_decisive_ids_and_memory_sources_fail(self):
        entry = self.reviewed()
        for ids in (["m1", "m1"], ["m1"]):
            entry["targets"]["decisive_evidence_ids"] = ids
            self.assertEqual(self.result(True)["status"], "FAIL")

    def test_public_source_requires_hash_allowlist_and_evidence_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.jsonl"
            def write(rows):
                path.write_text(json.dumps(rows[0]) + "\n")
                return hashlib.sha256(path.read_bytes()).hexdigest()
            fingerprint = write(self.rows)
            self.assertEqual(REVIEW.load_public(path, fingerprint)[0], self.rows)
            with self.assertRaises(ValueError):
                REVIEW.load_public(path, "wrong")
            self.rows[0]["evaluator_gold"] = "excluded"
            with self.assertRaises(ValueError):
                REVIEW.load_public(path, write(self.rows))
            del self.rows[0]["evaluator_gold"]
            self.rows[0]["candidate_memories"][0].pop("memory_id")
            with self.assertRaises(ValueError):
                REVIEW.load_public(path, write(self.rows))

    def test_html_escapes_source_script_and_has_no_network_dependencies(self):
        self.rows[0]["current_query"] = "</script><script>alert('test')</script>"
        html = REVIEW.build_html(self.rows, self.fingerprint)
        self.assertNotIn(self.rows[0]["current_query"], html)
        self.assertIn("\\u003c/script", html)
        self.assertIn("connect-src 'none'", html)
        self.assertNotIn("__REVIEW_DATA__", html)

    def test_embedded_proposals_remain_drafts_and_require_matching_source(self):
        self.bundle["cases"][0]["targets"]["risk"] = "LOW"
        self.bundle["cases"][0]["notes"] = "ASSISTANT PROPOSAL, NOT GOLD."
        html = REVIEW.build_html(self.rows, self.fingerprint, self.bundle)
        self.assertIn("ASSISTANT PROPOSAL, NOT GOLD.", html)
        self.assertEqual(self.result()["reviewed"], 0)
        self.bundle["source_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            REVIEW.build_html(self.rows, self.fingerprint, self.bundle)


if __name__ == "__main__":
    unittest.main()
