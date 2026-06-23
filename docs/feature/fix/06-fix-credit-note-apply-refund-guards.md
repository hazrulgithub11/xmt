# 06 - Fix Apply/Refund Timing and Action Guards

## Objective
Allow credit utilization only after approval and keep balances/stages synchronized safely.

## Primary files
- `application/forms/Credit Note/Credit_Notes.deluge`
- `application/forms/Credit Note/workflow/actions/Apply_Credits_to_Invoices.deluge`
- `application/forms/Credit Note/workflow/actions/Create_Refund_Note_From_C.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Apply_Credit_To_Invoices_.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Handle_Credit_Note_Select.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Handle_Credit_Note_Select1.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Apply_Credit_To_Invoices_1.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Handle_Form_Submission.deluge`
- `application/forms/Refund Note/workflow/Successful_form_submissio1.deluge`
- `application/forms/Credit Note/workflow/Handle_Deletion_of_Credit.deluge`
- `application/forms/Credit Note/workflow/Deletion_of_rows_of_Refun.deluge`

## Step-by-step
1. Tighten custom action visibility on Credit Note report:
   - Apply credit and refund actions must not appear during `Draft` or `Pending Approval`.
2. In apply-credit initialization/selection:
   - Prefer defaulting the source `Reference_Invoice` when available and still eligible.
3. In apply-credit submission:
   - Keep invoice and CN balance recalculation.
   - Use blueprint stage movement for `Open`/`Closed` updates.
4. In refund-note submission callback:
   - Keep CN balance recomputation.
   - Use blueprint stage movement for `Open`/`Closed`.
5. Block risky credit-application row deletion from Draft states.
6. Re-test guardrails:
   - Before approval: no utilization actions.
   - After approval: actions appear and work.

## Zoho safety
If modifying or deleting custom action conditions:
1. Update related workflow assumptions first.
2. Keep action link names stable unless all references are migrated.

## Exit criteria
- Issues #9, #10, #17, #21 are resolved.
- Utilization actions only execute in approved lifecycle states.

---

## Results (2026-06-23)

### 1. Report action guards (`Credit_Notes.deluge`)
- **Apply Credits to Invoices** and **Create Refund Note** conditions: `Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open"`.
- Actions hidden in Draft, Pending Approval, Rejected, and Closed.

### 2. Apply-credit picker (`Apply_Credit_To_Invoices_.deluge`)
- Credit note dropdown limited to `Approved` or `Open` with `Credits_Remaining > 0`.
- Uses live field link name `input.invoice` (not `Credit_Note`).

### 3. Reference invoice default (`Handle_Credit_Note_Select1.deluge`)
- When `Reference_Invoice` is set and appears in the unpaid invoice list, pre-fills `Credits_To_Apply` with `min(Amount_Due, Credits_Remaining)`.

### 4. Apply-credit validation (`Apply_Credit_To_Invoices_1.deluge`)
- Blocks submit if CN stage is not `Approved` or `Open`.
- Counts only rows with `Credits_To_Apply > 0` toward “at least one invoice” check.
- Validates total against `input.invoice.Credits_Remaining`.

### 5. Apply-credit success (`Handle_Form_Submission.deluge`)
- Balance recalculation unchanged.
- `changeStage` to Open/Closed only when CN is `Approved` or `Open` (not Draft/Pending/Rejected).

### 6. Refund success (`Successful_form_submissio1.deluge`)
- Same guarded `changeStage` pattern as apply-credit success.

### 7. Row deletion guards
- `cancel delete` is **not valid** on `on delete row of` subform events (Zoho only allows it on record `on delete` → `on validate`).
- **`Disable_Addition_And_Dele3.deluge`** — field rule hides delete row on `Credit_Applied_Invoices` and `Refund_History` when stage is Draft, Pending Approval, or Rejected.
- `Handle_Deletion_of_Credit.deluge` and `Deletion_of_rows_of_Refun.deluge` — restored to recalculation trigger only (no `cancel delete`).

### Sync
- All changes reflected in `XMT___Billing_System.ds`.

### Deploy to live Creator
1. **Credit Notes report** — verify Apply/Refund action conditions use `Blueprint.Current_Stage`.
2. **Apply Credit To Invoices** workflows: Initialization, Validation, Handle Credit Note Selection, Handle_Credit_Note_Selection_Trigger, Handle Form Submission.
3. **Refund Note** workflow: Successful form submission of Refund Note.
4. **Credit Note** workflows: Handle Deletion of Credit Applied Invoices, Deletion of rows of Refund History.
5. **Credit Note** field rule workflow: Disable Addition And Deletion Row — add conditional hide delete row for pre-approval stages.

### Known follow-up (not in scope for 06)
- Refund Note manual create (`Handle_Customer_Name_Chan4`) still filters CN picker by `Credits_Remaining > 0` only — not by blueprint stage. Primary path is gated via report action; tighten picker if manual refund entry is used.
