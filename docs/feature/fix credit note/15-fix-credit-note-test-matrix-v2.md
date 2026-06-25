# 15 - Test Matrix v2 and Rollout (Steps 09–14)

## Objective
Verify all new flow requirements from `creditNote_Flow.md` introduced in Steps 09–14 before going live.

Deploy in this batch order. Steps 01–08 (Batch A–D) must already be deployed.

---

## Deployment order for Steps 09–14

| Order | Batch | Steps | Scope |
|-------|-------|-------|-------|
| 1 | E | 09 | Mandatory `Reference_Invoice` + UUID block |
| 2 | F | 10–11 | Line cloning + Credit_Mode field |
| 3 | G | 12 | Cumulative cap at save + approval |
| 4 | H | 13–14 | Mode A auto-apply + Mode B apply controls |
| 5 | I | 15 | UAT below + final export |

Re-export `XMT___Billing_System.ds` and smoke-test one scenario after each batch before continuing.

---

### Batch E — Mandatory reference (Step 09)

| Artifact | Path |
|----------|------|
| Form field required flag | `application/forms/Credit Note/Credit_Note.deluge` |
| Save guard | `Handle_Submission_Form_an4.deluge` |
| Convert guard | `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge` |
| Reference validator | `Handle_reference_invoice_2.deluge` |

### Batch F — Line clone + mode field (Steps 10–11)

| Artifact | Path |
|----------|------|
| Line clone on reference select | `Handle_reference_invoice_2.deluge` |
| Per-line save guard | `Handle_Submission_Form_an4.deluge` |
| `Credit_Mode` field | `Credit_Note.deluge` |
| Mode detection on select | `Handle_reference_invoice_2.deluge` |
| Mode detection on convert | `Convert_To_Credit_Note.deluge` |
| Mode in reports | `Credit_Notes.deluge`, `Credit_Note_Report.deluge` |

### Batch G — Cumulative cap (Step 12)

| Artifact | Path |
|----------|------|
| Save-time cap check | `Handle_Submission_Form_an4.deluge` |
| Approval-time cap recheck | `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/script_01.deluge` |

### Batch H — Mode A auto-apply + Mode B controls (Steps 13–14)

| Artifact | Path |
|----------|------|
| Mode A auto-apply | `Approve/after/script_01.deluge` |
| Action visibility Mode B only | `Credit_Notes.deluge` |
| Mode B apply picker | `Handle_Credit_Note_Select1.deluge` |
| Mode B guard in apply form | `Apply_Credit_To_Invoices_1.deluge` |
| Mode B guard in refund form | `Handle_Validation_Submiss3.deluge` |

---

## Core test matrix v2

Use a **sandbox / test customer** and test invoices. Record CN ID, invoice ID, and observed stage for each row.

### Section 1 — Mandatory reference (Step 09)

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T09-1 | Manual CN without reference | Credit Notes → Add → do not pick Reference_Invoice → Save | **Blocked** — "must be linked to a reference invoice" | [ ] |
| T09-2 | Manual CN with unsubmitted invoice | Pick invoice with no `Invoice_UUID` → Save | **Blocked** — "not yet submitted to LHDN" | [ ] |
| T09-3 | Manual CN with valid LHDN invoice | Pick LHDN-validated invoice → Save | **Allowed** — Draft created | [ ] |
| T09-4 | Convert from unsubmitted invoice | Invoice with no UUID → Convert to Credit Note | **Blocked** with message | [ ] |
| T09-5 | Convert from valid invoice | LHDN-submitted invoice → Convert | **Allowed** — Draft created with Reference_Invoice set | [ ] |

### Section 2 — Line cloning (Step 10)

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T10-1 | Manual CN — lines load on reference select | Pick Reference_Invoice | Line items auto-populate matching source invoice | [ ] |
| T10-2 | Manual CN — item code read-only | Try to change item code on a line | **Blocked** — field disabled | [ ] |
| T10-3 | Reduce qty below source | Lower qty on a line | Sub_Total and Grand_Total recalculate correctly | [ ] |
| T10-4 | Qty exceeds source | Enter qty > source invoice qty | **Blocked at save** — "exceeds original invoice qty" | [ ] |
| T10-5 | Unit price exceeds source | Enter unit price > source invoice unit price | **Blocked at save** | [ ] |
| T10-6 | Change Reference_Invoice in Draft | Select different reference invoice | Old lines cleared; new lines from new reference loaded | [ ] |
| T10-7 | Convert — lines match source | Convert from invoice with 3 lines | CN has same 3 lines at same qty and price | [ ] |

### Section 3 — Credit_Mode detection (Step 11)

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T11-1 | Manual CN — Sent reference invoice | Pick a Sent (unpaid) invoice | `Credit_Mode = "Mode A - Debt Reduction"` | [x] |
| T11-2 | Manual CN — Overdue reference invoice | Pick an Overdue invoice | `Credit_Mode = "Mode A - Debt Reduction"` | [x] |
| T11-3 | Manual CN — Partially Paid reference | Pick a Partially Paid invoice | `Credit_Mode = "Mode B - Open Credit"` | [x] |
| T11-4 | Manual CN — Paid reference invoice | Pick a Paid invoice | `Credit_Mode = "Mode B - Open Credit"` | [x] |
| T11-5 | Non-eligible invoice stage | Pick Draft or Pending Approval invoice | **Blocked** — invoice stage not eligible | [x] |
| T11-6 | Convert — Sent/Overdue source | Convert from Sent invoice | `Credit_Mode = "Mode A - Debt Reduction"` | [x] |
| T11-7 | Convert — Partially Paid/Paid source | Convert from Paid invoice | `Credit_Mode = "Mode B - Open Credit"` | [x] |

### Section 4 — Cumulative cap (Step 12)

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T12-1 | First CN under cap | Invoice = RM 1,000. Create CN-1 for RM 600 | **Allowed** — saves as Draft | [ ] |
| T12-2 | Second CN under cap | CN-1 approved (RM 600). Create CN-2 for RM 300 | **Allowed** — RM 600 + RM 300 = RM 900 ≤ RM 1,000 | [ ] |
| T12-3 | CN that exactly hits cap | CN-1 approved (RM 600). Create CN-2 for RM 400 | **Allowed** — RM 600 + RM 400 = RM 1,000 exactly | [ ] |
| T12-4 | CN that exceeds cap | CN-1 approved (RM 600). Create CN-2 for RM 500 | **Blocked at save** — remaining = RM 400 only | [ ] |
| T12-5 | Concurrent approval race | CN-1 Draft RM 600, CN-2 Draft RM 600 (both under cap individually). CN-1 approved. CN-2 approval attempted. | CN-2 approval **rejected** — cumulative RM 1,200 > RM 1,000 | [ ] |
| T12-6 | Cap message shows values | CN blocked at cap | Error message shows original total, already-approved total, remaining | [ ] |

### Section 5 — Mode A auto-apply (Step 13)

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T13-1 | Mode A CN → Approve | Mode A Draft CN → Send → Approve | After approval: `Apply_Credit_To_Invoice_Line` created; invoice `Amount_Due` reduced; CN `Credits_Remaining = 0`; CN stage = **Closed** | [ ] |
| T13-2 | Mode A CN — invoice Amount_Due reduces correctly | Invoice Amount_Due = RM 800, CN = RM 300 | After approval: invoice Amount_Due = RM 500 | [ ] |
| T13-3 | Mode A CN — full amount matches invoice | Invoice Amount_Due = RM 500, CN = RM 500 | After approval: invoice Amount_Due = 0; CN Closed | [ ] |
| T13-4 | Mode A CN — paid before approval (edge) | Invoice Amount_Due = 0 at approval time | CN Closed; Credits_Remaining = 0; no apply row; no error | [ ] |
| T13-5 | Apply Credits hidden for Mode A | Mode A CN in any stage | **Apply Credits to Invoices** action not visible | [ ] |
| T13-6 | Create Refund Note hidden for Mode A | Mode A CN in any stage | **Create Refund Note** action not visible | [ ] |
| T13-7 | Mode B CN not auto-applied | Mode B CN → Approve | CN stage = Approved; Credits_Remaining = Grand_Total; Apply and Refund actions visible | [ ] |

### Section 6 — Mode B apply controls (Step 14)

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T14-1 | Mode B — ref invoice Partially Paid | Ref invoice Amount_Due > 0 | Apply Credits picker shows reference invoice + other open invoices | [ ] |
| T14-2 | Mode B — ref invoice Paid | Ref invoice Amount_Due = 0 | Apply Credits picker shows **only** other open invoices (not reference invoice) | [ ] |
| T14-3 | Mode B partial apply | Apply RM 200 of RM 500 CN to Invoice B | CN Credits_Remaining = RM 300; CN stage = Open | [ ] |
| T14-4 | Mode B apply until zero | Apply remaining RM 300 to Invoice C | CN Credits_Remaining = 0; CN stage = **Closed** | [ ] |
| T14-5 | Mode B refund | Mode B CN → Create Refund Note | Refund Note created; CN Refund updated; Credits_Remaining decreases | [ ] |
| T14-6 | Mode B mixed apply + refund | Apply RM 200, refund RM 150 on RM 500 CN | Credits_Remaining = 500 − 200 − 150 = 150; CN stays Open | [ ] |
| T14-7 | Mode A reaches apply form directly | Direct URL to Apply Credits form with Mode A CN | **Blocked** — "Mode A credit note cannot be manually applied" | [ ] |

### Section 7 — LHDN payload (regression on Step 07)

| # | Scenario | Expected | Pass |
|---|----------|----------|------|
| T15-1 | Mode A CN submitted to LHDN | Payload `reference_invoice_list` includes Reference_Invoice UUID | [ ] |
| T15-2 | Mode B CN applied to other invoices → LHDN | Payload includes Reference_Invoice UUID (priority 1) + applied invoice UUID(s) | [ ] |
| T15-3 | Mode B CN refund only → LHDN | Payload includes Reference_Invoice UUID | [ ] |

---

## Regression checks (carry-forward from v1)

| # | Check | Expected | Pass |
|---|-------|----------|------|
| R1 | No duplicate CN numbering | Still generates CN number once on add success | [ ] |
| R2 | Convert button shows for Sent, Partially Paid, Paid, Overdue | All four stages show Convert button | [ ] |
| R3 | Form load — no stage jump | Open Draft CN, edit, save → stays Draft | [ ] |
| R4 | Apply before approval blocked | Draft CN → Apply Credits action not visible | [ ] |
| R5 | Blueprint revert disabled | Approved CN (no CN UUID) does not auto-revert to Pending | [ ] |
| R6 | Legacy CNs (null Credit_Mode) | Old CNs open without error; Apply and Refund still available | [ ] |

---

## Rollback strategy (Steps 09–14)

### Before starting Batch E

```bash
git log -1 --oneline
```

Export live Creator → save as `XMT___Billing_System.pre-steps-09-14.ds` outside repo.

### Per batch rollback

| Batch | Revert |
|-------|--------|
| E | Restore `Credit_Note.deluge` (remove required flag), `Handle_Submission_Form_an4.deluge` (remove UUID/mandatory guards), `Convert_To_Credit_Note.deluge` (remove convert UUID guard) |
| F | Restore `Handle_reference_invoice_2.deluge` (remove line clone and mode detection), `Handle_Submission_Form_an4.deluge` (remove per-line guards), `Credit_Note.deluge` (remove `Credit_Mode` field), `Convert_To_Credit_Note.deluge` (remove mode set) |
| G | Restore `Handle_Submission_Form_an4.deluge` (remove cap check), `Approve/after/script_01.deluge` (remove cap recheck block) |
| H | Restore `script_01.deluge` (remove Mode A auto-apply), `Credit_Notes.deluge` (restore action conditions to Step 06 version), `Handle_Credit_Note_Select1.deluge`, `Apply_Credit_To_Invoices_1.deluge`, `Handle_Validation_Submiss3.deluge` |

---

## Export sync verification

Confirm these strings exist in **both** split files and `XMT___Billing_System.ds` after all batches:

| Check | Location |
|-------|----------|
| `Credit_Mode` field in Credit Note form | `Credit_Note.deluge` form field block |
| `Credit_Mode == "Mode A"` in Approve script | `Approve/after/script_01.deluge` |
| `Credit_Mode == "Mode B"` in action condition | `Credit_Notes.deluge` custom action |
| Per-line cap guard | `Handle_Submission_Form_an4.deluge` |
| Cumulative cap query | `Handle_Submission_Form_an4.deluge` |
| Line clone `deleteAll` + loop | `Handle_reference_invoice_2.deluge` |
| Convert UUID guard | `Convert_To_Credit_Note.deluge` |

---

## Post-deploy sign-off

| Item | Owner | Date | Status |
|------|-------|------|--------|
| Batch E deployed + smoke test | | | [ ] |
| Batch F deployed + smoke test | | | [ ] |
| Batch G deployed + smoke test | | | [ ] |
| Batch H deployed + smoke test | | | [ ] |
| Full test matrix T09–T15 | | | [ ] |
| Regression R1–R6 | | | [ ] |
| Final Creator export → repo sync | | | [ ] |

---

## Issue closure (Steps 09–14)

| New requirement | Step | Test |
|-----------------|------|------|
| Mandatory `Reference_Invoice` at creation | 09 | T09-1 to T09-5 |
| Reference invoice must have LHDN UUID | 09 | T09-2, T09-4 |
| Lines cloned from reference invoice | 10 | T10-1 to T10-7 |
| Per-line reduction-only rule | 10 | T10-4, T10-5 |
| `Credit_Mode` locked at creation | 11 | T11-1 to T11-7 |
| Cumulative approved CN cap | 12 | T12-1 to T12-6 |
| Approval-time concurrent cap recheck | 12 | T12-5 |
| Mode A auto-apply on approval | 13 | T13-1 to T13-4 |
| Apply / Refund hidden for Mode A | 13 | T13-5, T13-6 |
| Mode B apply — same ref if Amount_Due > 0 | 14 | T14-1, T14-2 |
| Mode B partial utilization cycle | 14 | T14-3 to T14-6 |
| LHDN reference UUID always present | 07+09 | T15-1 to T15-3 |
