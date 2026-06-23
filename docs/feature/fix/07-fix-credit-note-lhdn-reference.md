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
