# 05 — Fix `send_email_` Core Engine (Invoice)

## Problem

Current send engine mixes logic paths and lacks strict fail-closed controls for target-state flow.

## Target behavior

On Email Input Form submit:

1. Validate required fields (recipient, record context)
2. Fetch live invoice data
3. Merge placeholders safely
4. Attach correct PDF template by charge category
5. Send email
6. Hand off to first-send or resend post-actions

## File expected to change

- `application/forms/Email Input Form/workflow/send_email_.deluge`

## Implementation notes

- Trigger should be **on add** for send execution (avoid edit-trigger duplicate send)
- Fail closed: if validation/PDF/data fetch fails, do not send
- Keep Pro Forma/Debit Note logic untouched in this phase unless required for stability

## Test Gate (must pass before step 06)

- [ ] Successful send works for Invoice from popup
- [ ] Invalid email blocks send
- [ ] PDF/data fetch failure blocks send
- [ ] Editing old popup rows does not trigger unintended resend
