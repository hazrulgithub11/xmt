# Credit Note Fix Progress Tracker

Scope:

- Source issues: `docs/feature/creditNote_wrong.md`
- Target behavior: `docs/feature/creditNote_Flow.md`
- Execution guide: `docs/feature/fix/creditNote_Invoice.md`

Status legend:

- `[ ]` Not started
- `[-]` In progress
- `[x]` Done
- `[!]` Blocked

---

## Master Checklist

### Phase 1 — Steps 01–08 (Old flow fixes)

- [x] 01 - Preflight complete (`01-fix-credit-note-preflight.md`)
- [x] 02 - `Reference_Invoice` field added + exported (`02-fix-credit-note-reference-invoice-field.md`)
- [x] 03 - Credit Note blueprint structure aligned (`03-fix-credit-note-blueprint-structure.md`)
- [x] 04 - Status engine hardened (no early Open/Closed) (`04-fix-credit-note-status-engine-hardening.md`)
- [x] 05 - Convert path fixed (`05-fix-credit-note-convert-path.md`)
- [x] 06 - Apply/Refund guards fixed (`06-fix-credit-note-apply-refund-guards.md`)
- [x] 07 - LHDN reference payload fixed (`07-fix-credit-note-lhdn-reference.md`)
- [x] 08 - Test matrix + rollout package (`08-fix-credit-note-test-and-rollout.md`)

**UAT / live deploy:** See Step 08 sign-off table — runtime tests and final re-export are pending in Creator.

---

### Phase 2 — Steps 09–15 (New flow requirements from updated `creditNote_Flow.md`)

- [x] 09 - `Reference_Invoice` mandatory + LHDN UUID block (`09-fix-credit-note-mandatory-reference.md`)
- [x] 10 - Clone invoice lines from reference; reduce-only rule (`10-fix-credit-note-clone-invoice-lines.md`)
- [x] 11 - `Credit_Mode` field + lock Mode A vs Mode B at creation (`11-fix-credit-note-credit-mode-field.md`)
- [x] 12 - Cumulative approved CN cap at save + approval recheck (`12-fix-credit-note-cumulative-cap.md`)
- [ ] 13 - Mode A: auto-apply on approval → Closed; hide Apply/Refund (`13-fix-credit-note-mode-a-auto-apply.md`)
- [ ] 14 - Mode B: apply same ref if Amount_Due > 0; other invoices; refund (`14-fix-credit-note-mode-b-apply-controls.md`)
- [ ] 15 - Test matrix v2, deploy Batch E–I, rollback package (`15-fix-credit-note-test-matrix-v2.md`)

**Prerequisite:** Phase 1 UAT must be signed off before deploying Phase 2.

---

## Current Sprint Snapshot

### Phase 1

- Current step: `Complete (UAT pending)`
- Owner: `TBD`
- Started at: `2026-06-23`
- Current risk/blocker: `Live UAT + post-deploy export not yet run`

### Phase 2

- Current step: `Step 13 ready to start`
- Owner: `TBD`
- Started at: `2026-06-24`
- Current risk/blocker: `None for Step 12`

---

## Detailed Step Tracking

### 01 - Preflight

- Status: `[x]`
- Doc: `docs/feature/fix/01-fix-credit-note-preflight.md`
- Key checks:
  - [x] Required artifacts exist in local export and `XMT___Billing_System.ds`
  - [x] Missing artifacts synced from live Creator (if any) — none required; `Reference_Invoice` deferred to Step 02
  - [x] Rollback notes captured (see Preflight results section in step doc)
  - [x] Batch deployment plan confirmed (Batches A–D)
- Completed by / date: `2026-06-23`
- Notes: `Sync drift: Credit_Notes action conditions (Status vs Blueprint.Current_Stage); All_Invoices "paid" case.`

### 02 - Reference Invoice Field

- Status: `[x]`
- Doc: `docs/feature/fix/02-fix-credit-note-reference-invoice-field.md`
- Key checks:
  - [x] `Reference_Invoice` added to `Credit_Note` form (optional picklist)
  - [x] Field visible in Credit Notes list + quickview and Credit Note Report
  - [x] Selection validation workflow implemented (`Handle_reference_invoice_2`)
  - [x] Customer change filters picker; null allowed for standalone CN
  - [x] Export sync in local files and `XMT___Billing_System.ds`
- Completed by / date: `2026-06-23`
- Notes: `Deploy field + workflows to live Creator, then re-export. Convert mapping deferred to Step 05.`

### 03 - Blueprint Structure

- Status: `[x]`
- Doc: `docs/feature/fix/03-fix-credit-note-blueprint-structure.md`
- Key checks:
  - [x] Stage structure confirmed (`Draft`, `Pending Approval`, `Rejected`, `Approved`, `Open`, `Closed`)
  - [x] Utilization transition criteria corrected (LHDN fields removed from `Converted_to_Open`)
  - [x] `Approved -> Closed` path added (`Approved_to_Closed`)
  - [x] `Revert_to_Pending_Approva` auto-revert disabled (`ID == 0`)
  - [x] Blueprint export synced locally + `XMT___Billing_System.ds`
- Completed by / date: `2026-06-23`
- Notes: `Apply blueprint changes in live Creator blueprint editor, then re-export.`

### 04 - Status Engine Hardening

- Status: `[x]`
- Doc: `docs/feature/fix/04-fix-credit-note-status-engine-hardening.md`
- Key checks:
  - [x] No Open/Closed updates on Draft/Pending/Rejected
  - [x] Stage changes use `changeStage(...)` where needed
  - [x] Manual add/reopen stays Draft before approval
  - [x] Removed unguarded Open/Closed from `Handle_Submission_Form_an4` on save
- Completed by / date: `2026-06-23`
- Notes: `Apply/refund Status writes deferred to Step 06.`

### 05 - Convert Path

- Status: `[x]`
- Doc: `docs/feature/fix/05-fix-credit-note-convert-path.md`
- Key checks:
  - [x] Convert sets `Reference_Invoice` correctly
  - [x] CN number generated once only (removed from convert insert)
  - [x] Convert output explicitly `changeStage` → Draft
  - [x] `Paid` stage condition case corrected on All_Invoices
- Completed by / date: `2026-06-23`
- Notes: `CN number assigned in Handle_Invoice_Creation1 on add success.`

### 06 - Apply/Refund Guards

- Status: `[x]`
- Doc: `docs/feature/fix/06-fix-credit-note-apply-refund-guards.md`
- Key checks:
  - [x] Apply/Refund actions hidden before approval
  - [x] Apply flow prefers `Reference_Invoice` when valid
  - [x] Draft-stage destructive credit row delete blocked
  - [x] Open/Closed transitions consistent after utilization
- Completed by / date: `2026-06-23`
- Notes: `Subform guard uses field rule hide delete row (not cancel delete). Refund picker stage filter deferred.`

### 07 - LHDN Reference Payload

- Status: `[x]`
- Doc: `docs/feature/fix/07-fix-credit-note-lhdn-reference.md`
- Key checks:
  - [x] LHDN action visible only when Closed
  - [x] `reference_invoice_list` includes `Reference_Invoice` when present
  - [x] Deduplication of references validated
  - [x] Convert+refund-only case verified (logic)
- Completed by / date: `2026-06-23`
- Notes: `Manual LHDN payload test in Step 08 matrix (T11, T14, T15).`

### 08 - Testing + Rollout

- Status: `[x]` (package ready; UAT pending)
- Doc: `docs/feature/fix/08-fix-credit-note-test-and-rollout.md`
- Key checks:
  - [x] End-to-end test matrix documented (T1–T15)
  - [x] Regression checks documented (R1–R5)
  - [x] Rollback package + deploy manifest prepared
  - [x] Local export sync verified against `XMT___Billing_System.ds`
  - [ ] Runtime UAT passed in Creator
  - [ ] Final post-UAT export synced
- Completed by / date: `2026-06-23` (docs); UAT `TBD`
- Notes: `All code changes complete Steps 01–07. Run batches A→C in Creator, then UAT.`

### 09 - Mandatory Reference Invoice

- Status: `[x]`
- Doc: `docs/feature/fix credit note/09-fix-credit-note-mandatory-reference.md`
- Key checks:
  - [x] `Reference_Invoice` required on `Credit_Note` form (`must have`)
  - [x] Field moved to Invoice Info section (row 4, after Invoice Date)
  - [x] Save-time UUID guard in `Handle_Validation_Submiss2` (`on validate`)
  - [x] Field-selection validator unchanged (`Handle_reference_invoice_2`)
  - [ ] Convert pre-guard skipped (record action `alert` limitation; mitigated by invoice stage)
  - [ ] Alert message tweak in `Handle_reference_invoice_2` skipped (existing message sufficient)
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Validation lives in Handle_Validation_Submiss2 (not Handle_Submission_Form_an4 — single event per workflow). Manual creation blocked without LHDN-validated reference.`

### 10 - Clone Invoice Lines (Reduce-Only)

- Status: `[x]`
- Doc: `docs/feature/fix credit note/10-fix-credit-note-clone-invoice-lines.md`
- Key checks:
  - [x] Line clone on `Reference_Invoice` selection (`Handle_reference_invoice_2`)
  - [x] Reduce-only save guard (`Handle_Validation_Submiss2`)
  - [x] Item identity fields read-only (`Disable_Fields20`)
  - [x] Block add row on line subforms (`Disable_Addition_And_Dele3`)
  - [x] Convert path verified — copies all line fields (`Convert_To_Credit_Note`)
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Clone uses clear + insert pattern (Refund Note load workflow). Re-clone guarded to Draft/Rejected/new only.`

### 11 - Credit_Mode Field (Mode A / Mode B at Creation)

- Status: `[x]`
- Doc: `docs/feature/fix credit note/11-fix-credit-note-credit-mode-field.md`
- Key checks:
  - [x] `Credit_Mode` field on `Credit_Note` form
  - [x] Mode detection on manual reference selection (`Handle_reference_invoice_2`)
  - [x] Mode set on convert (`Convert_To_Credit_Note`)
  - [x] Save guard for missing mode on Draft/new (`Handle_Validation_Submiss2`)
  - [x] Field disabled in UI (`Disable_Fields20`)
  - [x] `Credit_Mode` column in `Credit_Notes` and `Credit_Note_Report`
  - [x] UAT T11-1 to T11-7 passed
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Mode locked at creation from reference invoice blueprint stage. Field hidden from form UX (report column for finance). Steps 13–14 consume Credit_Mode.`

### 12 - Cumulative Approved CN Cap (Save + Approval)

- Status: `[x]`
- Doc: `docs/feature/fix credit note/12-fix-credit-note-cumulative-cap.md`
- Key checks:
  - [x] Save-time cap in `Handle_Validation_Submiss2` (`on validate`, after per-line reduce-only checks)
  - [x] Approval-time recheck in `Approve/after/unconditional/script_01.deluge` (before LHDN validation)
  - [x] Only **Approved** CNs count toward cap at save (Draft/Pending not reserved — V1)
  - [x] Approval breach reverts to **Pending Approval** via `changeStage`
  - [x] Save guard covers new record (`input.ID == null`), Draft, Rejected, and Pending Approval
  - [x] `cn_grand_total` summed from line totals at validate (not stale `input.Grand_Total`)
  - [x] UAT T12-1 to T12-6 passed (save block, approval race, cap messages)
  - [x] Post-deploy re-export to `XMT___Billing_System.ds`
- Completed by / date: `2026-06-25`
- Notes: `Save validation lives in Handle_Validation_Submiss2 (not Handle_Submission_Form_an4). UAT found stage null on add skipped cap — fixed. changeStage uses stage name 3rd arg, record ID 4th (not transition link name).`

---

## Issue Closure Mapping (`creditNote_wrong.md`)


| Area                | Items                 | Status                               |
| ------------------- | --------------------- | ------------------------------------ |
| Convert path        | #1–10                 | Code complete (Steps 02, 04, 05, 06) |
| Manual path         | #11                   | Code complete (Step 04)              |
| Status/approval     | #14, #16–17, #21      | Code complete (Steps 03, 04, 06)     |
| LHDN                | #23–25                | Code complete (Step 07)              |
| Aligned (no change) | #12, #18–20, #22, #26 | N/A                                  |


---

## Change Log

- `2026-06-25` - Step 12 complete: cumulative cap at save (`Handle_Validation_Submiss2`) + approval recheck (`script_01`); UAT T12-1 to T12-6 passed; fixes for null stage on add and `changeStage` arg order
- `2026-06-25` - Step 10 complete: clone invoice lines on reference selection, reduce-only validation, line subform add-row blocked, item identity fields locked
- `2026-06-24` - Phase 2 planning complete: Steps 09–15 written; index and tracker updated
- `2026-06-23` - Step 08 package: test matrix T1–T15, regression R1–R5, deploy manifest, sync verification, issue closure table
- `2026-06-23` - Step 07 complete: LHDN reference_invoice_list includes Reference_Invoice; Submit button Closed-only
- `2026-06-23` - Step 06 complete: apply/refund guards, Reference_Invoice default, field-rule delete hide, guarded Open/Closed
- `2026-06-23` - Step 05 complete: convert sets Reference_Invoice, single numbering, Draft stage, Paid condition fix
- `2026-06-23` - Step 04 complete: stage-guarded Open/Closed, Draft on create, submission workflow cleaned
- `2026-06-23` - Step 03 complete: blueprint utilization transitions fixed, `Approved_to_Closed` added
- `2026-06-23` - Step 02 complete: `Reference_Invoice` field, reports, validator workflow, `.ds` sync
- `2026-06-23` - Step 01 preflight complete; rollback snapshot and deploy batches documented
- `YYYY-MM-DD HH:mm` - Tracker created

