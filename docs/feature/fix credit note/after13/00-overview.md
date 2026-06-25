# After 13 — Convert to Credit Note: Defer Save Until Submit

Master index for splitting convert from **insert-on-click** to **prefill-then-submit**.

## Context

Post–Step 13 testing exposed two convert-path issues:

1. **Cumulative cap on convert (fixed separately):** Convert bypassed save-time validation and counted only `Approved` CNs — Mode A CNs that go straight to **Closed** were invisible to the cap. Fixed by counting `Approved` + `Closed` + `Open` + `Pending Approval`, and blocking convert only when `remaining_creditable <= 0`.
2. **Save timing (this workstream):** Convert still **inserts a Draft CN immediately** on button click, then opens the form in **edit** mode (`recLinkID`). The user sees **Update**, not **Submit**, and the CN already appears in the Credit Notes list before they confirm.

Step 05 documented the intended UX:

> *"It is acceptable that initial converted amount equals source totals. Partial credit is handled by user edits in Draft before approval."*

That implies: open a form to review and adjust, then save. The current implementation saves first, then opens for edit — the opposite order.

### Example (XK26000057)

| Step | What happened |
|------|-----------------|
| 1 | Invoice RM 800, convert → CN RM 300 (Mode A), approved, Closed |
| 2 | Invoice `Amount_Due` = RM 500 |
| 3 | Convert again → popup should open for user to edit down to ≤ 500 |
| 4 | **Today:** CN inserted at RM 800 on click; user must **Update** an already-saved Draft |
| 5 | **Target:** Add form opens at RM 800; user edits; first persist on **Submit** |

---

## Objective

Change **Convert to Credit Note** so that:

1. Clicking convert runs **validation only** (stage, zero remaining credit, basic LHDN readiness).
2. The Credit Note **add** form opens prefilled from the source invoice.
3. **No database record** is created until the user clicks **Submit**.
4. Cumulative cap and line guards run on **Submit** and **Approve** as today.

---

## Current vs target flow

### Current (insert-then-edit)

```
User clicks Convert
  → insert into Credit_Note (+ line subforms)
  → openURL(#Form:Credit_Note?recLinkID={id})   // edit mode
  → CN visible in list as Draft
  → User clicks Update to commit edits
```

### Target (prefill-then-submit)

```
User clicks Convert
  → validate stage + remaining_creditable > 0
  → openURL(#Form:Credit_Note?Reference_Invoice={id}&Customer={id})   // add mode
  → on load: prefill header + lines + Credit_Mode from invoice
  → User adjusts lines, clicks Submit
  → on validate: cap + line guards
  → on add success: CN number (Handle_Invoice_Creation1), Draft stage
```

Close popup without Submit → **no CN record**.

---

## Dependency

- Steps 09–13 deployed (mandatory reference, line clone, Credit_Mode, cumulative cap, Mode A auto-apply).
- Cumulative cap hotfix (Closed CNs counted; convert blocks only when remaining = 0) should be deployed before or with this workstream.

**Out of scope:** Debit Note convert (same insert-first pattern; separate decision).

---

## Phase index

| Phase | Doc | Summary |
|-------|-----|---------|
| 1 | [01-phase-slim-convert-action.md](01-phase-slim-convert-action.md) | Remove insert from record action; open add form with URL params |
| 2 | [02-phase-on-load-prefill.md](02-phase-on-load-prefill.md) | On add load: prefill header, lines, Credit_Mode from reference invoice |
| 3 | [03-phase-shared-prefill-function.md](03-phase-shared-prefill-function.md) | Extract `prefill_from_reference_invoice` custom function |
| 4 | [04-phase-save-approval-path.md](04-phase-save-approval-path.md) | Confirm no change to Submit / add success / Approve paths |
| 5 | [05-phase-edge-cases.md](05-phase-edge-cases.md) | Edge cases and optional follow-ups |
| 6 | [06-test-plan-and-rollout.md](06-test-plan-and-rollout.md) | Zoho safety, test matrix, exit criteria, rollback, deploy order |

---

## Primary files (all phases)

| Artifact | Phase | Role |
|----------|-------|------|
| `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge` | 1 | Remove insert; open add form with URL params |
| `application/forms/Credit Note/workflow/Load_Of_The_Form_during_C1.deluge` or new `Handle_Convert_Prefill.deluge` | 2 | On add load: prefill when `Reference_Invoice` set via URL |
| `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` | 3 | Refactor to shared prefill |
| `application/Custom Functions/credit_note/prefill_from_reference_invoice` | 3 | New — shared clone logic |
| `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge` | 4 | No change — cap on Submit |
| `application/forms/Credit Note/workflow/Handle_Invoice_Creation1.deluge` | 4 | No change — CN number on first add success |
| `application/blueprints/.../Approve/after/unconditional/script_01.deluge` | 4 | No change — cap on Approve |

---

## Effort estimate

| Phase | Size |
|-------|------|
| Phase 1 — slim convert action | Small |
| Phase 2 — on-load prefill | Medium |
| Phase 3 — shared function + refactor | Medium |
| Phase 4 — verification only | Small |
| Phase 5 — documentation / QA reference | Small |
| UAT (Phase 6) | Medium |

**Batch:** Deploy after Step 13 UAT sign-off; can ship with or immediately after cumulative-cap convert hotfix.

**Implement in order:** Phase 1 → 2 → (3 recommended before production) → 4 verify → 5 reference → 6 UAT.
