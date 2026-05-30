#!/usr/bin/env python3
"""Shared helpers for syncing Deluge from XMT___Billing_System.ds exports."""

from __future__ import annotations


def normalize_deluge_body(text: str) -> str:
    """Remove export padding while preserving relative indentation."""
    if not text.strip():
        return ""
    expanded = text.expandtabs(4)
    lines = expanded.splitlines()
    non_empty = [line for line in lines if line.strip()]
    if not non_empty:
        return ""
    min_indent = min(len(line) - len(line.lstrip(" ")) for line in non_empty)
    dedented_lines: list[str] = []
    for line in lines:
        if not line.strip():
            dedented_lines.append("")
            continue
        dedented_lines.append(line[min_indent:] if len(line) >= min_indent else line.lstrip())
    out: list[str] = []
    for line in dedented_lines:
        if not line.strip():
            out.append("")
            continue
        leading = len(line) - len(line.lstrip(" "))
        tabs = "\t" * (leading // 4)
        spaces = " " * (leading % 4)
        out.append(tabs + spaces + line.lstrip(" "))
    return "\n".join(out).rstrip()


def normalize_deluge_block(block_lines: list[str]) -> str:
    return normalize_deluge_body("\n".join(block_lines)) + "\n\n"
