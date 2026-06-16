#!/usr/bin/env python3
"""Retrieve GPT-Image2 prompt references and synthesize a task-specific brief."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "references" / "prompt_cases.json"


CATEGORY_RULES = [
    ("ui-mockup", "UI & Interfaces", ["ui", "app", "dashboard", "界面", "截图", "网页", "小红书", "直播", "朋友圈"]),
    ("infographic-diagram", "Charts & Infographics", ["infographic", "diagram", "chart", "atlas", "信息图", "图谱", "图解", "科普", "结构", "流程", "系统"]),
    ("poster", "Posters & Typography", ["poster", "海报", "封面", "字体", "campaign", "主视觉", "kv"]),
    ("product-commerce", "Products & E-commerce", ["product", "packaging", "电商", "商品", "产品", "包装", "主图", "卖点", "咖啡", "咖啡豆"]),
    ("brand-logo", "Brand & Logos", ["brand", "logo", "identity", "品牌", "标志", "vi"]),
    ("architecture-space", "Architecture & Spaces", ["architecture", "interior", "建筑", "室内", "空间", "地图"]),
    ("photorealistic", "Photography & Realism", ["photo", "portrait", "realistic", "摄影", "写真", "写实", "镜头"]),
    ("illustration-art", "Illustration & Art", ["illustration", "painting", "插画", "绘画", "水彩", "艺术"]),
    ("character-design", "Characters & People", ["character", "pose", "角色", "人物", "头像", "姿态"]),
    ("story-scene", "Scenes & Storytelling", ["storyboard", "scene", "分镜", "叙事", "故事", "场景"]),
    ("historical-classical", "History & Classical Themes", ["history", "dynasty", "古风", "历史", "唐", "宋", "水墨"]),
    ("document-publishing", "Documents & Publishing", ["document", "manual", "文档", "手册", "报告", "白皮书"]),
]

STYLE_RULES = {
    "UI": ["ui", "界面", "截图", "app", "dashboard"],
    "Infographic": ["信息图", "图谱", "图解", "diagram", "chart", "atlas", "结构"],
    "Poster": ["海报", "poster", "封面", "campaign", "kv", "主视觉"],
    "Realistic": ["写实", "摄影", "写真", "realistic", "photo", "镜头"],
    "Product": ["产品", "商品", "包装", "电商", "product", "packaging", "咖啡豆"],
    "Brand": ["品牌", "brand", "logo", "identity"],
    "Illustration": ["插画", "illustration", "绘本", "手绘"],
    "Character": ["人物", "角色", "pose", "character"],
    "Classical": ["古风", "水墨", "历史", "classical"],
    "3D": ["3d", "立体", "渲染", "玩具"],
}

SCENE_RULES = {
    "Commerce": ["商业", "电商", "商品", "campaign", "卖点", "包装", "主图", "品牌"],
    "Education": ["科普", "教育", "解释", "学习", "知识", "信息图"],
    "Tech": ["ai", "技术", "系统", "数据", "软件", "科技", "rag"],
    "Social": ["社媒", "小红书", "抖音", "朋友圈", "直播"],
    "Fashion": ["时尚", "服装", "穿搭", "模特"],
    "Food": ["食物", "咖啡", "咖啡豆", "饮品", "食品"],
    "Travel": ["旅行", "城市", "地域", "产地"],
    "Story": ["叙事", "故事", "分镜", "世界观"],
    "History": ["历史", "古风", "朝代"],
}


def load_cases() -> dict[str, Any]:
    return json.loads(CASE_FILE.read_text(encoding="utf-8"))


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", text.lower())
    cjk = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    grams: list[str] = []
    for chunk in cjk:
        grams.append(chunk)
        grams.extend(chunk[i : i + 2] for i in range(max(0, len(chunk) - 1)))
        grams.extend(chunk[i : i + 3] for i in range(max(0, len(chunk) - 2)))
    return words + grams


def keyword_hits(text: str, rules: dict[str, list[str]]) -> list[str]:
    lower = text.lower()
    hits = []
    for label, keys in rules.items():
        if any(key.lower() in lower for key in keys):
            hits.append(label)
    return hits


def analyze_task(task: str) -> dict[str, Any]:
    lower = task.lower()
    selected = ("special-task", "Other Use Cases", [])
    for use_case, category, keys in CATEGORY_RULES:
        if any(key.lower() in lower for key in keys):
            selected = (use_case, category, keys)
            break
    styles = keyword_hits(task, STYLE_RULES)
    scenes = keyword_hits(task, SCENE_RULES)
    if selected[1] == "Products & E-commerce" and "Product" not in styles:
        styles.insert(0, "Product")
    if selected[1] == "Charts & Infographics" and "Infographic" not in styles:
        styles.insert(0, "Infographic")
    if selected[1] == "Products & E-commerce" and "Commerce" not in scenes:
        scenes.insert(0, "Commerce")
    return {
        "task": task,
        "use_case": selected[0],
        "category": selected[1],
        "styles": styles[:4],
        "scenes": scenes[:4],
        "tokens": tokenize(task),
    }


def score_case(case: dict[str, Any], analysis: dict[str, Any], idf: dict[str, float]) -> float:
    text = f"{case['title']} {case['category']} {' '.join(case.get('styles', []))} {' '.join(case.get('scenes', []))} {case['prompt']}"
    case_tokens = set(tokenize(text))
    score = 0.0
    for token in set(analysis["tokens"]):
        if token in case_tokens:
            score += idf.get(token, 1.0)
    if case["category"] == analysis["category"]:
        score += 8.0
    score += 2.5 * len(set(case.get("styles", [])) & set(analysis["styles"]))
    score += 1.5 * len(set(case.get("scenes", [])) & set(analysis["scenes"]))
    if any(key in case["title"] for key in ["图谱", "信息图", "技术详解"]) and analysis["category"] == "Charts & Infographics":
        score += 2.0
    if case["id"] in {1, 334, 341} and analysis["category"] == "Charts & Infographics":
        score += 3.0
    return score


def build_idf(cases: list[dict[str, Any]]) -> dict[str, float]:
    docs = []
    for case in cases:
        docs.append(set(tokenize(f"{case['title']} {case['prompt']} {case['category']}")))
    df = Counter(token for doc in docs for token in doc)
    total = len(docs)
    return {token: math.log((1 + total) / (1 + count)) + 1 for token, count in df.items()}


def retrieve(cases: list[dict[str, Any]], analysis: dict[str, Any], count: int) -> list[dict[str, Any]]:
    idf = build_idf(cases)
    ranked = sorted(cases, key=lambda c: score_case(c, analysis, idf), reverse=True)
    selected = ranked[: max(3, min(5, count))]
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "styles": item.get("styles", []),
            "scenes": item.get("scenes", []),
            "image": item.get("image", ""),
            "source": {
                "label": item.get("sourceLabel", ""),
                "url": item.get("sourceUrl", ""),
                "githubUrl": item.get("githubUrl", ""),
            },
            "prompt_excerpt": item.get("prompt", "").replace("\n", " ")[:500],
        }
        for item in selected
    ]


def extract_genes(references: list[dict[str, Any]]) -> list[str]:
    text = " ".join(item["prompt_excerpt"] for item in references)
    genes = []
    gene_rules = [
        ("Clear modular information hierarchy", ["module", "模块", "panel", "信息", "层级", "numbered"]),
        ("Locked aspect ratio and output format", ["9:16", "16:9", "3:4", "比例", "aspect ratio"]),
        ("Readable exact text and labels", ["文字", "label", "readable", "清晰", "中文", "标题"]),
        ("Specific composition and camera/framing", ["构图", "composition", "lens", "镜头", "framing"]),
        ("Concrete material, lighting, and texture language", ["材质", "lighting", "光影", "texture", "paper", "studio"]),
        ("Explicit negative constraints", ["avoid", "no ", "不要", "禁止", "约束"]),
    ]
    lower = text.lower()
    for label, keys in gene_rules:
        if any(key.lower() in lower for key in keys):
            genes.append(label)
    return genes[:6] or ["Concrete subject, composition, style, text, and constraints"]


def infer_structure(analysis: dict[str, Any]) -> list[str]:
    if analysis["category"] == "Charts & Infographics":
        return ["Title area", "3-5 content modules", "visual flow/connectors", "short labels", "negative constraints"]
    if analysis["category"] == "Products & E-commerce":
        return ["Hero product", "usage/ingredient context", "selling-point labels", "premium lighting/materials", "clean background"]
    if analysis["category"] == "Posters & Typography":
        return ["Main visual", "dominant title", "supporting copy", "palette/mood", "poster constraints"]
    if analysis["category"] == "UI & Interfaces":
        return ["Platform frame", "navigation chrome", "core content", "interaction/status layer", "readable text"]
    return ["Intent", "subject", "composition", "style", "text", "constraints"]


def synthesize_prompt(analysis: dict[str, Any], references: list[dict[str, Any]], genes: list[str], structure: list[str]) -> str:
    ref_line = "; ".join(f"case {r['id']} {r['title']}" for r in references)
    styles = ", ".join(analysis["styles"]) or analysis["category"]
    scenes = ", ".join(analysis["scenes"]) or "task-appropriate"
    return "\n".join(
        [
            f"Use case: {analysis['use_case']}",
            f"Primary request: {analysis['task']}",
            f"Reference prompts: {ref_line}",
            f"Reference genes: {', '.join(genes)}.",
            f"Structure: {', '.join(structure)}.",
            f"Style/medium: {styles}; scene context: {scenes}.",
            "Composition: make the visual hierarchy obvious at thumbnail size; keep one dominant focal area and enough whitespace for readable information.",
            "Text: quote every required visible phrase exactly; keep labels short; prefer Chinese text when the task is Chinese.",
            "Details: translate the task into concrete subjects, materials, lighting, palette, layout rhythm, and surface texture instead of generic praise words.",
            "Constraints: no gibberish text, no unrelated logos, no watermark, no clutter, no extra decorative copy, no low-resolution or blurry output.",
        ]
    )


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Grompt Synthesis",
        "",
        "## Analysis",
        f"- Use case: {data['analysis']['use_case']}",
        f"- Category: {data['analysis']['category']}",
        f"- Styles: {', '.join(data['analysis']['styles']) or 'none'}",
        f"- Scenes: {', '.join(data['analysis']['scenes']) or 'none'}",
        "",
        "## References",
    ]
    for item in data["references"]:
        lines.append(f"- case {item['id']} {item['title']} | {item['category']} | {item['source']['githubUrl']}")
    lines += [
        "",
        "## Extracted Genes",
        *[f"- {gene}" for gene in data["extracted_genes"]],
        "",
        "## Structure",
        *[f"- {part}" for part in data["structure"]],
        "",
        "## New Prompt",
        "```text",
        data["new_prompt"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Image task to analyze")
    parser.add_argument("--count", type=int, default=5, help="Number of references, clamped to 3-5")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    payload = load_cases()
    analysis = analyze_task(args.task)
    references = retrieve(payload["cases"], analysis, args.count)
    genes = extract_genes(references)
    structure = infer_structure(analysis)
    data = {
        "repository": payload["repository"],
        "sourceCommit": payload.get("sourceCommit", ""),
        "analysis": {k: v for k, v in analysis.items() if k != "tokens"},
        "references": references,
        "extracted_genes": genes,
        "structure": structure,
        "new_prompt": synthesize_prompt(analysis, references, genes, structure),
    }
    if args.format == "markdown":
        print(render_markdown(data), end="")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
