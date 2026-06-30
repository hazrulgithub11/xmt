# Financial Audit — Email Input Form / `send_email_.deluge`

**Document purpose:** Record finance-control findings on the current “Send Email” workflow so it can be fixed to behave like a governed billing system — not just a mail-sending script.

**Scope:** `application/forms/Email Input Form/workflow/send_email_.deluge`, related entry points (`Send_Email5`, `Send_Email6`), and comparison with `Send_Invoice.deluge` and Zoho’s documented PDF-via-email pattern ([Send page as PDF attachment via email](https://help.zoho.com/portal/en/kb/creator/zoho-creator-academy/pages/articles/send-page-as-pdf-attachment-via-email#Steps_to_Follow)).

**Auditor lens:** Can the wrong document, wrong PDF, or wrong recipient leave the system with no trace on the source billing record?

**Status:** Code and design review only — live UAT not yet run.

---

## Executive summary

The workflow **can** send emails with PDF attachments using Zoho’s documented `record-pdf` + `invokeurl` + `sendmail` pattern. Technically it works.

From a **billing control** perspective, it behaves like an **uncontrolled side door**: it can email customers without updating invoice status, without GL impact, without a reliable audit trail on the source document, and with several failure modes that finance would not accept in production.

**Plain English:** The button sends the email, but the billing system does not “know” or “remember” that the customer was officially notified.

---

## What this workflow does today

1. User opens **Email Input Form** popup from Invoice (`Send_Email5`) or Pro Forma (`Send_Email6`).
2. On load, subject/body are pre-filled from the active `Email_Templates` row for that document type.
3. User enters To/CC, may edit subject/body, and submits.
4. On success, `send_email_.deluge` fetches the source record, replaces `{placeholders}`, downloads a PDF via a public `record-pdf` URL, and sends the email.
5. Parent page refreshes. **No update** is made to the Invoice / Pro Forma / Debit Note source record.

**Plain English:** It’s a manual email composer with a PDF attached — not the official “invoice sent to customer” process.

---

## Control objectives (what a true billing system must guarantee)

| # | Control objective | Plain English |
|---|-------------------|---------------|
| C1 | Correct document sent | The PDF must be for the invoice the user thinks they are sending. |
| C2 | Correct amounts and customer details in email | Numbers and names in the email must match the live record. |
| C3 | Correct PDF layout by charge type | Fixed, telephone, and misc invoices must use the right template. |
| C4 | Send only when business rules allow | Draft or unapproved documents must not go to customers by accident. |
| C5 | Audit trail on source document | Finance must see who sent what, to whom, and when — on the invoice itself. |
| C6 | No silent failure | If the PDF or data fetch fails, the email must not go out with blank or wrong content. |
| C7 | One consistent send path per document type | Every send button should produce the same PDF and follow the same rules. |

---

## Findings

Severity: **Critical** = fix before production reliance · **High** = fix in this initiative · **Medium** = address soon · **Low** = hygiene / documentation

---

### F1 — No audit trail on the source billing document

**Finding (Critical):** `send_email_` creates an `Email_Input_Form` row and sends mail, but does **not** update the Invoice, Pro Forma, or Debit Note with sent date, sent-by, sent-to, or send method. Commented-out code in `Send_Invoice` suggests a `Send_Email` flag was planned but never finished.

**Plain English:** After you click Send Email, the invoice still looks like it was never sent — there is no official record that the customer received it.

---

### F2 — Bypasses billing lifecycle (blueprint / GL)

**Finding (Critical):** Unlike **Send Invoice** from Approved, this path does not move blueprint stage (e.g. Sent / Overdue) and does not create the accounts-receivable journal entry.

**Plain English:** You can email a customer an invoice without the system treating it as “sent” or recording it in the books.

---

### F3 — No stage or approval guard on Send Email button

**Finding (High):** `Send_Email5` (Invoice) has **no blueprint condition** — it is available regardless of stage. A user may be able to email a Draft or Approved invoice without going through the governed send path.

**Plain English:** Anyone with the button can email an invoice even when finance says it is not ready to go out.

---

### F4 — Resend on every form edit (`on add or edit`)

**Finding (High):** The workflow triggers on **`on success` for both add and edit**. Updating an existing Email Input Form record can send the email again.

**Plain English:** Saving the popup a second time can accidentally email the customer again.

---

### F5 — No error handling for API or PDF failure

**Finding (High):** If `zoho.creator.getRecordById` fails, `piData` / `invData` / `dnData` may never be set, but placeholder replacement still runs. If `invokeurl` fails to fetch the PDF, `sendmail` may still run with a bad or empty attachment. There is no guard, log, or user alert.

**Plain English:** The email might go out with wrong text in the body or a broken PDF, and nobody would be warned.

---

### F6 — Hardcoded public PDF URLs and private keys

**Finding (High):** PDF download URLs are hardcoded in Deluge with embedded `zohopublic.com` private keys and report link names (e.g. `Copy_of_All_Invoices`, `Copy_of_All_Pro_Forma_Invoices`).

**Plain English:** If someone changes the report or Zoho rotates the key, all customer emails could suddenly have missing or wrong PDFs — and fixing it means editing code, not settings.

**Additional finance concerns:**
- Public URLs may allow invoice download without login if the URL pattern is guessed (data privacy / PDPA).
- Report names like `Copy_of_All_Invoices` suggest copies of production reports — template drift risk.

**Plain English (privacy):** Customer invoice PDFs might be reachable by URL without logging in, which is a confidentiality risk.

---

### F7 — Two different PDF generation methods in the same app

**Finding (High):** **Send Invoice** (first send from Approved) uses native Deluge syntax:

```
Attachments :template:Fixed_And_Telephone_Charges_Invoice:Invoice recId as PDF
```

**Send Email** (`send_email_`) and **Send Invoice** (resend from Sent/Paid/Overdue) use `invokeurl` + public `record-pdf` URL instead.

**Plain English:** The same invoice might look different depending on which button you pressed — that is unacceptable for customer-facing documents.

**Audit test required:** For one invoice, compare PDF from Send Invoice vs Send Email. Layout, totals, tax, and document number must match.

---

### F8 — Invoice charge category branching may be incomplete

**Finding (Medium):** `send_email_` only branches on `Miscellaneous Charges` vs everything else. The system also distinguishes **Fixed Charges** and **Telephone Charges**. Reminder schedules use `Fixed_And_Telephone_Charges_Invoice` explicitly; the `else` branch in `send_email_` uses report `Copy_of_All_Invoices`.

**Plain English:** Telephone invoices might get the wrong PDF layout if the report tied to that URL is not the same template finance expects.

---

### F9 — Debit Note support may be orphaned

**Finding (Medium):** `send_email_` has a Debit Note branch, and `Email_Input_Form` lists Debit Note as a document type. Invoice and Pro Forma have record actions opening the popup; **no equivalent action** was found for Debit Note in the local repo. Debit Note has a `Send_Email` **checkbox field** on the form, not a popup workflow.

**Plain English:** The debit note email code may exist but nobody can reach it the same way as invoice — or staff use a different, unknown path.

**Note:** Debit note number is stored in field `Invoice_No` by design (`Handle_Invoice_Creation2`). Auditors must confirm the PDF filename and placeholders show the debit note number, not a reference invoice.

**Plain English:** The field is confusingly named “Invoice No” but holds the debit note number — verify the PDF shows the right number.

---

### F10 — Recipients are fully manual in the popup

**Finding (Medium):** `Handle_Load_Of_The_Form` pre-fills subject and body from template but does **not** auto-fill **To** from `Customer_E_mail`.

**Plain English:** Staff must type the customer email by hand, so typos can send invoices to the wrong person with no system check.

---

### F11 — Multiple parallel email paths for the same document types

**Finding (High):** Email is not sent through one governed channel.

| Document | Paths found |
|----------|-------------|
| Invoice | `Send_Invoice`, `Send_Email5` → `send_email_`, reminder schedules |
| Pro Forma | `Send_Email6` → `send_email_`, `Send_Email1` (checkbox + hardcoded body), `Send_Proforma_Invoice` |
| Debit Note | `send_email_` branch only (entry point unclear) |

**Plain English:** Different buttons send different wording and maybe different PDFs for the same type of document — finance cannot rely on one standard customer communication.

**Example:** `Send_Email1` on Pro Forma uses a **hardcoded** subject/body and `attachments : template : Proforma_Invoice as pdf` — not the `Email_Templates` table.

**Plain English:** Pro forma can be sent with old fixed text that finance cannot change without editing code.

---

### F12 — Credit Note and Payment Received not in Email Input Form

**Finding (Low / scope gap):** `Email_Input_Form` supports Invoice, Pro Forma Invoices, and Debit Note only. Payment Received and Credit Note have their own send actions elsewhere.

**Plain English:** If the goal is one standard “send document email” tool, it does not cover all billing documents yet.

---

### F13 — Alignment with Zoho documentation (technical, not sufficient alone)

**Finding (Informational):** The workflow follows the Academy pattern: build `record-pdf` URL → `invokeurl` GET → `.setparamname("file")` → `sendmail` with `Attachments :file:`. This matches [Zoho Deluge sendmail](https://www.zoho.com/deluge/help/misc-statements/send-mail.html) and [export URLs](https://www.zoho.com/creator/newhelp/app-settings/print-export-url.html).

**Plain English:** The developer followed Zoho’s how-to for attaching a PDF — but following the tutorial does not make it a proper billing control.

---

### F14 — Wrong template type risk (user education)

**Finding (Medium):** This path uses `Template_Type = "Invoice"` (loaded on form open), **not** `Invoice Reminder` (First/Final). That is correct for a delivery email, but staff must not confuse **Send Email** with overdue reminder emails sent by schedule.

**Plain English:** This sends “here is your invoice,” not “your payment is overdue” — but only if the right template is active in settings.

---

## Preliminary audit opinion

| Area | Rating | Plain English |
|------|--------|---------------|
| Zoho PDF pattern | Pass (technical) | The PDF attachment method is valid. |
| Billing controls | Fail | The system does not treat this as an official send. |
| Data integrity | Fail | Errors can slip through without stopping the email. |
| Consistency with Send Invoice | Fail | Two ways to send, possibly two different PDFs. |
| Maintainability | Fail | Secrets and report names are buried in code. |
| Completeness | Unclear | Debit note path may be unused; multiple pro forma paths. |

**Overall:** Treat **Send Email** as a **high-risk manual override** until controls in the target state below are implemented.

**Plain English:** Do not trust this as the main way invoices go to customers until it is fixed.

---

## Recommended UAT test plan (before and after fix)

Run these in live Creator and record pass/fail.

### Sample selection

5 records per document type: Draft (if send allowed), Approved, Sent, Miscellaneous invoice, Fixed or Telephone invoice.

### Per test, record

| Check | Plain English |
|-------|---------------|
| Document number | Which invoice are we testing? |
| Blueprint stage at send time | Was it allowed to go out? |
| Button used | Send Invoice vs Send Email |
| To / CC | Who actually received it? |
| Subject/body after placeholders | Do names and numbers look right? |
| PDF: doc no., grand total, tax, customer | Does the attachment match the system? |
| Source record updated? | Did the invoice show as sent? |
| Duplicate on form re-save? | Did editing the popup send twice? |

### Reconciliation tests

1. PDF grand total = source record `Grand_Total`.
2. Email body placeholders = live field values.
3. Send Email PDF = Send Invoice PDF (same invoice, same layout).
4. After Send Email, confirm whether GL / blueprint changed (today: expect none — document whether that is acceptable).

**Plain English:** Open the PDF and compare every dollar to the screen — they must match.

---

## Questions for prior developer / product owner

| # | Question | Plain English |
|---|----------|---------------|
| Q1 | Is Send Email meant for resend only, or alternate first-send? | Should this replace Send Invoice or only resend? |
| Q2 | Why `invokeurl` + public URL instead of `template:... as PDF`? | Was the simpler method broken, or just unknown? |
| Q3 | Who owns private key / report rotation and regression testing? | When Zoho changes, who checks emails still work? |
| Q4 | Why is Debit Note in code but no popup button like Invoice? | Is debit note email actually used? |
| Q5 | Why does edit retrigger send? | Was duplicate email intentional? |
| Q6 | Where is the audit log finance can report on? | Can we run a “all sends this month” report? |

---

## Target state — what “fixed” looks like for a true billing system

Use this section as the **fix goal** for the initiative.

| # | Requirement | Plain English |
|---|-------------|---------------|
| T1 | **Single PDF method** for all send paths (`Send_Invoice`, `send_email_`, reminders) — prefer `Attachments :template:... as PDF` unless there is a documented reason for `record-pdf` URLs. | One button, one PDF look. |
| T2 | **Stage guards** — Send Email only when allowed (e.g. resend from Sent+ ; first send only via Send Invoice / blueprint). | Cannot email a draft by mistake. |
| T3 | **Source document audit fields** — on successful send: `Sent_Date`, `Sent_By`, `Sent_To`, `Send_Method` (or equivalent) on Invoice / Pro Forma / Debit Note. | Invoice record shows “emailed to X on date Y by Z.” |
| T4 | **Auto-fill To** from `Customer_E_mail`; CC optional; validate email format. | Customer email fills in automatically. |
| T5 | **Fail closed** — if record fetch or PDF generation fails, do not send; show clear error to user. | No email goes out with a broken PDF. |
| T6 | **No accidental resend on edit** — trigger send on **add only**, or separate explicit “Resend” action with confirmation. | Saving twice does not spam the customer. |
| T7 | **Remove hardcoded URLs** — use template syntax or centrally maintained config, not embedded private keys in Deluge. | Change template in settings, not in code. |
| T8 | **Consolidate paths** — retire or align `Send_Email1` hardcoded pro forma path and duplicate logic across files. | One way to send each document type. |
| T9 | **Debit Note** — either wire up `Send_Email` action to Email Input Form with same controls, or remove dead code. | Debit note works the same as invoice or is removed. |
| T10 | **Reconciliation report** — list documents sent vs email dispatch log for month-end review. | Finance can audit sends without digging in code. |

---

## Files in scope for fix

| File | Role |
|------|------|
| `application/forms/Email Input Form/workflow/send_email_.deluge` | Main send engine (primary fix) |
| `application/forms/Email Input Form/workflow/Handle_Load_Of_The_Form.deluge` | Template pre-fill; should also pre-fill To |
| `application/forms/Invoice/workflow/actions/Send_Email5.deluge` | Opens popup — add stage guards |
| `application/forms/Pro Forma Invoices/workflow/actions/Send_Email6.deluge` | Opens popup |
| `application/forms/Invoice/workflow/actions/Send_Invoice.deluge` | Reference for governed first-send behaviour |
| `application/forms/Pro Forma Invoices/workflow/Send_Email1.deluge` | Legacy hardcoded path — consolidate or retire |

---

## References

- Zoho Creator Academy: [Send page as PDF attachment via email](https://help.zoho.com/portal/en/kb/creator/zoho-creator-academy/pages/articles/send-page-as-pdf-attachment-via-email#Steps_to_Follow)
- Zoho Deluge: [sendmail task](https://www.zoho.com/deluge/help/misc-statements/send-mail.html)
- Zoho Creator: [Export and print URLs](https://www.zoho.com/creator/newhelp/app-settings/print-export-url.html)
- Internal BRD: invoice send and reminder flows (`docs/BRD.md` § shared communications)

---

*Last updated: 2026-06-30 — financial audit from code review; UAT results to be appended when available.*
