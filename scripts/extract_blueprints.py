#!/usr/bin/env python3
"""
Extract Zoho Creator blueprint definitions from XMT___Billing_System.ds
into application/blueprints/<BlueprintName>/ for easier review and editing.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DS_FILE = ROOT / "XMT___Billing_System.ds"
OUT_DIR = ROOT / "application" / "blueprints"

BLUEPRINT_LINK_NAMES = [
    "Credit_Note_Blueprint",
    "Invoice_Blueprint",
    "Deposits_Blueprint",
    "Debit_Note_Blueprint",
]

# On-disk folder name when it differs from the Zoho blueprint link name.
BLUEPRINT_OUTPUT_DIRS: dict[str, str] = {
    "Deposits_Blueprint": "pro forma invoice",
}

BLUEPRINT_FORMS: dict[str, str] = {
    "Invoice_Blueprint": "Invoice",
    "Credit_Note_Blueprint": "Credit_Note",
    "Deposits_Blueprint": "Pro_Forma_Invoices",
    "Debit_Note_Blueprint": "Debit_Note",
}


def find_blueprint_block(content: str, link_name: str) -> tuple[int, int] | None:
    """Return (start, end) line indices (0-based) for blueprint block body."""
    pattern = rf"^\s+{re.escape(link_name)} as "
    start = None
    for i, line in enumerate(content.splitlines()):
        if re.match(pattern, line):
            start = i
            break
    if start is None:
        return None

    lines = content.splitlines()
    # Opening brace on same or next lines — find depth from blueprint name line
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
            return block_start, i
    return None


def extract_braced_section(text: str, keyword: str) -> str | None:
    """Extract body of `keyword { ... }` using brace balancing."""
    m = re.search(rf"\b{keyword}\s*\{{", text)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
    return None


def parse_header(block_lines: list[str]) -> dict:
    meta: dict = {}
    for line in block_lines[:10]:
        m = re.search(r"(\w+_Blueprint) as \"([^\"]+)\"", line)
        if m:
            meta["display_name"] = m.group(2)
        m = re.search(r"form = (\w+)", line)
        if m:
            meta["form"] = m.group(1)
        m = re.search(r'start stage = "([^"]+)"', line)
        if m:
            meta["start_stage"] = m.group(1)
    for line in block_lines[:80]:
        m = re.search(r"form = (\w+)", line)
        if m and "form" not in meta:
            meta["form"] = m.group(1)
        m = re.search(r'start stage = "([^"]+)"', line)
        if m and "start_stage" not in meta:
            meta["start_stage"] = m.group(1)
    stages = []
    in_stages = False
    for line in block_lines:
        if re.match(r"\s+stages\s*$", line.strip()) or line.strip() == "stages":
            in_stages = True
            continue
        if in_stages:
            if line.strip() == "transitions":
                break
            m = re.match(r'\s+"([^"]+)"\s*$', line)
            if m:
                stages.append(m.group(1))
    meta["stages"] = stages
    return meta


def extract_deluge_script_bodies(section_text: str) -> list[str]:
    """Pull script bodies from `custom deluge script ( ... )` with balanced parens."""
    scripts = []
    needle = "custom deluge script"
    pos = 0
    while True:
        idx = section_text.find(needle, pos)
        if idx < 0:
            break
        paren = section_text.find("(", idx)
        if paren < 0:
            break
        depth = 0
        end = paren
        for i in range(paren, len(section_text)):
            if section_text[i] == "(":
                depth += 1
            elif section_text[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        body = section_text[paren + 1 : end].strip()
        scripts.append(body)
        pos = end + 1
    return scripts


def extract_deluge_scripts(section_text: str) -> list[str]:
    scripts = []
    for body in extract_deluge_script_bodies(section_text):
        # Normalize excessive leading tabs from .ds export
        body_lines = body.splitlines()
        if body_lines:
            min_indent = min(
                len(line) - len(line.lstrip("\t"))
                for line in body_lines
                if line.strip()
            )
            body_lines = [
                (line[min_indent:] if line.strip() else line)
                for line in body_lines
            ]
        scripts.append("\n".join(body_lines).strip())
    return scripts


def slug_condition(cond: str) -> str:
    s = re.sub(r"[^\w]+", "_", cond.strip())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return "conditional"
    if len(s) > 48:
        digest = hashlib.md5(cond.encode()).hexdigest()[:8]
        s = s[:40].rstrip("_") + "_" + digest
    return s


def parse_transitions(block_lines: list[str]) -> list[dict]:
    text = "\n".join(block_lines)
    trans_start = text.find("transitions")
    if trans_start < 0:
        return []
    text = text[trans_start:]

    transitions = []
    # Match each transition: Name as "Display" ... until next transition at same indent
    trans_pattern = re.compile(
        r"(\w+) as \"([^\"]+)\"\s*\{",
        re.MULTILINE,
    )
    matches = list(trans_pattern.finditer(text))
    for idx, m in enumerate(matches):
        name = m.group(1)
        display = m.group(2)
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunk = text[start:end]

        from_stage = ""
        to_stage = ""
        fm = re.search(r'from stage = "([^"]+)"', chunk)
        tm = re.search(r'to stage = "([^"]+)"', chunk)
        if fm:
            from_stage = fm.group(1)
        if tm:
            to_stage = tm.group(1)

        transition = {
            "link_name": name,
            "display_name": display,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "phases": {},
            "phase_raw": {},
        }

        for phase in ("before", "during", "after"):
            phase_text = extract_braced_section(chunk, phase)
            transition["phase_raw"][phase] = phase_text
            if not phase_text:
                transition["phases"][phase] = []
                continue

            actions_list = []
            pos = 0
            while pos < len(phase_text):
                uncond_m = re.search(r"\bactions\s*\{", phase_text[pos:])
                cond_m = re.search(r"\bactions\s*\(", phase_text[pos:])
                if uncond_m is None and cond_m is None:
                    break
                use_cond = (
                    cond_m is not None
                    and (uncond_m is None or cond_m.start() < uncond_m.start())
                )
                if use_cond and cond_m is not None:
                    abs_start = pos + cond_m.start()
                    paren_end = phase_text.find(")", abs_start)
                    if paren_end < 0:
                        break
                    cond = phase_text[phase_text.find("(", abs_start) + 1 : paren_end].strip()
                    brace_start = phase_text.find("{", paren_end)
                    if brace_start < 0:
                        break
                    depth = 0
                    body_end = brace_start
                    for i in range(brace_start, len(phase_text)):
                        if phase_text[i] == "{":
                            depth += 1
                        elif phase_text[i] == "}":
                            depth -= 1
                            if depth == 0:
                                body_end = i
                                break
                    body = phase_text[brace_start + 1 : body_end]
                    pos = body_end + 1
                elif uncond_m is not None:
                    abs_start = pos + uncond_m.start()
                    brace_start = phase_text.find("{", abs_start)
                    depth = 0
                    body_end = brace_start
                    for i in range(brace_start, len(phase_text)):
                        if phase_text[i] == "{":
                            depth += 1
                        elif phase_text[i] == "}":
                            depth -= 1
                            if depth == 0:
                                body_end = i
                                break
                    body = phase_text[brace_start + 1 : body_end]
                    cond = None
                    pos = body_end + 1
                else:
                    break

                scripts = extract_deluge_scripts(body)
                updates = re.findall(
                    r"update\s+(\w+)\[ID == input\.ID\]\s*\[\s*(.*?)\s*\]",
                    body,
                    re.DOTALL,
                )
                actions_list.append(
                    {
                        "condition": cond,
                        "scripts": scripts,
                        "field_updates": [
                            {"form": u[0], "fields": u[1].strip()} for u in updates
                        ],
                    }
                )

            transition["phases"][phase] = actions_list

        transitions.append(transition)

    return transitions


def write_transition_files(bp_dir: Path, transition: dict) -> None:
    t_dir = bp_dir / "transitions" / transition["link_name"]
    t_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "link_name": transition["link_name"],
        "display_name": transition["display_name"],
        "from_stage": transition["from_stage"],
        "to_stage": transition["to_stage"],
    }
    (t_dir / "transition.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )

    for phase, action_groups in transition["phases"].items():
        if not action_groups:
            continue
        phase_dir = t_dir / phase
        phase_dir.mkdir(exist_ok=True)

        for gi, group in enumerate(action_groups):
            cond = group.get("condition")
            if cond:
                folder = phase_dir / f"if_{slug_condition(cond)}"
            else:
                folder = phase_dir / "unconditional"
            folder.mkdir(exist_ok=True)

            if cond:
                (folder / "CONDITION.txt").write_text(cond + "\n", encoding="utf-8")

            for si, script in enumerate(group.get("scripts") or []):
                fname = f"script_{si + 1:02d}.deluge"
                (folder / fname).write_text(script + "\n", encoding="utf-8")

            for ui, upd in enumerate(group.get("field_updates") or []):
                fname = f"update_{upd['form']}_{ui + 1:02d}.deluge"
                content = f"update {upd['form']}[ID == input.ID]\n[\n{upd['fields']}\n]\n"
                (folder / fname).write_text(content, encoding="utf-8")

    for phase in ("before", "during"):
        write_phase_config_files(t_dir, phase, transition.get("phase_raw", {}).get(phase))


def write_phase_config_files(t_dir: Path, phase: str, phase_text: str | None) -> None:
    if not phase_text or not phase_text.strip():
        return
    # Keep non-script before/during config (owners, confirmations, field visibility)
    stripped = phase_text
    stripped = re.sub(
        r"custom deluge script\s*\([^()]*(?:\([^()]*\)[^()]*)*\)",
        "",
        stripped,
        flags=re.DOTALL,
    )
    stripped = re.sub(
        r"update\s+\w+\[ID == input\.ID\]\s*\[[^\]]*\]",
        "",
        stripped,
        flags=re.DOTALL,
    )
    if stripped.strip():
        out = t_dir / phase / "phase_config.ds"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(stripped.strip() + "\n", encoding="utf-8")


def write_blueprint_md(bp_dir: Path, meta: dict, transitions: list[dict]) -> None:
    link_name = meta.get("link_name", bp_dir.name)
    title = meta.get("display_name") or bp_dir.name.replace("_", " ")
    lines = [
        f"# {title}",
        "",
        f"- **Link name:** `{link_name}`",
        f"- **Folder:** `{bp_dir.name}/`",
        f"- **Form:** `{meta.get('form', '?')}`",
        f"- **Start stage:** `{meta.get('start_stage', '?')}`",
        "",
        "## Stages",
        "",
    ]
    for s in meta.get("stages", []):
        lines.append(f"- {s}")
    lines.extend(["", "## Transitions", "", "| Transition | From | To | Scripts |", "|---|---|---|---|"])
    for t in transitions:
        count = sum(
            len(g.get("scripts") or [])
            for phase in t["phases"].values()
            for g in phase
        )
        lines.append(
            f"| [{t['display_name']}](transitions/{t['link_name']}/) "
            f"| {t['from_stage']} | {t['to_stage']} | {count} |"
        )
    lines.extend(
        [
            "",
            "## Folder layout",
            "",
            "```",
            f"{bp_dir.name}/",
            "  BLUEPRINT.md          ← this file",
            "  blueprint.json        ← machine-readable metadata",
            "  transitions/",
            "    <TransitionLinkName>/",
            "      transition.json",
            "      before|during|after/",
            "        unconditional/  or  if_<condition>/",
            "          script_01.deluge",
            "          CONDITION.txt   (if conditional)",
            "```",
            "",
            "Source: `XMT___Billing_System.ds` (blueprint section).",
            "Re-run `python3 scripts/extract_blueprints.py` after exporting from Zoho.",
            "",
        ]
    )
    (bp_dir / "BLUEPRINT.md").write_text("\n".join(lines), encoding="utf-8")


def blueprint_output_dir(link_name: str) -> Path:
    return OUT_DIR / BLUEPRINT_OUTPUT_DIRS.get(link_name, link_name)


def prune_obsolete_transition_dirs(bp_dir: Path, active_link_names: set[str]) -> list[str]:
    trans_dir = bp_dir / "transitions"
    if not trans_dir.is_dir():
        return []
    removed = []
    for child in trans_dir.iterdir():
        if child.is_dir() and child.name not in active_link_names:
            shutil.rmtree(child)
            removed.append(child.name)
    return removed


def extract_blueprint(content: str, link_name: str) -> tuple[dict, list[dict], int] | None:
    span = find_blueprint_block(content, link_name)
    if not span:
        return None
    block_lines = content.splitlines()[span[0] : span[1] + 1]
    meta = parse_header(block_lines)
    meta["link_name"] = link_name
    title_m = re.search(
        rf"^\s+{re.escape(link_name)} as \"([^\"]+)\"",
        content,
        re.MULTILINE,
    )
    if title_m:
        meta["display_name"] = title_m.group(1)
    transitions = parse_transitions(block_lines)

    bp_dir = blueprint_output_dir(link_name)
    bp_dir.mkdir(parents=True, exist_ok=True)
    (bp_dir / "blueprint.json").write_text(
        json.dumps({"meta": meta, "transitions": transitions}, indent=2) + "\n",
        encoding="utf-8",
    )
    for t in transitions:
        write_transition_files(bp_dir, t)
    write_blueprint_md(bp_dir, meta, transitions)
    prune_obsolete_transition_dirs(bp_dir, {t["link_name"] for t in transitions})

    script_count = sum(
        len(g.get("scripts") or [])
        for t in transitions
        for phase in t["phases"].values()
        for g in phase
    )
    return meta, transitions, script_count


def main() -> None:
    content = DS_FILE.read_text(encoding="utf-8", errors="replace")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = []
    for link_name in BLUEPRINT_LINK_NAMES:
        result = extract_blueprint(content, link_name)
        if not result:
            print(f"WARN: {link_name} not found")
            continue
        _meta, transitions, script_count = result
        out_dir = blueprint_output_dir(link_name)
        summary.append(
            (link_name, out_dir.name, len(transitions), script_count)
        )
        print(
            f"OK {link_name} -> {out_dir.name}: "
            f"{len(transitions)} transitions, {script_count} scripts"
        )

    readme = OUT_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# XMT Billing System — Blueprints",
                "",
                "## What is a Blueprint?",
                "",
                "In Zoho Creator, a **Blueprint** is a visual state machine on a form. Records move",
                "through **stages** (e.g. Draft → Pending Approval → Approved → Sent). Users or",
                "automation trigger **transitions** to change stage.",
                "",
                "Each transition has up to three execution phases:",
                "",
                "| Phase | When it runs | Typical use in this app |",
                "|---|---|---|",
                "| **Before** | Before the transition | Permissions, confirm dialogs |",
                "| **During** | While collecting input | Show fields (e.g. rejection reason) |",
                "| **After** | After stage change | Email, LHDN submit, journal entries, `changeStage` |",
                "",
                "After-phase actions can be **unconditional** or run only when a **criteria**",
                "expression is true (e.g. `Customer.Credit_Available > 0` on Send Invoice).",
                "",
                "## This repo layout",
                "",
                "```",
                "application/blueprints/",
                "  <BlueprintLinkName>/",
                "    BLUEPRINT.md              # human overview + transition table",
                "    blueprint.json            # full metadata (for tooling)",
                "    transitions/<Transition>/",
                "      transition.json",
                "      before/phase_config.ds  # owners, confirmations (if any)",
                "      during/phase_config.ds",
                "      after/unconditional/script_01.deluge",
                "      after/if_<criteria>/CONDITION.txt",
                "```",
                "",
                "Scripts here are extracted from `XMT___Billing_System.ds`. Related logic also",
                "lives in form workflows, schedules, and custom functions that call:",
                "`thisapp.blueprint.executeTransition(...)` or `thisapp.blueprint.changeStage(...)`.",
                "",
                "## Extracted blueprints",
                "",
                "| Blueprint | Form | Transitions | Deluge scripts |",
                "|---|---|---:|---:|",
            ]
            + [
                f"| [{name}]({out_name}/BLUEPRINT.md) | "
                + BLUEPRINT_FORMS.get(name, "?")
                + f" | {tc} | {sc} |"
                for name, out_name, tc, sc in summary
            ]
            + [
                "",
                "## Invoice Blueprint (largest)",
                "",
                "Stages: Draft → Pending Approval → Approved → Sent → Partially Paid / Paid / Overdue,",
                "with Rejected and Resubmit loop. Heavy scripts on **Approve** (LHDN, journals,",
                "balance) and **Send Invoice** (stage routing + credit popup). Payment transitions",
                "are often driven from **Payment Received** workflows via `changeStage`, not only",
                "from the blueprint UI.",
                "",
                "## Regenerate from export",
                "",
                "```bash",
                "python3 scripts/extract_blueprints.py",
                "```",
                "",
                "## Zoho references",
                "",
                "- [Creator Blueprint tasks (Deluge)](https://www.zoho.com/deluge/help/creator-blueprint-tasks.html)",
                "- [Execute transition](https://www.zoho.com/deluge/help/creator-blueprint-tasks/execute-transition.html)",
                "- [Blueprint attributes](https://www.zoho.com/deluge/help/creator-blueprint-tasks/blueprint-attributes.html)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {readme}")


if __name__ == "__main__":
    main()
