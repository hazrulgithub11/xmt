# Credit Note Fix Progress Tracker

Scope:

- Source issues: `docs/feature/creditNote_wrong.md`
- Target behavior: `docs/feature/creditNote_Flow.md`
- Execution guide: `docs/feature/fix credit note/creditNote_Invoice.md`

Status legend:

- `[ ]` Not started
- `[-]` In progress
- `[x]` Done (code complete / deployed)
- `[~]` Code complete — UAT or `.ds` sync pending
- `[!]` Blocked

---

## Master Checklist

### Phase 1 — Steps 01–08 (Old flow fixes)

- [x] 01 - Preflight complete (`01-fix-credit-note-preflight.md`)
- [x] 02 - `Reference_Invoice` field added + exported (`02-fix-credit-note-reference-invoice-field.md`)
- [x] 03 - Credit Note blueprint structure aligned (`03-fix-credit-note-blueprint-structure.md`)
- [x] 04 - Status engine hardened (no early Open/Closed) (`04-fix-credit-note-status-engine-hardening.md`)
- [x] 05 - Convert path fixed (`05-fix-credit-note-convert-path.md`) — superseded by After 13 for convert UX
- [x] 06 - Apply/Refund guards fixed (`06-fix-credit-note-apply-refund-guards.md`)
- [x] 07 - LHDN reference payload fixed (`07-fix-credit-note-lhdn-reference.md`)
- [x] 08 - Test matrix + rollout package (`08-fix-credit-note-test-and-rollout.md`)

**UAT / live deploy:** See Step 08 sign-off table — runtime tests and final re-export are pending in Creator.

---

### Phase 2 — Steps 09–15 (New flow requirements from updated `creditNote_Flow.md`)

- [x] 09 - `Reference_Invoice` mandatory + LHDN UUID block (`09-fix-credit-note-mandatory-reference.md`)
- [x] 10 - Clone invoice lines from reference; reduce-only rule (`10-fix-credit-note-clone-invoice-lines.md`)
- [x] 11 - `Credit_Mode` field + lock Mode A vs Mode B at creation (`11-fix-credit-note-credit-mode-field.md`)
- [x] 12 - Cumulative CN cap at save + approval recheck (`12-fix-credit-note-cumulative-cap.md`)
- [~] 13 - Mode A: auto-apply on approval → Closed; hide Apply/Refund (`13-fix-credit-note-mode-a-auto-apply.md`)
- [ ] 14 - Mode B: apply same ref if Amount_Due > 0; other invoices; refund (`14-fix-credit-note-mode-b-apply-controls.md`)
- [ ] 15 - Test matrix v2, deploy Batch E–I, rollback package (`15-fix-credit-note-test-matrix-v2.md`)

**Prerequisite:** Phase 1 UAT must be signed off before deploying Phase 2.

---

### After 13 — Convert defer save (`after13/`)

Post–Step 13 fix: convert no longer inserts a Draft CN on click; opens add form prefilled; first save on Submit.

- [x] After13-1 - Slim convert action — validation only, open add form with URL params (`after13/01-phase-slim-convert-action.md`)
- [x] After13-2 - On-load prefill when `Reference_Invoice` set via URL (`after13/02-phase-on-load-prefill.md`)
- [x] After13-3 - Shared prefill custom functions (`after13/03-phase-shared-prefill-function.md`)
- [~] After13-4 - Save/approval path verification — no code changes expected (`after13/04-phase-save-approval-path.md`)
- [~] After13-5 - Edge cases + optional follow-ups — UAT reference (`after13/05-phase-edge-cases.md`)
- [ ] After13-6 - Test plan + rollout (`after13/06-test-plan-and-rollout.md`)

**Deploy note:** After13-1 + After13-2 must ship together. After13-3 refactors clone logic into `credit_note.prefill_from_reference_invoice` + `credit_note.credit_mode_from_invoice_stage`.

---

## Current Sprint Snapshot

### Phase 1

- Current step: `Complete (UAT pending)`
- Owner: `TBD`
- Started at: `2026-06-23`
- Current risk/blocker: `Live UAT + post-deploy export not yet run`

### Phase 2

- Current step: `Step 14 ready to start`
- Owner: `TBD`
- Started at: `2026-06-24`
- Current risk/blocker: `Step 13 UAT (T13-1 to T13-7) pending sign-off`

### After 13

- Current step: `Phases 1–3 complete; UAT + .ds sync pending`
- Owner: `TBD`
- Started at: `2026-06-25`
- Current risk/blocker: `Custom functions + Handle_Convert_Prefill must exist in live Creator before re-export`

---

## Detailed Step Tracking

### 01 - Preflight

- Status: `[x]`
- Doc: `docs/feature/fix credit note/01-fix-credit-note-preflight.md`
- Key checks:
  - [x] Required artifacts exist in local export and `XMT___Billing_System.ds`
  - [x] Missing artifacts synced from live Creator (if any)
  - [x] Rollback notes captured
  - [x] Batch deployment plan confirmed (Batches A–D)
- Completed by / date: `2026-06-23`

### 02 - Reference Invoice Field

- Status: `[x]`
- Doc: `docs/feature/fix credit note/02-fix-credit-note-reference-invoice-field.md`
- Key checks:
  - [x] `Reference_Invoice` added to `Credit_Note` form
  - [x] Field visible in Credit Notes list + quickview and Credit Note Report
  - [x] Selection validation workflow (`Handle_reference_invoice_2`)
  - [x] Customer change filters picker
  - [x] Export sync in local files and `XMT___Billing_System.ds`
- Completed by / date: `2026-06-23`

### 03 - Blueprint Structure

- Status: `[x]`
- Doc: `docs/feature/fix credit note/03-fix-credit-note-blueprint-structure.md`
- Key checks:
  - [x] Stage structure confirmed
  - [x] Utilization transition criteria corrected
  - [x] `Approved_to_Closed` path added
  - [x] `Revert_to_Pending_Approva` auto-revert disabled
  - [x] Blueprint export synced
- Completed by / date: `2026-06-23`

### 04 - Status Engine Hardening

- Status: `[x]`
- Doc: `docs/feature/fix credit note/04-fix-credit-note-status-engine-hardening.md`
- Key checks:
  - [x] No Open/Closed updates on Draft/Pending/Rejected
  - [x] Stage changes use `changeStage(...)` where needed
  - [x] Manual add/reopen stays Draft before approval
  - [x] Removed unguarded Open/Closed from `Handle_Submission_Form_an4`
- Completed by / date: `2026-06-23`

### 05 - Convert Path (original)

- Status: `[x]` — superseded by After 13 for convert UX
- Doc: `docs/feature/fix credit note/05-fix-credit-note-convert-path.md`
- Key checks:
  - [x] Convert sets `Reference_Invoice` correctly (now via URL param + prefill)
  - [x] CN number generated once only on Submit (`Handle_Invoice_Creation1`)
  - [x] Convert output Draft on first Submit (not on click)
  - [x] `Paid` stage condition case corrected on All_Invoices
- Completed by / date: `2026-06-23` (original); After 13 completed `2026-06-25`
- Notes: `Insert-on-click removed in After13-1. See After 13 section below.`

### 06 - Apply/Refund Guards

- Status: `[x]`
- Doc: `docs/feature/fix credit note/06-fix-credit-note-apply-refund-guards.md`
- Key checks:
  - [x] Apply/Refund actions hidden before approval
  - [x] Apply flow prefers `Reference_Invoice` when valid
  - [x] Draft-stage destructive credit row delete blocked
  - [x] Open/Closed transitions consistent after utilization
- Completed by / date: `2026-06-23`
- Notes: `Step 13 further gates Apply/Refund to Mode B only.`

### 07 - LHDN Reference Payload

- Status: `[x]`
- Doc: `docs/feature/fix credit note/07-fix-credit-note-lhdn-reference.md`
- Key checks:
  - [x] LHDN action visible only when Closed
  - [x] `reference_invoice_list` includes `Reference_Invoice` when present
  - [x] Deduplication of references validated
- Completed by / date: `2026-06-23`

### 08 - Testing + Rollout (Phase 1)

- Status: `[x]` (package ready; UAT pending)
- Doc: `docs/feature/fix credit note/08-fix-credit-note-test-and-rollout.md`
- Key checks:
  - [x] End-to-end test matrix documented (T1–T15)
  - [x] Regression checks documented (R1–R5)
  - [x] Rollback package + deploy manifest prepared
  - [ ] Runtime UAT passed in Creator
  - [ ] Final post-UAT export synced
- Completed by / date: `2026-06-23` (docs); UAT `TBD`

### 09 - Mandatory Reference Invoice

- Status: `[x]`
- Doc: `docs/feature/fix credit note/09-fix-credit-note-mandatory-reference.md`
- Key checks:
  - [x] `Reference_Invoice` required on `Credit_Note` form
  - [x] Save-time UUID guard in `Handle_Validation_Submiss2`
  - [x] Field-selection validator (`Handle_reference_invoice_2`)
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`

### 10 - Clone Invoice Lines (Reduce-Only)

- Status: `[x]`
- Doc: `docs/feature/fix credit note/10-fix-credit-note-clone-invoice-lines.md`
- Key checks:
  - [x] Line clone on `Reference_Invoice` selection (`Handle_reference_invoice_2`)
  - [x] Reduce-only save guard (`Handle_Validation_Submiss2`)
  - [x] Item identity fields read-only (`Disable_Fields20`)
  - [x] Block add row on line subforms (`Disable_Addition_And_Dele3`)
  - [x] Convert path copies all line fields (via `Handle_Convert_Prefill` + shared function)
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Clone logic centralized in After13-3 (`credit_note.prefill_from_reference_invoice`).`

### 11 - Credit_Mode Field (Mode A / Mode B at Creation)

- Status: `[x]`
- Doc: `docs/feature/fix credit note/11-fix-credit-note-credit-mode-field.md`
- Key checks:
  - [x] `Credit_Mode` field on `Credit_Note` form
  - [x] Mode detection on manual reference selection (`Handle_reference_invoice_2`)
  - [x] Mode set on convert (`Handle_Convert_Prefill` via `credit_mode_from_invoice_stage`)
  - [x] Save guard for missing mode on Draft/new (`Handle_Validation_Submiss2`)
  - [x] Field disabled in UI (`Disable_Fields20`)
  - [x] `Credit_Mode` column in `Credit_Notes` and `Credit_Note_Report`
  - [x] UAT T11-1 to T11-7 passed
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`

### 12 - Cumulative CN Cap (Save + Approval)

- Status: `[x]`
- Doc: `docs/feature/fix credit note/12-fix-credit-note-cumulative-cap.md`
- Key checks:
  - [x] Save-time cap in `Handle_Validation_Submiss2` (`on validate`, after per-line reduce-only checks)
  - [x] Approval-time recheck in `Approve/after/unconditional/script_01.deluge` (before LHDN validation)
  - [x] Cap counts **Approved + Closed + Open + Pending Approval** CNs (hotfix — Mode A Closed CNs visible to cap)
  - [x] Convert blocks only when `remaining_creditable <= 0` (`Convert_To_Credit_Note`)
  - [x] Approval breach reverts to **Pending Approval** via `changeStage`
  - [x] Save guard covers new record, Draft, Rejected, and Pending Approval
  - [x] `cn_grand_total` summed from line totals at validate (not stale `input.Grand_Total`)
  - [~] UAT T12-1 to T12-6 — code verified; formal sign-off pending
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Enhanced beyond doc V1 (Approved-only). Save validation in Handle_Validation_Submiss2, not Handle_Submission_Form_an4.`

### 13 - Mode A Auto-Apply on Approval

- Status: `[~]` Code complete — UAT pending
- Doc: `docs/feature/fix credit note/13-fix-credit-note-mode-a-auto-apply.md`
- Key checks:
  - [x] Mode A auto-apply in `Approve/after/unconditional/script_01.deluge` (after LHDN validation)
  - [x] `Apply_Credit_To_Invoice_Line` record created on approve
  - [x] Invoice `Amount_Due` / `Credits_Applied_Total` updated (matches apply-credit form pattern)
  - [x] CN `Credits_Used` / `Credits_Remaining = 0`; stage → **Closed**
  - [x] Paid reference invoice edge (`Amount_Due = 0`): closes without error, no apply row
  - [x] Apply Credits + Create Refund Note hidden for Mode A (`Credit_Notes.deluge`)
  - [x] Legacy null `Credit_Mode` treated as Mode B (actions visible)
  - [x] Audit log on `Invoice_Related_List`
  - [ ] UAT T13-1 to T13-7 passed
  - [~] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25` (code)
- Notes: `Uses changeStage(..., "Closed", ...) directly. Mode B unchanged — stays Approved/Open.`

### 14 - Mode B Apply/Refund Controls

- Status: `[ ]`
- Doc: `docs/feature/fix credit note/14-fix-credit-note-mode-b-apply-controls.md`
- Key checks:
  - [ ] Invoice picker shows ref invoice only when `Amount_Due > 0` (Mode B)
  - [ ] Apply to other open invoices allowed (Mode B)
  - [ ] Refund always allowed (Mode B)
  - [ ] Mode A CNs cannot reach apply/refund paths
  - [ ] UAT T14-1 to T14-6 passed
- Notes: `Ready to start — Steps 11, 12, 13 prerequisites met.`

### 15 - Test Matrix v2 + Rollout

- Status: `[ ]`
- Doc: `docs/feature/fix credit note/15-fix-credit-note-test-matrix-v2.md`
- Key checks:
  - [ ] T09–T16 matrix executed in sandbox
  - [ ] Deploy batches E–I documented and run
  - [ ] Rollback package for Phase 2
  - [ ] Final post-UAT export synced

---

## After 13 — Detailed Tracking

### After13-1 - Slim Convert Action

- Status: `[x]`
- Doc: `docs/feature/fix credit note/after13/01-phase-slim-convert-action.md`
- File: `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge`
- Key checks:
  - [x] No `insert into Credit_Note` on convert click
  - [x] Opens `#Form:Credit_Note` in add mode (no `recLinkID`)
  - [x] Blocks when `remaining_creditable <= 0`
  - [x] Does not block when invoice total > remaining (Submit's job)
  - [x] URL params: `Reference_Invoice`, `Customer`, `Customer_Code`
  - [~] Synced to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`

### After13-2 - On-Load Prefill

- Status: `[x]`
- Doc: `docs/feature/fix credit note/after13/02-phase-on-load-prefill.md`
- File: `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge` (new workflow)
- Key checks:
  - [x] Convert opens add form with full header + lines prefilled
  - [x] `Credit_Mode` set from invoice stage
  - [x] Form shows **Submit**, not **Update**
  - [x] CN not in list until Submit
  - [x] Manual Add path unchanged (`Handle_reference_invoice_2`)
  - [x] `Reference_Invoice` + `Customer_Code` display correctly (re-commit + no Customer cascade)
  - [~] Workflow created in live Creator + synced to `.ds`
- Completed by / date: `2026-06-25`

### After13-3 - Shared Prefill Function

- Status: `[x]`
- Doc: `docs/feature/fix credit note/after13/03-phase-shared-prefill-function.md`
- Files:
  - `application/Custom Functions/credit_note/prefill_from_reference_invoice`
  - `application/Custom Functions/credit_note/credit_mode_from_invoice_stage`
  - Refactored: `Handle_Convert_Prefill.deluge`, `Handle_reference_invoice_2.deluge`
- Key checks:
  - [x] Line field mapping in one place (`prefill_from_reference_invoice`)
  - [x] `Credit_Mode` detection in one place (`credit_mode_from_invoice_stage`)
  - [x] Manual reference selection behavior unchanged
  - [x] Convert prefill behavior restored (subform rows built in workflow from returned Maps — Zoho CF constraint)
  - [~] Custom functions present in `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Custom functions cannot insert subform row objects into form input; function returns List of Maps, workflows construct Credit_Note.Monthly_Rental() etc.`

### After13-4 - Save/Approval Path Verification

- Status: `[~]` QA checklist — no code changes expected
- Doc: `docs/feature/fix credit note/after13/04-phase-save-approval-path.md`
- Key checks:
  - [x] No unintended edits to `Handle_Validation_Submiss2`, `Handle_Invoice_Creation1`, approve script
  - [ ] Smoke: converted CN → edit → Submit → Draft → Approve → Closed/Open
  - [ ] Smoke: prefill > remaining → blocked on Submit (not convert)
  - [ ] T16-3, T16-4, T16-9 from test plan

### After13-5 - Edge Cases

- Status: `[~]` UAT reference — no mandatory code
- Doc: `docs/feature/fix credit note/after13/05-phase-edge-cases.md`
- Key checks:
  - [ ] Close popup without Submit → no CN record
  - [ ] Double convert → two unsaved forms; cap on save prevents over-credit
  - [ ] Invoice paid between convert open and Submit → cap still applies
  - [ ] Optional follow-ups logged if deferred (lock Reference_Invoice, show remaining creditable)

### After13-6 - Test Plan + Rollout

- Status: `[ ]`
- Doc: `docs/feature/fix credit note/after13/06-test-plan-and-rollout.md`
- Key checks:
  - [ ] Sandbox URL param prefill verified
  - [ ] Deploy After13-1 + After13-2 + After13-3 together
  - [ ] Rollback documented
  - [ ] Final export synced

---

## Issue Closure Mapping (`creditNote_wrong.md`)

| Area                | Items                 | Status                               |
| ------------------- | --------------------- | ------------------------------------ |
| Convert path        | #1–10                 | Code complete (Steps 02, 04, 05, 06, After 13) |
| Manual path         | #11                   | Code complete (Step 04, 09, 10)      |
| Status/approval     | #14, #16–17, #21      | Code complete (Steps 03, 04, 06, 13) |
| LHDN                | #23–25                | Code complete (Step 07)              |
| Aligned (no change) | #12, #18–20, #22, #26 | N/A                                  |

---

## Change Log

- `2026-06-25` - After 13 Phases 1–3 complete: convert defer-save, `Handle_Convert_Prefill`, shared `prefill_from_reference_invoice` + `credit_mode_from_invoice_stage`; subform fix (Maps from CF, rows built in workflow)
- `2026-06-25` - Step 13 code complete: Mode A auto-apply in approve script, Apply/Refund gated to Mode B in `Credit_Notes.deluge`
- `2026-06-25` - Step 12 complete: cumulative cap at save + approval recheck; cap hotfix counts Closed/Open/Pending Approval CNs
- `2026-06-25` - Step 11 complete: `Credit_Mode` field, UAT T11-1 to T11-7 passed
- `2026-06-25` - Step 10 complete: clone invoice lines, reduce-only validation, line subform controls
- `2026-06-25` - Step 09 complete: mandatory `Reference_Invoice` + LHDN UUID save guard
- `2026-06-24` - Phase 2 planning complete: Steps 09–15 written; index and tracker updated
- `2026-06-23` - Steps 01–08 code complete; test matrix and rollout package prepared
- `2026-06-23` - Tracker created
