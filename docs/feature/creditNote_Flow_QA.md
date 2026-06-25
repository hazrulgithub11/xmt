# Credit Note Flow — Alignment Q&A

Use this before planning fix steps. For each question, pick **one** option (A–D).  
Correct answers are based on `[creditNote_Flow.md](./creditNote_Flow.md)`.

**How to use:** Work through the questions, note your choice, then compare with the answer key at the bottom. Flag any question where you disagree — that becomes a decision point before coding.

---

## A. Creation & Reference Invoice

### Q1. Can a credit note be created manually without selecting a `Reference_Invoice`?

- **A)** Yes — for promo / goodwill credits  
- **B)** Yes — but only if it will be applied to an invoice later  
- **C)** No — `Reference_Invoice` is mandatory at creation (convert and manual)  
- **D)** No — unless the customer has no invoices at all

**Your answer:** ___C

---

### Q2. What must the referenced invoice have before a credit note can be saved?

- **A)** Blueprint stage = Sent only  
- **B)** A valid LHDN `Invoice_UUID`  
- **C)** Amount_Due > 0  
- **D)** At least one payment recorded

**Your answer:** ___B

---

### Q3. When user picks Invoice A as `Reference_Invoice`, what can they do with credit note line items?

- **A)** Add any items (Monthly Rental, Internet, etc.) freely  
- **B)** Clone lines from Invoice A; only reduce qty or amount per line — no new unrelated items  
- **C)** Clone lines from Invoice A; can add new lines if total stays under invoice cap  
- **D)** Enter a single lump-sum credit amount with no line detail

**Your answer:** ___b

---

### Q4. Convert from Invoice vs Manual Add — what is the **only** difference at the start?

- **A)** Convert skips approval; manual requires approval  
- **B)** Convert auto-sets `Reference_Invoice` and clones lines; manual user picks invoice first then lines are cloned  
- **C)** Convert allows partial credit; manual must be full credit  
- **D)** Manual can reference multiple invoices; convert cannot

**Your answer:** ___b

---

## B. Invoice Status → Utilization Mode

### Q5. Reference invoice is **Sent** (unpaid). After CN is **Approved**, what happens?

- **A)** CN stays Open; user chooses Apply Credits or Refund Note  
- **B)** CN auto-applies to the same referenced invoice → `Credits_Remaining = 0` → Closed; no other invoices, no refund  
- **C)** CN auto-applies but stays Open until LHDN submit  
- **D)** CN stays Draft until user manually applies

**Your answer:** ___b

---

### Q6. Reference invoice is **Overdue** (unpaid). Which utilization mode is locked at creation?

- **A)** Mode B — open credit  
- **B)** Mode A — debt reduction only (same as Sent)  
- **C)** Depends on Amount_Due at approval time, not at creation  
- **D)** No mode lock — user decides at approval

**Your answer:** ___b

---

### Q7. Reference invoice is **Partially Paid**. After CN is **Approved**, what happens?

- **A)** Same as Sent — auto-apply to referenced invoice and Closed  
- **B)** CN stays **Open**; credit may be applied to **other** invoices or refunded; does **not** auto-reduce referenced invoice balance  
- **C)** CN is rejected — cannot credit a partially paid invoice  
- **D)** CN auto-applies to referenced invoice for the unpaid portion only, then stays Open for the rest

**Your answer:** ___b

---

### Q8. Reference invoice is **Paid**. After CN is **Approved**, what can finance do?

- **A)** Apply credit to the same paid invoice only  
- **B)** Apply to other open invoice(s) and/or create Refund Note for cash back  
- **C)** Nothing — paid invoices cannot have credit notes  
- **D)** Submit to LHDN only; no apply or refund in system

**Your answer:** ___b

---

### Q9. When is utilization mode (A vs B) determined?

- **A)** At approval time — based on latest invoice stage  
- **B)** At LHDN submit time  
- **C)** At credit note **creation** — locked from reference invoice stage at that moment  
- **D)** User selects mode manually on the CN form

**Your answer:** ___c

---

## C. Amount Caps & Concurrent Credit Notes

### Q10. Invoice total = RM 1,000. CN-1 (approved) = RM 400, CN-2 (approved) = RM 300. User creates CN-3 for RM 400 while still in **Draft**. What should happen at **save**?

- **A)** Allow save — cap only checked at apply time  
- **B)** Block save — RM 400 + RM 700 already approved = RM 1,100 exceeds RM 1,000  
- **C)** Allow save — drafts don't count toward cap  
- **D)** Allow save but cap at RM 300 only (remaining = 1,000 − 700)

**Your answer:** ___b

---

### Q11. Same as Q10, but CN-3 was saved as Draft when only CN-1 was approved (RM 400). CN-2 (RM 300) gets approved **after** CN-3 draft exists. User tries to **approve CN-3** for RM 400. What should happen?

- **A)** Approve CN-3 — it was valid when drafted  
- **B)** Reject approval — at approval time, 400 + 300 + 400 = 1,100 > 1,000  
- **C)** Approve CN-3 but auto-reduce amount to RM 300  
- **D)** Approve CN-3 — only per-CN cap matters, not cumulative

**Your answer:** ___b

---

### Q12. Multiple credit notes against one invoice are allowed. The rule is:

- **A)** Only one CN per invoice, ever  
- **B)** Unlimited CNs; each can exceed original invoice if applied to different invoices  
- **C)** Multiple CNs allowed; **sum of approved CN totals** on same reference invoice must not exceed original invoice total  
- **D)** Multiple CNs allowed; sum of **all** CNs (including Draft) counts toward cap

**Your answer:** ___c

---

### Q13. Per-line validation: Invoice A line "Internet" = RM 200. User credits RM 250 on that line in the CN. What should happen?

- **A)** Allow — only document total matters  
- **B)** Block — line credit cannot exceed source line amount  
- **C)** Allow if document total still under invoice cap  
- **D)** Allow with approver override only

**Your answer:** ___b

---

## D. Approval, Stages & Actions

### Q14. When can user click **Apply Credits to Invoices** on a credit note?

- **A)** Any time after Draft is saved  
- **B)** Only when CN is Approved **and** locked in **Mode B** (reference invoice Partially Paid or Paid)  
- **C)** Only when CN is Open, regardless of mode  
- **D)** Never — system always auto-applies

**Your answer:** ___b

---

### Q15. When can user click **Create Refund Note** from a credit note?

- **A)** Any time after Approved  
- **B)** Only in **Mode B** (Partially Paid or Paid reference invoice)  
- **C)** Only after LHDN submit  
- **D)** Mode A and Mode B both allow refund

**Your answer:** ___b

---

### Q16. Mode A CN (Sent reference invoice), RM 500 credit, approved. What is `Credits_Remaining` and blueprint stage immediately after approval?

- **A)** Credits_Remaining = 500, Open  
- **B)** Credits_Remaining = 0, Closed  
- **C)** Credits_Remaining = 500, Closed  
- **D)** Credits_Remaining = 0, Open until LHDN

**Your answer:** ___b

---

### Q17. Mode B CN, RM 500 approved. User applies RM 200 to Invoice B. What is the state?

- **A)** Credits_Used = 200, Credits_Remaining = 300, Open  
- **B)** Credits_Remaining = 0, Closed  
- **C)** Credits_Used = 500, Closed  
- **D)** Stays Approved until fully utilized

**Your answer:** ___a

---

## E. LHDN Submission

### Q18. When can **Submit Credit Note to LHDN** run?

- **A)** As soon as CN is Approved  
- **B)** When blueprint stage = **Closed** (credit fully consumed)  
- **C)** Any time after Draft  
- **D)** Only after Refund Note is paid

**Your answer:** ___b

---

### Q19. What must the LHDN payload include for the credit note reference?

- **A)** Applied invoice UUID(s) only — Reference_Invoice optional  
- **B)** `Reference_Invoice` UUID + invoice number (mandatory)  
- **C)** Nothing — standalone CN is valid for promo  
- **D)** Customer TIN only

**Your answer:** ___b

---

### Q20. Mode A CN auto-closed on unpaid invoice. LHDN submit references:

- **A)** The same `Reference_Invoice` UUID (the invoice that was reduced)  
- **B)** Whichever invoice user picked in Apply Credits popup  
- **C)** No reference — internal adjustment only  
- **D)** Refund Note UUID instead

**Your answer:** ___a

---

## F. Edge Cases (confirm intent)

### Q21. Reference invoice stage changes from **Sent** to **Partially Paid** while CN is still in **Pending Approval**. Utilization mode should:

- **A)** Re-evaluate at approval — switch to Mode B if now Partially Paid  
- **B)** Stay locked to Mode A (locked at creation)  
- **C)** Cancel the CN automatically  
- **D)** Block approval until invoice is Paid

**Your answer:** ___a

---

### Q22. Mode B CN: can user apply credit back to the **same** reference invoice (the Paid invoice it was created against)?

- **A)** Yes — always allowed  
- **B)** No — Mode B only allows **other** invoices (reference was Paid/Partially Paid; credit is not for reducing that invoice's balance)  
- **C)** Yes — but only if Amount_Due > 0 on reference invoice  
- **D)** Not defined in flow yet

**Your answer:** ___c

---

### Q23. Draft credit notes count toward the cumulative cap when checking a **new** draft save?

- **A)** Yes — all drafts count  
- **B)** No — only **approved** CNs count; drafts checked only at their own save/approval against remaining creditable amount  
- **C)** No — drafts never count  
- **D)** Yes — but only drafts from same user

**Your answer:** ___b

---

## Answer Key


| Q   | Answer         | One-line rationale                                                                      |
| --- | -------------- | --------------------------------------------------------------------------------------- |
| 1   | **C**          | No standalone manual CN; reference mandatory                                            |
| 2   | **B**          | Valid LHDN `Invoice_UUID` required on reference                                         |
| 3   | **B**          | Clone source lines; reduce qty/amount only                                              |
| 4   | **B**          | Convert auto-sets reference; manual user picks first                                    |
| 5   | **B**          | Mode A: auto-apply same invoice → Closed                                                |
| 6   | **B**          | Overdue = unpaid = Mode A                                                               |
| 7   | **B**          | Partially Paid = Mode B, no auto-attack on reference                                    |
| 8   | **B**          | Paid = Mode B: other invoices or refund                                                 |
| 9   | **C**          | Mode locked at creation *(v1; Q21 re-eval at approval = later)*                         |
| 10  | **B**          | v1: approved CNs only at save — **later:** strict draft/pending reservation (Q10/Q23)   |
| 11  | **B**          | Approval-time recheck rejects concurrent over-cap                                       |
| 12  | **C**          | Cumulative approved total ≤ original invoice                                            |
| 13  | **B**          | Per-line cap                                                                            |
| 14  | **B**          | Apply action only in Mode B after Approved                                              |
| 15  | **B**          | Refund only in Mode B                                                                   |
| 16  | **B**          | Auto-applied; remaining 0; Closed                                                       |
| 17  | **A**          | Partial apply; stays Open                                                               |
| 18  | **B**          | LHDN when Closed                                                                        |
| 19  | **B**          | Mandatory Reference_Invoice UUID + number                                               |
| 20  | **A**          | Same reference invoice UUID                                                             |
| 21  | **B** *(v1)*   | Locked at creation for first fix — **later:** A (re-evaluate at approval)               |
| 22  | **C**          | Same reference invoice in Mode B only if `Amount_Due > 0`                               |
| 23  | **B** *(v1)*   | Approved only at save — **later:** strict pending/draft reservation (Q10/Q23)         |


---

## Deferred — later implementation ⏳

Not in the first fix pass. Accepted as known edge-case gaps until a follow-up.

### Q21 — Mode re-evaluation at approval

| | |
|---|---|
| **Your answer** | A — re-evaluate at approval if reference invoice stage changed |
| **Ship now (v1)** | B — mode locked at creation |
| **Later** | Implement A when invoice moves Sent → Partially Paid / Paid while CN is Pending Approval |
| **Risk if deferred** | CN may auto-apply (Mode A) even though invoice was paid before approval |

---

### Q10 / Q23 — Draft and pending CNs in cumulative cap

| | |
|---|---|
| **Your answer** | B — only approved CNs count at save |
| **Ship now (v1)** | B — same; approval-time recheck on approved totals |
| **Later** | Strict: reserve cap for Draft + Pending Approval CNs on same invoice |
| **Risk if deferred** | Multiple concurrent drafts can pass save individually; one may fail only at approval |

---

## Resolved decisions

### Q22 — Apply to same reference invoice in Mode B ✅

**Decision:** **C** — Yes, but only if `Amount_Due > 0` on the reference invoice.

| Reference stage | Same reference invoice in Apply Credits? |
|-----------------|------------------------------------------|
| Partially Paid (Amount_Due > 0) | Yes — manual apply allowed |
| Paid (Amount_Due = 0) | No — other invoices or Refund Note only |

---

## Notes on ambiguous items

### Q10 / Q23 — Do pending drafts reserve cap at save?

**Status:** ⏳ **Deferred — later implementation** (v1 uses **B**; see Deferred section above.)

**Flow doc today:** Cap at save uses "remaining creditable amount" against **approved** CNs only; approval recheck uses approved totals.


| Option                   | Behavior                                                                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Strict (later)**       | At save: `remaining = invoice total − sum(approved CNs) − sum(pending-approval CNs on same invoice)`. Prevents three drafts each for full amount. |
| **Looser (v1 ship now)** | At save: only approved CNs count; Q10 blocks CN-3 at save if 400+700>1000; concurrent drafts could still race until approval.                     |


**Your preference:** **B** — ship in v1; strict reservation later.

---

## Sign-off checklist

When all answers match (or ambiguities resolved), we are aligned to write fix steps.


| Topic                                                 | Aligned? (Y/N) | Notes |
| ----------------------------------------------------- | -------------- | ----- |
| Reference invoice mandatory + UUID                    |                |       |
| Line clone / reduce only                              |                |       |
| Mode A (Sent/Overdue) vs Mode B (Partially Paid/Paid) |                |       |
| Mode locked at creation (Q21)                         | Y (v1)         | Locked at creation; re-eval at approval = later |
| Cumulative cap save + approval                        | Y (v1)         | Approved totals only; strict draft reserve = later |
| Draft reservation policy (Q10/Q23)                    | ⏳ Later       | v1 = B; known race until strict cap             |
| Mode B apply-to-same-invoice (Q22)                    | Y              | C — only if Amount_Due > 0 |
| LHDN when Closed + mandatory reference UUID           |                |       |


**Reviewed by:** _______________ **Date:** _______________