# 11 — LHDN Gate Decision (Invoice Send)

## Problem

Policy for send behavior when `Invoice_UUID` (LHDN state) is missing is unclear across paths.

## Required decision

Choose one policy:

1. **Block send** until LHDN submission exists
2. **Warn only** and allow send

## Target behavior

One consistent rule enforced at send entry and tested in all first-send paths.

## Files expected to change (if rule changes)

- `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`
- Related blueprint transition script(s) for Invoice send behavior

## Test Gate (must pass before step 12)

- [ ] Finance formally approves policy (block or warn)
- [ ] Same policy observed in all first-send branches
- [ ] UAT evidence captured for missing UUID case
