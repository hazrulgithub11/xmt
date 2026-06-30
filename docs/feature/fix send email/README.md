# Fix Send Email — Implementation Index (Invoice MVP)

This folder is split into **small, testable fix files**.  
Rule: **do not move to the next file until the current file test gate passes**.

**MVP ends at step 06.** Credit notify, audit fields, LHDN policy doc, and full signoff matrix are deferred.

## Reading and execution order

1. `overview.md` — finance audit findings (context)
2. `send-email-flow.md` — target flow reference (see MVP scope note at top)
3. `01-preflight.md`
4. `02-fix-remove-send-email-button.md`
5. `03-fix-send-invoice-entry-gate.md`
6. `04-fix-email-input-form-load.md`
7. `05-fix-send-email-engine-core.md`
8. `06-fix-journal-on-first-send.md` — **MVP complete**
9. `progress_tracker.md` — live checkpoint

## Working rule (mandatory)

- Implement one file scope only.
- Run that file's **Test Gate**.
- Mark pass/fail in `progress_tracker.md`.
- Only continue when gate is green.

## MVP scope (steps 01–06)

| In scope | Out of scope (later) |
|----------|----------------------|
| One Send Invoice button | Notify Credits / apply credit before send |
| Email review popup before every send | Customer email when CN issued/applied |
| Fail-closed send + template PDF | Full audit fields on invoice |
| Journal once on first send | LHDN policy write-up (live blueprint gate unchanged) |
| Resend = email only | Pro forma / debit note send alignment |

## Deferred initiatives (no step files in this folder)

- Credit notify + pre-send apply + customer credit communications
- Invoice `Sent_Date` / resend audit fields
- PDF URL cleanup beyond MVP template path in step 05
