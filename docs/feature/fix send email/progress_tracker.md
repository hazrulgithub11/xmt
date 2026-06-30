# Fix Send Email — Progress Tracker (Invoice)

Update this tracker after each file gate.

| Step | File | Owner | Status | Test Gate Result | Notes |
|---|---|---|---|---|---|
| 01 | `01-preflight.md` | Agent | Blocked | Partial | Files verified; `Send_Invoice.deluge` drift vs `.ds`; LHDN policy pending |
| 02 | `02-fix-remove-send-email-button.md` | Agent | Passed | Code review | Send Email removed from `Invoices`; `Send_Email5.deluge` deleted — deploy to Creator required |
| 03 | `03-fix-send-invoice-entry-gate.md` |  | Not Started |  |  |
| 04 | `04-fix-email-input-form-load.md` |  | Not Started |  |  |
| 05 | `05-fix-send-email-engine-core.md` |  | Not Started |  |  |
| 06 | `06-fix-journal-on-first-send.md` |  | Not Started |  |  |
| 07 | `07-fix-notify-credits-available.md` |  | Not Started |  |  |
| 08 | `08-fix-first-send-vs-resend-orchestration.md` |  | Not Started |  |  |
| 09 | `09-fix-invoice-audit-fields.md` |  | Not Started |  |  |
| 10 | `10-fix-pdf-template-standardization.md` |  | Not Started |  |  |
| 11 | `11-fix-lhdn-gate-decision.md` |  | Not Started |  |  |
| 12 | `12-test-matrix-and-signoff.md` |  | Not Started |  |  |

## Status values

- Not Started
- In Progress
- Blocked
- Passed

## Gate rule

No downstream step may move to **In Progress** until upstream step is **Passed**.
