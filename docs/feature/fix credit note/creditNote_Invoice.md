# Credit Note Fix Plan (Step-by-Step)

This folder contains the executable fix runbook. Target behavior is defined in `docs/feature/creditNote_Flow.md`.

---

## Phase 1 — Steps 01–08 (Old flow fixes — status: code complete, UAT pending)

Fixes from `creditNote_wrong.md`: `Reference_Invoice` field, blueprint structure, status engine, convert path, apply/refund guards, LHDN payload.

1. `01-fix-credit-note-preflight.md`
2. `02-fix-credit-note-reference-invoice-field.md`
3. `03-fix-credit-note-blueprint-structure.md`
4. `04-fix-credit-note-status-engine-hardening.md`
5. `05-fix-credit-note-convert-path.md`
6. `06-fix-credit-note-apply-refund-guards.md`
7. `07-fix-credit-note-lhdn-reference.md`
8. `08-fix-credit-note-test-and-rollout.md`

---

## Phase 2 — Steps 09–15 (New flow requirements — status: planning)

New requirements from the updated `creditNote_Flow.md`: mandatory reference invoice, line cloning, Credit_Mode detection, cumulative cap, Mode A auto-apply, Mode B apply controls.

**Must deploy Phase 1 (Steps 01–08) before starting Phase 2.**

9. `09-fix-credit-note-mandatory-reference.md` — Make `Reference_Invoice` required; block save without LHDN-validated invoice
10. `10-fix-credit-note-clone-invoice-lines.md` — Clone lines from reference invoice; reduce-only rule
11. `11-fix-credit-note-credit-mode-field.md` — Add `Credit_Mode` field; lock Mode A vs Mode B at creation
12. `12-fix-credit-note-cumulative-cap.md` — Cumulative approved CN cap at save + approval recheck
13. `13-fix-credit-note-mode-a-auto-apply.md` — Mode A: auto-apply on approval → Closed; hide Apply/Refund actions
14. `14-fix-credit-note-mode-b-apply-controls.md` — Mode B: apply to same ref if Amount_Due > 0 or other invoices; refund allowed
15. `15-fix-credit-note-test-matrix-v2.md` — Test matrix v2, deploy order Batch E–I, rollback package

---

## Deferred (not in Phase 2)

| Item | Tracked in |
|------|-----------|
| Q21 — Re-evaluate Credit_Mode at approval (if invoice stage changes during Pending Approval) | `creditNote_Flow_QA.md` deferred section |
| Q10/Q23 — Reserve cap for Draft + Pending Approval CNs (strict concurrent lock) | `creditNote_Flow_QA.md` deferred section |

---

## Important rules (all phases)

- Do not skip sequence within each phase.
- In Zoho Creator, remove references before deleting/renaming fields, actions, or transitions.
- Re-export and sync `XMT___Billing_System.ds` after each major Creator change set.
- Do not start Phase 2 on live until Phase 1 UAT is signed off.
