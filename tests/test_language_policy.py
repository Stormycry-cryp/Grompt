import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LanguagePolicyTest(unittest.TestCase):
    def test_skill_uses_local_common_language_without_hardcoded_default(self):
        skill = (ROOT / "SKILL.md").read_text()

        self.assertIn("## Language Policy", skill)
        self.assertIn("user's local/common language", skill)
        self.assertIn("host locale", skill)
        self.assertIn("Do not hard-code Chinese or English as the default", skill)
        self.assertIn("Preserve exact visible text", skill)
        self.assertIn("If the task explicitly requests another language", skill)


if __name__ == "__main__":
    unittest.main()
