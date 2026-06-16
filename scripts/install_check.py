#!/usr/bin/env python3
"""Check whether an image generation provider is available for this skill."""

from __future__ import annotations

import json
import os
from pathlib import Path


HOME = Path.home()
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))


def exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def detect() -> dict:
    imagegen_skill = CODEX_HOME / "skills" / ".system" / "imagegen" / "SKILL.md"
    imagegen_cli = CODEX_HOME / "skills" / ".system" / "imagegen" / "scripts" / "image_gen.py"
    gpt_image_2_skill = CODEX_HOME / "skills" / "gpt-image-2" / "SKILL.md"
    gpt_image_2_cli = CODEX_HOME / "skills" / "gpt-image-2" / "scripts" / "gpt_image.py"
    codex_auth = CODEX_HOME / "auth.json"
    codex_config = CODEX_HOME / "config.toml"

    available_paths = {
        "imagegen_skill": exists(imagegen_skill),
        "imagegen_cli": exists(imagegen_cli),
        "gpt_image_2_skill": exists(gpt_image_2_skill),
        "gpt_image_2_cli": exists(gpt_image_2_cli),
        "codex_auth": exists(codex_auth),
        "codex_config": exists(codex_config),
        "OPENAI_IMAGE_API_KEY": bool(os.environ.get("OPENAI_IMAGE_API_KEY")),
        "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
    }
    image_generation_available = (
        available_paths["imagegen_skill"]
        or available_paths["imagegen_cli"]
        or available_paths["gpt_image_2_skill"]
        or available_paths["gpt_image_2_cli"]
    )
    provider_configured = (
        available_paths["OPENAI_IMAGE_API_KEY"]
        or available_paths["OPENAI_API_KEY"]
        or (available_paths["codex_auth"] and available_paths["codex_config"])
    )
    provider_request = (
        "Image generation is not ready. Please provide an image generation provider; "
        "the best fit for this skill is GPT Image 2 / gpt-image-2, ideally via the existing imagegen skill "
        "or a GPT Image 2-compatible provider with API key and base URL."
    )
    if image_generation_available and not provider_configured:
        provider_request = (
            "Image generation tooling was found, but provider credentials/configuration were not confirmed. "
            "Please provide the provider details; GPT Image 2 / gpt-image-2 is recommended for this prompt library."
        )
    elif image_generation_available and provider_configured:
        provider_request = (
            "Image generation tooling and likely provider configuration were found. "
            "Prefer GPT Image 2 / gpt-image-2 for this skill unless the user specifies another provider."
        )

    return {
        "image_generation_available": bool(image_generation_available and provider_configured),
        "tooling_available": bool(image_generation_available),
        "provider_configured": bool(provider_configured),
        "recommended_provider": "gpt-image-2",
        "available_paths": available_paths,
        "provider_request": provider_request,
        "prompt_only_fallback": (
            "If the user chooses not to provide a provider, continue in prompt-only mode: "
            "analyze the task, retrieve references, extract genes/structure, and deliver the final prompt without generating an image."
        ),
    }


def main() -> None:
    print(json.dumps(detect(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
