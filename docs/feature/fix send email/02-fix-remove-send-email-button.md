# 02 — Remove Separate `Send Email` Button (Invoice)

## Problem

Invoice has two manual send actions (`Send Invoice` and `Send Email`) causing inconsistent controls.

## Target behavior

- Only one customer-send action remains: **Send Invoice**
- All manual sends must route through one governed flow

## Files expected to change

- `application/forms/Invoice/workflow/actions/Send_Email5.deluge`
- `application/forms/Invoice/Invoices` (action visibility)
- `application/forms/Invoice/Invoice.deluge` (button definition if present)

## Implementation notes

- Remove action from UI/report and related references
- Do not remove historical logs/data

## Risks

- Hidden references to `Send_Email5` in report actions
- Users losing resend ability unless step 03+ is done immediately

## Test Gate (must pass before step 03)

- [x] `Send Email` action no longer visible on Invoice UI (removed from `Invoices` custom actions + detailview menu)
- [x] `Send Invoice` still visible and callable (`Miscellaneous_Template`, `Fixed_And_Telephone_Charges_Template` — unchanged)
- [x] No runtime error from missing `Send_Email5` (no remaining `workflow = Send_Email5` references in repo)
