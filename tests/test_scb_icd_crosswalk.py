"""Fail-closed regression tests for SCB cause-of-death ICD candidate crosswalk."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/data/scb-icd-crosswalk-audit.json"
EXPECTED = {"tot", "tot2", "and", "hjärt", "tum", "alk", "daalk", "dacov", "sjalv", "skad", "övr"}

class CrosswalkSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.groups = {g["scb_code"]: g for g in cls.doc["groups"]}

    def test_exact_group_set(self):
        self.assertEqual(set(self.groups), EXPECTED)
        self.assertEqual(len(self.doc["groups"]), len(EXPECTED))

    def test_unverified_candidates_never_approved(self):
        self.assertEqual(self.doc["status"], "candidate_crosswalk_not_approved_for_aggregation")
        for code, group in self.groups.items():
            with self.subTest(code=code):
                self.assertIs(group["approved_for_aggregation"], False)
                self.assertNotEqual(group["validation_status"], "approved")
                self.assertEqual(set(group["code_presence"]), set(group["candidate_socialstyrelsen_codes"]))
                self.assertTrue(all(group["code_presence"].values()), f"Missing code for {code}")

    def test_known_hazardous_groups_remain_blocked(self):
        for code in ("tot2", "alk", "daalk", "dacov", "sjalv", "skad", "övr"):
            self.assertFalse(self.groups[code]["approved_for_aggregation"])

    def test_injury_candidate_is_not_a_validated_exclusion(self):
        injury = self.groups["skad"]
        self.assertIn("V01-Y98", injury["candidate_socialstyrelsen_codes"])
        self.assertFalse(injury["approved_for_aggregation"])
        self.assertIn("Y10-Y34", self.groups["sjalv"]["candidate_socialstyrelsen_codes"])

if __name__ == "__main__":
    unittest.main()
