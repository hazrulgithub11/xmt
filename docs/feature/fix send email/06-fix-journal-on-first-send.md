# 06 — First Send Completion + Journal (Invoice) — **MVP final step**

## Problem

Journal creation is duplicated; first send vs resend side effects are not centralized on Email Input Form submit.

## Target behavior

On Email Input Form submit for **Invoice**:

**First send** (invoice stage **Approved** at open time):

- Send email + PDF
- Create journal entry **once** (idempotency guard)
- Blueprint -> **Sent** or **Overdue** (by due date)

**Resend** (invoice already **Sent / Partially Paid / Paid / Overdue**):

- Send email + PDF only
- **No** new journal
- **No** blueprint stage change

## Files expected to change

- `application/Custom Functions/invoice/*` (new helper, e.g. `create_journal_on_send`)
- `application/forms/Email Input Form/workflow/send_email_.deluge`

## Implementation notes

- Determine first send vs resend from invoice blueprint stage when popup opens or on submit (before stage changes)
- Guard: skip journal insert if journal already linked to invoice
- Preserve existing account mapping / subtotal / tax / grand-total postings
- Audit fields (`Sent_Date`, etc.) — nice-to-have; not required for MVP

## MVP Test Gate (sign-off after this step)

- [ ] Approved -> Send Invoice -> popup -> submit: customer email sent, **one** journal, stage Sent/Overdue
- [ ] Sent+ -> Send Invoice -> popup -> submit: customer email sent, **no** new journal, stage unchanged
- [ ] Cancel/close popup: no email, no journal, no stage change
- [ ] Re-click submit does not duplicate journal on first send
- [ ] Journal totals reconcile with invoice totals
