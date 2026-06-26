# Unified Credit Note Rule

## Problem summary

The credit note system had two artificial code paths called "Mode A" and "Mode B" that no longer reflect any real business distinction. This caused:

- **Silent discard** — Mode A forced `Credits_Remaining = 0` even when only part of the CN amount was applied, throwing away the difference with no record.
- **Mode B never auto-applied** — CNs from Paid/Partially Paid invoices were approved but never reduced the reference invoice balance. The user had to manually apply credits.
- **Approval-time drift** — a payment could arrive between CN creation and approval. A temporary drift guard was added that *blocked* approval instead of handling the excess correctly.
- **Confusing field** — `Credit_Mode` ("Mode A - Debt Reduction" / "Mode B - Open Credit") was opaque to new developers and drove branching logic that is no longer necessary.

## The unified rule

```
apply_amount    = min(CN Grand_Total, ref_invoice.Amount_Due)
credits_remaining = CN Grand_Total - apply_amount

if credits_remaining == 0  →  CN → Closed
if credits_remaining  > 0  →  CN → Open  (user applies excess to other invoices or refunds)
```

This single rule handles every invoice state correctly:

| Invoice state at approval | Amount_Due | CN amount | apply_amount | credits_remaining | CN result |
|---|---|---|---|---|---|
| Sent, no drift | 1000 | 1000 | 1000 | 0 | Closed |
| Sent, drift (payment received before approval) | 300 | 1000 | 300 | 700 | Open |
| Partially Paid | 400 | 500 | 400 | 100 | Open |
| Paid | 0 | 500 | 0 | 500 | Open |

No modes. No branching on `Credit_Mode`. No silent discard.

## Approach

Two steps. Do **not** combine into one deployment.

| Step | What | Why separate |
|---|---|---|
| [Step A](01-step-a-core-fix.md) | Replace Mode A/B logic with unified rule; fix action visibility | Core billing correctness — deploy and verify first |
| [Step B](02-step-b-retire-credit-mode.md) | Remove all remaining `Credit_Mode` references; delete custom function; delete field | Housekeeping — safe only after Step A is confirmed working |

## What is NOT in scope

- LHDN submission timing (balance reduces before LHDN submission) — separate architectural concern.
- Approval workflow removal — the Draft → Pending Approval → Approved lifecycle is kept.
- `fix sent invoice to credit note flow` docs (`docs/feature/fix sent invoice to credit note flow/`) — those docs are **superseded** by this workstream. Archive them.

## Primary files changed across both steps

| File | Step |
|---|---|
| `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge` | A |
| `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge` | A |
| `application/forms/Credit Note/Credit_Notes.deluge` | A |
| `application/Custom Functions/credit_note/prefill_from_reference_invoice` | A |
| `application/Custom Functions/credit_note/credit_mode_from_invoice_stage` | B (delete) |
| `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` | B |
| `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge` | B |
| `application/forms/Credit Note/workflow/Disable_Fields20.deluge` | B |
| `application/forms/Credit Note/Credit_Note_Report.deluge` | B |
| `application/forms/Credit Note/Credit_Note.deluge` | B |
| Creator UI — Credit_Note form field | B (last action) |
| `XMT___Billing_System.ds` | A + B (mirror after each step) |
