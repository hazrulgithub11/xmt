# 03 — Fix `Send_Invoice` Entry Gate (Invoice)

## Problem

`Send_Invoice` currently performs direct send/journal in some branches instead of acting as a routing entry.

## Target behavior

`Send_Invoice` should only route:

- Approved -> Email Input Form popup (first send)
- Sent/Partially Paid/Paid/Overdue -> Email Input Form popup (resend)
- Draft/Pending approval/Rejected -> blocked

**Out of scope (MVP):** Notify Credits Available / credit apply before send — deferred to a later credit-comms initiative.

## File expected to change

- `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`

## Implementation notes

- Remove direct `sendmail` from entry action
- Remove direct inline journal insert from entry action
- Pass context to popup: `Record_ID`, `Document_Type=Invoice`
- No `Credit_Available` / notify popup on Approved

## Test Gate (must pass before step 04)

- [x] Entry action does not directly email customer
- [x] Entry action does not directly create journal
- [x] Approved opens Email Input Form
- [x] Sent+ opens Email Input Form for resend
- [x] Draft cannot proceed (alert popup)
- [x] No notify-credits branch on Approved
