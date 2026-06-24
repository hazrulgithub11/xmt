# 08 - Test Matrix, Deployment Order, and Rollback

## Objective

Ship safely with clear verification and rollback points.

---

## Deployment order (recommended)

Deploy in Creator in this sequence. Re-export after each batch and spot-check one scenario before continuing.


| Order | Batch | Steps | Scope                                             |
| ----- | ----- | ----- | ------------------------------------------------- |
| 1     | A     | 02–03 | `Reference_Invoice` field + blueprint transitions |
| 2     | B     | 04–05 | Status engine + convert path                      |
| 3     | C     | 06–07 | Apply/refund guards + LHDN reference payload      |
| 4     | D     | 08    | UAT below + final full export                     |


### Batch A — Field + blueprint (Steps 02–03)


| Artifact   | Path                                                                     |
| ---------- | ------------------------------------------------------------------------ |
| Form field | `application/forms/Credit Note/Credit_Note.deluge`                       |
| Reports    | `Credit_Notes.deluge`, `Credit_Note_Report.deluge`                       |
| Workflows  | `Handle_reference_invoice_2.deluge`, `Handle_Customer_Name_Chan3.deluge` |
| Blueprint  | `application/blueprints/Credit_Note_Blueprint/`                          |


### Batch B — Status + convert (Steps 04–05)


| Artifact         | Path                                                                                                        |
| ---------------- | ----------------------------------------------------------------------------------------------------------- |
| Status engine    | `User_Input_Trigger_Workfl2.deluge`, `Handle_Invoice_Creation1.deluge`, `Handle_Submission_Form_an4.deluge` |
| Convert          | `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge`                                  |
| Report condition | `application/forms/Invoice/Invoices` (All_Invoices — `Paid` case)                                           |


### Batch C — Utilization + LHDN (Steps 06–07)


| Artifact       | Path                                                                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| Report actions | `application/forms/Credit Note/Credit_Notes.deluge`                                                         |
| Apply credit   | `Apply_Credit_To_Invoices_*.deluge`, `Handle_Credit_Note_Select*.deluge`, `Handle_Form_Submission.deluge`   |
| Refund success | `application/forms/Refund Note/workflow/Successful_form_submissio1.deluge`                                  |
| Subform guards | `Disable_Addition_And_Dele3.deluge`, `Handle_Deletion_of_Credit.deluge`, `Deletion_of_rows_of_Refun.deluge` |
| LHDN submit    | `application/forms/Credit Note/workflow/actions/Submit_Credit_Note_to_LHD1.deluge`                          |


---

## Core test matrix

Use a **sandbox / test customer** first. Record CN ID and invoice ID for each row.


| #   | Scenario                              | Steps                                                                              | Expected                                                                                                         | Pass    |
| --- | ------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------- |
| T1  | Manual create → save → reopen         | Credit Notes → Add → pick customer → add line → Save → reopen record               | Blueprint = **Draft**; `Credits_Remaining` = `Grand_Total`; no jump to Open/Closed                               | [ pass] |
| T2  | Manual create — actions hidden        | On Draft CN, open Credit Notes report actions                                      | **No** Apply Credit / Create Refund / Submit LHDN                                                                | [ pass] |
| T3  | Convert from invoice                  | Pick invoice (Sent/Partially Paid/Paid/Overdue) → Convert to Credit Note           | CN opens as **Draft**; `Reference_Invoice` = source invoice; CN number assigned **once** on save                 | [ pass] |
| T4  | Convert — no early Open               | After convert popup loads, before save                                             | Blueprint stays **Draft** (not Open)                                                                             | [pass ] |
| T5  | Approval loop                         | Draft → Send for Approval → Approve (pass LHDN taxpayer validation)                | **Pending Approval** → **Approved**                                                                              | [ pass] |
| T6  | Reject / resubmit                     | Reject → edit → Resubmit → Approve                                                 | **Rejected** → **Pending Approval** → **Approved**                                                               | [ pass] |
| T7  | Apply credit — default reference      | Approved CN with `Reference_Invoice` (unpaid) → Apply Credits                      | Source invoice pre-filled in `Credits_To_Apply`                                                                  | [ pass] |
| T8  | Apply credit — balances               | Apply partial credit → submit                                                      | Invoice `Amount_Due` reduced; CN `Credits_Used` / `Credits_Remaining` correct; stage → **Open** if remaining > 0 | [ pass] |
| T9  | Apply credit — full close             | Apply full remaining credit                                                        | CN stage → **Closed**; `Credits_Remaining` = 0                                                                   | [ pass] |
| T10 | Refund path                           | Approved CN → Create Refund Note → save refund                                     | CN `Refund` and `Credits_Remaining` updated; stage Open or Closed per balance                                    | [pass]  |
| T11 | Convert + refund only (no apply)      | Convert → approve → refund full amount (no apply)                                  | CN **Closed**; LHDN payload still includes source invoice UUID (T13)                                             | [ pass] |
| T12 | Subform delete blocked (pre-approval) | Draft CN — Credit Applied / Refund History subforms                                | Delete row button **hidden**                                                                                     | [pass ] |
| T13 | LHDN — button visibility              | CN not Closed                                                                      | Submit LHDN action **hidden**                                                                                    | [ pass] |
| T14 | LHDN — submit + payload               | Closed CN → Submit Credit Note to LHDN                                             | Submission succeeds; `info reference_invoice_list` includes `Reference_Invoice` UUID when set                    | [ pass] |
| T15 | LHDN — manual standalone              | Manual CN (no `Reference_Invoice`), applied to invoice(s), fully utilized → Closed | Payload includes applied invoice UUID(s) only                                                                    | [ ]     |


### Regression checks


| #   | Check                         | Expected                                                                       | Pass                                                                               |
| --- | ----------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| R1  | No duplicate CN numbering     | Convert + manual add each produce one `Invoice_No`; no skip/duplicate sequence | [ ]                                                                                |
| R2  | Convert button stages         | Visible for Sent, Partially Paid, **Paid**, Overdue                            | [ ]                                                                                |
| R3  | Form load — no stage jump     | Open Draft CN, edit lines, save without apply/refund                           | Stays Draft (or Pending/Approved per workflow — never Open/Closed from load alone) |
| R4  | Apply before approval blocked | Try Apply Credits on Draft CN (direct URL/form if possible)                    | Validation blocks submit                                                           |
| R5  | Blueprint revert disabled     | Approved CN without LHDN UUID on CN itself                                     | Does **not** auto-revert to Pending Approval                                       |


---

## Issue closure (`creditNote_wrong.md`)


| Issue  | Resolution                                            | Verified by |
| ------ | ----------------------------------------------------- | ----------- |
| #1     | Draft until approved; Open only after utilization     | T1, T4, T8  |
| #2     | `Reference_Invoice` on convert                        | T3          |
| #3     | `changeStage` → Draft after convert insert            | T3          |
| #4     | Single CN numbering (`Handle_Invoice_Creation1` only) | T3, R1      |
| #5     | Link via `Reference_Invoice` (minimum)                | T3          |
| #6     | Issue date = today; link on `Reference_Invoice`       | T3 (visual) |
| #7     | User adjusts in Draft before approval                 | T1, T4      |
| #8     | Convert condition includes `Paid`                     | R2          |
| #9     | Apply only after approval                             | T2, T7, R4  |
| #10    | Apply defaults to `Reference_Invoice`                 | T7          |
| #11    | Manual CN stays Draft                                 | T1          |
| #12    | No change (already correct)                           | T1          |
| #14    | No Open/Closed on form load in pre-approval           | T1, R3      |
| #16    | Strict stage order                                    | T5–T10      |
| #17    | Actions gated on Approved/Open                        | T2          |
| #18–20 | Apply/refund/validation logic unchanged               | T8–T10      |
| #21    | Subform delete hidden pre-approval                    | T12         |
| #22    | LHDN script requires Closed                           | T14         |
| #23–24 | `reference_invoice_list` includes `Reference_Invoice` | T11, T14    |
| #25    | Submit button only when Closed                        | T13         |
| #26    | Approve LHDN taxpayer validation                      | T5          |


**Aligned / no code change:** #12, #18–20, #22, #26.

---

## Rollback strategy

### Before deploy

1. Tag or note current git commit: `git log -1 --oneline`
2. Export current live Creator app → save as `XMT___Billing_System.pre-credit-note-fix.ds` (outside repo or separate branch)

### Per batch rollback


| Batch | Revert                                                                                                                               |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------ |
| A     | Restore `Credit_Note` form (remove `Reference_Invoice`), blueprint folder, step 02–03 workflows                                      |
| B     | Restore `User_Input_Trigger_Workfl2`, `Handle_Invoice_Creation1`, `Handle_Submission_Form_an4`, `Convert_To_Credit_Note`, `Invoices` |
| C     | Restore `Credit_Notes.deluge`, apply/refund workflows, `Submit_Credit_Note_to_LHD1`, `Disable_Addition_And_Dele3`                    |


### Severe issue

1. Revert latest batch scripts in Creator first
2. Revert blueprint transitions second (Batch A)
3. Re-export → replace `XMT___Billing_System.ds` and `application/` split files

Existing CN records with `Reference_Invoice` populated are safe to keep after rollback (field can remain optional).

---

## Export sync verification (local repo)

Confirm these strings exist in **both** split files and `XMT___Billing_System.ds` before sign-off:


| Check                                                | Grep / location                                          |
| ---------------------------------------------------- | -------------------------------------------------------- |
| `Reference_Invoice` on Credit Note form              | `form Credit_Note` field block                           |
| Convert sets `Reference_Invoice=input.ID`            | `Convert_To_Credit_Note`                                 |
| Convert `changeStage` → Draft with `.toLong()`       | `Convert_To_Credit_Note`                                 |
| Submit LHDN condition `Closed`                       | `Credit_Notes` custom action                             |
| `reference_invoice_list` + `Reference_Invoice` block | `Submit_Credit_Note_to_LHD1`                             |
| Hide delete row pre-approval                         | `Disable_Addition_And_Dele3` field rules                 |
| No `cancel delete` on subform row delete             | `Handle_Deletion_of_Credit`, `Deletion_of_rows_of_Refun` |
| All_Invoices `Paid` (capital P)                      | `Invoices` list — Convert condition                      |


**Status (2026-06-23):** All checks verified in local export + `XMT___Billing_System.ds`.

---

## Post-deploy sign-off


| Item                             | Owner | Date | Status |
| -------------------------------- | ----- | ---- | ------ |
| Batch A deployed + smoke test    |       |      | [ ]    |
| Batch B deployed + smoke test    |       |      | [ ]    |
| Batch C deployed + smoke test    |       |      | [ ]    |
| Full test matrix T1–T15          |       |      | [ ]    |
| Regression R1–R5                 |       |      | [ ]    |
| Final Creator export → repo sync |       |      | [ ]    |


---

## Completion criteria

- [x] Test matrix and rollback documented (this file)
- [x] Local export sync verified against `XMT___Billing_System.ds`
- [x] All code-targeted issues in `creditNote_wrong.md` addressed (Steps 01–07)
- [ ] Runtime UAT passed in Creator (T1–T15, R1–R5) — **pending live execution**
- [ ] Final post-UAT export committed — **pending user re-export after deploy**