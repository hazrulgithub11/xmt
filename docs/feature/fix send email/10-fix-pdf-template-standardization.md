# 10 — Standardize Invoice PDF Attachment Method

## Problem

Invoice send paths currently mix `invokeurl` public URL downloads and template attachment syntax.

## Target behavior

Use one consistent PDF method for invoice email sends:

- `Attachments :template:... as PDF`

Template selection:

- Miscellaneous -> `Miscellaneous_Invoice`
- Fixed/Telephone -> `Fixed_And_Telephone_Charges_Invoice`

## Files expected to change

- Invoice send paths in:
  - `application/forms/Email Input Form/workflow/send_email_.deluge`
  - `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`
  - `application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge`

## Implementation notes

- Remove hardcoded record-pdf URL dependency for invoice send path
- Keep output template fidelity identical to current approved templates

## Test Gate (must pass before step 11)

- [ ] All invoice manual send paths use template attachment syntax only
- [ ] Misc vs fixed/telephone template routing works
- [ ] PDF output content matches expected invoice template
