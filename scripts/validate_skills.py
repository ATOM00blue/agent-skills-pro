#!/usr/bin/env python3
"""Validate every SKILL.md in this repo against the open Agent Skills spec.

Spec reference: https://agentskills.io/specification

Checks per skill (skills/<name>/SKILL.md):
  - File exists and has YAML frontmatter delimited by `---` ... `---`.
  - Required fields `name` and `description` are present and non-empty.
  - `name`: 1-64 chars, lowercase a-z/0-9/hyphen, no leading/trailing hyphen,
    no consecutive `--`, and equals the parent folder name.
  - `description`: 1-1024 chars.
  - `compatibility` (optional): 1-500 chars.
  - `metadata` (optional): a mapping of string keys to scalar values.
  - `allowed-tools` / `license` (optional): non-empty strings if present.
  - Only spec-defined top-level frontmatter keys are used.
  - The Markdown body after the frontmatter is non-empty.

Zero third-party dependencies (Python 3.8+ stdlib only) so CI needs no install step.
Exit code 0 when all skills pass, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---- Spec constants -------------------------------------------------------
REQUIRED_FIELDS = {"name", "description"}
OPTIONAL_FIELDS = {"license", "compatibility", "metadata", "allowed-tools"}
ALLOWED_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


# ---- Tiny YAML frontmatter parser ----------------------------------------
# Supports the small subset our SKILL.md frontmatter uses: top-level
# `key: value` scalars and one level of nested mapping (for `metadata`).
def parse_frontmatter(text: str):
    """Return (frontmatter_dict, body_str). Raises ValueError on malformed input."""
    # Tolerate a leading UTF-8 BOM (some editors add one) so the delimiter check works.
    if text.startswith("﻿"):
        text = text[1:]
    if not text.startswith("---"):
        raise ValueError("missing opening '---' frontmatter delimiter")

    lines = text.splitlines()
    # First line must be exactly the opening delimiter.
    if lines[0].strip() != "---":
        raise ValueError("missing opening '---' frontmatter delimiter")

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("missing closing '---' frontmatter delimiter")

    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])

    data: dict = {}
    current_key = None  # active nested-mapping key (e.g. "metadata")
    for raw in fm_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        # YAML forbids tabs for indentation; flag them instead of silently
        # mis-parsing the line (a tab counts as zero spaces of indent below).
        if raw[: len(raw) - len(raw.lstrip())].find("\t") != -1:
            raise ValueError(f"tab indentation is not allowed in frontmatter: {raw!r}")
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if ":" not in line:
            raise ValueError(f"malformed frontmatter line (no colon): {raw!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if indent == 0:
            if key in data:
                raise ValueError(f"duplicate frontmatter key: {key!r}")
            if value == "":
                # Start of a nested mapping (e.g. metadata:).
                data[key] = {}
                current_key = key
            else:
                data[key] = _scalar(value)
                current_key = None
        else:
            # Nested key under the most recent top-level mapping.
            if current_key is None or not isinstance(data.get(current_key), dict):
                raise ValueError(f"unexpected indented line: {raw!r}")
            if key in data[current_key]:
                raise ValueError(f"duplicate {current_key} key: {key!r}")
            data[current_key][key] = _scalar(value)

    return data, body


def _scalar(value: str):
    """Strip matching surrounding quotes from a scalar value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


# ---- Validation -----------------------------------------------------------
def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        return [f"missing SKILL.md in {skill_dir.name}/"]

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as exc:
        return [f"frontmatter error: {exc}"]

    # Unknown / missing fields.
    for field in fm:
        if field not in ALLOWED_FIELDS:
            errors.append(f"unknown frontmatter field: {field!r}")
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"missing required field: {field!r}")

    # name
    name = fm.get("name")
    if isinstance(name, str):
        if not (1 <= len(name) <= NAME_MAX):
            errors.append(f"name must be 1-{NAME_MAX} chars (got {len(name)})")
        if not NAME_RE.match(name):
            errors.append(
                f"name {name!r} must be lowercase a-z/0-9/hyphen, no leading/"
                "trailing/consecutive hyphens"
            )
        if name != skill_dir.name:
            errors.append(
                f"name {name!r} must match folder name {skill_dir.name!r}"
            )
    elif name is not None:
        errors.append("name must be a string")

    # description
    desc = fm.get("description")
    if isinstance(desc, str):
        if not (1 <= len(desc) <= DESCRIPTION_MAX):
            errors.append(
                f"description must be 1-{DESCRIPTION_MAX} chars (got {len(desc)})"
            )
    elif desc is not None:
        errors.append("description must be a string")

    # compatibility
    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str) or not (1 <= len(compat) <= COMPATIBILITY_MAX):
            errors.append(f"compatibility must be a 1-{COMPATIBILITY_MAX} char string")

    # metadata
    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            errors.append("metadata must be a mapping")
        else:
            for mkey, mval in meta.items():
                if not isinstance(mval, str) or not mval.strip():
                    errors.append(
                        f"metadata.{mkey} must be a non-empty string value"
                    )

    # license / allowed-tools
    for field in ("license", "allowed-tools"):
        if field in fm and (not isinstance(fm[field], str) or not fm[field].strip()):
            errors.append(f"{field} must be a non-empty string if present")

    # body
    if not body.strip():
        errors.append("SKILL.md body is empty")

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills directory not found at {SKILLS_DIR}")
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print(f"ERROR: no skill folders found in {SKILLS_DIR}")
        return 1

    total = len(skill_dirs)
    failed = 0
    print(f"Validating {total} skill(s) against the Agent Skills spec...\n")

    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            failed += 1
            print(f"  FAIL  {skill_dir.name}")
            for err in errors:
                print(f"          - {err}")
        else:
            print(f"  PASS  {skill_dir.name}")

    print()
    if failed:
        print(f"{failed}/{total} skill(s) failed validation.")
        return 1
    print(f"All {total} skill(s) passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
