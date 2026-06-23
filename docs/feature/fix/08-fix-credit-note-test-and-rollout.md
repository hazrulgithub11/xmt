# 08 - Test Matrix, Deployment Order, and Rollback

## Objective
Ship safely with clear verification and rollback points.

## Deployment order (recommended)
1. Deploy Step 02 (field dependency).
2. Deploy Step 03 + Step 04 together (blueprint + status hardening).
3. Deploy Step 05 (convert path cleanup).
4. Deploy Step 06 (apply/refund timing and guards).
5. Deploy Step 07 (LHDN references).

## Core test matrix
1. Manual create -> save -> reopen:
   - stays `Draft`
2. Convert from invoice -> popup open:
   - CN is `Draft`
   - `Reference_Invoice` populated
   - CN number generated once
3. Approval loop:
   - `Draft -> Pending Approval -> Approved`
   - Reject/resubmit still works
4. Apply credit after approval:
   - Invoice `Amount_Due` reduced correctly
   - CN `Credits_Used` and `Credits_Remaining` updated
   - Stage moves to `Open` or `Closed`
5. Refund path after approval:
   - CN `Refund` and `Credits_Remaining` updated
   - Stage moves correctly
6. LHDN submit:
   - Available only at `Closed`
   - Payload includes expected reference invoice list

## Regression checks
- No duplicate CN numbering.
- Convert action visible for correct invoice stages (`Sent`, `Partially Paid`, `Paid`, `Overdue`).
- No unintended state changes on normal form load/edit.

## Rollback strategy
For each deployment batch:
1. Keep a copy of previous exported scripts/json.
2. If severe issue appears:
   - Revert latest batch scripts first.
   - Revert blueprint transition changes second.
   - Re-export and sync local repo.

## Completion criteria
- All targeted items in `docs/feature/creditNote_wrong.md` are closed.
- Runtime behavior matches `docs/feature/creditNote_Flow.md`.
- Exported artifacts are synchronized in repo and `XMT___Billing_System.ds`.
