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

- [x] 01 - Preflight complete (`01-fix-credit-note-preflight.md`)
- [x] 02 - `Reference_Invoice` field added + exported (`02-fix-credit-note-reference-invoice-field.md`)
- [x] 03 - Credit Note blueprint structure aligned (`03-fix-credit-note-blueprint-structure.md`)
- [x] 04 - Status engine hardened (no early Open/Closed) (`04-fix-credit-note-status-engine-hardening.md`)
- [x] 05 - Convert path fixed (`05-fix-credit-note-convert-path.md`)
- [x] 06 - Apply/Refund guards fixed (`06-fix-credit-note-apply-refund-guards.md`)
- [x] 07 - LHDN reference payload fixed (`07-fix-credit-note-lhdn-reference.md`)
- [ ] 08 - Test matrix passed + rollout complete (`08-fix-credit-note-test-and-rollout.md`)

---

## Current Sprint Snapshot

- Current step: `08 - Testing + rollout`
- Owner: `TBD`
- Started at: `2026-06-23`
- Target finish: `TBD`
- Current risk/blocker: `None`

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
- Notes: `Refund picker stage filter deferred; report actions gated. Workflow file: Successful_form_submissio1 (not an5).`

### 07 - LHDN Reference Payload
- Status: `[x]`
- Doc: `docs/feature/fix/07-fix-credit-note-lhdn-reference.md`
- Key checks:
  - [x] LHDN action visible only when Closed
  - [x] `reference_invoice_list` includes `Reference_Invoice` when present
  - [x] Deduplication of references validated
  - [x] Convert+refund-only case verified (logic)
- Completed by / date: `2026-06-23`
- Notes: `Manual LHDN payload test deferred to Step 08.`

### 08 - Testing + Rollout
- Status: `[ ]`
- Doc: `docs/feature/fix/08-fix-credit-note-test-and-rollout.md`
- Key checks:
  - [ ] End-to-end test matrix passed
  - [ ] Regression checks passed
  - [ ] Rollback package prepared
  - [ ] Final export sync completed
- Completed by / date: `TBD`
- Notes: ``

---

## Issue Closure Mapping (`creditNote_wrong.md`)

- Convert path: #1-10 -> Steps 02, 04, 05, 06
- Manual path: #11 -> Step 04
- Status/approval: #14, #16-17, #21 -> Steps 03, 04, 06
- LHDN: #23-25 -> Step 07
- Already aligned/no change expected: #12, #18-20, #22, #26

---

## Change Log

- `2026-06-23` - Step 07 complete: LHDN reference_invoice_list includes Reference_Invoice; Submit button Closed-only
- `2026-06-23` - Step 06 complete: apply/refund guards, Reference_Invoice default, deletion blocks, guarded Open/Closed
- `2026-06-23` - Step 05 complete: convert sets Reference_Invoice, single numbering, Draft stage, Paid condition fix
- `2026-06-23` - Step 04 complete: stage-guarded Open/Closed, Draft on create, submission workflow cleaned
- `2026-06-23` - Step 03 complete: blueprint utilization transitions fixed, `Approved_to_Closed` added
- `2026-06-23` - Step 02 complete: `Reference_Invoice` field, reports, validator workflow, `.ds` sync
- `2026-06-23` - Step 01 preflight complete; rollback snapshot and deploy batches documented
- `YYYY-MM-DD HH:mm` - Tracker created
