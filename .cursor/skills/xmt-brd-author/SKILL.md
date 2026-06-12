---
name: xmt-brd-author
description: Researches a Zoho Creator Deluge module and writes a complete BRD section for XMT_Billing_Requirements.md following the project's authoring and evidence rules. Use when the user asks to fill, write, document, or research any module section in the XMT BRD — such as Invoice, Credit Note, Subscription, Payment Received, or any §5.x section.
---

# XMT BRD Author

Fills one module section of `docs/XMT_Billing_Requirements.md` by tracing Deluge code and mapping findings to the BRD template.

`XMT___Billing_System.ds` is the source of truth. Use local split files only as secondary convenience references.

## Before Starting

Read both rules first:
- `.cursor/rules/xmt-brd-authoring.mdc` — section template, requirement IDs, confidence tags
- `.cursor/rules/xmt-brd-evidence.mdc` — citation format, canonical names, terminology

Check `module-map.md` (in this skill folder) to get the file list for the target module.

---

## Step-by-step Workflow

### Step 1 — Identify DS anchors for the module

From `module-map.md`, locate DS anchors for:
- Form declaration (`form <Form_Name>`)
- Workflow definitions (`type = form; form = <Form_Name>`)
- Record actions (`type = functions; form = <Form_Name>`)
- Schedule block entries (if applicable)
- Blueprint block entry (if applicable)
- Global function namespaces (`thisapp.{module}.*`)

### Step 2 — Read form structure from DS

Read the module's `form <Form_Name>` block in `XMT___Billing_System.ds` to extract:
- Field names and types (note: these become canonical field references)
- Picklist values (valid statuses, categories, types)
- Subform structure (line items)
- Default values and required/optional fields

### Step 3 — Read workflow definitions from DS

Within the DS workflow block, gather all entries where `form = <Form_Name>`. For each, extract:
- **Trigger** (`on load`, `on user input of {field}`, `on success`, `on add`, `on edit`)
- **Condition** (what state or value triggers the logic)
- **Behavior** (what the code does: sets field, validates, inserts record, sends email, calls function)
- **Exception** (any guard clauses, early returns, skip conditions)

Group findings by trigger type, not by file name.

### Step 4 — Trace global functions

Search for calls to `thisapp.{module}.*` in workflows and schedules. For each function called:
- Note the function name
- Note what it computes or performs
- Note where it is called from (which workflow/schedule)

This drives the **Calculations** and **Relationships** subsections.

### Step 5 — Read schedules from DS (if applicable)

For modules driven by time (Invoice, Subscription): read the DS `schedule` block entries and extract:
- Schedule frequency / trigger condition
- What records are queried and how
- What actions are taken (insert, update, email)

### Step 6 — Identify the Blueprint

If a `{Module}_Blueprint` exists, note all valid states and transitions as declared. These form the **Status Lifecycle** subsection.

### Step 7 — Write the section

Write the module section using the template from `xmt-brd-authoring.mdc`. Fill every subsection:

```
#### Purpose
#### When and How It Is Created
#### Business Rules and Validations   ← BR-{MODULE}-NNN rules with [confidence] + Source:
#### Calculations
#### Relationships to Other Modules
#### Status Lifecycle
#### Implementation Status
```

Rules: one rule per `BR-{MODULE}-NNN` line. Every rule gets a confidence tag. Every `[Confirmed]` or `[Inferred]` rule gets a `Source:` line.

If behavior cannot be traced to code, write the rule as `[Open Question]` — do not invent behavior.

### Step 8 — Post-module updates

After writing the section, update three places in the BRD:

1. **§6 Document Conversion Matrix** — add any conversion flows found (e.g. Invoice → Credit Note)
2. **§8 Implementation Status Matrix** — set Done / Partial / Not Started for this module with a one-line note
3. **§9 Open Questions** — log every `[Open Question]` rule as a numbered item

---

## Source-of-Truth Rule

If DS and local split files differ:

1. Treat `XMT___Billing_System.ds` as authoritative.
2. Cite DS-based evidence in BRD `Source:` lines.
3. Mark uncertainty as `[Open Question]` instead of using stale local artifacts.

---

## Confidence Assignment Quick Reference

| Situation | Tag |
|-----------|-----|
| Traced to specific `.deluge` file and line | `[Confirmed]` |
| Strongly implied by code structure or naming | `[Inferred]` |
| Commented-out code, inactive workflow, or no trace found | `[Open Question]` |

---

## Additional Resources

- For the module-to-file mapping, see [module-map.md](module-map.md)
