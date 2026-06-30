# Debit Note — Wrong Flow Test Plan

Test plan to prove gaps between **current system behaviour** and **real billing flow**.  
Run in **UAT / sandbox** only. Record evidence as you go — we will update the **Test Results** section after each case.

**Source of truth (code):** `XMT___Billing_System.ds`  
**Compare against:** Credit Note fixes in `docs/feature/CREDIT_NOTE_CHANGES_SUMMARY.md` — Debit Note did not get the same treatment.

---

## Summary for manager (draft — update after testing)

> Debit Note was built by copying the Invoice pattern. In real billing, a debit note is an **additional charge** linked to an original tax invoice — not a duplicate invoice. Initial code review found: full-invoice clone on convert, no cumulative cap vs reference invoice, customer statements omit debit notes, payment prefill may pull wrong customers, and journal entries post at Approve before LHDN/Send. This document tracks UAT tests to **prove** each issue before we fix it.

| Area | Suspected wrong flow | Test ID | Confirmed? |
|------|----------------------|---------|------------|
| Convert from invoice | Clones full invoice → double billing | DN-01 | — |
| Approval guard | No debit cap vs reference invoice | DN-02 | — |
| AR / balances | Reference invoice & roll-ups ignore DN | DN-03, DN-08 | — |
| Payment Received | Wrong customer's DNs in prefill | DN-04 | — |
| Customer Statement | Debit notes missing in period | DN-05 | — |
| Journal timing | JE at Approve, not Send/LHDN | DN-06, DN-07 | — |
| Lifecycle | Payable only after Sent | DN-09 | — |
| Audit trail | Paid → Sent allowed | DN-10 | — |
| Controls that work | Delete block, LHDN ref validation | DN-11, DN-12 | — |

---

## Before you start

### Environment

- [ ] Testing on **live Creator app** (not only local repo files)
- [ ] Sandbox LHDN or production — note which: _______________

### Test data to create

| Label | Purpose | Record no. | Notes |
|-------|---------|------------|-------|
| **Customer X** | Payment prefill cross-customer test | | |
| **Customer Y** | Payment prefill cross-customer test | | |
| **INV-A** | Sent invoice, LHDN UUID + public link, e.g. RM 100 due | | |
| **DN-B** | Manual DN vs INV-A, e.g. RM 50 | | |
| **DN-C** | Second DN vs same INV-A (cap test) | | |
| **DN-A** | From Convert To Debit Note on INV-A | | |

### Users

| Role | User | Used for |
|------|------|----------|
| Finance Executive | | Create, submit, LHDN |
| Finance Manager | | Approve, Send |

### What to capture each test

- Screenshot or screen recording
- Record numbers (`Invoice_No`, DN `Invoice_No`, Payment `Payment_Received_No`)
- Field values: `Grand_Total`, `Amount_Due`, `Amount_Paid`, blueprint stage
- Journal Entry no. (if created)
- Date/time of action

---

## Real billing — quick reference

| Rule | Correct behaviour |
|------|-------------------|
| Purpose | Debit note **increases** what customer owes (under-bill, extra usage, price correction up) |
| Reference | Must link to an **LHDN-valid** original invoice |
| Document | **Separate** number; not a full duplicate of the original unless original is voided/replaced |
| Convert | Should open prefill for **additional charges only** — not clone full invoice totals |
| Cap | Total debits against one invoice should be **controlled** (mirror credit note cap logic) |
| AR | Customer total owed must include open debit notes (statements, opening balance, invoice roll-ups) |
| Journal | Should align with policy — typically **Send** or post-LHDN, not before customer-facing send |
| Payment | Allocate to DN; update `Amount_Paid` / `Amount_Due` and stage |

---

## P0 — Critical (financial risk)

### DN-01 — Convert To Debit Note clones full invoice

**Suspected bug:** `Convert_To_Debit_Note1` copies all header totals and line items from invoice → customer may owe **twice** for same charges.

**Precondition:** INV-A = Sent, `Grand_Total` = RM ______, `Amount_Due` = RM ______, LHDN submitted.

| Step | Action | Done |
|------|--------|------|
| 1 | Open INV-A | [ ] |
| 2 | Run **Convert To Debit Note** | [ ] |
| 3 | Open new DN-A (Draft) | [ ] |

**Checks**

| # | Real billing (expected) | Actual (fill when tested) | Pass? |
|---|-------------------------|---------------------------|-------|
| 1 | Line items empty or **additional charges only** | | |
| 2 | `Grand_Total` = additional amount only (not full INV-A total) | | |
| 3 | `Reference_Invoice` = INV-A | | |
| 4 | If both INV-A + DN-A approved/sent: customer total ≠ 2× same base charge | | |

**Evidence:** INV-A record: ______ | DN-A record: ______

**Result status:** ⬜ Not tested | ⬜ Fail (wrong flow) | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-02 — No cumulative debit cap vs reference invoice

**Suspected bug:** Credit Note blocks approval if credits exceed invoice total; Debit Note has **no** equivalent cap.

**Precondition:** INV-A `Grand_Total` = RM ______

| Step | Action | Done |
|------|--------|------|
| 1 | Create DN-B: `Reference_Invoice` = INV-A, `Grand_Total` = RM 50 (or half of INV-A) | [ ] |
| 2 | Approve + LHDN + Send DN-B | [ ] |
| 3 | Create DN-C: same reference, `Grand_Total` = RM 60 (or amount that makes total > INV-A) | [ ] |
| 4 | Submit for approval → **Approve** DN-C | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | System **blocks** approval or warns cumulative debits > reference | | |
| 2 | Compare: Credit Note would block in same scenario (optional) | | |

**Evidence:** DN-B: ______ | DN-C: ______ | Approval message: ______

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-03 — Reference invoice balance unchanged; roll-ups may ignore DN

**Suspected bug:** DN is standalone receivable but invoice `Amount_Due`, previous balance, and `Total_Amount_Due` do not include debit notes.

**Precondition:** INV-A `Amount_Due` = RM ______ before DN

| Step | Action | Done |
|------|--------|------|
| 1 | Note INV-A `Amount_Due`, `Amount_Paid`, blueprint stage | [ ] |
| 2 | DN-B (RM 50) approved + sent | [ ] |
| 3 | Re-open INV-A — note fields again | [ ] |
| 4 | Create or open another **later invoice** for same customer — check `Previous_Balance` / `Total_Amount_Due` if shown | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | INV-A `Amount_Due` unchanged **only if** DN tracked elsewhere in AR | | |
| 2 | Customer total AR includes DN RM 50 somewhere visible to finance | | |
| 3 | Later invoice previous balance **includes** open DN | | |

**Evidence:** INV-A before/after: ______ | Later invoice: ______

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-04 — Payment Received prefill — wrong customer's debit notes

**Suspected bug:** Live `.ds` query operator precedence may list **Partially Paid** / **Sent** DNs from **any** customer when prefilling payment for Customer Y.

**Precondition:** Customer X and Customer Y each have at least one Sent DN with `Amount_Due` > 0

| Step | Action | Done |
|------|--------|------|
| 1 | New **Payment Received**, type **Invoice/Debit Note** | [ ] |
| 2 | Select **Customer Y** only | [ ] |
| 3 | Review prefilled line items | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | Lines show **only Customer Y** documents | | |
| 2 | No Customer X invoice or debit note in list | | |

**Evidence:** Screenshot of line items with customer/doc numbers: ______

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-05 — Customer Statement omits debit notes in period

**Suspected bug:** `collect_debit_note_info` returns empty list — DN rows missing from statement transactions.

**Precondition:** DN-B Sent/Overdue in test period with `Amount_Due` > 0

| Step | Action | Done |
|------|--------|------|
| 1 | Generate **Statement of Outstanding** for customer, date range including DN-B `Invoice_Date` | [ ] |
| 2 | Check opening balance vs transaction lines | [ ] |
| 3 | Manual sum: invoice due + DN due vs statement `Balance_Due` | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | Transaction line **Debit Note** with amount in period | | |
| 2 | `Balance_Due` matches manual AR total | | |

**Evidence:** Statement record: ______ | Manual total: RM ______ | Statement total: RM ______

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

## P1 — High (process / accounting timing)

### DN-06 — Journal created at Approve (before LHDN and Send)

**Suspected bug:** Debit Note creates Journal Entry on **Approve**; Invoice journal is created at **Send** (live `.ds`).

| Step | Action | Done |
|------|--------|------|
| 1 | New DN, Pending Approval, **no** LHDN UUID yet | [ ] |
| 2 | **Approve** only — do not LHDN submit, do not Send | [ ] |
| 3 | Find Journal Entry linked to this DN | [ ] |
| 4 | (Optional) Compare: approve invoice without send — journal behaviour | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | No JE until Send / post-LHDN (per invoice policy) | | |
| 2 | DN blueprint = Approved, UUID still empty, but JE exists | | |

**Evidence:** DN: ______ | JE no.: ______ | DN stage: ______ | UUID: ______

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-07 — Send blocked without LHDN; manual LHDN vs invoice auto

| Step | Action | Done |
|------|--------|------|
| 1 | Approved DN without `Invoice_UUID` / `QR_Invoice_Public_Link` | [ ] |
| 2 | Try blueprint **Send Invoice** | [ ] |
| 3 | Run **Submit Debit Note to LHDN**, then Send again | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | Send **blocked** until LHDN fields populated | | |
| 2 | After LHDN submit, Send succeeds → Sent or Overdue | | |
| 3 | Note: Invoice submits LHDN on Approve — process inconsistency | | |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-08 — Tenancy opening balance ignores debit note payment

**Suspected bug:** Invoice payment calls `tenancy.calculate_opening_balance_by_tenancy`; debit note payment does not. Opening balance function only sums invoices.

| Step | Action | Done |
|------|--------|------|
| 1 | Note **Tenancy → Opening Balance** for customer | RM ______ |
| 2 | Pay DN fully via Payment Received | [ ] |
| 3 | Re-check Opening Balance | RM ______ |
| 4 | Pay an invoice (partial or full) for same customer | [ ] |
| 5 | Re-check Opening Balance again | RM ______ |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | Opening balance decreases after DN payment (if DN in OB logic) | | |
| 2 | Opening balance changes after invoice payment | | |
| 3 | Asymmetric behaviour = bug | | |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-09 — Payment only after Sent (not Approved)

**Documents lifecycle gap with DN-06 (JE at Approved, pay only after Sent).

| Step | Action | Done |
|------|--------|------|
| 1 | DN **Approved**, not Sent, `Amount_Due` > 0 | [ ] |
| 2 | New Payment Received — check prefill for this DN | [ ] |
| 3 | Send DN, then check prefill again | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | DN **not** in payment prefill while Approved only | | |
| 2 | DN **appears** after Sent/Overdue/Partially Paid | | |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

## P2 — Medium (audit / controls)

### DN-10 — Paid → Sent blueprint transition

**Suspected bug:** Blueprint allows moving Paid debit note back to Sent without controlled reversal.

| Step | Action | Done |
|------|--------|------|
| 1 | Fully pay DN → stage **Paid** | [ ] |
| 2 | Check if **Paid → Sent** transition is available | [ ] |
| 3 | If executed, note effect on `Amount_Due` / JE | [ ] |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-11 — Cannot delete invoice with linked debit note (control — should pass)

| Step | Action | Done |
|------|--------|------|
| 1 | INV-A referenced by DN-B | [ ] |
| 2 | Try delete INV-A | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | Delete **blocked** with clear message | | |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-12 — Reference invoice without LHDN rejected (control — should pass)

| Step | Action | Done |
|------|--------|------|
| 1 | New DN, select reference invoice **without** UUID or public link | [ ] |

**Checks**

| # | Real billing (expected) | Actual | Pass? |
|---|-------------------------|--------|-------|
| 1 | Alert / field cleared — cannot use as reference | | |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

### DN-13 — Credit-available popup on Send (environment-specific)

**Suspected bug (local repo only):** Send Invoice may open `Notify_Credits_Available` with Debit Note ID in Invoice field — broken credit apply.

**Note:** Live `.ds` Send Invoice for DN may **not** show this popup. Mark N/A if not shown.

| Step | Action | Done |
|------|--------|------|
| 1 | Customer with `Credit_Available` > 0 | [ ] |
| 2 | Send approved DN | [ ] |
| 3 | If popup appears, click Yes — observe error or wrong record | [ ] |

**Result status:** ⬜ Not tested | ⬜ Fail | ⬜ Pass | ⬜ N/A

**Tester notes:**

```

```

---

## Quick results tracker

Update after each test. **Pass** = matches real billing. **Fail** = wrong flow confirmed.

| ID | Title | Status | Record refs | Date tested |
|----|-------|--------|-------------|-------------|
| DN-01 | Convert clones full invoice | ⬜ | | |
| DN-02 | No debit cap | ⬜ | | |
| DN-03 | AR roll-ups ignore DN | ⬜ | | |
| DN-04 | Payment wrong customer | ⬜ | | |
| DN-05 | Statement missing DN | ⬜ | | |
| DN-06 | JE at Approve | ⬜ | | |
| DN-07 | LHDN / Send gate | ⬜ | | |
| DN-08 | Tenancy OB ignores DN | ⬜ | | |
| DN-09 | Pay only after Sent | ⬜ | | |
| DN-10 | Paid → Sent | ⬜ | | |
| DN-11 | Delete invoice blocked | ⬜ | | |
| DN-12 | LHDN ref validation | ⬜ | | |
| DN-13 | Credit popup on Send | ⬜ | | |

---

## Confirmed bugs log (fill as tests complete)

_Agent will help expand this section when you report results._

| ID | Confirmed? | Wrong behaviour observed | Real billing expectation |
|----|------------|--------------------------|--------------------------|
| DN-01 | | | |
| DN-02 | | | |
| DN-03 | | | |
| DN-04 | | | |
| DN-05 | | | |
| DN-06 | | | |
| DN-07 | | | |
| DN-08 | | | |
| DN-09 | | | |
| DN-10 | | | |
| DN-11 | | | |
| DN-12 | | | |
| DN-13 | | | |

---

## Recommended test order

1. **DN-01** — strongest proof for manager (double billing)
2. **DN-02** — shows missing guard vs Credit Note
3. **DN-04** — payment data integrity
4. **DN-05** — reporting gap
5. **DN-06** — accounting timing
6. DN-03, DN-07, DN-08, DN-09
7. DN-11, DN-12 (confirm controls work)
8. DN-10, DN-13 if time permits

---

## Changelog

| Date | Update |
|------|--------|
| 2026-06-29 | Initial test plan created from code audit (`XMT___Billing_System.ds`) |
