#!/usr/bin/env python3
"""Progressively disclose prompt-library tags and prompts."""

from __future__ import annotations

import argparse
import json
from collections import Counter

from library_common import DEFAULT_USER_LIBRARY, load_all_prompts, tag_values


TAG_TYPES = ["category", "style", "scene", "source"]


def list_types(prompts: list[dict]) -> dict:
    counts = {tag_type: 0 for tag_type in TAG_TYPES}
    for item in prompts:
        for tag_type in TAG_TYPES:
            if tag_values(item.get("tags", {}), tag_type):
                counts[tag_type] += 1
    visible_types = [tag_type for tag_type in TAG_TYPES if counts[tag_type]]
    return {
        "level": "types",
        "tag_types": visible_types,
        "tag_type_counts": {tag_type: counts[tag_type] for tag_type in visible_types},
    }


def list_tags(prompts: list[dict], tag_type: str) -> dict:
    counter = Counter()
    for item in prompts:
        for tag in tag_values(item.get("tags", {}), tag_type):
            counter[tag] += 1
    return {
        "level": "tags",
        "tag_type": tag_type,
        "tags": [
            {"tag": tag, "prompt_count": count}
            for tag, count in counter.most_common()
        ],
    }


def list_prompts(prompts: list[dict], tag_type: str, tag: str, limit: int) -> dict:
    selected = []
    for item in prompts:
        if tag in tag_values(item.get("tags", {}), tag_type):
            selected.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "source": item.get("source", ""),
                    "source_url": item.get("source_url", ""),
                    "tags": item.get("tags", {}),
                    "prompt_excerpt": item.get("prompt", "").replace("\n", " ")[:500],
                }
            )
    return {
        "level": "prompts",
        "tag_type": tag_type,
        "tag": tag,
        "prompts": selected[: max(1, limit)],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["types", "tags", "prompts"], required=True)
    parser.add_argument("--tag-type", choices=TAG_TYPES)
    parser.add_argument("--tag")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--library", default=str(DEFAULT_USER_LIBRARY))
    args = parser.parse_args()

    prompts = load_all_prompts(user_library=__import__("pathlib").Path(args.library))
    if args.level == "types":
        output = list_types(prompts)
    elif args.level == "tags":
        if not args.tag_type:
            parser.error("--tag-type is required for --level tags")
        output = list_tags(prompts, args.tag_type)
    else:
        if not args.tag_type or not args.tag:
            parser.error("--tag-type and --tag are required for --level prompts")
        output = list_prompts(prompts, args.tag_type, args.tag, args.limit)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
