# 14 - Mode B: Apply Credit Controls and Refund Eligibility

## Context
**Mode B** CNs (reference invoice was Partially Paid or Paid at creation) stay **Open** after approval. Finance chooses how to consume the credit:

| Option | Rule |
|--------|------|
| Apply to same reference invoice | Allowed only if `Amount_Due > 0` on reference invoice (Q22 = C) |
| Apply to other open invoices | Always allowed in Mode B |
| Create Refund Note | Always allowed in Mode B |

Mode B CNs can be **partially consumed** across multiple apply/refund actions until `Credits_Remaining = 0` → Closed.

## Objective
Update Apply Credit To Invoices initialization to expose the correct invoice options for Mode B. Ensure the same reference invoice appears in the picker only when it still has outstanding balance. Enforce Mode B exclusivity — Mode A CNs must never reach these paths.

## Primary files
- `application/forms/Apply Credit To Invoices/workflow/Handle_Credit_Note_Select1.deluge` — picker init when CN is selected
- `application/forms/Apply Credit To Invoices/workflow/Apply_Credit_To_Invoices_1.deluge` — validation on submit
- `application/forms/Apply Credit To Invoices/workflow/Handle_Form_Submission.deluge` — balance updates on success
- `application/forms/Refund Note/workflow/Handle_Validation_Submiss3.deluge` — refund note validation
- `application/forms/Credit Note/Credit_Notes.deluge` — action conditions (already updated in Step 13 to gate on Mode B)

## Dependency
Steps 06 (apply/refund guards), 11 (Credit_Mode), 13 (Mode A blocked) must all be deployed. This step refines the Mode B path only.

---

## Step-by-step

### 1. Update invoice picker in `Handle_Credit_Note_Select1.deluge`

Step 06 already pre-fills `Credits_To_Apply` with the reference invoice when eligible. Update to correctly apply Mode B rules:

```deluge
credit_note_id = input.invoice;   // the CN selected in Apply Credit form
cn_record = Credit_Note[ID == credit_note_id];
ref_invoice_id = cn_record.Reference_Invoice;
credit_mode = cn_record.Credit_Mode;

// Build eligible invoice list for Mode B
eligible_invoice_list = {};

// Option 1: same reference invoice, only if Amount_Due > 0
if(ref_invoice_id != null && credit_mode == "Mode B - Open Credit")
{
    ref_inv = Invoice[ID == ref_invoice_id];
    if(ref_inv.Amount_Due > 0)
    {
        eligible_invoice_list.add(ref_invoice_id);
        // Pre-fill Credits_To_Apply with min(Amount_Due, Credits_Remaining)
        input.Credits_To_Apply = min(ref_inv.Amount_Due, cn_record.Credits_Remaining);
    }
}

// Option 2: other open invoices for the same customer (excluding reference invoice)
customer_id = cn_record.Customer_Name;
other_open_invoices = Invoice[Customer_Name == customer_id
                              && Amount_Due > 0
                              && ID != ref_invoice_id
                              && (Blueprint.Current_Stage == "Sent"
                                  || Blueprint.Current_Stage == "Overdue"
                                  || Blueprint.Current_Stage == "Partially Paid")];
for each inv in other_open_invoices
{
    eligible_invoice_list.add(inv.ID);
}

// Populate picker
input.Unpaid_Invoices:ui.add(eligible_invoice_list);
```

**If the reference invoice has Amount_Due = 0 (Paid):** It will not appear in the picker. Only other open invoices for that customer will be shown.

### 2. Add Mode B guard in `Apply_Credit_To_Invoices_1.deluge` (validation)

Step 06 already blocks non-Approved/Open stages. Add Mode B check:

```deluge
cn_record = Credit_Note[ID == input.invoice];
if(cn_record.Credit_Mode == "Mode A - Debt Reduction")
{
    alert("This credit note (Mode A) was automatically applied at approval. Manual apply is not permitted.");
    cancel submit;
}
```

This is a safety net in case the action condition in `Credit_Notes.deluge` is bypassed (e.g., direct URL navigation).

### 3. Confirm balance update formula in `Handle_Form_Submission.deluge`

Step 06 already uses `changeStage` for Open/Closed after apply. No logic change needed here. Confirm the balance recalculation formula is:

```deluge
// CN balance update after apply
new_credits_used = cn_record.Credits_Used + applied_this_time;
new_credits_remaining = cn_record.Grand_Total - new_credits_used - cn_record.Refund;
Credit_Note[ID == cn_id].Credits_Used = new_credits_used;
Credit_Note[ID == cn_id].Credits_Remaining = new_credits_remaining;

// Stage move
if(new_credits_remaining <= 0)
{
    thisapp.blueprint.changeStage("Credit_Note", "Credit_Note_Blueprint", cn_id.toLong(), "Converted_to_Closed");
    // or "Approved_to_Closed" if still at Approved
}
else
{
    if(current_stage == "Approved")
    {
        thisapp.blueprint.changeStage("Credit_Note", "Credit_Note_Blueprint", cn_id.toLong(), "Converted_to_Open");
    }
}
```

### 4. Refund Note — add Mode B guard in `Handle_Validation_Submiss3.deluge`

The Refund Note form already checks `Is_Refund_Note_Created_from_Credit_Note`. Add a Mode B check:

```deluge
ref_cn_id = input.Reference_Credit_Note;
cn_record = Credit_Note[ID == ref_cn_id];
if(cn_record.Credit_Mode == "Mode A - Debt Reduction")
{
    alert("Refund Notes cannot be created from a Mode A credit note. Mode A credits are automatically applied to the referenced invoice.");
    cancel submit;
}
```

### 5. Summary: Mode A vs Mode B — what is allowed

| Action | Mode A | Mode B | Legacy (null Credit_Mode) |
|--------|--------|--------|---------------------------|
| Auto-apply to reference invoice at approval | ✅ automatic | ✗ | ✗ |
| Apply Credits to Invoices (same reference) | ✗ hidden | ✅ if Amount_Due > 0 | ✅ |
| Apply Credits to Invoices (other invoices) | ✗ hidden | ✅ | ✅ |
| Create Refund Note | ✗ hidden | ✅ | ✅ |
| Submit to LHDN | ✅ when Closed | ✅ when Closed | ✅ when Closed |

### 6. Mode B partial utilization cycle (confirm existing flow handles it)

Mode B can be partially consumed across multiple apply actions:

1. Approved → apply RM 200 → Open (Credits_Remaining = RM 300)
2. Open → apply RM 150 → Open (Credits_Remaining = RM 150)
3. Open → refund RM 150 → Closed (Credits_Remaining = 0) → LHDN

The Step 06 `changeStage` logic already handles this. Confirm `Credits_Used + Refund` is used correctly in the remaining balance formula — not just `Credits_Used` alone.

---

## Zoho safety

- The Mode B guard in `Apply_Credit_To_Invoices_1.deluge` is a belt-and-suspenders check. The primary gate is the action visibility condition in `Credit_Notes.deluge` (Step 13).
- `Handle_Credit_Note_Select1.deluge` rebuilds the picker dynamically. Existing Mode B behavior from Step 06 is preserved; this step only adds the Mode B/A filter.

## Exit criteria

- [ ] Mode B CN (Partially Paid ref invoice): Apply Credits picker shows same reference invoice AND other open invoices
- [ ] Mode B CN (Paid ref invoice): Apply Credits picker shows only other open invoices (not reference invoice)
- [ ] Mode A CN: Apply Credits action hidden (Step 13); validation in apply form also blocks if reached
- [ ] Mode A CN: Create Refund Note action hidden (Step 13); refund form validation also blocks if reached
- [ ] Mode B partial apply: Credits_Remaining decreases correctly; CN stays Open until 0
- [ ] Mode B partial apply → partial refund: combined Credits_Used + Refund drives Credits_Remaining
- [ ] Mode B CN → Credits_Remaining = 0 → blueprint moves to Closed
- [ ] Legacy CN (null Credit_Mode): still shown in Apply Credits and Refund Note (backward compatible)
- [ ] `Handle_Credit_Note_Select1.deluge`, `Apply_Credit_To_Invoices_1.deluge`, `Handle_Validation_Submiss3.deluge` synced to `XMT___Billing_System.ds`
