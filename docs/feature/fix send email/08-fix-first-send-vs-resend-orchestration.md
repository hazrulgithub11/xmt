# 08 — First Send vs Resend Orchestration (Invoice)

## Problem

System behavior differs by path, and the same action can trigger side effects intended only for first send.

## Target behavior

Use explicit send mode context:

- `first_send`: email + journal + stage + audit
- `resend`: email + resend audit only

## Files expected to change

- `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`
- `application/forms/Email Input Form/workflow/Handle_Load_Of_The_Form.deluge`
- `application/forms/Email Input Form/workflow/send_email_.deluge`

## Implementation notes

- Pass mode via popup parameter or deterministic stage logic
- Keep logic deterministic and testable

## Test Gate (must pass before step 09)

- [ ] Approved first-send follows first-send branch
- [ ] Sent/Partially Paid/Paid/Overdue follows resend branch
- [ ] Resend does not change blueprint stage
- [ ] Resend does not create journal
