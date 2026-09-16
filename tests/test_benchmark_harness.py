from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_benchmark.py"


class BenchmarkHarnessTests(unittest.TestCase):
    def test_markdown_table_covers_examples_and_extras(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("Synthetic guard outcomes", result.stdout)
        self.assertIn("schema/examples/superseded-pool.json", result.stdout)
        self.assertIn("benchmarks/scenarios/conflicting-permission.json", result.stdout)
        self.assertIn("not production validated", result.stdout)

    def test_json_mode_lists_stable_fields(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("not production validated", payload["boundary"])
        self.assertGreaterEqual(len(payload["results"]), 10)
        first = payload["results"][0]
        self.assertEqual(
            set(first),
            {
                "scenario",
                "proposed_memory_action",
                "guard_verdict",
                "memory_action",
                "memory_state",
                "reason_code",
            },
        )


if __name__ == "__main__":
    unittest.main()
