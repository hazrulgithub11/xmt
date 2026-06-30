# Fix User-Facing Messages

Messages that contain internal jargon, raw variable dumps, or developer-only context. A finance user should be able to read any alert or info log and immediately understand what happened and what to do next.

---

## Priority 1 — Developer jargon (must fix)

### 1. `script_01.deluge` — lines 335 & 340 (CN closed / CN open after auto-apply)

**Current:**
```
info "Unified auto-apply complete. CN " + input.ID + " closed. Applied: " + apply_amount;
info "Unified auto-apply complete. CN " + input.ID + " open. Applied: " + apply_amount + ", Remaining: " + credits_remaining;
```

**Problems:**
- "Unified auto-apply" is internal feature naming — means nothing to finance
- "CN" is an abbreviation — write it out
- Raw record ID exposed (`input.ID`) — show the CN number instead (`input.Invoice_No`)

**Suggested replacement:**
```
info "Credit note " + input.Invoice_No + " approved. RM " + apply_amount + " applied to reference invoice. Credit note is now Closed.";
info "Credit note " + input.Invoice_No + " approved. RM " + apply_amount + " applied to reference invoice. RM " + credits_remaining + " remaining credit is available for future use. Credit note is now Open.";
```

---

### 2. `script_01.deluge` — line 16 (cumulative cap exceeded)

**Current:**
```
info "Approval rejected: cumulative credit note cap exceeded. Original invoice total: " + original_total + ", Already credited: " + crediting_cn_total + ", This CN: " + input.Grand_Total + ", Remaining: " + remaining_creditable;
```

**Problems:**
- "cumulative credit note cap" — internal rule name, not a finance term
- "This CN:" — abbreviation
- Raw comma-separated variable dump is hard to read
- "Approval rejected" used as a log prefix — no human context

**Suggested replacement:**
```
info "Approval blocked: the total credit notes for invoice " + ref_invoice_id + " would exceed the original invoice amount of RM " + original_total + ". Already credited: RM " + crediting_cn_total + ". This credit note: RM " + input.Grand_Total + ". Maximum remaining creditable: RM " + remaining_creditable + ". Please reduce the credit note amount and resubmit.";
```

---

### 3. Three item-change workflows — "Ensure Exchange Rate is not empty"

Files:
- `application/forms/Credit Note/workflow/Handle_Call_Charges_Item3.deluge` line 16
- `application/forms/Credit Note/workflow/Handle_Internet_Charges_I2.deluge` line 16
- `application/forms/Credit Note/workflow/Handle_Monthly_Rental_Ite2.deluge` line 16

**Current:**
```
info "Ensure Exchange Rate is not empty";
```

**Problems:**
- `info` is a silent server log — finance user never sees it. If this is meant as a user warning, it should be `alert`.
- "Ensure X is not empty" is a developer instruction, not a user-facing message.

**Suggested replacement (if meant for user):**
```
alert "Please enter the Exchange Rate before adding line items.";
```
If this is intentionally a silent developer trace (not shown to user), prefix it clearly:
```
info "[trace] Exchange Rate missing when item selected on Credit Note " + input.Invoice_No;
```

---

## Priority 2 — Slightly technical (clean up when convenient)

### 4. `Handle_Validation_Submiss2.deluge` — line 28 (reference invoice not selected)

**Current:**
```
alert "A Credit Note must be linked to a reference invoice. Please select a Reference_Invoice.";
```

**Problem:** `Reference_Invoice` (with underscore) is a field name leaked into the UI message.

**Suggested replacement:**
```
alert "A credit note must be linked to a reference invoice. Please select a reference invoice before saving.";
```

---

### 5. `Handle_reference_invoice_2.deluge` — line 142 & `Handle_Convert_Prefill.deluge` — line 128 (ineligible stage)

**Current:**
```
alert "Invoice stage '" + ref_stage + "' is not eligible for a credit note. Choose a different invoice.";
alert "Invoice stage '" + ref_stage + "' is not eligible for a credit note.";
```

**Problem:** "Invoice stage" is internal terminology. Finance users think in terms of invoice status (Paid, Sent, etc.) and know what those mean, but "stage" sounds like a workflow state.

**Suggested replacement:**
```
alert "A credit note cannot be raised against an invoice with status '" + ref_stage + "'. Only Sent, Overdue, Partially Paid, or Paid invoices are eligible. Please select a different invoice.";
```

---

### 6. `Submit_Credit_Note_to_LHD1.deluge` — line 3 (wrong status)

**Current:**
```
info "A credit note can only be submitted to LHDN when its status is closed.";
```

**Problem:** "closed" should be "Closed" (capitalised, consistent with Creator stage names). Also `info` is a server log — if a user clicks the button and nothing happens, they won't see this.

**Suggested replacement (as alert):**
```
alert "This credit note cannot be submitted to LHDN yet. Only credit notes with a status of Closed are eligible for LHDN submission.";
```

---

## Files to change

| File | Lines | Action |
|---|---|---|
| `blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge` | 16, 335, 340 | Rewrite (Priority 1) |
| `forms/Credit Note/workflow/Handle_Call_Charges_Item3.deluge` | 16 | Rewrite (Priority 1) |
| `forms/Credit Note/workflow/Handle_Internet_Charges_I2.deluge` | 16 | Rewrite (Priority 1) |
| `forms/Credit Note/workflow/Handle_Monthly_Rental_Ite2.deluge` | 16 | Rewrite (Priority 1) |
| `forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge` | 28 | Minor clean-up (Priority 2) |
| `forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` | 142 | Minor clean-up (Priority 2) |
| `forms/Credit Note/workflow/Handle_Convert_Prefill.deluge` | 128 | Minor clean-up (Priority 2) |
| `forms/Credit Note/workflow/actions/Submit_Credit_Note_to_LHD1.deluge` | 3 | Change info → alert + rewrite (Priority 2) |
