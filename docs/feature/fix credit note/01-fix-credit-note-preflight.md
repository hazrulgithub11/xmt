# 01 - Fix Credit Note Preflight

## Objective
Prepare safely before any billing logic change. This step is mandatory to avoid breaking live behavior or creating export drift.

## Source of truth
- Local export files under `application/...`
- Full export snapshot in `XMT___Billing_System.ds`
- Use `docs/feature/creditNote_wrong.md` as issue list
- Use `docs/feature/creditNote_Flow.md` as target flow

## Step-by-step
1. Confirm all target artifacts exist in both local files and `XMT___Billing_System.ds`:
   - `application/forms/Credit Note/...`
   - `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge`
   - `application/forms/Apply Credit To Invoices/...`
   - `application/forms/Refund Note/...`
   - `application/blueprints/Credit_Note_Blueprint/...`
2. If any target artifact is missing in local export but exists in live Creator, stop and export from live first.
3. Create a rollback note with current transition/stage and action conditions before edits.
4. Group implementation into small deploy batches:
   - Batch A: field + blueprint scaffolding
   - Batch B: status logic and convert path
   - Batch C: apply/refund + LHDN payload
5. Define success criteria for each batch before coding.

## Zoho safety rules for this project
- Do not delete a field/transition/action before removing all references to it.
- For blueprint behavior, prefer `thisapp.blueprint.changeStage(...)` over writing stage/status text directly.
- Keep business logic edits minimal and scoped to approved behavior only.

## Exit criteria
- All required artifacts verified present.
- Batches and rollback points documented.
- Ready to execute Step 02.

---

## Preflight results (2026-06-23)

### 1. Artifact verification

| Area | Local | `XMT___Billing_System.ds` | Notes |
|---|---|---|---|
| `application/forms/Credit Note/` | 48 files | `form Credit_Note` present | No `Reference_Invoice` field yet (expected — Step 02) |
| `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge` | Yes | Yes | |
| `application/forms/Apply Credit To Invoices/` | 12 files | `form Apply_Credit_To_Invoices` present | |
| `application/forms/Refund Note/` | 43 files | `form Refund_Note` present | |
| `application/blueprints/Credit_Note_Blueprint/` | 12 files | `Credit_Note_Blueprint` present | Local extract includes `Approve/after/unconditional/script_01.deluge` |

**Sync drift to watch (non-blocking for preflight):**
- `Credit_Notes.deluge` locally uses `Status == "Approved"` for action conditions; `.ds` uses `Blueprint.Current_Stage == "Approved"`. Reconcile on next live export.
- `All_Invoices.deluge` convert condition uses lowercase `"paid"` in one branch; other invoice reports use `"Paid"`.

**Missing from live (expected):** `Reference_Invoice` on Credit Note — created in Step 02.

### 2. Rollback snapshot (before any edits)

#### Blueprint `Credit_Note_Blueprint`

| Stage | Order |
|---|---|
| Start | `Draft` |
| All | `Draft` → `Pending Approval` → `Rejected` → `Approved` → `Open` → `Closed` |

| Transition | From | To | Criteria / scripts |
|---|---|---|---|
| Send For Approval | Draft | Pending Approval | none |
| Approve | Pending Approval | Approved | After: LHDN taxpayer validation (`script_01`); on failure reverts to Pending Approval via `changeStage` |
| Reject | Pending Approval | Rejected | none |
| Resubmit | Rejected | Pending Approval | none |
| Converted to Open | Approved | Open | **Before:** `Invoice_UUID is not null && QR_Invoice_Public_Link is not null` |
| Converted to Closed | Open | Closed | none |
| Revert to Pending Approval | Approved | Pending Approval | **Before:** `Invoice_UUID is null \|\| QR_Invoice_Public_Link is null` |

**Rollback:** Restore `blueprint.json`, transition folders, and blueprint section in `XMT___Billing_System.ds` from git HEAD.

#### Record action conditions (live `.ds` / report)

| Action | Form | Condition (live `.ds`) |
|---|---|---|
| Convert To Credit Note | Invoice | `Sent \|\| Partially Paid \|\| paid \|\| Overdue` |
| Apply Credits to Invoices | Credit Note | `Approved \|\| Open` |
| Create Refund Note | Credit Note | `Approved \|\| Open` |
| Submit Credit Note to LHDN | Credit Note | `Approved` (script also requires `Closed`) |

#### Status engine (current behavior to restore if rolled back)

- `User_Input_Trigger_Workfl2`: on `User_Input_Trigger`, when `input.ID != null`, recalculates balances then sets `Status` text to `Open` if `Credits_Remaining > 0`, else `Closed` — **no blueprint stage guard**.
- `Handle_Invoice_Creation1`: on add success, generates `Invoice_No` and sets `Status = "Draft"`.
- `Convert_To_Credit_Note`: insert sets `Invoice_No = generate_credit_note_no()` at insert time (double-number risk with `Handle_Invoice_Creation1`); no `Reference_Invoice`; no `changeStage` to Draft.
- LHDN submit: `reference_invoice_list` built only from `Credit_Applied_Invoices` subform.

### 3. Deploy batches

#### Batch A — Field + blueprint scaffolding (Steps 02–03)

| Step | Scope |
|---|---|
| 02 | Add `Reference_Invoice` lookup on `Credit_Note`; layout + validator workflow |
| 03 | Fix utilization transitions (`Converted_to_Open`, `Converted_to_Closed`, `Revert_to_Pending_Approva`); add `Approved → Closed` if needed |

**Success criteria:**
- `Reference_Invoice` exported in `Credit_Note.deluge` and `.ds`; manual CN allows null.
- Blueprint stages unchanged; utilization transitions no longer gated on CN LHDN UUID fields.
- Approval path (`Send_For_Approval`, `Approve`, `Reject`, `Resubmit`) still works.

**Rollback point:** git restore Credit Note form + blueprint folder after Batch A deploy.

#### Batch B — Status logic + convert path (Steps 04–05)

| Step | Scope |
|---|---|
| 04 | Harden `User_Input_Trigger_Workfl2`; keep Draft through approval |
| 05 | Fix `Convert_To_Credit_Note`; single CN numbering; set `Reference_Invoice`; explicit Draft stage |

**Success criteria:**
- Converted and manual CN stay **Draft** until Send For Approval → Approved.
- CN number generated once (on add success only).
- Convert sets `Reference_Invoice = source invoice ID`.
- Convert button visible for `Paid` (case fix).
- Issues #1, #2, #3, #4, #5, #8, #11, #14, #16 resolved.

**Rollback point:** restore Batch B files; `Reference_Invoice` data on new CNs may remain (harmless if unused).

#### Batch C — Apply/refund + LHDN payload (Steps 06–07)

| Step | Scope |
|---|---|
| 06 | Tighten action guards; default apply to `Reference_Invoice`; block Draft credit-row deletes |
| 07 | LHDN `reference_invoice_list` includes `Reference_Invoice`; button hidden unless Closed |

**Success criteria:**
- Apply/Refund hidden before approval; work after Approved.
- Apply flow preselects source invoice when eligible.
- LHDN payload includes convert source UUID even without apply rows.
- Submit button only when Closed.
- Issues #9, #10, #17, #21, #23, #24, #25 resolved.

**Rollback point:** restore action scripts + `Credit_Notes.deluge` conditions.

#### Batch D — Test + rollout (Step 08)

End-to-end matrix per `08-fix-credit-note-test-and-rollout.md`; final export sync.

### 4. Preflight status

- [x] Required artifacts verified (local + `.ds`)
- [x] No missing live artifacts requiring export-first stop
- [x] Rollback snapshot captured
- [x] Batches A–D defined with success criteria
- [x] Ready for Step 02
