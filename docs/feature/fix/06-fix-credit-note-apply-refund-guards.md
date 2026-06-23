# 06 - Fix Apply/Refund Timing and Action Guards

## Objective
Allow credit utilization only after approval and keep balances/stages synchronized safely.

## Primary files
- `application/forms/Credit Note/Credit_Notes.deluge`
- `application/forms/Credit Note/workflow/actions/Apply_Credits_to_Invoices.deluge`
- `application/forms/Credit Note/workflow/actions/Create_Refund_Note_From_C.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Handle_Credit_Note_Select1.deluge`
- `application/forms/Apply Credit To Invoices/workflow/Handle_Form_Submission.deluge`
- `application/forms/Refund Note/workflow/Handle_Submission_Form_an5.deluge`
- `application/forms/Credit Note/workflow/Handle_Deletion_of_Credit.deluge`

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
