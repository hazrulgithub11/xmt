#!/usr/bin/env python3
"""Sync Invoice workflows and record actions from XMT___Billing_System.ds to local files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ds_deluge_utils import normalize_deluge_block

ROOT = Path(__file__).resolve().parents[1]
DS_FILE = ROOT / "XMT___Billing_System.ds"
OUT_DIR = ROOT / "application" / "forms" / "Invoice" / "workflow"
ACTIONS_DIR = OUT_DIR / "actions"
WORKFLOW_PREFIX = "\t\t\t"


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


def extract_invoice_workflows(content: str) -> dict[str, tuple[str, bool]]:
    lines = content.splitlines()
    workflows: dict[str, tuple[str, bool]] = {}
    pattern = re.compile(rf"^{re.escape(WORKFLOW_PREFIX)}(\S+) as \"(.+)\"$")

    i = 0
    while i < len(lines):
        m = pattern.match(lines[i])
        if not m:
            i += 1
            continue
        link_name = m.group(1)
        if i + 1 >= len(lines) or lines[i + 1].strip() != "{":
            i += 1
            continue
        end = find_block_end(lines, i + 1)
        block_lines = lines[i : end + 1]
        block_text = "\n".join(block_lines)
        if "form = Invoice" not in block_text:
            i = end + 1
            continue
        is_action = bool(re.search(r"type\s*=\s*functions", block_text))
        workflows[link_name] = (normalize_deluge_block(block_lines), is_action)
        i = end + 1
    return workflows


def main() -> None:
    content = DS_FILE.read_text(encoding="utf-8", errors="replace")
    workflows = extract_invoice_workflows(content)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ACTIONS_DIR.mkdir(parents=True, exist_ok=True)

    expected_paths: set[Path] = set()
    for link_name, (body, is_action) in sorted(workflows.items()):
        target = (ACTIONS_DIR if is_action else OUT_DIR) / f"{link_name}.deluge"
        target.write_text(body, encoding="utf-8")
        expected_paths.add(target.resolve())
        kind = "action" if is_action else "workflow"
        print(f"WROTE {kind}: {target.relative_to(ROOT)}")

    for path in list(OUT_DIR.rglob("*.deluge")):
        if path.resolve() not in expected_paths:
            print(f"DELETE orphan: {path.relative_to(ROOT)}")
            path.unlink()

    print(f"\nTotal synced: {len(workflows)}")


if __name__ == "__main__":
    main()
