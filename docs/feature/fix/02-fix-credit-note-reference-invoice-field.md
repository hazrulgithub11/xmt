# 02 - Add `Reference_Invoice` to Credit Note (Dependency First)

## Objective
Create the invoice linkage needed for convert traceability and LHDN references.

## Why this step comes early
Several fixes depend on this field:
- Convert path should set `Reference_Invoice` from source invoice.
- Apply-credit should prioritize source invoice.
- LHDN submission should include source invoice UUID even when no applied rows exist.

## Step-by-step
1. Add lookup field `Reference_Invoice` in Credit Note form:
   - Form: `Credit_Note`
   - Lookup target: `Invoice`
   - Required: `No` (manual CN can remain standalone)
2. Add the field to form/report layout where finance can audit source invoice.
3. Add credit-note-side validator workflow (mirror debit note behavior):
   - If selected reference invoice lacks `Invoice_UUID` or `Invoice_Public_Link`, block selection and show warning.
4. Update any convert/report logic to tolerate null for manual standalone CN.
5. Re-export Creator metadata and verify the new field appears in:
   - `application/forms/Credit Note/Credit_Note.deluge`
   - `XMT___Billing_System.ds`

## Zoho reference safety
If later you need to rename or delete `Reference_Invoice`:
1. Remove script references first (workflows, record actions, payload builders).
2. Remove report/list references.
3. Remove blueprint criteria using the field.
4. Delete/rename field last.

## Exit criteria
- `Reference_Invoice` exists and is exported.
- Manual CN allows null reference.
- Convert path can now safely map source invoice in Step 05.

---

## Step 02 results (2026-06-23)

### Changes made

| File | Change |
|---|---|
| `application/forms/Credit Note/Credit_Note.deluge` | Optional `Reference_Invoice` picklist → `Invoice` |
| `application/forms/Credit Note/Credit_Notes.deluge` | Column + quickview field |
| `application/forms/Credit Note/Credit_Note_Report.deluge` | Column added |
| `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` | UUID/public-link validation on selection (mirrors Debit Note) |
| `application/forms/Credit Note/workflow/Handle_Customer_Name_Chan3.deluge` | Filters picker by customer; empty list allowed (standalone CN OK) |
| `XMT___Billing_System.ds` | Form field, report columns, both workflows synced |

### Deploy to live Creator

Apply in Zoho Creator UI (or paste from local files):

1. **Credit Note form** — add lookup field `Reference_Invoice` → Invoice, not required, display `Invoice_No`.
2. **Credit Notes report** — add `Reference_Invoice` to list + quickview (after Payable To).
3. **Workflow** `Handle_reference_invoice_2` — copy from local file.
4. **Workflow** `Handle_Customer_Name_Chan3` — add second `on user input of Customer` action block.
5. Re-export and replace `XMT___Billing_System.ds` to confirm live match.

### Not in scope (Step 05)

`Convert_To_Credit_Note` does not set `Reference_Invoice` yet — intentional; convert mapping is Step 05.
