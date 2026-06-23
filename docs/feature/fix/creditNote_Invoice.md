# Credit Note Invoice Fix Plan (Step-by-Step)

This folder contains the executable fix runbook to move from current behavior in `docs/feature/creditNote_wrong.md` to target behavior in `docs/feature/creditNote_Flow.md`.

Follow in order:

1. `01-fix-credit-note-preflight.md`
2. `02-fix-credit-note-reference-invoice-field.md`
3. `03-fix-credit-note-blueprint-structure.md`
4. `04-fix-credit-note-status-engine-hardening.md`
5. `05-fix-credit-note-convert-path.md`
6. `06-fix-credit-note-apply-refund-guards.md`
7. `07-fix-credit-note-lhdn-reference.md`
8. `08-fix-credit-note-test-and-rollout.md`

Important:
- Do not skip sequence.
- In Zoho Creator, remove references before deleting/renaming fields, actions, or transitions.
- Re-export and sync `XMT___Billing_System.ds` after each major Creator change set.
