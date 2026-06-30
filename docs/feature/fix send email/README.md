# Fix Send Email — Implementation Index (Invoice First)

This folder is split into **small, testable fix files**.  
Rule: **do not move to the next file until the current file test gate passes**.

## Reading and execution order

1. `overview.md` — finance audit findings and risks
2. `send-email-flow.md` — target-state end-to-end flow (invoice only)
3. `01-preflight.md`
4. `02-fix-remove-send-email-button.md`
5. `03-fix-send-invoice-entry-gate.md`
6. `04-fix-email-input-form-load.md`
7. `05-fix-send-email-engine-core.md`
8. `06-fix-journal-on-first-send.md`
9. `07-fix-notify-credits-available.md`
10. `08-fix-first-send-vs-resend-orchestration.md`
11. `09-fix-invoice-audit-fields.md`
12. `10-fix-pdf-template-standardization.md`
13. `11-fix-lhdn-gate-decision.md` (policy-dependent)
14. `12-test-matrix-and-signoff.md`
15. `progress_tracker.md` — live checkpoint

## Working rule (mandatory)

- Implement one file scope only.
- Run that file's **Test Gate**.
- Mark pass/fail in `progress_tracker.md`.
- Only continue when gate is green.

## Scope

- Current phase is **Invoice only**.
- Debit Note / Pro Forma follow in a separate phase.
