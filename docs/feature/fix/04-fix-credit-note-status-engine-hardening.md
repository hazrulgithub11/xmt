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
