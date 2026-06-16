import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "synthesize_prompt.py"
QUERY_SCRIPT = ROOT / "scripts" / "library_query.py"
ADD_SCRIPT = ROOT / "scripts" / "library_add.py"
TMP_LIBRARY = ROOT / "tests" / "tmp_user_prompt_library.json"


def run_task(task: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--task", task, "--count", "4"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout)


class SynthesizePromptTest(unittest.TestCase):
    def tearDown(self):
        if TMP_LIBRARY.exists():
            TMP_LIBRARY.unlink()

    def test_infographic_task_returns_reference_backed_prompt(self):
        data = run_task("做一张城市生命系统信息图，要求信息结构清楚，中文标签可读，竖版")

        references = data["references"]
        self.assertTrue(3 <= len(references) <= 5)
        self.assertTrue(any(item["id"] in {1, 334, 341} for item in references))
        self.assertTrue(all(item["source"]["githubUrl"] for item in references))
        self.assertTrue(data["new_prompt"].startswith("Use case:"))
        self.assertIn("城市生命系统", data["new_prompt"])
        self.assertIn("Reference genes:", data["new_prompt"])
        self.assertTrue(data["extracted_genes"])
        self.assertTrue(data["structure"])

    def test_product_task_prefers_product_or_commerce_references(self):
        data = run_task("给一款高端咖啡豆包装做电商主图，突出产地、风味和质感")

        categories = {item["category"] for item in data["references"]}
        self.assertTrue(
            "Products & E-commerce" in categories
            or any("Product" in item["styles"] for item in data["references"])
        )
        self.assertIn("咖啡豆", data["new_prompt"])
        use_case = data["analysis"]["use_case"].lower()
        self.assertTrue("product" in use_case or "commerce" in use_case)

    def test_progressive_tag_query_lists_types_then_tags_then_prompts(self):
        types = subprocess.run(
            [sys.executable, str(QUERY_SCRIPT), "--level", "types"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        type_data = json.loads(types.stdout)
        self.assertIn("category", type_data["tag_types"])
        self.assertIn("style", type_data["tag_types"])
        self.assertIn("scene", type_data["tag_types"])

        tags = subprocess.run(
            [sys.executable, str(QUERY_SCRIPT), "--level", "tags", "--tag-type", "category"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        tag_data = json.loads(tags.stdout)
        self.assertTrue(any(item["tag"] == "Charts & Infographics" for item in tag_data["tags"]))

        prompts = subprocess.run(
            [
                sys.executable,
                str(QUERY_SCRIPT),
                "--level",
                "prompts",
                "--tag-type",
                "category",
                "--tag",
                "Charts & Infographics",
                "--limit",
                "3",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        prompt_data = json.loads(prompts.stdout)
        self.assertTrue(1 <= len(prompt_data["prompts"]) <= 3)
        self.assertTrue(all(item["tags"]["category"] == "Charts & Infographics" for item in prompt_data["prompts"]))

    def test_confirmed_prompt_can_be_added_to_user_library_with_tags(self):
        prompt = "Use case: poster\nPrimary request: 生成一张夜航计划音乐节海报"
        result = subprocess.run(
            [
                sys.executable,
                str(ADD_SCRIPT),
                "--library",
                str(TMP_LIBRARY),
                "--title",
                "夜航计划音乐节海报",
                "--prompt",
                prompt,
                "--category",
                "Posters & Typography",
                "--style",
                "Poster",
                "--scene",
                "Music",
                "--task",
                "做一张赛博朋克音乐节海报",
                "--source",
                "user-confirmed",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["added"]["title"], "夜航计划音乐节海报")
        self.assertEqual(data["added"]["tags"]["category"], "Posters & Typography")
        saved = json.loads(TMP_LIBRARY.read_text())
        self.assertEqual(len(saved["prompts"]), 1)
        self.assertEqual(saved["prompts"][0]["source"], "user-confirmed")


if __name__ == "__main__":
    unittest.main()
