# 07 — Fix Notify Credits Available (Invoice)

## Problem

Current No-path can bypass email review flow; Yes/No outcomes are not aligned to one governed send process.

## Target behavior

- Notify popup appears only on first-send attempt when credit > 0
- **Yes** -> open Apply Credits form; no customer email yet
- **No** -> continue to Email Input Form review popup (not direct send)
- Close popup without decision -> no send

## Files expected to change

- `application/forms/Notify Credits Available/workflow/Open_Form_Apply_Credit_Fo.deluge`
- `application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge`
- `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`

## Implementation notes

- Keep popup as internal staff checkpoint only
- Do not include unused-credit notice in customer email when No-path chosen

## Test Gate (must pass before step 08)

- [ ] Credit > 0 shows notify popup on first-send attempt
- [ ] Yes opens Apply Credits and does not send email immediately
- [ ] No opens Email Input Form (review first)
- [ ] Close popup aborts send
- [ ] Notify popup does not appear on resend
