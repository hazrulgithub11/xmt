# 11 - Add Credit_Mode Field and Lock Utilization Mode at Creation

## Context
The new flow introduces two utilization modes determined by the **reference invoice stage at creation**:

| Mode | Reference invoice stage at creation | Post-approval behaviour |
|------|-------------------------------------|-------------------------|
| **Mode A** | Sent or Overdue (unpaid) | Auto-apply to same reference invoice → Closed immediately |
| **Mode B** | Partially Paid or Paid | Stays Open → user applies or refunds |

This mode is **locked at creation** (Q21 deferred — re-eval at approval is a later implementation).

## Objective
Add a `Credit_Mode` field to the Credit Note form. Detect and write the mode when `Reference_Invoice` is set (manual) or when convert runs. Make the field read-only after creation.

## Primary files
- `application/forms/Credit Note/Credit_Note.deluge` — new field
- `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` — set mode on manual selection
- `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge` — set mode on convert

## Dependency
Step 09 (mandatory reference) must be deployed. Mode detection requires a valid `Reference_Invoice` to always be present.

---

## Step-by-step

### 1. Add `Credit_Mode` field to Credit Note form

In `Credit_Note.deluge`, add a new dropdown/picklist field:

```
Credit_Mode
  type = dropdown
  displayname = "Credit Mode"
  values = ["Mode A - Debt Reduction", "Mode B - Open Credit"]
  required = false   // set programmatically; never by user
  disabled = true    // always read-only in UI
```

**In Creator:** Add as a single-line / dropdown field named `Credit_Mode`. Mark as disabled in form layout so user cannot edit it. It is a system-set field.

### 2. Add mode detection helper logic

The detection rule is:

```deluge
// Determine Credit_Mode from reference invoice blueprint stage
ref_stage = Invoice[ID == ref_invoice_id].Blueprint.Current_Stage;

if(ref_stage == "Sent" || ref_stage == "Overdue")
{
    credit_mode = "Mode A - Debt Reduction";
}
else if(ref_stage == "Partially Paid" || ref_stage == "Paid")
{
    credit_mode = "Mode B - Open Credit";
}
else
{
    // Unexpected stage — block and warn
    alert("Cannot create a credit note against an invoice in stage: " + ref_stage + ". Only Sent, Overdue, Partially Paid, or Paid invoices are eligible.");
    cancel submit;
    // or clear Reference_Invoice if in selection workflow
}
```

### 3. Set mode in `Handle_reference_invoice_2.deluge` (manual path)

After line cloning (Step 10) and UUID validation, add:

```deluge
ref_invoice_id = input.Reference_Invoice;
ref_stage = Invoice[ID == ref_invoice_id].Blueprint.Current_Stage;

if(ref_stage == "Sent" || ref_stage == "Overdue")
{
    input.Credit_Mode = "Mode A - Debt Reduction";
}
else if(ref_stage == "Partially Paid" || ref_stage == "Paid")
{
    input.Credit_Mode = "Mode B - Open Credit";
}
else
{
    alert("Invoice stage '" + ref_stage + "' is not eligible for a credit note. Choose a different invoice.");
    clear Reference_Invoice;
    input.Reference_Invoice:ui.add({});
    return;
}
```

### 4. Set mode in `Convert_To_Credit_Note.deluge` (convert path)

After setting `Reference_Invoice = input.ID`, detect stage from the source invoice being converted:

```deluge
source_stage = input.Blueprint.Current_Stage;

if(source_stage == "Sent" || source_stage == "Overdue")
{
    CN_Credit_Mode = "Mode A - Debt Reduction";
}
else if(source_stage == "Partially Paid" || source_stage == "Paid")
{
    CN_Credit_Mode = "Mode B - Open Credit";
}

// Include CN_Credit_Mode in the insert map
new_cn = Credit_Note();
// ... existing fields ...
new_cn.Credit_Mode = CN_Credit_Mode;
new_cn.Reference_Invoice = input.ID;
insert into Credit_Note values new_cn;
```

**Important:** The `Blueprint.Current_Stage` of the **source invoice** is what determines mode — not the CN's own stage.

### 5. Add `Credit_Mode` to Credit Notes report (read-only visibility)

In `Credit_Notes.deluge` and `Credit_Note_Report.deluge`, add `Credit_Mode` as a visible column so finance can see at a glance which mode a CN is in.

### 6. Guard against unexpected stage at save

In `Handle_Submission_Form_an4.deluge`, verify `Credit_Mode` is set and valid before allowing save:

```deluge
if(input.Credit_Mode == null || input.Credit_Mode == "")
{
    alert("Credit Mode could not be determined. Please re-select the Reference Invoice.");
    cancel submit;
}
```

---

## Deferred note (Q21)

The current logic **locks mode at creation** — i.e., the stage read is taken when `Reference_Invoice` is first set, not at approval time. If the reference invoice moves from Sent to Partially Paid while the CN is in Pending Approval, the mode stays Mode A.

**Known risk:** Mode A CN may auto-apply to a reference invoice that the customer has since partially paid. Finance should be aware of this edge case until Q21 is implemented in a later pass.

---

## Zoho safety

- Adding a new field to an existing form does not break existing records or workflows.
- `Credit_Mode = null` on old CNs is safe — Steps 13 and 14 must guard against null Credit_Mode on legacy records.

## Exit criteria

- [ ] `Credit_Mode` field added to `Credit_Note` form and visible in reports
- [ ] Manual CN: pick Sent/Overdue invoice → `Credit_Mode = "Mode A - Debt Reduction"`
- [ ] Manual CN: pick Partially Paid/Paid invoice → `Credit_Mode = "Mode B - Open Credit"`
- [ ] Manual CN: pick Draft/Pending/Approved (non-eligible) invoice → **blocked with message**
- [ ] Convert from Sent/Overdue invoice → `Credit_Mode = "Mode A"`
- [ ] Convert from Partially Paid/Paid invoice → `Credit_Mode = "Mode B"`
- [ ] `Credit_Mode` is read-only in form layout (user cannot change it)
- [ ] `Credit_Mode` null on existing CNs does not crash form load
- [ ] `Credit_Note.deluge`, `Credit_Notes.deluge`, `Convert_To_Credit_Note.deluge`, `Handle_reference_invoice_2.deluge` synced to `XMT___Billing_System.ds`
