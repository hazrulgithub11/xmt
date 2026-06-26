# Step A — Core Fix: Unified Rule

Part of: [Unified Credit Note Rule](00-overview.md)

Deploy and verify this step **before** Step B.

## Files changed in this step

1. `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge`
2. `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge`
3. `application/Custom Functions/credit_note/prefill_from_reference_invoice`
4. `application/forms/Credit Note/Credit_Notes.deluge`
5. `XMT___Billing_System.ds` (mirror all above)

---

## Change 1 — `script_01.deluge`

**Verify file exists in `XMT___Billing_System.ds` before editing.** ✓ (confirmed present)

### Remove

The entire Mode A block including the drift guard — **lines 248–340**:

```deluge
// Mode A auto-apply: debt reduction on reference invoice, then close CN
if(input.Credit_Mode == "Mode A - Debt Reduction")
{
    // ... drift guard (lines 255–263) ...
    // ... apply logic (~80 lines) ...
    input_credit_note.Credits_Remaining=0;             // <- the silent discard
    thisapp.blueprint.changeStage("Credit_Note","Credit_Note_Blueprint","Closed",input.ID);
    info "Mode A auto-apply complete. CN " + input.ID + " closed. Applied: " + apply_amount;
}
```

### Replace with

```deluge
// Unified auto-apply: apply min(CN, Amount_Due) to reference invoice on approval.
// Credits_Remaining = CN amount - applied amount.
// CN → Closed if Credits_Remaining = 0, → Open if Credits_Remaining > 0.
if(input.Reference_Invoice != null)
{
	ref_invoice_id = input.Reference_Invoice;
	ref_invoice = Invoice[ID == ref_invoice_id];
	cn_amount = input.Grand_Total;
	apply_amount = 0;
	if(ifnull(ref_invoice.Amount_Due,0) > 0)
	{
		apply_amount = cn_amount;
		if(apply_amount > ref_invoice.Amount_Due)
		{
			apply_amount = ref_invoice.Amount_Due;
		}
		insert into Apply_Credit_To_Invoice_Line
		[
			Invoice=ref_invoice_id
			Credit_Note=input.ID
			Amount_Applied_Date=today
			Amount_Applied=apply_amount
			Added_User=zoho.loginuser
		]
		curr_input_invoice = Invoice[ID == ref_invoice_id];
		curr_input_invoice.Credits_Applied=null;
		curr_apply_credit_to_invoice_line_list = Apply_Credit_To_Invoice_Line[Invoice == ref_invoice_id];
		curr_credits_applied_total = 0;
		for each  curr_apply_credit_to_invoice_line in curr_apply_credit_to_invoice_line_list
		{
			curr_new_credits_applied_row = Invoice.Credits_Applied();
			curr_new_credits_applied_row.CA_Apply_Credit_To_Invoice_Line_ID=curr_apply_credit_to_invoice_line.ID;
			curr_new_credits_applied_row.CA_Date=curr_apply_credit_to_invoice_line.Amount_Applied_Date;
			curr_new_credits_applied_row.CA_Credit_Note=curr_apply_credit_to_invoice_line.Credit_Note;
			curr_new_credits_applied_row.CA_Total=curr_apply_credit_to_invoice_line.Amount_Applied;
			curr_credits_applied_total = curr_credits_applied_total + curr_apply_credit_to_invoice_line.Amount_Applied;
			curr_input_invoice.Credits_Applied.insert(curr_new_credits_applied_row);
		}
		curr_input_invoice.Credits_Applied_Total=curr_credits_applied_total;
		curr_input_invoice.Amount_Due=curr_input_invoice.Grand_Total - curr_input_invoice.Amount_Paid - curr_credits_applied_total;
		if(ifnull(curr_input_invoice.Amount_Due,0) <= 0)
		{
			thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint","Paid",curr_input_invoice.ID);
		}
		else if(ifnull(curr_input_invoice.Amount_Paid,0) > 0 || ifnull(curr_credits_applied_total,0) > 0)
		{
			thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint","Partially Paid",curr_input_invoice.ID);
		}
		else if(curr_input_invoice.Due_Date > zoho.currentdate)
		{
			thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint","Sent",curr_input_invoice.ID);
		}
		else
		{
			thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint","Overdue",curr_input_invoice.ID);
		}
		thisapp.invoice.calculate_invoice_previous_balance_and_total_amount_due(curr_input_invoice.ID);
		thisapp.tenancy.calculate_opening_balance_by_tenancy(curr_input_invoice.Customer_Code);
		current_date_time = zoho.currenttime;
		log_row = Invoice.Invoice_Related_List();
		log_row.USERNAME=zoho.loginuser;
		log_row.INVOICE_NUMBER=ref_invoice.Invoice_No;
		log_row.Related_List_Date=current_date_time.toDate();
		log_row.Related_List_Time=current_date_time.toTime();
		log_row.MESSAGE="Credit note " + input.Invoice_No + " auto-applied. Amount: " + apply_amount;
		curr_input_invoice.Invoice_Related_List.insert(log_row);
	}
	input_credit_note = Credit_Note[ID == input.ID];
	input_credit_note.Credit_Applied_Invoices=null;
	apply_credit_to_invoice_line_list = Apply_Credit_To_Invoice_Line[Credit_Note == input.ID];
	credits_used_total = 0;
	for each  curr_apply_credit_to_invoice_line in apply_credit_to_invoice_line_list
	{
		curr_new_credit_applied_invoices_row = Credit_Note.Credit_Applied_Invoices();
		curr_new_credit_applied_invoices_row.CAI_Apply_Credit_To_Invoice_Line_ID=curr_apply_credit_to_invoice_line.ID;
		curr_new_credit_applied_invoices_row.CAI_Date=curr_apply_credit_to_invoice_line.Amount_Applied_Date;
		curr_new_credit_applied_invoices_row.CAI_Invoice_No=curr_apply_credit_to_invoice_line.Invoice;
		curr_new_credit_applied_invoices_row.CAI_Amount_Credited=curr_apply_credit_to_invoice_line.Amount_Applied;
		credits_used_total = credits_used_total + curr_apply_credit_to_invoice_line.Amount_Applied;
		input_credit_note.Credit_Applied_Invoices.insert(curr_new_credit_applied_invoices_row);
	}
	input_credit_note.Credits_Used=credits_used_total;
	credits_remaining = cn_amount - credits_used_total;
	input_credit_note.Credits_Remaining=credits_remaining;
	if(credits_remaining <= 0)
	{
		thisapp.blueprint.changeStage("Credit_Note","Credit_Note_Blueprint","Closed",input.ID);
		info "Unified auto-apply complete. CN " + input.ID + " closed. Applied: " + apply_amount;
	}
	else
	{
		thisapp.blueprint.changeStage("Credit_Note","Credit_Note_Blueprint","Open",input.ID);
		info "Unified auto-apply complete. CN " + input.ID + " open. Applied: " + apply_amount + ", Remaining: " + credits_remaining;
	}
}
```

### Key differences from old Mode A code


| Old                                                       | New                                                        |
| --------------------------------------------------------- | ---------------------------------------------------------- |
| Only runs when `Credit_Mode == "Mode A - Debt Reduction"` | Runs for ALL CNs with a Reference_Invoice                  |
| `Credits_Remaining = 0` hardcoded                         | `Credits_Remaining = CN - applied` (correct)               |
| Drift guard blocks approval when CN > Amount_Due          | No guard — applies min(), excess becomes Credits_Remaining |
| Always closes CN                                          | Closes only if Credits_Remaining = 0; otherwise opens      |


---

## Change 2 — `Handle_Validation_Submiss2.deluge`

**Remove lines 34–46** — the Credit_Mode null check that blocks save if mode cannot be determined:

```deluge
// REMOVE THIS ENTIRE BLOCK (lines 34–46):
if(input.Credit_Mode == null || input.Credit_Mode == "")
{
    recovered_mode = thisapp.credit_note.credit_mode_from_invoice_stage(input.Reference_Invoice);
    if(recovered_mode != "")
    {
        input.Credit_Mode = recovered_mode;
    }
    else
    {
        alert "Credit Mode could not be determined. Please re-select the Reference Invoice.";
        cancel submit;
    }
}
```

The outer `if(input.ID == null || cn_stage == "Draft" || cn_stage == "Rejected")` block on line 32 stays — it wraps other validations that are still needed. Only the Credit_Mode sub-block inside is removed.

**After removal, line 32 block goes directly to line 48** (`// Count Total Line Items`).

---

## Change 3 — `prefill_from_reference_invoice`

**Lines 13–15**: Replace Credit_Mode-based eligibility with a direct stage check.

**Before:**

```deluge
credit_mode = thisapp.credit_note.credit_mode_from_invoice_stage(invoice_id);
result.put("credit_mode",credit_mode);
result.put("credit_eligible",credit_mode != "");
```

**After:**

```deluge
eligible_stages = {"Sent","Overdue","Partially Paid","Paid"};
result.put("credit_eligible",eligible_stages.contains(ref_stage));
```

The `credit_mode` key is removed from the result map. Any caller reading `prefill_data.get("credit_mode")` will get null — which is handled in Step B. In Step A the callers still call `get("credit_mode")` but only to set `input.Credit_Mode`, which is a benign null write. No logic breaks.

---

## Change 4 — `Credit_Notes.deluge`

**Apply Credits to Invoices** action condition — line 91:

```
// Before:
condition = (Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open") && (Credit_Mode == "Mode B - Open Credit" || Credit_Mode == null)

// After:
condition = Blueprint.Current_Stage == "Open"
```

**Create Refund Note** action condition — line 111:

```
// Before:
condition = (Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Open") && (Credit_Mode == "Mode B - Open Credit" || Credit_Mode == null)

// After:
condition = Blueprint.Current_Stage == "Open"
```

**Why remove `Approved` from the condition:** With the unified rule, the Approve after-script calls `changeStage` directly to Open or Closed. A CN should never remain in Approved for more than an instant. Showing Apply/Refund for Approved CNs was only needed because Mode B CNs could be stuck at Approved — that problem is now fixed by the unified script.

**Submit Credit Note to LHDN** condition — line 98: unchanged (`Blueprint.Current_Stage == "Closed"`).

---

## Zoho safety notes

- `changeStage("Credit_Note","Credit_Note_Blueprint","Closed",input.ID)` — uses stage name "Closed". The available transition from Approved is `Approved_to_Closed`. Verify in sandbox that this resolves correctly.
- `changeStage("Credit_Note","Credit_Note_Blueprint","Open",input.ID)` — uses stage name "Open". The available transition from Approved is `Converted_to_Open`. Verify in sandbox.
- If either `changeStage` fails, the CN stays at Approved. No data corruption — apply row and balance are already updated. An admin can manually transition. Check Creator logs for the failure.

---

## Test matrix


| Test      | Setup                                                                                              | Expected                                                                                                                                            |
| --------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-A1 PASS | Sent invoice, Amount_Due = 1000, CN = 1000, approve                                                | CN Closed; `Credits_Remaining` = 0; invoice Paid                                                                                                    |
| T-A2 PASS | Sent invoice, Amount_Due = 1000, CN = 600 (partial), approve                                       | CN Closed; `Credits_Remaining` = 0; invoice Amount_Due = 400                                                                                        |
| T-A3 PASS | Sent invoice, drift: payment 300 received before approval, CN = 1000, Amount_Due = 700 at approval | apply 700; CN Open; `Credits_Remaining` = 300; invoice Paid                                                                                         |
| T-A4 PASS | Partially Paid invoice, Amount_Due = 400, CN = 500, approve                                        | apply 400; CN Open; `Credits_Remaining` = 100; invoice Paid                                                                                         |
| T-A5 PASS | Paid invoice, Amount_Due = 0, CN = 500, approve                                                    | apply 0; CN Open; `Credits_Remaining` = 500; invoice unchanged                                                                                      |
| T-A6 pass | Open CN with 300 remaining — Apply Credits action visible                                          | Apply Credits button shows on Open CN                                                                                                               |
| T-A7 pass | Closed CN — Apply Credits action NOT visible                                                       | Apply Credits button hidden                                                                                                                         |
| T-A8 pass | Cumulative cap: prior CN 800 on invoice total 1000, new CN 300                                     | Approval blocked: "cap exceeded. Remaining: 200"                                                                                                    |
| T-A9 pass | Legacy Mode B CN already in Open/Approved before deploy                                            | Apply Credits and Create Refund Note still visible (stage = Open/Approved... but after deploy Approved CNs should be handled — re-approve or leave) |


---

## Exit criteria

- [ ] T-A1 through T-A8 pass in sandbox
- [ ] No CN ends up with `Credits_Remaining = 0` when partial apply occurred
- [ ] No CN stuck at Approved after approval
- [ ] `Apply Credits` and `Create Refund Note` show only for Open CNs
- [ ] `Submit Credit Note to LHDN` shows only for Closed CNs (unchanged)
- [ ] All 4 changed files synced to `XMT___Billing_System.ds`