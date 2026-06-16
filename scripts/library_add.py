#!/usr/bin/env python3
"""Add a user-confirmed prompt to the iterative prompt library."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from library_common import DEFAULT_USER_LIBRARY, load_user_library, save_user_library


def split_tags(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for part in value.split(","):
            tag = part.strip()
            if tag and tag not in result:
                result.append(tag)
    return result


def make_id(title: str, prompt: str) -> str:
    digest = hashlib.sha1(f"{title}\n{prompt}".encode("utf-8")).hexdigest()[:12]
    return f"user-{digest}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", default=str(DEFAULT_USER_LIBRARY))
    parser.add_argument("--title", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--style", action="append", default=[])
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--task", default="")
    parser.add_argument("--source", default="user-confirmed")
    parser.add_argument("--source-url", default="")
    args = parser.parse_args()

    library_path = Path(args.library)
    payload = load_user_library(library_path)
    prompt_id = make_id(args.title, args.prompt)
    payload["prompts"] = [item for item in payload.get("prompts", []) if item.get("id") != prompt_id]
    entry = {
        "id": prompt_id,
        "title": args.title,
        "prompt": args.prompt,
        "task": args.task,
        "source": args.source,
        "source_url": args.source_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": {
            "category": args.category,
            "style": split_tags(args.style),
            "scene": split_tags(args.scene),
            "source": "user",
        },
    }
    payload["prompts"].append(entry)
    save_user_library(payload, library_path)
    print(json.dumps({"library": str(library_path), "added": entry, "total_user_prompts": len(payload["prompts"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
