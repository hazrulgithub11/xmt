# 04 — Fix Email Popup Load Defaults (Invoice)

## Problem

Email popup does not consistently preload all send-critical values (especially recipient).

## Target behavior

On popup load for Invoice:

- To = `Customer_E_mail`
- Cc = template/org default if configured
- Subject/Body = active Invoice template
- Placeholders and selected placeholders loaded correctly
- Record/document context locked (read-only/hidden)

## Files expected to change

- `application/forms/Email Input Form/workflow/Handle_Load_Of_The_Form.deluge`
- `application/forms/Email Input Form/workflow/Disable_Fields17.deluge`
- `application/forms/Email Input Form/workflow/hide_record_id.deluge`

## Implementation notes

- Maintain user ability to edit To/Cc/Subject/Body before submit
- Do not allow user to alter source record id/document type

## Test Gate (must pass before step 05)

- [ ] Approved invoice opens popup with To auto-filled from customer
- [ ] Subject/body placeholders prefilled from active template
- [ ] Record context fields hidden/locked
- [ ] User can still edit message fields before sending
