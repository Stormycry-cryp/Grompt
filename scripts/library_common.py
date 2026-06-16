from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "references" / "prompt_cases.json"
DEFAULT_USER_LIBRARY = ROOT / "references" / "user_prompt_library.json"


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_prompts() -> list[dict[str, Any]]:
    payload = load_json(CASE_FILE, {"cases": []})
    prompts = []
    for item in payload.get("cases", []):
        prompts.append(
            {
                "id": f"case-{item['id']}",
                "title": item["title"],
                "prompt": item.get("prompt", ""),
                "source": "awesome-gpt-image-2",
                "source_url": item.get("githubUrl", ""),
                "tags": {
                    "category": item.get("category", "Other Use Cases"),
                    "style": item.get("styles", []),
                    "scene": item.get("scenes", []),
                    "source": "upstream",
                },
            }
        )
    return prompts


def load_user_library(path: Path = DEFAULT_USER_LIBRARY) -> dict[str, Any]:
    return load_json(
        path,
        {
            "version": 1,
            "description": "User-confirmed prompts added by grompt.",
            "prompts": [],
        },
    )


def save_user_library(payload: dict[str, Any], path: Path = DEFAULT_USER_LIBRARY) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_all_prompts(user_library: Path = DEFAULT_USER_LIBRARY) -> list[dict[str, Any]]:
    return load_source_prompts() + load_user_library(user_library).get("prompts", [])


def tag_values(tags: dict[str, Any], tag_type: str) -> list[str]:
    value = tags.get(tag_type)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]
