# 04 - Harden Credit Note Status Engine (No Early Open/Closed)

## Objective
Prevent credit notes from becoming `Open`/`Closed` before approval, especially on form load/edit.

## Primary files
- `application/forms/Credit Note/workflow/User_Input_Trigger_Workfl2.deluge`
- `application/forms/Credit Note/workflow/Load_of_the_form_Initiali1.deluge`
- `application/forms/Credit Note/workflow/Handle_Invoice_Creation1.deluge`

## Step-by-step
1. In `User_Input_Trigger_Workfl2.deluge`:
   - Keep balance calculations (`Refund`, `Credits_Used`, `Credits_Remaining`).
   - Add guard by current blueprint stage.
   - Do not set `Open`/`Closed` when stage is `Draft`, `Pending Approval`, or `Rejected`.
2. Replace direct status writes with blueprint transition calls when stage changes are needed:
   - Use `thisapp.blueprint.changeStage("Credit_Note","Credit_Note_Blueprint",...)`.
3. In `Load_of_the_form_Initiali1.deluge`:
   - Keep initialization behavior.
   - Ensure initialization trigger does not implicitly force status conversion.
4. In `Handle_Invoice_Creation1.deluge`:
   - Keep single CN number generation.
   - Ensure post-create state remains explicitly `Draft` in blueprint terms.
5. Validate manual path behavior:
   - Add credit note
   - Save
   - Reopen
   - Must still be `Draft` until approval.

## Anti-regression checks
- Send for approval still works.
- Approve/Reject/Resubmit behavior remains intact.
- No status drift on plain edit/load.

## Exit criteria
- Issues #1, #11, #14, #16 are resolved.
- Open/Closed can only occur after approval and utilization events.

---

## Step 04 results (2026-06-23)

### Changes made

| File | Change |
|---|---|
| `User_Input_Trigger_Workfl2.deluge` | Balance calculations only — **no** `changeStage` (Zoho allows blueprint tasks only in `on success` / `on update`, not `on user input`) |
| `Handle_Invoice_Creation1.deluge` | After CN number generation, explicit `changeStage(..., "Draft", ...)` on `on success` |
| `Handle_Submission_Form_an4.deluge` | On `on success`, guarded `changeStage` to Open/Closed only when stage is `Approved` or `Open` |
| `Load_of_the_form_Initiali1.deluge` | No change — initialization only toggles triggers; no stage writes |

### Stage movement rules (after this step)

| Current stage | Credits_Remaining | Action |
|---|---|---|
| Draft / Pending Approval / Rejected | any | No stage change |
| Approved / Open | > 0 | → Open (if not already) |
| Approved / Open | = 0 | → Closed (if not already) |

### Deploy to live Creator

1. **User_Input_Trigger_Workfl2** — balance calculations only; remove any `changeStage` or `Status = "Open"/"Closed"` (not allowed on `on user input`).
2. **Handle_Invoice_Creation1** — add `changeStage` to Draft after number generation (`on success`).
3. **Handle_Submission_Form_an4** — add stage-guarded `changeStage` on `on success` (before redirect).
4. Re-export and sync `.ds`.

### Deferred to Step 06

Apply-credit and refund-note submission workflows still use direct `Status` writes — will be migrated to `changeStage` in Step 06.
