import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p2_operational as OP
import test_p2_review


class OperationalTests(unittest.TestCase):
    def setUp(self):
        fixture = test_p2_review.ReviewTests()
        fixture.setUp()
        self.rows = fixture.rows

    def test_balanced_plan_differs_only_by_rubric(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        self.rows[1]["eval_id"] = "synthetic-2"
        plan = OP.paired_plan(self.rows)
        self.assertEqual([x["condition"] for x in plan], [*OP.CONDITIONS, *OP.CONDITIONS[::-1]])
        for left, right in (plan[:2], plan[2:]):
            requests = {x["condition"]: copy.deepcopy(x["request"]) for x in (left, right)}
            requests["contract_only"].pop("instructions")
            requests["with_rubric"].pop("instructions")
            self.assertEqual(requests["contract_only"], requests["with_rubric"])
        self.assertEqual(OP.paired_plan(self.rows[::-1]), plan)

    def test_request_tampering_rejected_before_transport(self):
        plan = OP.paired_plan(self.rows)
        self.assertEqual(OP.check_request(plan[0], self.rows), plan[0]["request"])
        for field, value in (("model", "different"), ("tools", [{}]), ("max_output_tokens", 9000)):
            changed = copy.deepcopy(plan[0])
            changed["request"][field] = value
            changed["request_sha256"] = OP.fingerprint(changed["request"])
            with self.assertRaises(ValueError):
                OP.check_request(changed, self.rows)

    def response(self, value):
        return {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps(value)}]}]}

    def test_incomplete_invalid_json_and_source_tampering(self):
        row = self.rows[0]
        self.assertEqual(OP.validate_response({"status": "incomplete"}, row)["status"], "INCOMPLETE")
        self.assertEqual(OP.validate_response({"status": "completed", "output": []}, row)["status"], "INVALID_JSON")
        value = {"current_task": row["current_query"], "candidate_memory": row["candidate_memories"][0]["content"],
                 "proposed_memory_action": "USE", "permission": "UNKNOWN", "relationship": "UNKNOWN",
                 "risk": "LOW", "evidence_status": "UNKNOWN", "robust_action_available": False,
                 "evidence": [{"id": "m1", "text": json.dumps(row["candidate_memories"][0]),
                               "kind": "MEMORY_SOURCE", "decisive": False}]}
        self.assertEqual(OP.validate_response(self.response(value), row)["status"], "VALID")
        value["evidence"][0]["text"] = '"invented"'
        self.assertEqual(OP.validate_response(self.response(value), row)["status"], "SOURCE_MISMATCH")

    def test_budget_reserves_reasoning_and_keeps_uncertain_charge(self):
        budget = OP.Budget()
        reserved = budget.reserve(100)
        self.assertEqual(budget.committed, reserved)
        with self.assertRaises(ValueError):
            budget.reserve(100)
        actual = budget.settle({"input_tokens": 100, "output_tokens": 1000,
                                "output_tokens_details": {"reasoning_tokens": 900}})
        self.assertEqual(actual, OP.Budget.INPUT * 100 + OP.Budget.OUTPUT * 1000)
        self.assertEqual(budget.committed, actual)

    def test_hard_limits_and_invalid_usage_stop(self):
        for value in ("NaN", "Infinity", "-1", "3"):
            with self.assertRaises(ValueError):
                OP.Budget(value)
        budget = OP.Budget("0.001")
        with self.assertRaises(ValueError):
            budget.reserve(100)
        self.assertEqual(budget.calls, 0)
        budget = OP.Budget(call_limit=1)
        budget.reserve(100)
        for usage in ({"input_tokens": -1, "output_tokens": 1},
                      {"input_tokens": 2000, "output_tokens": 1},
                      {"input_tokens": 100, "output_tokens": 4097}):
            with self.assertRaises(ValueError):
                budget.settle(usage)
            self.assertIsNotNone(budget.pending)
        budget.settle({"input_tokens": 100, "output_tokens": 100})
        with self.assertRaises(ValueError):
            budget.reserve(100)


if __name__ == "__main__":
    unittest.main()
