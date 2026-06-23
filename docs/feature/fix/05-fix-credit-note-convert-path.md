# 05 - Fix Invoice -> Credit Note Convert Path

## Objective
Make conversion produce a clean Draft CN linked to source invoice, with single numbering.

## Primary files
- `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge`
- `application/forms/Credit Note/workflow/Handle_Invoice_Creation1.deluge`
- `application/forms/Invoice/All_Invoices.deluge`

## Step-by-step
1. In `Convert_To_Credit_Note.deluge`:
   - Set `Reference_Invoice = input.ID`.
   - Do not generate CN number here if already generated on CN add success.
2. Keep line/header copy behavior, but ensure result stays Draft after create.
3. Ensure stage is explicitly set to `Draft` after insert (blueprint stage, not only text status).
4. In `Handle_Invoice_Creation1.deluge`:
   - Keep CN number generation as single source.
5. In invoice report action condition (`All_Invoices.deluge`):
   - Correct stage case mismatch (`Paid` not `paid`).
6. Validate convert scenarios:
   - Source invoice in `Sent`, `Partially Paid`, `Paid`, `Overdue`.
   - Converted CN opens as `Draft`, not `Open`.
   - CN number generated exactly once.

## Notes
- It is acceptable that initial converted amount equals source totals.
- Partial credit is handled by user edits in Draft before approval.

## Exit criteria
- Issues #2, #3, #4, #5, #8 are resolved.
- Converted CN reliably enters lifecycle at Draft.

---

## Step 05 results (2026-06-23)

### Changes made

| File | Change |
|---|---|
| `Convert_To_Credit_Note.deluge` | `Reference_Invoice=input.ID`; removed `Invoice_No` at insert; `changeStage` → Draft after insert |
| `Handle_Invoice_Creation1.deluge` | Unchanged — single CN number on `on add` success (Step 04) |
| `Invoices` (`All_Invoices` report) | Convert action condition: `"paid"` → `"Paid"` |

### Convert flow (after fix)

1. Insert CN with source link, no doc number at insert time
2. `changeStage` → **Draft** (record action)
3. `Handle_Invoice_Creation1` on add success → generate CN number once
4. Form opens in Draft; balances calc does not promote to Open (Step 04)

### Deploy to live Creator

1. **Convert To Credit Note** record action — apply insert field + `changeStage` changes
2. **All_Invoices** report — fix Convert button condition to include `"Paid"`
3. Ensure `Reference_Invoice` field exists on Credit Note (Step 02)
4. Re-export and sync `.ds`
