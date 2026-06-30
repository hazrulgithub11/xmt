# Phase 3 — Extract Shared Prefill Logic

Part of: [After 13 — Convert defer save](00-overview.md)

## Objective

Single source of truth for cloning invoice data into a Credit Note — used by both **manual** (`Reference_Invoice` user input) and **convert** (on load prefill) paths.

## Primary files

- **New:** `application/Custom Functions/credit_note/prefill_from_reference_invoice`
- **Refactor:** `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge`
- **Refactor:** Phase 2 convert on-load workflow (`Handle_Convert_Prefill.deluge` or equivalent)

## Dependency

- Phase 2 working in sandbox (inline clone logic proven before extract).

---

## Custom function sketch

**Namespace / name:** `credit_note.prefill_from_reference_invoice`

**Suggested signature** (adjust after reading Zoho constraints — may need to work on `input` in workflow caller instead of passing form context):

```deluge
void credit_note.prefill_from_reference_invoice(int invoice_id)
{
    ref_invoice = Invoice[ID == invoice_id];
    // Header field copy
    // Line subform clone (Monthly_Rental, Internet_Charges, Call_Charges)
    // Credit_Mode from ref_invoice.Blueprint.Current_Stage
}
```

**Note:** Custom functions cannot always mutate `input` of an open form. If not supported, split into:

| Function | Purpose |
|----------|---------|
| `credit_note.clone_lines_from_invoice(invoice_id)` | Returns or inserts line rows |
| `credit_note.credit_mode_from_invoice_stage(invoice_id)` | Returns Mode A / B string |

Callers assign header fields inline; function owns line clone + mode detection only.

---

## Callers

| Caller | When | Extra logic before call |
|--------|------|-------------------------|
| `Handle_reference_invoice_2.deluge` | `on user input of Reference_Invoice` | LHDN UUID + document status API validation |
| Convert on-load workflow | `on add` / `on load` with URL-prefilled reference | Light UUID check only (Phase 2) |

After refactor, remove duplicated clone blocks from:

- `Convert_To_Credit_Note.deluge` (already removed in Phase 1)
- `Handle_reference_invoice_2.deluge` (replace inline loop with function call)

---

## What stays in `Handle_reference_invoice_2`

Keep in the workflow (not the function):

- LHDN access token + document status API call
- Alerts and `clear Reference_Invoice` on validation failure
- Customer-scoped invoice list refresh on error
- `input.User_Input_Trigger` toggle after successful clone

---

## Exit criteria (Phase 3)

- [x] Line clone logic exists in one place only
- [x] `Credit_Mode` detection exists in one place only
- [x] Manual reference selection behavior unchanged (T16-6)
- [x] Convert prefill behavior unchanged (T16-7, T16-8) — subform rows built in workflow from Maps returned by CF
- [~] Custom function present in `XMT___Billing_System.ds`

---

## Optional deferral

Phase 3 can ship **after** Phase 1 + 2 if timeline is tight — duplicate clone code temporarily in Phase 2, then refactor in a follow-up deploy. Recommended to complete Phase 3 before production to avoid drift between manual and convert paths.
