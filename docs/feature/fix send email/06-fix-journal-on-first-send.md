# 06 — Journal on First Send Only (Invoice)

## Problem

Journal creation logic is duplicated and risks inconsistent behavior or duplicate posting.

## Target behavior

- Journal entry is created **once** on first official send
- Resend never creates another journal
- Shared function handles journal creation and idempotency check

## Files expected to change

- `application/Custom Functions/invoice/*` (new helper, e.g. `create_journal_on_send`)
- Call sites:
  - `application/forms/Email Input Form/workflow/send_email_.deluge`
  - (if needed) `application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge`

## Implementation notes

- Guard: skip insert if journal already linked to invoice
- Preserve existing account mapping/subtotal/tax/grand-total postings

## Test Gate (must pass before step 07)

- [ ] First send creates exactly one journal entry
- [ ] Re-send creates zero new journal entries
- [ ] Re-click/retry does not duplicate first-send journal
- [ ] Journal totals reconcile with invoice totals
