from __future__ import annotations

import re
import unittest

from test_guard_decision import GUARD, ROOT

SKILL_ROOT = ROOT / "memory-applicability-guard"


class SkillContractTests(unittest.TestCase):
    def test_discovery_description_stays_concise(self):
        text = (SKILL_ROOT / "SKILL.md").read_text()
        description = next(line.split(":", 1)[1].strip() for line in text.splitlines() if line.startswith("description:"))
        self.assertLessEqual(len(description), 200)
        self.assertNotIn("production", description.lower())

    def test_entrypoint_stays_short_and_has_exclusions(self):
        text = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertLessEqual(len(text.splitlines()), 90)
        self.assertIn("When not to use", text)

    def test_entrypoint_references_resolve(self):
        text = (SKILL_ROOT / "SKILL.md").read_text()
        references = re.findall(r"\]\((references/[^)]+)\)", text)
        self.assertTrue(references)
        for relative in references:
            self.assertTrue((SKILL_ROOT / relative).is_file(), relative)

    def test_rubric_covers_enums_and_relationship_support(self):
        text = (SKILL_ROOT / "references/classification-rubric.md").read_text()
        for values in (GUARD.PERMISSIONS, GUARD.RELATIONSHIPS, GUARD.EVIDENCE_STATUSES, GUARD.RISKS, GUARD.EVIDENCE_KINDS):
            for value in values:
                self.assertIn(f"`{value}`", text)
        for relationship, required in GUARD.CLAIM_SUPPORT["relationship"].items():
            row = next(line for line in text.splitlines() if line.startswith(f"| `{relationship}` |"))
            kinds = set(re.findall(r"`([A-Z_]+)`", row)) & GUARD.EVIDENCE_KINDS
            self.assertEqual(kinds, required, relationship)


if __name__ == "__main__":
    unittest.main()
