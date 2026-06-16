---
name: grompt
description: Use when any agent or system needs to create, rewrite, improve, or generate an image prompt by analyzing a user's image task against the freestylefly/awesome-gpt-image-2 prompt case library, selecting 3-5 repository-backed reference prompts, extracting reusable visual genes and prompt structure, synthesizing a task-specific GPT Image 2 prompt, then generating the image with an available image-generation provider.
---

# Grompt

Use the awesome-gpt-image-2 prompt corpus as evidence, not decoration. The skill turns a user task into a reference-backed prompt, then hands it to an image generation skill.

This is an agent-agnostic skill. It can live under any agent or system skill root as long as the folder name is `grompt` and scripts are run from the skill directory.

## Portable Path Setup

Use the current skill folder as `GROMPT_DIR`. If the host provides a skill-root variable, derive it from that; otherwise use the absolute folder path where this skill is installed.

```bash
export GROMPT_DIR="${GROMPT_DIR:-/path/to/skills/grompt}"
```

All commands below use `$GROMPT_DIR` so the same workflow works for Codex, Claude Code, OpenAI Agents, local MCP runners, CI, and other agent systems.

## Install or Activation Check

When installing, copying, enabling, or first using this skill in a new environment, run:

```bash
python "$GROMPT_DIR/scripts/install_check.py"
```

If `image_generation_available` is false, stop before promising generation. Ask the user to provide an image generation provider, API key/base URL if needed, and explain that GPT Image 2 / `gpt-image-2` is the best fit for this corpus. If the user chooses not to provide a provider, continue in prompt-only mode: still analyze the task, retrieve references, extract genes/structure, and deliver the final prompt without generating an image.

## Language Policy

Prefer the user's local/common language for normal outputs. Infer it from the current user message, the ongoing conversation, host locale, project language, or prior user preference; if uncertain, use the language of the user's latest task. Do not hard-code Chinese or English as the default.

Apply this to the final response, reference summary, gene/structure explanation, and generated prompt wording. Preserve exact visible text the user asks to place in the image, even when it differs from the surrounding response language. If the task explicitly requests another language or bilingual output, follow that request.

## Required Workflow

1. Determine the output language using the Language Policy above.
2. Analyze the user's task: output type, subject, exact text, aspect ratio, style, scene, constraints, and whether this is generation or edit.
3. If this is the first use in the current environment, run the install/activation check above.
4. Run the helper:
   ```bash
   python "$GROMPT_DIR/scripts/synthesize_prompt.py" \
     --task "<user task>" --count 5 --format markdown
   ```
5. Review the 3-5 returned references yourself. Keep only references that actually fit the task. If a reference is weak, rerun with a more specific task phrase.
6. Extract two layers:
   - **Genes:** reusable visual DNA, such as hierarchy, composition, material language, text handling, camera, palette, and negative constraints.
   - **Structure:** prompt skeleton, such as intent, subject, scene, modules, labels, style, and constraints.
7. Write a new prompt for this task in the chosen output language. Do not paste a source prompt with nouns swapped. Preserve the useful genes and structure, but make the subject, text, and constraints specific to the user.
8. Generate the image by invoking the existing `imagegen` skill by default. If the user explicitly wants the GPT Image 2 CLI path, use `gpt-image-2`. Prefer GPT Image 2 providers over generic image providers for this skill. If no provider is available and the user declines to provide one, skip generation and deliver the prompt-only result.
9. Visually inspect the generated result before reporting success. If text, layout, or style fails, revise one dimension and regenerate.
10. Report the final prompt, selected references with source links, generated image path when generated, and any known limitations in the chosen output language.
11. Ask whether the user wants to add this result to the local reference library. Only add it after explicit confirmation. If the user replies `1` after this yes/no question, treat that as confirmation.

## Self-Iteration Library

Keep upstream data immutable. User-approved results go into:

```text
references/user_prompt_library.json
```

After each successful generation or prompt-only completion, ask:

```text
要不要把这次结果加入参考库？我会保存最终提示词，并打上 category/style/scene/source 标签，之后检索会优先把它作为可选参考之一。
```

If confirmed, save it with explicit labels:

```bash
python "$GROMPT_DIR/scripts/library_add.py" \
  --title "<short title>" \
  --prompt "<final prompt>" \
  --category "<category>" \
  --style "<style tag>" \
  --scene "<scene tag>" \
  --task "<original user task>" \
  --source "user-confirmed"
```

Do not save failed generations, rejected drafts, or unconfirmed prompts.

## Progressive Disclosure Query

When browsing the reference library, query in layers instead of loading the full corpus:

1. See available tag types:
   ```bash
   python "$GROMPT_DIR/scripts/library_query.py" --level types
   ```
2. Pick one or more relevant tag types, then list tags under each type:
   ```bash
   python "$GROMPT_DIR/scripts/library_query.py" --level tags --tag-type category
   python "$GROMPT_DIR/scripts/library_query.py" --level tags --tag-type style
   python "$GROMPT_DIR/scripts/library_query.py" --level tags --tag-type scene
   ```
3. Inspect prompt excerpts under selected tags:
   ```bash
   python "$GROMPT_DIR/scripts/library_query.py" \
     --level prompts --tag-type category --tag "Posters & Typography" --limit 8
   ```
4. Select the strongest 3-5 prompts after comparing title, tags, source, and excerpt. Load full prompt JSON only if excerpts are not enough.

## References

- `references/index.md`: small corpus summary and upstream size/count notes.
- `references/prompt_cases.json`: 503 full prompt cases with case id, category, style tags, scene tags, source label, source URL, GitHub anchor, image path, and full prompt.
- `references/templates.json`: upstream template/category/style/scene library.
- `scripts/install_check.py`: provider/tooling probe for install or first-use checks.
- `scripts/library_query.py`: progressive tag and prompt browser.
- `scripts/library_add.py`: adds user-confirmed prompts to the self-iteration library.
- `references/user_prompt_library.json`: optional local user-confirmed prompt library, created on first save.

Do not load `prompt_cases.json` into context unless the script result is insufficient. Prefer script retrieval first.

## Helper Output

The helper returns:

- `analysis`: inferred use case, category, styles, and scenes.
- `references`: 3-5 case references with GitHub anchors and prompt excerpts.
- `extracted_genes`: candidate reusable visual DNA.
- `structure`: candidate prompt skeleton.
- `new_prompt`: a first draft, not a final answer.

Treat `new_prompt` as a draft. Improve it with judgment before generating.

## Good Prompt Requirements

- Start with the asset intent: poster, infographic, product shot, UI screenshot, portrait, edit, etc.
- Specify aspect ratio and output usage.
- Quote exact visible text once.
- Use concrete composition, lighting, material, palette, and hierarchy terms.
- Include negative constraints from the references when relevant.
- Avoid empty booster words: 4K, 8K, masterpiece, ultra detailed, trending on artstation, unless a source-specific visual convention truly requires resolution language.

## Failure Rules

- If fewer than 3 relevant references can be found, say so and use the best available references instead of fabricating.
- If the task requires a source image that the user did not provide, ask for it before generation.
- If image generation credentials or tools are unavailable, ask the user for a provider and say GPT Image 2 / `gpt-image-2` is recommended. If the user declines, deliver the reference-backed prompt only and clearly say generation was intentionally skipped.
