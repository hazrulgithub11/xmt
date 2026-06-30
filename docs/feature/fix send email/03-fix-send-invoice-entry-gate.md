# 03 — Fix `Send_Invoice` Entry Gate (Invoice)

## Problem

`Send_Invoice` currently performs direct send/journal in some branches instead of acting as a routing entry.

## Target behavior

`Send_Invoice` should only route:

- Approved + credit > 0 -> Notify Credits popup
- Approved + no credit -> Email Input Form popup
- Sent/Partially Paid/Paid/Overdue -> Email Input Form popup (resend)
- Draft/Pending approval -> blocked

## File expected to change

- `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`

## Implementation notes

- Remove direct `sendmail` from entry action
- Remove direct inline journal insert from entry action
- Pass enough context to popup (document type, record id, send type)

## Test Gate (must pass before step 04)

- [ ] Entry action does not directly email customer
- [ ] Entry action does not directly create journal
- [ ] Approved/no-credit opens Email Input Form
- [ ] Approved/credit opens Notify Credits popup
- [ ] Sent+ opens Email Input Form for resend
- [ ] Draft cannot proceed
