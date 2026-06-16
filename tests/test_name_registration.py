import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_REGISTERED_NAME = "gpt-image-2-" + "prompt-synthesizer"
OLD_DISPLAY_NAME = "GPT Image 2 " + "Prompt Synthesizer"


class NameRegistrationTest(unittest.TestCase):
    def test_registered_name_and_display_name_are_grompt(self):
        skill = (ROOT / "SKILL.md").read_text()
        openai = (ROOT / "agents" / "openai.yaml").read_text()

        self.assertIn("name: grompt", skill)
        self.assertIn('display_name: "Grompt"', openai)
        self.assertIn("$grompt", openai)
        self.assertNotIn(OLD_REGISTERED_NAME, skill)
        self.assertNotIn(OLD_DISPLAY_NAME, skill)
        self.assertNotIn(OLD_REGISTERED_NAME, openai)
        self.assertNotIn(OLD_DISPLAY_NAME, openai)


if __name__ == "__main__":
    unittest.main()
