# 10 - Clone Invoice Lines from Reference Invoice at Creation

## Context
Old flow: user adds any line items freely on manual credit note.
New flow: line items must be **cloned from the referenced invoice** at creation. The user can only **reduce** qty or amount per line. No new unrelated items may be added. This ensures the LHDN credit note accurately represents a reduction of the original taxable supply.

## Objective
When `Reference_Invoice` is selected (manual path) or set by convert (convert path), automatically populate CN line items mirroring the source invoice lines. Lock item identity and tax structure. Allow only downward adjustment.

## Primary files
- `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` — fires on `Reference_Invoice` field selection
- `application/forms/Credit Note/workflow/Handle_Submission_Form_an4.deluge` — line-level save guard
- `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge` — already copies lines (verify coverage)

## Dependency
Step 09 (mandatory reference) must be in place first. Lines are only cloned when a reference is guaranteed to exist.

---

## Step-by-step

### 1. Understand current Credit Note line subforms

From `Credit_Note.deluge`, the CN has three line item subforms matching invoice structure:

| Subform | Fields (key ones) |
|---------|-------------------|
| `Monthly_Rental` | `Item_Code_Monthly_Rental`, `Description_Monthly_Rental`, `Quantity_Monthly_Rental`, `Unit_Price_Monthly_Rental`, `Sub_Total_Monthly_Rental`, tax fields, `Classification_Codes_Monthly_Rental` |
| `Internet` | Same pattern with `_Internet` suffix |
| `Call_Charges` | Same pattern with `_Call_Charges` suffix |

The cloning logic must read each subform from the referenced invoice and write matching rows into the CN subforms.

### 2. Add line cloning to `Handle_reference_invoice_2.deluge`

This workflow already fires on `on user input of Reference_Invoice`. After UUID validation, add line cloning:

```deluge
// After UUID validation passes:

// Clear existing lines first
input.Monthly_Rental:ui.deleteAll();
input.Internet:ui.deleteAll();
input.Call_Charges:ui.deleteAll();

ref_invoice_id = input.Reference_Invoice;

// Clone Monthly_Rental lines
for each row in Invoice.Monthly_Rental[Invoice == ref_invoice_id]
{
    new_row = Credit_Note.Monthly_Rental();
    new_row.Item_Code_Monthly_Rental = row.Item_Code_Monthly_Rental;
    new_row.Description_Monthly_Rental = row.Description_Monthly_Rental;
    new_row.Quantity_Monthly_Rental = row.Quantity_Monthly_Rental;
    new_row.Unit_Price_Monthly_Rental = row.Unit_Price_Monthly_Rental;
    new_row.Sub_Total_Monthly_Rental = row.Sub_Total_Monthly_Rental;
    new_row.Classification_Codes_Monthly_Rental = row.Classification_Codes_Monthly_Rental;
    // Copy tax fields
    new_row.Tax_Type_Monthly_Rental = row.Tax_Type_Monthly_Rental;
    new_row.Tax_Rate_Monthly_Rental = row.Tax_Rate_Monthly_Rental;
    new_row.Tax_Amount_Monthly_Rental = row.Tax_Amount_Monthly_Rental;
    input.Monthly_Rental:ui.add(new_row);
}

// Clone Internet lines
for each row in Invoice.Internet[Invoice == ref_invoice_id]
{
    new_row = Credit_Note.Internet();
    new_row.Item_Code_Internet = row.Item_Code_Internet;
    new_row.Description_Internet = row.Description_Internet;
    new_row.Quantity_Internet = row.Quantity_Internet;
    new_row.Unit_Price_Internet = row.Unit_Price_Internet;
    new_row.Sub_Total_Internet = row.Sub_Total_Internet;
    new_row.Classification_Codes_Internet = row.Classification_Codes_Internet;
    new_row.Tax_Type_Internet = row.Tax_Type_Internet;
    new_row.Tax_Rate_Internet = row.Tax_Rate_Internet;
    new_row.Tax_Amount_Internet = row.Tax_Amount_Internet;
    input.Internet:ui.add(new_row);
}

// Clone Call_Charges lines
for each row in Invoice.Call_Charges[Invoice == ref_invoice_id]
{
    new_row = Credit_Note.Call_Charges();
    new_row.Item_Code_Call_Charges = row.Item_Code_Call_Charges;
    new_row.Description_Call_Charges = row.Description_Call_Charges;
    new_row.Quantity_Call_Charges = row.Quantity_Call_Charges;
    new_row.Unit_Price_Call_Charges = row.Unit_Price_Call_Charges;
    new_row.Sub_Total_Call_Charges = row.Sub_Total_Call_Charges;
    new_row.Classification_Codes_Call_Charges = row.Classification_Codes_Call_Charges;
    new_row.Tax_Type_Call_Charges = row.Tax_Type_Call_Charges;
    new_row.Tax_Rate_Call_Charges = row.Tax_Rate_Call_Charges;
    new_row.Tax_Amount_Call_Charges = row.Tax_Amount_Call_Charges;
    input.Call_Charges:ui.add(new_row);
}
```

**Field names:** Verify exact subform field names against `Credit_Note.deluge` before writing. The names above follow the Debit Note pattern in the same codebase.

### 3. Lock item identity — what user CAN and CANNOT change

After cloning, the following fields must be read-only (UI level or save-time guard):

| Field type | Rule |
|------------|------|
| `Item_Code_*` | Read-only — cannot change item |
| `Classification_Codes_*` | Read-only — tax classification locked to source |
| `Tax_Type_*`, `Tax_Rate_*` | Read-only — tax structure locked |
| `Description_*` | Read-only or editable — user preference, does not affect LHDN |
| `Quantity_*` | Editable — user may reduce (must not exceed source qty) |
| `Unit_Price_*` | Editable — user may reduce (must not exceed source unit price) |
| `Sub_Total_*`, `Tax_Amount_*` | Calculated — auto-recalculate on qty/price input |

Implement read-only via `Disable_Fields` workflow (mirror `Disable_Fields20.deluge` pattern already in Credit Note folder) triggered after line clone.

### 4. Add per-line save guard in `Handle_Validation_Submiss2.deluge`

On save, validate that no line exceeds the source invoice line values (use nested loop — subforms do not support `.first()`):

```deluge
ref_invoice = Invoice[ID == input.Reference_Invoice];

for each curr_monthly_rental in input.Monthly_Rental
{
    item_code = curr_monthly_rental.Item_Code_Monthly_Rental;
    source_row_found = false;
    for each source_row in ref_invoice.Monthly_Rental
    {
        if(source_row.Item_Code_Monthly_Rental == item_code)
        {
            source_row_found = true;
            if(curr_monthly_rental.Quantity_Monthly_Rental > source_row.Quantity_Monthly_Rental)
            {
                alert "Credit note qty for " + item_code + " exceeds original invoice qty. Reduce the quantity.";
                cancel submit;
            }
            if(curr_monthly_rental.Unit_Price_Monthly_Rental > source_row.Unit_Price_Monthly_Rental)
            {
                alert "Credit note unit price for " + item_code + " exceeds original invoice unit price.";
                cancel submit;
            }
            break;
        }
    }
    if(source_row_found == false)
    {
        alert "Credit note line item " + item_code + " does not exist on the reference invoice.";
        cancel submit;
    }
}
// Repeat same pattern for Internet_Charges and Call_Charges subforms
```

### 5. Convert path — verify lines already cloned

`Convert_To_Credit_Note.deluge` (Step 05) already copies lines via insert with the source invoice data. Confirm it copies:
- Item codes
- Classification codes
- Tax type and rate
- Qty and unit price

If any of these are missing from the convert insert, add them. The user editing lines in Draft after convert follows the same reduce-only rule as manual.

### 6. Handle edge: user changes `Reference_Invoice` after lines loaded

If user clears and re-selects a different reference invoice (before save), `Handle_reference_invoice_2.deluge` fires again. The `deleteAll()` + re-clone logic in step 2 handles this correctly — old lines are wiped and new ones loaded.

---

## Zoho safety

- `ui.deleteAll()` on a subform only clears the UI buffer, not saved rows. This is safe before first save.
- After first save (if CN already has rows), editing and changing `Reference_Invoice` would clear and reload lines. This is intentional — changing the reference invoice on an existing Draft should reset lines.
- Do not use `deleteAll()` after CN is in Pending Approval or later stages — lines are committed.

## Exit criteria

- [x] Manual CN: pick `Reference_Invoice` → lines auto-populate from that invoice
- [x] Lines match source invoice exactly (item code, tax, qty, price)
- [x] User reduces qty on a line → `Sub_Total` and `Grand_Total` recalculate
- [x] User tries to enter qty > source qty → blocked at save with message
- [x] User tries to enter unit price > source price → blocked at save
- [x] Item code fields are read-only on CN form
- [x] Convert from invoice: lines already match (existing behavior verified)
- [x] Change `Reference_Invoice` in Draft → lines reload from new reference
- [ ] `Handle_reference_invoice_2.deluge` and `Handle_Validation_Submiss2.deluge` synced to `XMT___Billing_System.ds`
