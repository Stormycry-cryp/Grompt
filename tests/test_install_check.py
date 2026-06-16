import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_check.py"


class InstallCheckTest(unittest.TestCase):
    def test_install_check_reports_provider_guidance(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        data = json.loads(result.stdout)

        self.assertIn("image_generation_available", data)
        self.assertIn("recommended_provider", data)
        self.assertEqual(data["recommended_provider"], "gpt-image-2")
        self.assertIn("provider_request", data)
        self.assertIn("provider", data["provider_request"].lower())
        self.assertIn("GPT Image 2", data["provider_request"])
        self.assertIn("prompt_only_fallback", data)
        self.assertIn("prompt", data["prompt_only_fallback"].lower())


if __name__ == "__main__":
    unittest.main()
