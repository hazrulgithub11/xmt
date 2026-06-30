# 12 - Cumulative Cap Validation (Save + Approval)

## Context

Multiple credit notes can be created against the same reference invoice, but the **total approved CN amount must not exceed the original invoice total**. This is checked twice:

1. **At save (Draft):** sum of already-approved CNs + this CN ≤ original invoice total
2. **At approval:** re-check using live approved totals — catches concurrent approvals where two CNs were drafted simultaneously and both would exceed the cap if both approved

V1 ships the looser variant (Q10/Q23): only **approved** CNs count toward the cap at save. Draft and Pending Approval CNs are not reserved. The approval-time recheck is the safety net for concurrent races.

## Objective

Block saves and approval transitions when the cumulative approved CN total on the same reference invoice would exceed the original invoice amount.

## Primary files

- `application/forms/Credit Note/workflow/Handle_Submission_Form_an4.deluge` — save-time cap check
- `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/script_01.deluge` — approval-time recheck

## Dependency

Steps 09, 10, 11 must be in place. `Reference_Invoice` is always set; `Grand_Total` is populated from cloned lines.

---

## Step-by-step

### 1. Define the cap formula

```
Remaining Creditable Amount = Original Invoice Grand_Total
                             − SUM of Grand_Total of all Approved CNs on same Reference_Invoice
                             (excluding the CN being checked)

This CN is allowed if: this CN's Grand_Total <= Remaining Creditable Amount
```

**Original Invoice Grand_Total** = `Invoice[ID == input.Reference_Invoice].Grand_Total`
**Approved CNs on same reference** = all Credit Notes where `Reference_Invoice == input.Reference_Invoice AND Blueprint.Current_Stage == "Approved" AND ID != input.ID`

### 2. Add save-time cap check in `Handle_Submission_Form_an4.deluge`

Add this block in the `on validate` or at the start of `on success`, before any balance calculations:

```deluge
if(input.Reference_Invoice != null && (input.Blueprint.Current_Stage == "Draft" || input.Blueprint.Current_Stage == "Rejected"))
{
    ref_invoice_id = input.Reference_Invoice;
    original_total = Invoice[ID == ref_invoice_id].Grand_Total;

    // Sum of Grand_Total of all Approved CNs against same reference, excluding this CN
    approved_cn_list = Credit_Note[Reference_Invoice == ref_invoice_id
                                   && Blueprint.Current_Stage == "Approved"
                                   && ID != input.ID];
    approved_cn_total = 0;
    for each cn in approved_cn_list
    {
        approved_cn_total = approved_cn_total + cn.Grand_Total;
    }

    remaining_creditable = original_total - approved_cn_total;

    if(input.Grand_Total > remaining_creditable)
    {
        alert("This credit note amount (RM " + input.Grand_Total + ") exceeds the remaining creditable amount (RM " + remaining_creditable + ") for the referenced invoice. Reduce the credit note amount or lines.");
        cancel submit;
    }
}
```

### 3. Add approval-time recheck in blueprint Approve transition

The `Approve` transition already runs a script (`script_01.deluge`) that performs LHDN taxpayer validation. Add the cumulative cap check **before** the taxpayer validation call so a hard amount breach is caught first:

```deluge
// === Cumulative cap check ===
ref_invoice_id = input.Reference_Invoice;
original_total = Invoice[ID == ref_invoice_id].Grand_Total;

// Re-read all approved CNs at this moment (catches concurrent approvals)
approved_cn_list = Credit_Note[Reference_Invoice == ref_invoice_id
                               && Blueprint.Current_Stage == "Approved"
                               && ID != input.ID];
approved_cn_total = 0;
for each cn in approved_cn_list
{
    approved_cn_total = approved_cn_total + cn.Grand_Total;
}

remaining_creditable = original_total - approved_cn_total;

if(input.Grand_Total > remaining_creditable)
{
    // Revert stage to Pending Approval
    thisapp.blueprint.changeStage("Credit_Note", "Credit_Note_Blueprint", input.ID.toLong(), "Revert_to_Pending_Approva");
    info "Approval rejected: cumulative credit note cap exceeded. Original invoice total: " + original_total + ", Already approved: " + approved_cn_total + ", This CN: " + input.Grand_Total + ", Remaining: " + remaining_creditable;
    return;
}
// === End cap check — continue with LHDN taxpayer validation below ===
```

**Note on transition name:** The existing revert transition is `Revert_to_Pending_Approva` (Step 03 set its criteria to `ID == 0` to prevent auto-trigger). Call it explicitly here with the CN's ID.

### 4. Add per-line guard (already in Step 10, confirm here)

Step 10 added per-line qty/price guards. Confirm the per-line check runs before the cumulative cap check in `Handle_Submission_Form_an4.deluge` — per-line is the inner check, cumulative cap is the outer check:

```
Order of validation at save:
1. Reference_Invoice present + UUID valid (Step 09)
2. Per-line: qty and unit price ≤ source invoice line (Step 10)
3. Grand_Total ≤ remaining creditable amount on reference invoice (Step 12)
4. Credit_Mode is set (Step 11)
```

### 5. Edge case: reference invoice with zero Grand_Total

If the referenced invoice has `Grand_Total = 0` (unusual but possible for adjustments), the remaining creditable amount is also 0, and no CN can be created against it. The cap check will block. This is correct behaviour.

### 6. Display remaining creditable amount on CN form (optional, helpful UX)

Consider adding a **calculated display field** `Remaining_Creditable_Amount` on the Credit Note form (read-only) that shows:

```
Invoice Grand_Total − sum(Approved CNs on same reference, excluding this CN)
```

This lets finance see at a glance how much credit room remains before submitting. Implement as a `on user input of Reference_Invoice` field update in `Handle_reference_invoice_2.deluge`.

---

## Zoho safety

- `Credit_Note[Reference_Invoice == ref_invoice_id && Blueprint.Current_Stage == "Approved"]` is a live query — it re-reads the table at approval time, which is exactly the behaviour needed to catch concurrent approvals.
- The approval-time revert uses the existing `Revert_to_Pending_Approva` transition — no new transitions needed.
- Existing CNs created before this step (with null `Reference_Invoice`) skip the cap check due to the `if(input.Reference_Invoice != null)` guard.

## Exit criteria

- [x] CN save blocked when `Grand_Total > original invoice total − approved CNs`
- [x] CN save allowed when `Grand_Total <= remaining creditable amount`
- [x] Approval of 3rd CN blocked when CN-1 + CN-2 already = invoice total (concurrent race scenario)
- [x] Approval-time message logged with original total, approved total, remaining, this CN amount
- [x] Approval reverts to Pending Approval on cap breach (user can edit and resubmit)
- [x] Per-line check runs before cumulative cap check
- [x] CNs with null `Reference_Invoice` (legacy) are not affected
- [~] `Handle_Validation_Submiss2.deluge` and `Approve/after/unconditional/script_01.deluge` synced to `XMT___Billing_System.ds`

**Implementation note:** Cap counts Approved + Closed + Open + Pending Approval (not Approved-only). Save validation lives in `Handle_Validation_Submiss2`, not `Handle_Submission_Form_an4`.