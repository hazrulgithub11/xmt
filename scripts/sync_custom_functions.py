#!/usr/bin/env python3
"""Sync custom functions from XMT___Billing_System.ds to application/Custom Functions/."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ds_deluge_utils import normalize_deluge_body

ROOT = Path(__file__).resolve().parents[1]
DS_FILE = ROOT / "XMT___Billing_System.ds"
OUT_ROOT = ROOT / "application" / "Custom Functions"

SYNC_NAMESPACES = {
    "invoice",
    "payment_received",
}

FUNC_PATTERN = re.compile(
    r"^\t+\s*((?:void|map|string|int|float|bool|date|list:\w+|collection)\s+(\w+)\.(\w+)\(.*\))\s*$"
)


def find_block_end(lines: list[str], start: int) -> int:
    depth = 0
    block_start = None
    for i in range(start, len(lines)):
        if "{" in lines[i]:
            if block_start is None:
                block_start = i
            depth += lines[i].count("{") - lines[i].count("}")
        elif block_start is not None:
            depth += lines[i].count("{") - lines[i].count("}")
        if block_start is not None and depth == 0:
            return i
    raise ValueError(f"Unclosed block starting at line {start + 1}")


def extract_functions(content: str) -> dict[tuple[str, str], str]:
    lines = content.splitlines()
    functions: dict[tuple[str, str], str] = {}

    i = 0
    while i < len(lines):
        m = FUNC_PATTERN.match(lines[i])
        if not m:
            i += 1
            continue
        signature = m.group(1).strip()
        namespace = m.group(2)
        func_name = m.group(3)
        if namespace not in SYNC_NAMESPACES:
            i += 1
            continue
        if i + 1 >= len(lines) or lines[i + 1].strip() != "{":
            i += 1
            continue
        end = find_block_end(lines, i + 1)
        body = normalize_deluge_body("\n".join(lines[i + 2 : end]))
        functions[(namespace, func_name)] = f"{signature}\n{{\n{body}\n}}\n"
        i = end + 1
    return functions


def main() -> None:
    content = DS_FILE.read_text(encoding="utf-8", errors="replace")
    functions = extract_functions(content)

    expected_paths: set[Path] = set()
    for (namespace, func_name), body in sorted(functions.items()):
        target = OUT_ROOT / namespace / func_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        expected_paths.add(target.resolve())
        print(f"WROTE: {target.relative_to(ROOT)}")

    for namespace in SYNC_NAMESPACES:
        ns_dir = OUT_ROOT / namespace
        if not ns_dir.is_dir():
            continue
        for path in ns_dir.iterdir():
            if path.is_file() and path.resolve() not in expected_paths:
                print(f"DELETE orphan: {path.relative_to(ROOT)}")
                path.unlink()

    print(f"\nTotal synced: {len(functions)}")


if __name__ == "__main__":
    main()
