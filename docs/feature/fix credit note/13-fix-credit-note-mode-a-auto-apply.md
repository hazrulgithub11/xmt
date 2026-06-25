# 13 - Mode A: Auto-Apply on Approval and Block Apply/Refund Actions

## Context
When a CN is in **Mode A** (reference invoice was Sent or Overdue at creation), the credit note's sole purpose is to reduce the debt on that specific unpaid invoice. No other usage is permitted.

After approval:
1. System automatically applies the full CN amount to the same reference invoice
2. Invoice `Amount_Due` is reduced immediately
3. CN `Credits_Remaining` is set to 0
4. CN is moved to **Closed** via `changeStage`
5. Apply Credits and Create Refund Note actions must be **hidden** for Mode A CNs

## Objective
Wire the Approve blueprint transition to trigger auto-apply for Mode A CNs, and hide utilization actions on Mode A CNs at all times.

## Primary files
- `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/script_01.deluge` — already runs post-approve; add Mode A auto-apply here
- `application/forms/Credit Note/Credit_Notes.deluge` — action visibility conditions
- `application/forms/Apply Credit To Invoices/workflow/` — no change needed; Mode A CNs never reach this form

## Dependency
Steps 11 (Credit_Mode field), 12 (cumulative cap), and 03 (Approved → Closed transition exists) must all be deployed first.

---

## Step-by-step

### 1. Add Mode A auto-apply in the Approve after-script

`Approve/after/script_01.deluge` currently runs LHDN taxpayer validation. Add Mode A processing **after** taxpayer validation passes and the Approved stage is confirmed:

```deluge
// === After cap check (Step 12) and taxpayer validation pass ===
// === Mode A auto-apply ===

if(input.Credit_Mode == "Mode A - Debt Reduction")
{
    ref_invoice_id = input.Reference_Invoice;
    ref_invoice = Invoice[ID == ref_invoice_id];
    cn_amount = input.Grand_Total;

    // Safety: only apply if reference invoice still has Amount_Due > 0
    if(ref_invoice.Amount_Due > 0)
    {
        apply_amount = min(cn_amount, ref_invoice.Amount_Due);

        // Create Apply_Credit_To_Invoice_Line record
        new_apply_row = Apply_Credit_To_Invoice_Line();
        new_apply_row.Credit_Note = input.ID;
        new_apply_row.CAI_Invoice_No = ref_invoice_id;
        new_apply_row.Credits_Applied = apply_amount;
        insert into Apply_Credit_To_Invoice_Line values new_apply_row;

        // Update invoice balances
        new_credits_applied_total = ref_invoice.Credits_Applied_Total + apply_amount;
        new_amount_due = ref_invoice.Grand_Total - ref_invoice.Total_Amount_Paid - new_credits_applied_total;
        if(new_amount_due < 0) { new_amount_due = 0; }

        Invoice[ID == ref_invoice_id].Credits_Applied_Total = new_credits_applied_total;
        Invoice[ID == ref_invoice_id].Amount_Due = new_amount_due;

        // Update CN balances
        input.Credits_Used = apply_amount;
        input.Credits_Remaining = 0;
        input.Credit_Note_ID.Credits_Used = apply_amount;  // direct field update
        Credit_Note[ID == input.ID].Credits_Used = apply_amount;
        Credit_Note[ID == input.ID].Credits_Remaining = 0;
    }
    else
    {
        // Reference invoice Amount_Due = 0 (paid between creation and approval)
        // Mode A still closes with Credits_Remaining = 0, no apply row created
        Credit_Note[ID == input.ID].Credits_Used = 0;
        Credit_Note[ID == input.ID].Credits_Remaining = 0;
    }

    // Move CN to Closed
    thisapp.blueprint.changeStage("Credit_Note", "Credit_Note_Blueprint", input.ID.toLong(), "Approved_to_Closed");
    info "Mode A auto-apply complete. CN " + input.ID + " closed.";
}
// Mode B: do nothing here — stays Approved (Step 04 will move to Open via Handle_Submission_Form_an4)
```

**Field names to verify:** `Apply_Credit_To_Invoice_Line` subform field names (`CAI_Invoice_No`, `Credits_Applied`) — confirm against `Apply_Credit_To_Invoices` form definition.
**Transition name:** `Approved_to_Closed` was added in Step 03.

### 2. Invoice balance update — align with existing apply-credit logic

The existing `Handle_Form_Submission.deluge` (Apply Credit To Invoices form) recalculates invoice balances. The formula above must match. Confirm `Amount_Due = Grand_Total − Total_Amount_Paid − Credits_Applied_Total` against `Handle_Form_Submission.deluge` and use the same formula.

If the formula differs, use the same formula as `Handle_Form_Submission.deluge` to ensure consistency.

### 3. Hide Apply Credits and Create Refund Note for Mode A CNs

In `Credit_Notes.deluge`, update the action conditions for both record actions:

**Before (Step 06):**
```
Apply Credits to Invoices: Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open"
Create Refund Note: Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open"
```

**After (Step 13):**
```
Apply Credits to Invoices:
  (Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open")
  && Credit_Mode == "Mode B - Open Credit"

Create Refund Note:
  (Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open")
  && Credit_Mode == "Mode B - Open Credit"
```

This means Mode A CNs — which go straight from Approved to Closed automatically — never show these actions. Mode B CNs continue to show them per Step 06 rules.

### 4. Legacy guard: CNs with null Credit_Mode

For existing CNs (created before Step 11 deployed), `Credit_Mode` will be null. These CNs should behave as Mode B (the old flow's behavior). Update conditions:

```
Apply Credits to Invoices:
  (Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open")
  && (Credit_Mode == "Mode B - Open Credit" || Credit_Mode == null)

Create Refund Note:
  (Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open")
  && (Credit_Mode == "Mode B - Open Credit" || Credit_Mode == null)
```

### 5. Verify Mode A CN cannot be reopened after Closed

Mode A CNs reach Closed via `Approved_to_Closed` directly. Confirm there is no "reopen" transition from Closed. If one exists, add a condition that prevents reopen for Mode A CNs.

### 6. Audit log entry (optional but recommended)

After auto-apply, log an entry in `Invoice_Related_List` or an activity log on the invoice:

```deluge
log_row = Invoice.Invoice_Related_List();
log_row.INVOICE_NUMBER = input.Invoice_No;
log_row.USERNAME = zoho.loginuser;
log_row.MESSAGE = "Credit note " + input.Invoice_No + " auto-applied (Mode A). Amount: " + apply_amount;
log_row.Related_List_Date = zoho.currenttime.toDate();
Invoice[ID == ref_invoice_id].Invoice_Related_List.insert(log_row);
```

---

## Zoho safety

- `changeStage` to `Approved_to_Closed` is called within the Approve after-script. This is valid — `on success` / blueprint after-script allows `changeStage`.
- If the `changeStage` fails (transition not available), Mode A CN will stay at Approved. Add `info` logging so this failure is visible in Creator logs.
- The auto-apply insert into `Apply_Credit_To_Invoice_Line` must follow the same field structure as the existing apply-credit form creates, or balance queries will be inconsistent.

## Exit criteria

- [ ] Mode A CN approved → `Apply_Credit_To_Invoice_Line` record created linking CN to reference invoice
- [ ] Reference invoice `Amount_Due` reduced by CN amount after approval
- [ ] Mode A CN `Credits_Used = Grand_Total`, `Credits_Remaining = 0` after approval
- [ ] Mode A CN blueprint = **Closed** after approval (not Approved, not Open)
- [ ] **Apply Credits to Invoices** action hidden for Mode A CN
- [ ] **Create Refund Note** action hidden for Mode A CN
- [ ] Mode A CN with paid reference invoice (Amount_Due = 0): closes with Credits_Remaining = 0, no apply row, no error
- [ ] Mode B CN approved → NOT auto-applied; stays Approved/Open; Apply and Refund actions visible
- [ ] Legacy CNs (null Credit_Mode) → Apply and Refund actions still visible (treated as Mode B)
- [ ] `Approve/after/script_01.deluge` and `Credit_Notes.deluge` synced to `XMT___Billing_System.ds`
