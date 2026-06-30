# 01 — Preflight (Invoice Send Email Fix)

## Objective

Confirm baseline and scope before changing behavior.

## In scope

- Invoice send flow only
- Entry actions, email popup flow, journal timing, credit notify path

## Out of scope

- Debit note send flow
- Pro forma send flow
- Payment Received / Credit Note enhancements

## Checklist

- Confirm target references:
  - `overview.md`
  - `send-email-flow.md`
- Confirm affected files exist locally and match latest export:
  - `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`
  - `application/forms/Invoice/workflow/actions/Send_Email5.deluge`
  - `application/forms/Email Input Form/workflow/send_email_.deluge`
  - `application/forms/Email Input Form/workflow/Handle_Load_Of_The_Form.deluge`
  - `application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge`
  - `application/forms/Notify Credits Available/workflow/Open_Form_Apply_Credit_Fo.deluge`
- Confirm finance policy decisions:
  - First-send journal on email confirm (Yes/No)
  - LHDN gate behavior (block or warn)
  - Gross-send email should not mention unused credit

## Deliverable

Preflight notes complete and blockers listed.

## Test Gate (must pass before step 02)

- [ ] All in-scope files confirmed present and current
- [ ] Policy decisions above captured
- [ ] No unresolved blocker for step 02
