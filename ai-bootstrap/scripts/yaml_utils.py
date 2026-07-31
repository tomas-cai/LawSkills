#!/usr/bin/env python3
"""Small dependency-free YAML subset used by AI Bootstrap.

Blueprint files intentionally use a conservative YAML subset: mappings,
indentation-based nesting, inline lists/maps, quoted strings, booleans and
numbers.  Keeping this parser local makes the skill runnable without an
optional PyYAML installation while still matching the checked-in blueprints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _strip_comment(value: str) -> str:
    quote = None
    depth = 0
    for index, char in enumerate(value):
        if char in "\"'":
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        elif quote is None:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth = max(0, depth - 1)
            elif char == "#" and depth == 0 and (index == 0 or value[index - 1].isspace()):
                return value[:index].rstrip()
    return value.rstrip()


def _split_top_level(value: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    quote = None
    depth = 0
    for index, char in enumerate(value):
        if char in "\"'":
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        elif quote is None:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth = max(0, depth - 1)
            elif char == delimiter and depth == 0:
                parts.append(value[start:index].strip())
                start = index + 1
    parts.append(value[start:].strip())
    return [part for part in parts if part]


def _find_top_level_colon(value: str) -> int:
    quote = None
    depth = 0
    for index, char in enumerate(value):
        if char in "\"'":
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        elif quote is None:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth = max(0, depth - 1)
            elif char == ":" and depth == 0:
                return index
    return -1


def parse_scalar(raw: str) -> Any:
    value = _strip_comment(raw.strip())
    if not value:
        return None

    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        if value[0] == '"':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value[1:-1].replace("''", "'")

    if value.startswith("[") and value.endswith("]"):
        return [parse_scalar(item) for item in _split_top_level(value[1:-1])]

    if value.startswith("{") and value.endswith("}"):
        result: dict[str, Any] = {}
        for item in _split_top_level(value[1:-1]):
            colon = _find_top_level_colon(item)
            if colon < 0:
                continue
            key = item[:colon].strip().strip("\"'")
            result[key] = parse_scalar(item[colon + 1 :])
        return result

    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+)", value):
        return float(value)
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    """Load the conservative YAML subset used by Blueprint files."""
    return load_yaml_text(path.read_text(encoding="utf-8"))


def load_yaml_text(text: str) -> dict[str, Any]:
    """Parse the conservative YAML subset from an in-memory string."""
    raw_lines = text.splitlines()
    lines: list[tuple[int, str]] = []
    for raw in raw_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        content = raw.strip()
        if content in {"---", "..."}:
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, _strip_comment(content)))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        is_list = lines[index][0] == indent and (
            lines[index][1] == "-" or lines[index][1].startswith("- ")
        )
        result: Any = [] if is_list else {}

        while index < len(lines):
            current_indent, content = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                break

            if is_list:
                if content != "-" and not content.startswith("- "):
                    break
                item = content[1:].strip()
                index += 1
                if not item:
                    if index < len(lines) and lines[index][0] > indent:
                        value, index = parse_block(index, lines[index][0])
                    else:
                        value = None
                else:
                    colon = _find_top_level_colon(item)
                    if colon >= 0:
                        value = {
                            item[:colon].strip().strip("\"'"): parse_scalar(item[colon + 1 :])
                        }
                        if index < len(lines) and lines[index][0] > indent:
                            extra, index = parse_block(index, lines[index][0])
                            if isinstance(extra, dict):
                                value.update(extra)
                    else:
                        value = parse_scalar(item)
                result.append(value)
                continue

            if content.startswith("- "):
                break
            colon = _find_top_level_colon(content)
            if colon < 0:
                index += 1
                continue
            key = content[:colon].strip().strip("\"'")
            remainder = content[colon + 1 :].strip()
            index += 1
            if remainder:
                result[key] = parse_scalar(remainder)
            elif index < len(lines) and lines[index][0] > indent:
                result[key], index = parse_block(index, lines[index][0])
            else:
                result[key] = {}

        return result, index

    parsed, _ = parse_block(0, lines[0][0] if lines else 0)
    return parsed if isinstance(parsed, dict) else {}


def dump_yaml(data: dict[str, Any], indent: int = 0) -> str:
    """Serialize the manifest subset with valid handling for empty lists."""
    lines: list[str] = []
    for key, value in data.items():
        prefix = " " * indent
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            nested = dump_yaml(value, indent + 2)
            if nested:
                lines.append(nested)
        elif isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            else:
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        nested = dump_yaml(item, indent + 4)
                        if nested:
                            lines.append(nested)
                    else:
                        lines.append(f"{prefix}  - {format_scalar(item)}")
        else:
            lines.append(f"{prefix}{key}: {format_scalar(value)}")
    return "\n".join(lines)


def format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
