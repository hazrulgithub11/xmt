# 07 - Fix LHDN Reference Payload for Credit Note

## Objective
Ensure LHDN payload includes correct reference invoice data for both convert-originated and manually applied credit notes.

## Primary files
- `application/forms/Credit Note/workflow/actions/Submit_Credit_Note_to_LHD1.deluge`
- `application/forms/Credit Note/Credit_Notes.deluge`

## Step-by-step
1. Keep stage gate in script (`Closed` only) and add matching UI action condition so button is hidden unless eligible.
2. Build `reference_invoice_list` with priority order:
   - Add `Reference_Invoice` (if present and valid UUID).
   - Add applied invoices from `Credit_Applied_Invoices`.
   - De-duplicate by invoice number or UUID.
3. Handle convert-with-refund scenario:
   - If no applied rows but `Reference_Invoice` exists, include it.
4. Keep standalone manual CN behavior:
   - If no reference and no applied invoices, allow empty reference list only where business policy permits.
5. Validate payload samples for:
   - Convert + applied
   - Convert + refunded only
   - Manual + applied
   - Manual standalone

## Dependency warning
Do not enforce reference-invoice payload rule before `Reference_Invoice` field is deployed (Step 02), or submit may fail unexpectedly.

## Exit criteria
- Issues #23, #24, #25 are resolved.
- LHDN submission reference data is complete and consistent.

---

## Results (2026-06-23)

### 1. Submit action — `reference_invoice_list` (`Submit_Credit_Note_to_LHD1.deluge`)
- **Priority 1:** `Reference_Invoice` added first when set and `Invoice_UUID` is non-empty.
- **Priority 2:** Applied invoices from `Credit_Applied_Invoices` subform (unchanged loop).
- **Dedup:** `used_reference_invoice_no_list` prevents duplicate invoice numbers (covers Reference_Invoice already applied to same invoice).
- **Convert + refund only:** Reference invoice included even when `Credit_Applied_Invoices` is empty.
- **Standalone manual CN:** Empty list allowed when no `Reference_Invoice` and no applied rows.
- Script guard unchanged: returns early unless `Blueprint.Current_Stage == "Closed"`.

### 2. Report action visibility (`Credit_Notes.deluge`)
- **Submit Credit Note to LHDN** condition changed from `Approved` → `Closed` (matches script guard and issue #25).

### Sync
- Changes reflected in `XMT___Billing_System.ds`.

### Deploy to live Creator
1. **Credit Notes** report — update Submit LHDN action condition to `Blueprint.Current_Stage == "Closed"`.
2. **Submit Credit Note to LHDN** record action — paste updated `reference_invoice_list` block.

### Test matrix (manual)
| Scenario | Expected `reference_invoice_list` |
|---|---|
| Convert + applied to source invoice | Source invoice UUID (once) |
| Convert + refunded only | Source invoice UUID from `Reference_Invoice` |
| Manual + applied to other invoice(s) | Applied invoice UUID(s) only |
| Manual standalone, no reference | Empty list |
