import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_ONLY_TRIGGER = "Use when " + "Codex"


class PortabilityTest(unittest.TestCase):
    def test_skill_docs_use_agent_agnostic_paths(self):
        skill = (ROOT / "SKILL.md").read_text()
        openai = (ROOT / "agents" / "openai.yaml").read_text()

        self.assertNotIn(CODEX_ONLY_TRIGGER, skill)
        self.assertNotIn("$HOME/.codex", skill)
        self.assertIn("GROMPT_DIR", skill)
        self.assertIn("any agent", skill.lower())
        self.assertIn("$grompt", openai)


if __name__ == "__main__":
    unittest.main()
