# XMT Billing System — Business Requirements Document (BRD)

> **Format:** Table-based. Fill rows under each table.
> **Audience:** Management, client, finance, operations, QA
> **Export to Google Docs:** `pandoc docs/BRD.md -o docs/BRD.docx` then upload to Google Drive.

---

## Table of Contents

- [Document Information](#document-information)
- [1. Document Orientation](#1-document-orientation)
  - [1.1 Purpose of This Document](#11-purpose-of-this-document)
  - [1.2 System Overview](#12-system-overview)
  - [1.3 Scope](#13-scope)
  - [1.4 Who Uses the System](#14-who-uses-the-system)
  - [1.5 How to Read This Document](#15-how-to-read-this-document)
- [2. Foundation](#2-foundation)
  - [2.1 Glossary](#21-glossary)
  - [2.2 End-to-End Billing Flow](#22-end-to-end-billing-flow)
  - [2.3 Manual vs Automatic Actions](#23-manual-vs-automatic-actions)
  - [2.4 How Documents Connect](#24-how-documents-connect)
- [3. Module Requirements](#3-module-requirements)
  - [3.1 Tenancy](#31-tenancy)
  - [3.2 Subscription](#32-subscription)
  - [3.3 Pro Forma Invoice](#33-pro-forma-invoice)
  - [3.4 Invoice](#34-invoice)
  - [3.5 Payment Received](#35-payment-received)
  - [3.6 Credit Note](#36-credit-note)
  - [3.7 Debit Note](#37-debit-note)
  - [3.8 Refund Note](#38-refund-note)
  - [3.9 Journal Entry](#39-journal-entry)
- [4. Cross-Cutting](#4-cross-cutting)
  - [4.1 Shared Business Rules](#41-shared-business-rules)
  - [4.2 Status Summary (All Modules)](#42-status-summary-all-modules)
  - [4.3 Notifications and Emails](#43-notifications-and-emails)
  - [4.4 Setup and Master Data](#44-setup-and-master-data)
- [5. Alignment and Ongoing Use](#5-alignment-and-ongoing-use)
  - [5.1 Assumptions and Dependencies](#51-assumptions-and-dependencies)
  - [5.2 Open Questions and Decisions Needed](#52-open-questions-and-decisions-needed)
  - [5.3 Implementation Status](#53-implementation-status)
  - [5.4 Related Documents](#54-related-documents)
- [Appendix](#appendix-optional)
  - [Appendix A. Roles and Responsibilities](#appendix-a-roles-and-responsibilities)
  - [Appendix B. Revision History](#appendix-b-revision-history)

## Document Information

| Field    | Value                                   |
|----------|-----------------------------------------|
| Title    | XMT : Billing System                    |
| Version  | 1.1                                     |
| Date     | 19 Jun 2026                             |
| Owner    | Hazrul                                  |
| Status   | Under Review                            |
| Audience | Management, client, finance, operations |
## 1. Document Orientation

### 1.1 Purpose of This Document

| Item    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Purpose | This document describes how the **XMT Billing System** (Zoho Creator application) is expected to work from a business perspective. It is the shared reference for management, the client, finance, and operationsto understand what the system does. It covers the full billing lifecycle: customer and tenancy setup, recurring subscriptions, pro forma invoices, tax invoices, payments, credit and debit notes, refunds, and journal entries. For each area it sets out business rules, calculations, document relationships, status changes, and restrictions. **Use this document to:** align stakeholders on expected behaviour; guide UAT and day-to-day operations; support finance reconciliation and audit; and track what is implemented versus what still needs a decision. |
### 1.2 System Overview

| Item     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Overview | **XMT : Billing System** is a Zoho Creator application that manages customer billing for XMT — from contract setup through invoicing, payment collection, corrections, and accounting entries. **What the system does** 1. **Setup** — Stores customer profiles, organization settings, taxes, payment terms, chart of accounts, and other master data used across all billing documents. 2. **Contracts** — Users create a **Tenancy** (customer account with billing cycle and payment terms) and one or more **Subscriptions** (contracted services with line items, contract dates, and billing schedule). 3. **Recurring billing** — A daily schedule (`Subscription_Schedule`) generates **Invoices** automatically when a tenancy’s next billing date is reached and active subscriptions are due. Invoices can also be created manually or from subscription save logic in near-billing conditions. 4. **Billing documents** — The system issues **Pro Forma Invoices** (deposits/advances), **Invoices** (tax invoices), **Credit Notes**, **Debit Notes**, and **Refund Notes**. Each document supports line items by charge type (monthly rental, internet charges, call charges), tax calculation, and printable PDF templates. 5. **Document lifecycle** — Key documents follow approval workflows (Draft → Pending Approval → Approved → Sent / Paid / Partially Paid / Overdue, with module-specific stages). Users approve and send documents; the system updates status when payments are recorded or due dates pass. 6. **Payments and credits** — **Payment Received** records allocate amounts to invoices, pro forma invoices, or debit notes. **Credit Notes** can be applied to open invoices; unused credit can be refunded via **Refund Note**. Payment and deletion flows update document balances and status automatically. 7. **Accounting** — Approved billing events create **Journal Entry** records. Deleting certain documents removes linked journal entries. 8. **LHDN e-Invoicing** — Invoices, credit notes, debit notes, and refund notes can be submitted to **LHDN** (Malaysia tax authority). The system validates supplier/customer identity data and requires invoice UUID and public link before certain send and reference actions. 9. **Automated follow-up** — Scheduled jobs send first and final payment reminder emails after the due date, and move unpaid invoices to **Overdue** when the due date is reached. **How work enters the system** - **Manual** — Users create and edit records, run record actions (e.g. record payment, convert invoice to credit/debit note, apply credits, submit to LHDN). - **On save** — Form workflows validate data, calculate totals, update related records, and trigger side effects when a record is saved. - **Scheduled** — Daily jobs handle recurring invoice generation, payment reminders, and overdue status changes without user action. |
### 1.3 Scope

| #   | Item                                                                            | In Scope (Y/N) | Notes                                                                                                                      |
|-----|---------------------------------------------------------------------------------|----------------|----------------------------------------------------------------------------------------------------------------------------|
| 1   | Customer and account setup (`Customer_Profile`, `Tenancy`)                      | Y              | Customer identity, billing cycle, payment terms                                                                            |
| 2   | Recurring contracts (`Subscription`, `Work_Order_Creation`)                     | Y              | Line items, contract dates, billing schedule, optional work orders                                                         |
| 3   | Pro forma / deposit billing (`Pro_Forma_Invoices`)                              | Y              | Advance charges before or alongside main invoicing                                                                         |
| 4   | Tax invoicing (`Invoice`)                                                       | Y              | Recurring and manual invoices; LHDN submission; reminders and overdue                                                      |
| 5   | Payment collection (`Payment_Received`, `Payment_Received_Line_Item`)           | Y              | Allocation to invoices, pro forma, and debit notes                                                                         |
| 6   | Credit application (`Apply_Credit_To_Invoices`, `Apply_Credit_To_Invoice_Line`) | Y              | Applying open credit to outstanding invoices                                                                               |
| 7   | Correction documents (`Credit_Note`, `Debit_Note`, `Refund_Note`)               | Y              | Credits, additional charges, and refunds; LHDN submission where applicable                                                 |
| 8   | Accounting entries (`Journal_Entry`)                                            | Y              | Auto-created from billing events; linked to document numbers                                                               |
| 9   | Master data and setup                                                           | Y              | Organization Settings, Tax, Payment Term, Chart of Account, Bank, Email Templates, Business Unit/Segment, Circuit ID, etc. |
| 10  | Scheduled automation                                                            | Y              | `Subscription_Schedule`, invoice reminders, overdue status change                                                          |
| 11  | Notifications and customer statements                                           | Y              | Reminder emails, credit-available notices, `Customer_Statement`                                                            |
| 12  | LHDN e-Invoicing integration                                                    | Y              | Submit and validate UUID/public link for compliant documents                                                               |
| 13  | User access and profiles                                                        | Y              | Profiles: Administrator, Finance Manager, Finance Executive, Customer portal                                               |
| 14  | UI layout and styling only                                                      | N              | Unless a layout change affects data or workflow behaviour                                                                  |
| 15  | Platform hosting and infrastructure                                             | N              | Zoho Creator platform administration                                                                                       |
| 16  | Non-billing modules with no billing impact                                      | N              | e.g. `Announcement`, `Alert_Message`, `Date_form` — excluded unless they affect billing documents                          |
### 1.4 Who Uses the System

| Role                   | What they do in the system                                                                                                                                                                                                              | Key documents they work with                                                                        |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **Administrator**      | Full system access — organization settings, master data, user management, and all billing modules. Configures taxes, payment terms, chart of accounts, email templates, and LHDN portal environment.                                    | Organization Settings, Tax, Payment Term, Chart of Account, User, all billing modules               |
| **Finance Manager**    | Oversees billing operations — approves and sends invoices and correction documents, submits documents to LHDN, reviews journal entries and customer statements. Shares approval-level actions with Administrator on key record actions. | Invoice, Pro Forma Invoice, Credit Note, Debit Note, Refund Note, Journal Entry, Customer Statement |
| **Finance Executive**  | Day-to-day billing processing — creates tenancies and subscriptions, records payments, applies credits to invoices, creates refund notes, and maintains customer billing data.                                                          | Tenancy, Subscription, Payment Received, Apply Credit to Invoice, Invoice, Credit Note              |
| **Operations / Sales** | Sets up customer accounts and contracts — creates customer profiles, tenancies, subscriptions, and work orders where required. Does not typically handle LHDN submission or journal review.                                             | Customer Profile, Tenancy, Subscription, Work Order                                                 |
| **Customer (portal)**  | Views own billing information through the customer portal profile (`Customer`). Limited to add and view permissions on portal-enabled content.                                                                                          | Own invoices and related documents (as exposed in portal)                                           |
| **QA / UAT**           | Verifies end-to-end flows against this document — setup → subscription → invoice → payment → corrections → closure. Uses test data and schedule triggers to validate automated behaviour.                                               | All modules (read and test); see related end-to-end flow guide                                      |
### 1.5 How to Read This Document

| Section area           | What you will find there                                                                                     | Primary reader                       |
|------------------------|--------------------------------------------------------------------------------------------------------------|--------------------------------------|
| Section 2 — Foundation    | Glossary, end-to-end billing flow, manual vs automatic actions, and how documents link to each other         | All readers — start here for context |
| Section 3 — Module tables | Per-module summary, business rules, calculations, relationships, status lifecycle, and restrictions (§3.1–3.9) | Finance, operations, QA              |
| Section 4 — Cross-cutting | Rules that apply across modules, status summary, emails, and master data setup                               | Finance Manager, Administrator       |
| Section 5 — Alignment     | Assumptions, open questions, implementation status, and links to related documents                           | Management, project owner            |
## 2. Foundation

### 2.1 Glossary

| Term                         | Definition                                                                                                                                                                                                                                                             |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Tenancy**                  | A customer billing account. Holds the account number, billing cycle (Monthly / Quarterly / Half Yearly / Yearly), bill-every day, bill-for period (Current Duration or Previous Duration), payment term, and next billing date. Subscriptions are linked to a tenancy. |
| **Subscription**             | A contracted service agreement under a tenancy. Contains line items (monthly rental, internet charges, call charges), contract dates, billing dates, and status (Active / Inactive / Terminated). Drives recurring invoice generation.                                 |
| **Pro Forma Invoice**        | An advance or deposit invoice issued before or alongside main billing. Follows its own approval and payment lifecycle; payments update amount paid and status like a standard receivable document.                                                                     |
| **Invoice**                  | The primary tax invoice for customer charges. Created manually, from subscription save logic when timing matches, or by the daily billing schedule. Supports approval, send, payment, LHDN submission, reminders, and overdue handling.                                |
| **Credit Note**              | A document that reduces what the customer owes. Can be created manually or converted from an invoice. Open credit can be applied to invoices or refunded.                                                                                                              |
| **Debit Note**               | A document that increases what the customer owes. Can be created manually or converted from an invoice. Supports payment allocation like an invoice.                                                                                                                   |
| **Refund Note**              | A document recording money returned to the customer against credit on a credit note.                                                                                                                                                                                   |
| **Payment Received**         | A payment record that allocates amounts to one or more target documents (invoice, pro forma invoice, or debit note). Updates paid/due balances and document status on save; reverses on delete.                                                                        |
| **Apply Credit to Invoice**  | The process (via `Apply_Credit_To_Invoices`) of applying open credit from a credit note to reduce an invoice balance.                                                                                                                                                  |
| **Journal Entry**            | An accounting record auto-created when certain billing events occur (e.g. invoice send, payment posting, debit note approval). Linked to document numbers; removed when some source documents are deleted.                                                             |
| **Blueprint**                | The approval and status workflow on a billing document — e.g. Draft → Pending Approval → Approved → Sent → Partially Paid / Paid / Overdue. User transitions move the record; payments and schedules can also change status.                                           |
| **Charge Category**          | Classifies invoice line content: Fixed Charges, Telephone Charges, or Miscellaneous Charges. Affects validation (call charges required for telephone) and reminder email attachment templates.                                                                         |
| **Bill For**                 | Tenancy setting that controls which billing period an invoice covers: **Current Duration** (charges for the period being billed) or **Previous Duration** (charges for the prior period).                                                                              |
| **LHDN**                     | Malaysia tax authority e-Invoicing portal. Invoices, credit notes, debit notes, and refund notes can be submitted to LHDN; UUID and public link are required before certain send and reference actions.                                                                |
| **Record action**            | A button on a document record that opens a related flow — e.g. Record Payment, Convert to Credit Note, Apply Credits, Submit to LHDN.                                                                                                                                  |
| **Schedule**                 | A time-based job that runs automatically (daily or relative to due date) — e.g. recurring invoice creation, payment reminders, overdue status change.                                                                                                                  |
| **On save**                  | Logic that runs when a user saves a form — validations, total recalculation, related record updates, and side effects such as invoice creation or journal posting.                                                                                                     |
| **Amount Due / Amount Paid** | Running balances on a billing document. Payment Received allocations increase Amount Paid and reduce Amount Due; status (Paid, Partially Paid, etc.) follows the resulting balance.                                                                                    |
| **Credits Remaining**        | Open credit balance on a credit note after applications and refunds. Drives whether the credit note is Open or Closed.                                                                                                                                                 |
### 2.2 End-to-End Billing Flow

| Step | What happens                                                                                                                              | Who/what triggers it                                              | Document or module                                                          | Notes                                                                                                    |
|------|-------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| 1    | Master data is configured — organization settings, taxes, payment terms, chart of accounts, email templates                               | User (Administrator)                                              | Organization Settings, Tax, Payment Term, Chart of Account, Email Templates | Required before billing documents can be created correctly                                               |
| 2    | Customer profile is created with identity, address, and tax registration details                                                          | User                                                              | Customer Profile                                                            | Upstream of tenancy and all billing documents                                                            |
| 3    | Tenancy is created for the customer — billing cycle, bill every, bill for, payment term, payable account                                  | User                                                              | Tenancy                                                                     | Account number auto-generated if missing on save                                                         |
| 4    | Subscription is created with line items, contract dates, and charge category                                                              | User                                                              | Subscription                                                                | Validations require line items and positive quantities/prices                                            |
| 5    | Subscription billing dates are initialized; first invoice may be created immediately if timing conditions match and no invoice exists yet | On save (`Successful_subscription_s`)                             | Subscription → Invoice                                                      | Edge case for near-billing or prorate scenarios                                                          |
| 6    | Daily job finds active subscriptions due on the tenancy’s next billing date and creates invoices for current or previous duration         | Schedule (`Subscription_Schedule`)                                | Tenancy + Subscription → Invoice                                            | Runs daily (Asia/Singapore); monthly and non-monthly cycles handled separately                           |
| 7    | Invoice is reviewed, approved, and sent to the customer; LHDN submission may occur on approval                                            | User (blueprint transitions + record actions)                     | Invoice                                                                     | Send requires UUID and public link when LHDN-compliant; status becomes Sent or Overdue based on due date |
| 8    | Pro forma invoice is created, approved, and sent where deposits or advances are needed                                                    | User                                                              | Pro Forma Invoice                                                           | Parallel path to step 7 for deposit billing                                                              |
| 9    | Customer payment is recorded and allocated to invoice, pro forma, or debit note                                                           | User (record action) + on save                                    | Payment Received                                                            | `Record_Payment_Invoice` or `Record_Payment_Deposit1` opens prefilled payment form                       |
| 10   | Target document balances and status update — Amount Paid, Amount Due, Paid / Partially Paid                                               | On save (Payment Received success workflow)                       | Invoice, Pro Forma Invoice, Debit Note                                      | Journal entry created on payment posting                                                                 |
| 11   | If invoice remains unpaid, first reminder email sends one week after due date; final reminder at two weeks                                | Schedule (`W1st_Remainder_Invoice_Due`, `Final_Invoice_Reminder`) | Invoice                                                                     | Skipped for Miscellaneous Charges category                                                               |
| 12   | Unpaid invoice moves to Overdue when due date is reached                                                                                  | Schedule (`Change_status_to_Overdue_`)                            | Invoice                                                                     | Applies to Approved, Sent, or Partially Paid invoices past due date                                      |
| 13   | Invoice is converted to credit note or debit note for corrections                                                                         | User (record action) + on save                                    | Invoice → Credit Note / Debit Note                                          | Copies header and line-item context from source invoice                                                  |
| 14   | Open credit is applied to outstanding invoices or refunded to customer                                                                    | User (record action) + on save                                    | Credit Note → Apply Credit to Invoice / Refund Note                         | Credit note moves to Open or Closed based on credits remaining                                           |
| 15   | Journal entries reflect approved/sent documents and payments; customer statement can be generated for reconciliation                      | On save / record actions                                          | Journal Entry, Customer Statement                                           | Journal entries deleted when some source documents or payments are removed                               |
### 2.3 Manual vs Automatic Actions

| Action                                     | Module                                        | Manual or Automatic  | When it runs                                         | Notes                                                                          |
|--------------------------------------------|-----------------------------------------------|----------------------|------------------------------------------------------|--------------------------------------------------------------------------------|
| Create / edit customer profile             | Customer Profile                              | Manual + On save     | User submits form                                    | Validations and field updates on save                                          |
| Create / edit tenancy                      | Tenancy                                       | Manual + On save     | User submits form                                    | Account number generation; billing field locks when active subscriptions exist |
| Create / edit subscription                 | Subscription                                  | Manual + On save     | User submits form                                    | Line totals recalculated on input; billing dates initialized on success        |
| First invoice from subscription timing     | Subscription → Invoice                        | Automatic (On save)  | `Successful_subscription_s` on subscription save     | Only when no invoice linked yet and billing timing matches                     |
| Recurring invoice generation               | Subscription → Invoice                        | Automatic (Schedule) | Daily — `Subscription_Schedule`                      | Active subscriptions aligned to tenancy next billing date                      |
| Create pro forma invoice                   | Pro Forma Invoice                             | Manual + On save     | User creates and submits                             | Document number generated on create                                            |
| Approve / send pro forma                   | Pro Forma Invoice                             | Manual               | User runs blueprint transitions                      | Status routes to Sent or Overdue by due date                                   |
| Create / edit invoice manually             | Invoice                                       | Manual + On save     | User creates and submits                             | Totals, due date, and balance fields recalculated on input                     |
| Approve / send invoice                     | Invoice                                       | Manual               | User runs blueprint transitions                      | LHDN validation on approval; UUID/link required to send                        |
| Submit document to LHDN                    | Invoice, Credit Note, Debit Note, Refund Note | Manual               | User clicks Submit to LHDN record action             | Credit note LHDN submit requires Closed stage                                  |
| Record payment against invoice             | Invoice → Payment Received                    | Manual + On save     | `Record_Payment_Invoice` then submit payment         | Updates invoice balances and blueprint stage                                   |
| Record payment against pro forma (deposit) | Pro Forma Invoice → Payment Received          | Manual + On save     | `Record_Payment_Deposit1` then submit payment        | Updates pro forma balances and stage                                           |
| Record payment against debit note          | Debit Note → Payment Received                 | Manual + On save     | Payment record action then submit                    | Same payment form; allocation to debit note line                               |
| Delete payment (reversal)                  | Payment Received                              | Manual + On save     | User deletes payment record                          | Reverts target document balances, stages, and linked journal entries           |
| Convert invoice to credit note             | Invoice → Credit Note                         | Manual + On save     | `Convert_To_Credit_Note`                             | Copies source invoice data                                                     |
| Convert invoice to debit note              | Invoice → Debit Note                          | Manual + On save     | `Convert_To_Debit_Note1`                             | Copies source invoice data                                                     |
| Apply credit to invoice                    | Credit Note → Apply Credit to Invoice         | Manual + On save     | `Apply_Credits_to_Invoices`                          | Updates invoice credit totals and amount due                                   |
| Create refund from credit note             | Credit Note → Refund Note                     | Manual + On save     | `Create_Refund_Note_From_C`                          | Synchronizes credit note balance                                               |
| First payment reminder email               | Invoice                                       | Automatic (Schedule) | 1 week after due date — `W1st_Remainder_Invoice_Due` | Template by charge category; not for Miscellaneous Charges                     |
| Final payment reminder email               | Invoice                                       | Automatic (Schedule) | 2 weeks after due date — `Final_Invoice_Reminder`    | Same category exclusion as first reminder                                      |
| Move invoice to overdue                    | Invoice                                       | Automatic (Schedule) | Daily from due date — `Change_status_to_Overdue_`    | Eligible stages: Approved, Sent, Partially Paid                                |
| Post journal entry                         | Journal Entry                                 | Automatic (On save)  | Triggered by payment, send, or approval flows        | User does not typically create journal entries manually                        |
| Generate customer statement                | Customer Statement                            | Manual + On save     | User submits statement request                       | Aggregates invoices, payments, credits across date range                       |
### 2.4 How Documents Connect

| From document                                    | To document                                | How they connect                                                                                                | When it happens                                        |
|--------------------------------------------------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| Customer Profile                                 | Tenancy                                    | Tenancy references customer identity and address fields                                                         | Tenancy creation                                       |
| Tenancy                                          | Subscription                               | Subscription `Customer_Code` links to tenancy; inherits billing cycle, bill for, payment term                   | Subscription creation                                  |
| Tenancy + Subscription                           | Invoice                                    | Daily schedule or subscription save creates invoice with subscription line items                                | Billing date reached or subscription timing edge case  |
| Subscription                                     | Work Order                                 | Optional work order created when `Create_Work_Order` is enabled on subscription                                 | Subscription save (when flagged)                       |
| Pro Forma Invoice                                | Payment Received                           | Record action `Record_Payment_Deposit1` opens prefilled payment form                                            | User records deposit payment                           |
| Invoice                                          | Payment Received                           | Record action `Record_Payment_Invoice` opens prefilled payment form                                             | User records invoice payment                           |
| Debit Note                                       | Payment Received                           | Payment record action with debit note allocation on payment line item                                           | User records debit note payment                        |
| Invoice                                          | Credit Note                                | Record action `Convert_To_Credit_Note` copies invoice header and lines                                          | User converts overbilled or disputed invoice           |
| Invoice                                          | Debit Note                                 | Record action `Convert_To_Debit_Note1` copies invoice header and lines                                          | User converts to additional charge                     |
| Credit Note                                      | Refund Note                                | Record action `Create_Refund_Note_From_C` opens refund form linked to credit note                               | User refunds unused credit                             |
| Credit Note                                      | Apply Credit to Invoice                    | Record action `Apply_Credits_to_Invoices` creates credit application lines against target invoices              | User applies open credit                               |
| Credit Note                                      | Invoice (balance)                          | Applied credit reduces invoice `Credits_Applied_Total` and `Amount_Due`                                         | Credit application saved                               |
| Payment Received                                 | Invoice / Pro Forma / Debit Note (balance) | Payment line allocation updates `Amount_Paid` and `Amount_Due`; blueprint stage recalculated                    | Payment saved or deleted                               |
| Invoice                                          | Journal Entry                              | Send/approval path posts accounting lines linked by document number                                             | Invoice approved or sent                               |
| Debit Note                                       | Journal Entry                              | Blueprint approval posts journal lines linked to debit note                                                     | Debit note approved                                    |
| Payment Received                                 | Journal Entry                              | Payment posting creates journal entry; deletion removes linked entries                                          | Payment saved or deleted                               |
| Pro Forma Invoice                                | Journal Entry                              | Refund action on pro forma can post deposit-related journal lines                                               | Deposit refund processed                               |
| Invoice / Credit Note / Debit Note / Refund Note | LHDN (external)                            | Submit to LHDN record actions; UUID and public link stored on document                                          | User submits after approval (credit note: when Closed) |
| Multiple billing documents                       | Customer Statement                         | Statement aggregates invoices, pro forma, debit notes, credit notes, and payments for a customer and date range | User generates statement                               |
## 3. Module Requirements

Each module (§3.1–3.9) uses the same table set: **Module Summary**, **Business Rules**, **Calculations**, **Relationships**, **Status Lifecycle**, **Exceptions and Restrictions**.
### 3.1 Tenancy

#### 3.1.1 Module Summary

| Aspect                     | Description                                                                                                                                                                                                                                                                     |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Purpose                    | Holds the customer billing account context used by downstream billing documents. It stores billing cycle setup (`Billing_Cycle`, `Bill_Every`, `Bill_For`), payment term, payable account, tenancy identity (`Customer_Code`, `Account_Number`), and technical contact details. |
| When it is created         | Created when a new customer tenancy/account is onboarded before creating `Subscription` and invoice-related records.                                                                                                                                                            |
| Created by (User / System) | User creates and edits the record; system auto-generates/maintains key fields on save (for example `Account_Number`, `Display_Name`) and syncs account/contact data to Zoho Desk.                                                                                               |
#### 3.1.2 Business Rules

| Rule ID | When (condition)                                       | System must (behavior)                                                                                                                     | Notes                                               |
|---------|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| TEN-001 | `Billing_Cycle` is `Monthly` and `Bill_Every` is empty | Block save and require `Bill_Every`                                                                                                        | `Validation on form submission for Tenancy`         |
| TEN-002 | `Account_Number` is empty on save                      | Require `Account_Type` and generate `Account_Number` via tenancy number function                                                           | `thisapp.tenancy.generate_tenancy_no(...)`          |
| TEN-003 | Tenancy is opened in add mode                          | Hide system-maintained fields (`Account_Number`, `Next_Billing_Date`, `Latest_Billing_Date`, `Final_Billing_Date`)                         | `Hide Fields During Create`                         |
| TEN-004 | Tenancy is opened in add/edit mode                     | Keep derived/system fields read-only; when active `Subscription` exists, lock `Bill_Every`, `Bill_For`, and `Billing_Cycle` from edits     | `Disable Fields`                                    |
| TEN-005 | Tenant name matches customer profile name              | Set `Display_Name` to customer name; otherwise set `Display_Name = Customer Name - Tenant Name`                                            | `Validation on form submission for Tenancy`         |
| TEN-006 | `Billing_Cycle` is not `Monthly`                       | Clear and hide `Bill_Every`                                                                                                                | `Handle Billing Cycle` + `Field Rule Billing Cycle` |
| TEN-007 | Tenancy technical email changes                        | Validate no conflicting Desk contact on another account; sync Desk technical contact details                                               | `Change technical information in desk`              |
| TEN-008 | New tenancy is submitted                               | Create linked account in Zoho Desk                                                                                                         | `Create Account in Desk`                            |
| TEN-009 | User attempts to delete tenancy with dependent records | Block deletion and show dependency summary (subscriptions, invoices, credit/debit/refund notes, pro forma invoices, payments, work orders) | Tenancy `on delete` validation                      |
#### 3.1.3 Calculations

| What is calculated           | How it is calculated                                                                    | Notes                                                                                               |
|------------------------------|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `Account_Number`             | Generated automatically from `Account_Type` through tenancy numbering logic             | Triggered during tenancy validation before save                                                     |
| `Display_Name`               | Customer name only, or concatenated as `Customer Name - Tenant Name`                    | Keeps consistent label for reporting/references                                                     |
| Billing-cycle interval usage | Billing cycle text value is converted to integer interval using tenancy helper function | Used by downstream subscription/invoice date logic rather than stored as a numeric field in Tenancy |
#### 3.1.4 Relationship to Other Documents

| Direction  | Related document                                                                                | Relationship                                                                                                                                   |
|------------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Upstream   | `Customer_Profile`                                                                              | Tenancy links to customer identity (`Customer_Name`) and uses customer context for naming/display behavior.                                    |
| Upstream   | `Payment_Term`                                                                                  | Tenancy stores payment-term default used by downstream billing documents.                                                                      |
| Upstream   | `Chart_Of_Account`                                                                              | `Payable_To` references bank account setup for payment instructions.                                                                           |
| Downstream | `Subscription`                                                                                  | Each subscription is attached to a tenancy via `Customer_Code`; tenancy billing settings drive subscription billing dates and invoice cadence. |
| Downstream | `Invoice`, `Pro_Forma_Invoices`, `Credit_Note`, `Debit_Note`, `Refund_Note`, `Payment_Received` | All major billing documents reference tenancy/customer code either directly or through subscription flow.                                      |
| Downstream | `Work_Order_Creation`                                                                           | Work orders can be associated to tenancy and are included in tenancy deletion dependency checks.                                               |
#### 3.1.5 Status Lifecycle

| Status                             | Meaning                                                              | Moved by (User / System)   | Allowed next statuses                                               |
|------------------------------------|----------------------------------------------------------------------|----------------------------|---------------------------------------------------------------------|
| Active Billing Setup (implicit)    | Tenancy is in operational use for active subscription billing        | User + System              | Remains operational until business stops using tenancy              |
| Billing Settings Locked (implicit) | Billing cadence fields are locked because active subscriptions exist | System (form load rule)    | Unlocks only when no active subscriptions exist                     |
| Deletable (implicit)               | No dependent records found across billing/work-order modules         | System (delete validation) | Can transition to deleted                                           |
| Non-deletable (implicit)           | One or more dependent records exist                                  | System (delete validation) | Can become deletable only after dependencies are removed/reassigned |
#### 3.1.6 Exceptions and Restrictions

| Situation                                              | What is not allowed                                                                                              | Notes                                           |
|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Monthly billing without bill day                       | Save is not allowed when `Bill_Every` is empty for `Billing_Cycle = Monthly`                                     | Validation error shown to user                  |
| Missing account type during auto-numbering             | Save is not allowed when `Account_Number` is blank and `Account_Type` is empty                                   | System requires account type to generate number |
| Editing billing cadence with active subscriptions      | User cannot edit `Billing_Cycle`, `Bill_Every`, or `Bill_For` once active subscriptions exist                    | Protects downstream billing consistency         |
| Deleting referenced tenancy                            | Delete is not allowed when linked records exist in subscription, billing, payment, refund, or work-order modules | Dependency counts are shown in alert            |
| Reusing technical email across different Desk accounts | Save is not allowed if technical email is already attached to another Desk account                               | Prevents cross-account contact conflict         |
### 3.2 Subscription

#### 3.2.1 Module Summary

| Aspect                     | Description                                                                                                                                                                                                                  |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Purpose                    | Defines the recurring service contract for a tenancy, including charge line items, contract period, billing dates, payment term, and optional work-order creation. It is the primary upstream driver for invoice generation. |
| When it is created         | Created after `Tenancy` setup when service billing should begin for a customer account.                                                                                                                                      |
| Created by (User / System) | User creates/edits the contract; system initializes defaults, recalculates totals, computes billing dates, and can auto-create invoices and work orders based on trigger conditions.                                         |
#### 3.2.2 Business Rules

| Rule ID | When (condition)                                                      | System must (behavior)                                                                                                                                 | Notes                                                                             |
|---------|-----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| SUB-001 | `Customer_Code` is selected/changed                                   | Copy tenancy defaults (`Payment_Term`, `Payable_To`), reset contract/pro-rate fields, and align line-item quantities to tenancy billing-cycle interval | `Handle Tenant Code Changes`                                                      |
| SUB-002 | Contract dates/period inputs change                                   | Recompute `Contract_End_Date` and update pro-rate guidance note according to tenancy `Billing_Cycle` and `Bill_For`                                    | `Handle Contract Start Date`, `Handle Contract Period Changes`, `Handle Prorate?` |
| SUB-003 | `Charge_Category` is not telephone-based                              | Hide and clear `Call_Charges` rows                                                                                                                     | Subscription field/load script                                                    |
| SUB-004 | Subscription is validated for save                                    | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, `Call_Charges`                                                             | `Handle Validation Submission`                                                    |
| SUB-005 | Any line item has quantity or unit price less than/equal to zero      | Block submit                                                                                                                                           | `Handle Validation Submission`                                                    |
| SUB-006 | `Create_Work_Order` is checked but `Work_Order_Type` is empty         | Block submit and require work-order type                                                                                                               | `Handle Validation Submission`                                                    |
| SUB-007 | Subscription add form loads                                           | Set `Subscription_Status` to `Active`, load base currency from organization settings, and limit initial work-order type options                        | `Initialize Form Defaults on Load`                                                |
| SUB-008 | Subscription is successfully added and `Create_Work_Order` is true    | Create linked work-order/ticket flow                                                                                                                   | `Create ticket in Zoho Desk`                                                      |
| SUB-009 | Subscription is saved and no invoice exists yet for that subscription | Compute/update billing dates and trigger invoice creation based on tenancy cycle and near-billing timing                                               | `Successful subscription submission`                                              |
| SUB-010 | Billing reaches final billing date in update logic                    | Set `Next_Billing_Date = null`, update `Latest_Billing_Date`, and mark `Subscription_Status = Inactive`                                                | `subscription.update_subscription_next_and_last_billing_date(...)`                |
| SUB-011 | User tries to reuse the same customer PO number for the same tenancy  | Reject duplicate PO number for that tenancy                                                                                                            | `Handle Customer PO No. Changes`, tenant-code handler check                       |
| SUB-012 | User attempts to delete a subscription with dependent records         | Block delete and show dependency summary (invoices, credit/refund notes, work orders, linked pro forma)                                                | `Validate Record Deletion` (Subscription)                                         |
#### 3.2.3 Calculations

| What is calculated            | How it is calculated                                                                                                              | Notes                                                |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| `Contract_End_Date`           | `Contract_Start_Date + Contract_Period (months)`                                                                                  | Recomputed on contract start/period changes          |
| Line item quantities default  | Quantity is set from tenancy billing-cycle interval (`convert_bill_cycle_to_int`) when customer code is selected                  | Applies to all three line-item grids                 |
| Billing date progression      | Next/final/latest billing dates are computed from tenancy settings (`Billing_Cycle`, `Bill_For`, `Bill_Every`) and contract dates | Used by on-save invoice-generation and schedule flow |
| Subscription totals           | Row subtotals/tax/grand totals are recalculated through input-trigger toggling (`User_Input_Trigger`)                             | Drives downstream invoice amounts                    |
| Status transition to inactive | On final billing occurrence, subscription status changes from `Active` to `Inactive`                                              | Implemented in helper update function                |
#### 3.2.4 Relationship to Other Documents

| Direction  | Related document                                              | Relationship                                                                                                        |
|------------|---------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Upstream   | `Tenancy`                                                     | Subscription references tenancy via `Customer_Code`; tenancy billing settings govern subscription billing behavior. |
| Upstream   | `Customer_Profile`                                            | Subscription customer context is selected through tenancy and customer linkage.                                     |
| Upstream   | `Payment_Term`, `Chart_Of_Account`, `Transaction_Type`, `Tax` | Used as defaults and references for payment terms, payable account, line items, and tax details.                    |
| Downstream | `Invoice`                                                     | Subscription save logic and `Subscription_Schedule` create invoices for eligible billing periods.                   |
| Downstream | `Pro_Forma_Invoices`                                          | Optional linkage through `Pro_Forma_Invoices` field on subscription and deletion dependency checks.                 |
| Downstream | `Credit_Note`, `Refund_Note`                                  | Records can reference subscription context; dependencies prevent unsafe subscription deletion.                      |
| Downstream | `Work_Order_Creation`                                         | Work orders can be created from subscription when enabled; linked records block deletion.                           |
#### 3.2.5 Status Lifecycle

| Status       | Meaning                                                         | Moved by (User / System)                    | Allowed next statuses                                                                            |
|--------------|-----------------------------------------------------------------|---------------------------------------------|--------------------------------------------------------------------------------------------------|
| `Active`     | Subscription is billable and participates in invoice generation | System default on add; user/system on edits | `Inactive`, `Terminated` (value available in form)                                               |
| `Inactive`   | Billing has reached final cycle or record is no longer billable | System (billing-date update logic)          | May remain inactive; reactivation behavior should be controlled by business process              |
| `Terminated` | Contract explicitly ended by business action                    | User (status field)                         | No automatic transition confirmed in DS; billing impact should be confirmed in operations policy |
#### 3.2.6 Exceptions and Restrictions

| Situation                                       | What is not allowed                                                                               | Notes                             |
|-------------------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------------------|
| Empty service lines                             | Save is not allowed if no line exists across all charge grids                                     | Prevents zero-line subscriptions  |
| Invalid line-item amounts                       | Quantity or unit price less than/equal to zero is not allowed                                     | Checked per row during validation |
| Missing work-order type with work order enabled | Save is not allowed when `Create_Work_Order = true` and `Work_Order_Type` is blank                | Explicit validation rule          |
| Duplicate PO number per tenancy                 | Reusing same `Customer_PO_No` under one tenancy is not allowed                                    | Clears PO field and alerts user   |
| Deleting referenced subscription                | Delete is not allowed if linked invoices/credit notes/refunds/work orders/pro forma linkage exist | Dependency summary alert shown    |
### 3.3 Pro Forma Invoice

#### 3.3.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Issues deposit/advance billing documents (`Pro_Forma_Invoices`) to request payment before or alongside main invoicing. Captures charge lines, tax totals, amount due, approval/sending lifecycle, and deposit-payment linkage. |
| When it is created         | Created manually by finance/operations when a deposit or advance charge is needed for a customer tenancy. |
| Created by (User / System) | User creates and processes the document; system generates document number, calculates totals, manages blueprint status, and updates balances when deposit payments are recorded. |

#### 3.3.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| PFI-001 | Pro forma record is created | Generate `Invoice_No` using pro forma numbering function | `Handle Invoice Creation` → `thisapp.deposit.generate_proforma_invoice_no()` |
| PFI-002 | Pro forma is validated on save | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges` | `Handle Validation Submission` |
| PFI-003 | `Charge_Category` includes telephone charges | Require at least one `Call_Charges` row | `Handle Validation Submission` |
| PFI-004 | Any line item quantity or unit price is ≤ 0 | Block submit | `Handle Validation Submission` |
| PFI-005 | Line items, tax, exchange rate, or charge category change | Recalculate totals and `Amount_Due` via input-trigger workflow | `User_Input_Trigger_Workflow` |
| PFI-006 | `Invoice_Date` or `Payment_Term` changes (with customer code context) | Recompute `Due_Date` as invoice date plus payment-term days | `Handle Invoice Date`, `Handle Customer Code Changes` |
| PFI-007 | User selects `Reference_Invoice` | Reject invoice references missing `Invoice_UUID` or `Invoice_Public_Link` | `Handle reference invoice selection` |
| PFI-008 | Approved pro forma is sent | Set status to `Sent` if due date is in the future, otherwise `Overdue` | `Pro_Forma_Invoices_Bluepr` transition `Send_Invoice` |
| PFI-009 | Pro forma has payment allocations | Block deletion | `Validation Of Deletion` checks `Payment_Received_Line_Item` |
| PFI-010 | Pro forma is deleted successfully | Remove linked journal entries for that deposit record | `Successful pro forma invoice deletion` |
| PFI-011 | Pro forma is submitted successfully | Currently redirects to Debit Notes report — confirm intended navigation | `Handle Submission Form and Submit Invoice to LHDN` (open question) |

#### 3.3.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Line subtotals | `Quantity × Unit_Price` per line grid (monthly rental, internet, call charges) | Recalculated on `User_Input_Trigger` |
| Line tax amounts | `Sub_Total × Tax_Pct / 100` | Per line row |
| Line totals | `Sub_Total + Tax_Amount` | Per line row |
| Document subtotal | Sum of subtotals across all three charge grids | `Sub_Total` |
| Document tax total | Sum of tax amounts across all three charge grids | `Total_Tax` |
| Grand total | Sum of line grand totals across all charge grids | `Grand_Total` |
| Base-currency total | `Exchange_Rate × Grand_Total` (or `0` if exchange rate is null) | `Grand_Total_Base_Currency` |
| Amount due | Set to `Grand_Total` before payment updates | Updated again when deposit payments are posted |

#### 3.3.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Customer_Profile`, `Tenancy` | Customer and tenancy context drive payable account, payment term, and due-date defaults. |
| Upstream   | `Organization_Settings`, `Payment_Term`, `Transaction_Type`, `Tax` | Supplier defaults, payment terms, line-item catalog, and tax setup. |
| Upstream   | `Invoice` | Optional `Reference_Invoice` link; must have LHDN UUID and public link when selected. |
| Downstream | `Payment_Received` | Deposit payments recorded via `Record_Payment_Deposit1`; updates `Amount_Paid`, `Amount_Due`, and blueprint stage. |
| Downstream | `Journal_Entry` | Can be created from refund flow (`Refund1`); removed on pro forma deletion. |
| Downstream | `Subscription` | Subscription may link to a pro forma record; linkage blocks subscription deletion. |

#### 3.3.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| `Draft` | Document created, not yet submitted for approval | User | `Pending Approval` |
| `Pending Approval` | Awaiting approver action | User (send for approval) | `Approved`, `Rejected` |
| `Rejected` | Approval declined | User (approver) | `Pending Approval` (resubmit) |
| `Approved` | Approved but not yet sent to customer | User (approver) | `Sent`, `Overdue` (on send, based on due date) |
| `Closed` | Document closed in blueprint (module-specific use) | User / System | Per blueprint configuration |
| `Sent` | Issued to customer and awaiting payment | User (send) or System (payment reversal) | `Partially Paid`, `Paid`, `Overdue` |
| `Partially Paid` | Deposit partially received | System (payment posting) | `Paid`, `Sent`, `Overdue` |
| `Paid` | Fully paid | System (payment posting) | — |
| `Overdue` | Past due date with outstanding balance | System (send routing or payment state) | `Partially Paid`, `Paid` |

Blueprint: `Pro_Forma_Invoices_Bluepr`. Declared stages in DS: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Closed`, `Sent`, `Paid`, `Partially Paid`, `Overdue`.

#### 3.3.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Saving with no line items | Submit blocked | At least one charge line required |
| Telephone category without call charges | Submit blocked | `Charge_Category` validation |
| Zero/negative quantity or unit price | Submit blocked | Per-row validation on all charge grids |
| Referencing non-LHDN-compliant invoice | Reference selection rejected | UUID and public link required |
| Deleting pro forma with payments applied | Delete blocked | Payment allocation must be removed first |
| Post-submit navigation ambiguity | N/A (behavior exists but intent unclear) | Success workflow opens Debit Notes report — confirm with business owner |
### 3.4 Invoice

#### 3.4.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Primary tax invoice for customer charges. Consolidates line-based charges (monthly rental, internet, call charges), applies tax and credits, tracks `Amount_Paid` and `Amount_Due`, and drives customer communication, LHDN submission, reminders, and accounting entries. |
| When it is created         | Created manually by finance; or auto-generated from `Subscription` save logic and daily `Subscription_Schedule` when billing dates match. |
| Created by (User / System) | User creates/edits and runs approval/send actions; system generates invoice number, calculates totals, posts journal entries, sends reminder emails, and updates status on payment or overdue. |

#### 3.4.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| INV-001 | Invoice is created (on add) | Generate and persist `Invoice_No` using invoice numbering function | `_Successful_invoice_submi` → `thisapp.invoice.generate_invoice_number()` |
| INV-002 | Invoice is validated on save | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges` | `Handle Validation Submission` |
| INV-003 | `Charge_Category` includes telephone charges | Require at least one `Call_Charges` row | `Handle Validation Submission` |
| INV-004 | Any line quantity or unit price is ≤ 0 | Block submit | `Handle Validation Submission` |
| INV-005 | `Credits_Applied_Total` exceeds `Grand_Total` | Block submit | `Handle Validation Submission` |
| INV-006 | `Customer_Code` or `Invoice_Date` changes | Copy tenancy reminder/payment settings; recompute `Due_Date`, `Previous_Balance`, and `Total_Amount_Due` | `Handle Customer Code Changes`, `Handle Invoice Date`, form load initialization |
| INV-007 | Line items, tax, exchange rate, or credits change | Recalculate subtotals, tax, grand totals, `Amount_Due`, and `Total_Amount_Due` | `User_Input_Trigger_Workflow` |
| INV-008 | Invoice is approved through blueprint | Validate supplier/customer identity data and attempt LHDN API submission before advancing | `Invoice_Blueprint` transition `Approve` |
| INV-009 | Approved invoice is sent | Require `Invoice_UUID` and `QR_Invoice_Public_Link`; set status to `Sent` or `Overdue` based on `Due_Date` | `Invoice_Blueprint` `Send_Invoice`, record action `Send_Invoice` |
| INV-010 | Invoice has payments, debit-note references, or applied credits | Block deletion until dependencies are removed | `Validations on invoice deletion` |
| INV-011 | Invoice is deleted successfully | Remove linked `Journal_Entry` records and recalculate tenancy opening balance | `Successful invoice deletion` |
| INV-012 | Invoice remains unpaid after due date | Send first reminder at 1 week and final reminder at 2 weeks after `Due_Date` (excludes Miscellaneous Charges) | Schedules `W1st_Remainder_Invoice_Due`, `Final_Invoice_Reminder` |
| INV-013 | Invoice is past due in eligible blueprint stage | Move status to `Overdue` | Schedule `Change_status_to_Overdue_` |
| INV-014 | User runs record actions on invoice | Support record payment, convert to credit/debit note, and submit to LHDN | `Record_Payment_Invoice`, `Convert_To_Credit_Note`, `Convert_To_Debit_Note1`, `Submit_Invoice_to_LHDN` |

#### 3.4.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Line subtotals | `Quantity × Unit_Price` per charge grid row | Recalculated on `User_Input_Trigger` |
| Line tax amounts | `Sub_Total × Tax_Pct / 100` | Per line row |
| Line totals | `Sub_Total + Tax_Amount` | Per line row |
| Document subtotal / tax / grand total | Sum across monthly rental, internet, and call charge sections | `Sub_Total`, `Total_Tax`, `Grand_Total` |
| Base-currency total | `Exchange_Rate × Grand_Total` (or `0` if exchange rate is null) | `Grand_Total_Base_Currency` |
| Amount due | `Grand_Total - Amount_Paid - Credits_Applied_Total` (for saved invoices) | Updated on payment and credit application |
| Total amount due | `Amount_Due + Previous_Balance` | `Previous_Balance` from `get_previous_balance_for_customer` |
| Invoice usage period | Derived from `Invoice_Date` via usage helper | `Invoice_For_Usage` field |

#### 3.4.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Subscription`, `Tenancy` | Recurring invoices created by subscription save logic and `Subscription_Schedule`; tenancy provides payment term, reminder flag, payable account. |
| Upstream   | `Customer_Profile`, `Organization_Settings`, `Payment_Term`, `Tax`, `Transaction_Type` | Customer/supplier defaults, tax setup, and line-item catalog. |
| Downstream | `Payment_Received` | Payments allocated via `Record_Payment_Invoice`; updates `Amount_Paid`, `Amount_Due`, and blueprint stage. |
| Downstream | `Credit_Note`, `Debit_Note` | Created from invoice via convert record actions; credit applications update invoice credit totals. |
| Downstream | `Apply_Credit_To_Invoice_Line` | Credit applied to invoice reduces `Amount_Due` and populates `Credits_Applied` subform. |
| Downstream | `Journal_Entry` | Created on send/approval; removed on invoice deletion. |
| Downstream | `Pro_Forma_Invoices` | Invoice can be referenced by pro forma with LHDN UUID/link requirement. |
| External   | LHDN (e-Invoicing) | Submission on approval; UUID and public link stored on invoice for compliance. |

#### 3.4.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| `Draft` | Invoice created, not yet submitted for approval | User | `Pending Approval` |
| `Pending Approval` | Awaiting approver action | User (send for approval) | `Approved`, `Rejected` |
| `Rejected` | Approval declined | User (approver) | `Pending Approval` (resubmit) |
| `Approved` | Approved but not yet sent; LHDN submission attempted on approval | User (approver) | `Sent`, `Overdue` (on send routing) |
| `Sent` | Issued to customer and awaiting payment | User (send) or System (payment reversal) | `Partially Paid`, `Paid`, `Overdue` |
| `Partially Paid` | Payment received but balance remains | System (payment posting) | `Paid`, `Sent`, `Overdue` |
| `Paid` | Fully paid | System (payment posting) | — |
| `Overdue` | Past due date with outstanding balance | System (send routing, overdue schedule, or payment state) | `Partially Paid`, `Paid` |

Blueprint: `Invoice_Blueprint`. Declared stages in DS: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Partially Paid`, `Paid`, `Overdue`.

#### 3.4.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Saving with no line items | Submit blocked | At least one charge line required |
| Telephone category without call charges | Submit blocked | `Charge_Category` validation |
| Credits exceeding grand total | Submit blocked | `Credits_Applied_Total` cap |
| Sending without LHDN compliance fields | Send blocked or fails validation | `Invoice_UUID` and `QR_Invoice_Public_Link` required |
| Deleting invoice with payments | Delete blocked | Remove payment allocations first |
| Deleting invoice with linked debit notes or applied credits | Delete blocked | Remove references/applications first |
| Miscellaneous charge invoices | Reminder emails skipped | First/final reminder schedules exclude this category |
| Reminder schedule stage casing | Behavior may vary by schedule filter | DS uses mixed `"paid"` vs `"Paid"` in different schedule queries — confirm canonical stage value |
### 3.5 Payment Received

#### 3.5.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Records customer cash receipts and allocates amounts to open receivable documents — `Invoice`, `Debit_Note`, or `Pro_Forma_Invoices`. Posts balancing journal entries and updates document balances and blueprint stages. |
| When it is created         | Created when finance records a payment — manually, or via record actions `Record_Payment_Invoice` (invoice/debit) or `Record_Payment_Deposit1` (pro forma deposit) which open a prefilled payment form. |
| Created by (User / System) | User enters payment details and allocations; system assigns receipt number, calculates totals, posts journal entry, updates target document balances/stages, and reverses all impacts on deletion. |

#### 3.5.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| PAY-001 | Payment is saved (on add) | Assign `Payment_Received_No` using type-specific generator (`Invoice/Debit Note` vs `Deposit`) | `Successful payment received submission` |
| PAY-002 | Payment form opens from single-record action | Prefill line item for selected invoice, debit note, or pro forma in single-record mode | `Pre_fill_Fields1` |
| PAY-003 | `Customer_Name` is selected | Load open receivables into line items based on `Payment_Type`; compute `Amount_Received`, `Amount_Received_MYR`, `Total_Still_Owing` | `Handle Customer Name` |
| PAY-004 | User edits line `Allocation` | Require document reference; block negative or over-allocation; recompute MYR allocation and totals | `Handle Payment Received Line Item Allocation`, `Validate Payment Received Submission` |
| PAY-005 | Payment is validated on submit | Block submit if no line items exist or no positive allocation for the chosen payment type | `Validate Payment Received Submission` |
| PAY-006 | Payment add succeeds | Create balancing `Journal_Entry` (debit `Paid_To` account, credit trade receivables) linked to receipt | `Successful payment received submission` |
| PAY-007 | `Payment_Type = Invoice/Debit Note` and payment posts | Update `Amount_Paid`/`Amount_Due` on invoice or debit note; set blueprint stage to `Paid`, `Partially Paid`, `Sent`, or `Overdue`; recalculate tenancy opening balance for invoices | Success workflow + blueprint `changeStage` |
| PAY-008 | `Payment_Type = Deposit` and payment posts | Update pro forma `Amount_Paid`/`Amount_Due`; set `Pro_Forma_Invoices_Bluepr` stage by balance and due date | Success workflow deposit branch |
| PAY-009 | Payment record is deleted | Reverse allocations on linked documents, restore blueprint stages, remove payment line items, delete linked `Journal_Entry` records | `_Successful payment received deletion` |

#### 3.5.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Line allocation (MYR) | `Allocation_MYR = Allocation × document Exchange_Rate` | Exchange rate from linked invoice, debit note, or pro forma |
| Amount received | Sum of line `Allocation` values | `Amount_Received` |
| Amount received (MYR) | Sum of line `Allocation_MYR` values | `Amount_Received_MYR` |
| Still owing (per line) | `Outstanding_Balance - Allocation` | Per payment line item |
| Total still owing | Sum of per-line still-owing amounts | `Total_Still_Owing` |
| Target document impact (on post) | `Amount_Paid += Allocation`; `Amount_Due -= Allocation` | Reversed on payment deletion |
| Target document impact (on reversal) | `Amount_Paid -= Allocation`; `Amount_Due += Allocation` | Deletion workflow |

#### 3.5.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Invoice` | Launches payment via `Record_Payment_Invoice`; receives allocation and balance/stage updates. |
| Upstream   | `Debit_Note` | Allocated via invoice/debit payment type on same payment form. |
| Upstream   | `Pro_Forma_Invoices` | Launches deposit payment via `Record_Payment_Deposit1`; receives allocation and stage updates. |
| Upstream   | `Customer_Profile`, `Tenancy`, `Chart_Of_Account` | Customer context and `Paid_To` bank account for receipt and journal posting. |
| Downstream | `Journal_Entry` | Created on payment add; deleted on payment delete (and deposit-linked entries for pro forma reversals). |
| Downstream | `Payment_Received_Line_Item` | Child allocation rows linking receipt to target documents. |
| Related    | `Apply_Credit_To_Invoices` | Separate flow for applying credit note balance to invoices (see §3.5.7). |

#### 3.5.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| New (implicit) | Payment form opened, not yet saved | User | Posted (on successful add) |
| Posted (implicit) | Payment saved; allocations and journal entry applied | System (on add success) | Reversed (on delete) |
| Reversed (implicit) | Payment deleted; document balances and journals restored | User + System (on delete success) | — |
| Receipt sent (field) | Customer receipt email dispatched | User (send receipt action) | `Receipt_Sent = true` |

No dedicated blueprint for `Payment_Received` in DS — lifecycle is workflow-driven via balance and stage updates on target documents.

#### 3.5.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Allocation without document reference | Save blocked | Each positive allocation must reference invoice, debit note, or pro forma |
| Allocation exceeding outstanding balance | Save blocked | Per-line cap at `Outstanding_Balance` |
| Negative allocation | Save blocked | Validation on line and form level |
| Submit with no allocatable documents | Save blocked | Message varies by `Payment_Type` |
| Submit with zero total allocation | Save blocked | At least one positive allocation required |
| Deleting posted payment | Allowed — triggers full reversal | User must understand downstream balance/stage impact |

#### 3.5.7 Apply Credit to Invoice

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| ACI-001 | `Apply_Credit_To_Invoices` form loads without preselected credit note | Show only credit notes in `Approved` or `Open` stage with `Credits_Remaining > 0`, excluding notes already in active apply-credit forms | `Apply Credit To Invoices Initialization` |
| ACI-002 | Apply-credit form is validated | Require at least one invoice with credit amount; block if any amount exceeds invoice `Amount_Due` or total exceeds credit note `Credits_Remaining` | `Apply Credit To Invoices Validation` |
| ACI-003 | User cannot add/remove unpaid-invoice rows manually | Subform rows are system-managed (add/delete hidden) | Field rules on `Unpaid_Invoices` |
| ACI-004 | Apply-credit form saves successfully | Insert `Apply_Credit_To_Invoice_Line` rows; update invoice `Credits_Applied_Total` and `Amount_Due`; recompute credit note `Credits_Used`/`Credits_Remaining`; set credit note blueprint to `Open` or `Closed`; delete transient apply-credit record | `Handle Form Submission` |
| ACI-005 | Apply credit is launched | Opened from `Credit_Note` record action `Apply_Credits_to_Invoices` | Record action on credit note |
### 3.6 Credit Note

#### 3.6.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Records post-issuance credits that reduce what a customer owes. Supports approval routing, credit application to invoices, refund tracking, remaining-credit management, and LHDN e-invoicing submission when fully utilised. |
| When it is created         | Created manually by finance; or converted from an `Invoice` via record action `Convert_To_Credit_Note`, which copies header and line-item context from the source invoice. |
| Created by (User / System) | User enters or edits credit details and runs approval/LHDN actions; system assigns credit note number, calculates totals and credit balances, routes blueprint stage, and synchronises linked refund and credit-application rows. |

#### 3.6.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| CRN-001 | Credit note is created (on add) | Generate and persist `Invoice_No` using credit-note numbering function | `Handle Invoice Creation` → `thisapp.credit_note.generate_credit_note_no()` |
| CRN-002 | Credit note is validated on save | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges` | `Handle Validation Submission` |
| CRN-003 | `Charge_Category` includes telephone charges | Require at least one `Call_Charges` row | `Handle Validation Submission` |
| CRN-004 | Any line quantity or unit price is ≤ 0 | Block submit | `Handle Validation Submission` and line input workflows |
| CRN-005 | `Credit_Applied_Invoices` references invoices | Block submit if any referenced invoice lacks `Invoice_UUID` | `Handle Validation Submission` |
| CRN-006 | `Credits_Remaining` is negative | Block submit | `Handle Validation Submission` |
| CRN-007 | Refund-history or applied-credit rows are removed on edit | Delete orphaned `Refund_Note` / `Apply_Credit_To_Invoice_Line` records and recompute affected invoice credit totals | `Handle Validation Submission` sync blocks |
| CRN-008 | Credit note save succeeds | Set blueprint stage to `Open` if `Credits_Remaining > 0`, or `Closed` if `Credits_Remaining == 0` | `Handle Submission Form and Submit Invoice to LHDN` |
| CRN-009 | Credit note is deleted | Block deletion if linked to `Apply_Credit_To_Invoice_Line` or `Refund_Note` records; remove linked `Journal_Entry` records on successful delete | `Validate Record Deletion` |
| CRN-010 | User submits credit note to LHDN | Allow submission only when blueprint stage is `Closed` | `Submit Credit Note to LHDN` |
| CRN-011 | User converts invoice to credit note | Create new credit note and copy invoice header/line values | `Convert_To_Credit_Note` |
| CRN-012 | User runs record actions on credit note | Support apply credits to invoices and create refund note | `Apply_Credits_to_Invoices`, `Create_Refund_Note_From_C` |
| CRN-013 | Credit note is approved through blueprint | Validate supplier/customer identity via LHDN API before advancing to `Approved` | `Credit_Note_Blueprint` transition `Approve` |
| CRN-014 | `Invoice_Date` or `Payment_Term` changes | Recompute `Due_Date` and `Invoice_For_Usage` | `Handle Invoice Date` |

#### 3.6.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Line subtotals | `Quantity × Unit_Price` per charge grid row | Recalculated on `User_Input_Trigger` |
| Line tax amounts | `Sub_Total × Tax_Pct / 100` | Per line row |
| Line totals | `Sub_Total + Tax_Amount` | Per line row |
| Document subtotal / tax / grand total | Sum across monthly rental, internet, and call charge sections | `Sub_Total`, `Total_Tax`, `Grand_Total` |
| Base-currency total | `Exchange_Rate × Grand_Total` (or `0` if exchange rate is null) | `Grand_Total_Base_Currency` |
| Refund total | Sum of `Refund_History.Refund_History_Amount_Refunded` | `Refund` |
| Credits used | Sum of `Credit_Applied_Invoices.CAI_Amount_Credited` | `Credits_Used` |
| Credits remaining | `Grand_Total - Refund - Credits_Used` | Drives `Open` vs `Closed` routing |

#### 3.6.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Invoice` | Source for conversion via `Convert_To_Credit_Note`; applied credits reduce invoice `Credits_Applied_Total` and `Amount_Due`. |
| Upstream   | `Customer_Profile`, `Tenancy`, `Organization_Settings`, `Payment_Term` | Customer/supplier defaults and due-date context. |
| Downstream | `Apply_Credit_To_Invoice_Line` | Persistent credit-application rows created from apply-credit flow (see §3.5.7). |
| Downstream | `Refund_Note` | Created via `Create_Refund_Note_From_C`; linked through `Reference_Credit_Note`. |
| Downstream | `Journal_Entry` | Linked entries removed on credit note deletion. |
| External   | LHDN (e-Invoicing) | Submission via record action when stage is `Closed`; UUID and public link stored on document. |

#### 3.6.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| `Draft` | Credit note created, not yet submitted for approval | User | `Pending Approval` |
| `Pending Approval` | Awaiting approver action | User (send for approval) | `Approved`, `Rejected` |
| `Rejected` | Approval declined | User (approver) | `Pending Approval` (resubmit) |
| `Approved` | Approved; LHDN validation attempted on approval transition | User (approver) | `Open` (when UUID/link present), `Pending Approval` (revert if missing) |
| `Open` | Credit issued with remaining balance available for application or refund | System (on save when `Credits_Remaining > 0`) or User (`Converted_to_Open`) | `Closed` |
| `Closed` | All credit utilised (applied or refunded) | System (on save when `Credits_Remaining == 0`) or User (`Converted_to_Closed`) | LHDN submission eligible |

Blueprint: `Credit_Note_Blueprint`. On form save success, system may also auto-route directly to `Open` or `Closed` based on `Credits_Remaining`, in addition to manual blueprint transitions.

#### 3.6.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Saving with no line items | Submit blocked | At least one charge line required |
| Telephone category without call charges | Submit blocked | `Charge_Category` validation |
| Applied invoice without LHDN UUID | Submit blocked | Ensures target invoice is e-invoice compliant |
| Negative credits remaining | Submit blocked | Balance integrity check |
| Deleting credit note with applications or refunds | Delete blocked | Remove applications/refunds first |
| LHDN submission while not `Closed` | Action blocked | User message on record action |
| Removing refund/credit rows on edit | Orphan downstream records cleaned automatically | May affect invoice balances — user should verify totals |
### 3.7 Debit Note

#### 3.7.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Records upward billing adjustments — additional charges issued after initial invoicing. Tracks `Amount_Paid` and `Amount_Due`, supports approval and send lifecycle, payment allocation, due-date-driven status, and LHDN e-invoicing with reference to a source invoice. |
| When it is created         | Created manually by finance; or converted from an `Invoice` via record action `Convert_To_Debit_Note1`, which copies invoice header/line values and links `Reference_Invoice`. |
| Created by (User / System) | User creates/edits and runs approval/send/LHDN actions; system assigns debit note number, calculates totals, updates stages on payment, and enforces reference-invoice requirements. |

#### 3.7.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| DBN-001 | Debit note is created (on add) | Generate and persist `Invoice_No` using debit-note numbering function | `Handle Invoice Creation` → `thisapp.debit_note.generate_debit_note_no()` |
| DBN-002 | Debit note is validated on save | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges` | `Handle Validation Submission` |
| DBN-003 | `Charge_Category` includes telephone charges | Require at least one `Call_Charges` row | `Handle Validation Submission` |
| DBN-004 | Any line quantity or unit price is ≤ 0 | Block submit | `Handle Validation Submission` and line input workflows |
| DBN-005 | `Customer` changes | Load candidate `Reference_Invoice` records for customer; warn if none exist | `Handle Customer Name Change` |
| DBN-006 | `Customer_Code` or `Invoice_Date` changes | Recompute `Due_Date` as `Invoice_Date + Payment_Term.Days` when payment term is set | `Handle Customer Code Change`, `Handle Invoice Date` |
| DBN-007 | Line items, tax, exchange rate, or charge category change | Recalculate subtotals, tax, grand totals, and `Amount_Due` | `User_Input_Trigger_Workflow` and related line handlers |
| DBN-008 | Debit note is approved/sent through blueprint | Follow approval loop and route to `Sent` or `Overdue` based on due-date logic | `Debit_Note_Blueprint` |
| DBN-009 | Payment is posted or reversed via `Payment_Received` | Update `Amount_Paid`/`Amount_Due`; set blueprint stage to `Paid`, `Partially Paid`, `Sent`, or `Overdue` | Payment received success/deletion workflows |
| DBN-010 | Debit note is deleted | Block deletion if linked `Payment_Received_Line_Item` records exist | `Validation Of Deletion` |
| DBN-011 | User converts invoice to debit note | Create debit note copying invoice data with `Reference_Invoice` link | `Convert_To_Debit_Note1` |
| DBN-012 | User submits debit note to LHDN | Build reference payload from `Reference_Invoice.Invoice_No` and `Reference_Invoice.Invoice_UUID` before API call | `Submit Debit Note to LHDN` |
| DBN-013 | User records payment on debit note | Open payment form via `Record_Payment_Invoice` (shared with invoice payments) | Record action on debit note |

#### 3.7.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Line subtotals | `Quantity × Unit_Price` per charge grid row | Recalculated on `User_Input_Trigger` |
| Line tax amounts | `Sub_Total × Tax_Pct / 100` | Per line row |
| Line totals | `Sub_Total + Tax_Amount` | Per line row |
| Document subtotal / tax / grand total | Sum across monthly rental, internet, and call charge sections | `Sub_Total`, `Total_Tax`, `Grand_Total` |
| Base-currency total | `Exchange_Rate × Grand_Total` (or `0` if exchange rate is null) | `Grand_Total_Base_Currency` |
| Amount due | `Grand_Total - Amount_Paid` (after payment allocations) | Updated on payment posting/reversal |

#### 3.7.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Invoice` | Source for conversion via `Convert_To_Debit_Note1`; referenced for LHDN submission payload. |
| Upstream   | `Customer_Profile`, `Tenancy`, `Organization_Settings`, `Payment_Term` | Customer/supplier defaults and due-date context. |
| Downstream | `Payment_Received` | Payments allocated via `Record_Payment_Invoice`; updates balances and blueprint stage. |
| Downstream | `Payment_Received_Line_Item` | Child allocation rows linking payment to debit note. |
| External   | LHDN (e-Invoicing) | Submission references original invoice UUID/number; stores UUID and public link on debit note. |

#### 3.7.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| `Draft` | Debit note created, not yet submitted for approval | User | `Pending Approval` |
| `Pending Approval` | Awaiting approver action | User (send for approval) | `Approved`, `Rejected` |
| `Rejected` | Approval declined | User (approver) | `Pending Approval` (resubmit) |
| `Approved` | Approved but not yet sent | User (approver) | `Sent`, `Overdue` (on send routing) |
| `Sent` | Issued to customer and awaiting payment | User (send) or System (payment reversal) | `Partially Paid`, `Paid`, `Overdue` |
| `Partially Paid` | Payment received but balance remains | System (payment posting) | `Paid`, `Sent`, `Overdue` |
| `Paid` | Fully paid | System (payment posting) | — |
| `Overdue` | Past due date with outstanding balance | System (send routing or payment state) | `Partially Paid`, `Paid` |

Blueprint: `Debit_Note_Blueprint`. Declared stages in DS: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Paid`, `Partially Paid`, `Overdue`.

#### 3.7.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Saving with no line items | Submit blocked | At least one charge line required |
| Telephone category without call charges | Submit blocked | `Charge_Category` validation |
| Customer with no reference invoices | Warning shown | User may still proceed depending on form state |
| Deleting debit note with payments | Delete blocked | Remove payment allocations first |
| LHDN submission without reference invoice UUID | Submission may fail or be incomplete | Payload requires `Reference_Invoice` LHDN fields |
### 3.8 Refund Note

#### 3.8.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Records refund amounts issued against unused credit on a `Credit_Note`. Preserves customer/supplier billing context, validates LHDN reference readiness, and synchronises refund balances back to the source credit note. |
| When it is created         | Created from a `Credit_Note` via record action `Create_Refund_Note_From_C`, which opens a prefilled refund form with `Reference_Credit_Note` and customer/address context. Direct manual creation is blocked by validation. |
| Created by (User / System) | User completes refund details and submits; system assigns refund note number, validates against available credit, updates source credit note balances/stage on success, and supports LHDN submission. |

#### 3.8.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| RFN-001 | Refund note is created (on add) | Generate and persist `Invoice_No` using refund-note numbering function | `Handle Invoice Creation` → `thisapp.refund_note.generate_refund_note_no()` |
| RFN-002 | Refund note is validated on save | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges` | `Handle Validation Submission` |
| RFN-003 | `Charge_Category` includes telephone charges | Require at least one `Call_Charges` row | `Handle Validation Submission` |
| RFN-004 | Any line quantity or unit price is ≤ 0 | Block submit | `Handle Validation Submission` |
| RFN-005 | Refund `Grand_Total` exceeds `Reference_Credit_Note.Credits_Remaining` | Block submit | `Handle Validation Submission` |
| RFN-006 | `Is_Refund_Note_Created_from_Credit_Note` is false | Block submit | Enforces credit-note conversion path only |
| RFN-007 | `Customer` changes | Populate `Reference_Credit_Note` options from customer credit notes with positive `Credits_Remaining`; warn if none exist | `Handle Customer Name Change` |
| RFN-008 | `Reference_Credit_Note` is selected | Require credit note UUID/public link and validate LHDN document status | `Handle reference credit note` |
| RFN-009 | Refund note save succeeds | Recalculate source credit note refund history, applied-credit history, and `Credits_Remaining`; set credit note blueprint to `Open` or `Closed` | `Successful form submission` |
| RFN-010 | Refund note is deleted | Block deletion — user must remove via credit note refund history handling | `Validate Record Deletion` |
| RFN-011 | User submits refund note to LHDN | Send refund payload and store returned UUID/public-link metadata | `Submit Refund Note to LHDN` |

#### 3.8.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Line subtotals | `Quantity × Unit_Price` per charge grid row | Recalculated on `User_Input_Trigger` |
| Line tax amounts | `Sub_Total × Tax_Pct / 100` | Per line row |
| Line totals | `Sub_Total + Tax_Amount` | Per line row |
| Document subtotal / tax / grand total | Sum across monthly rental, internet, and call charge sections | `Sub_Total`, `Total_Tax`, `Grand_Total` |
| Base-currency total | `Exchange_Rate × Grand_Total` (or `0` if exchange rate is null) | `Grand_Total_Base_Currency` |
| Source credit note impact | `Refund = sum(refund notes)`; `Credits_Remaining = Grand_Total - Refund - Credits_Used` | Updated on refund save |

#### 3.8.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Credit_Note` | Mandatory reference via `Reference_Credit_Note`; launched from `Create_Refund_Note_From_C`. |
| Upstream   | `Customer_Profile`, `Tenancy`, `Organization_Settings`, `Payment_Term` | Customer/supplier defaults and due-date context. |
| Downstream | `Credit_Note` (balances) | Refund save updates refund history, `Credits_Used`, `Credits_Remaining`, and blueprint stage. |
| External   | LHDN (e-Invoicing) | Submission via record action; references source credit note LHDN metadata. |

#### 3.8.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| New (implicit) | Refund form opened from credit note | User | Posted (on successful add) |
| Posted (implicit) | Refund saved; source credit note balances updated | System (on add success) | — |

No dedicated blueprint for `Refund_Note` in DS — operational state is enforced through validation gates and cross-module credit-note stage updates.

#### 3.8.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Creating refund without credit-note path | Submit blocked | `Is_Refund_Note_Created_from_Credit_Note` gate |
| Refund exceeding available credit | Submit blocked | Compared to `Credits_Remaining` |
| Reference credit note without LHDN readiness | Selection blocked or warned | UUID/public link and status validation |
| Direct deletion of refund note | Delete blocked | Manage through credit note refund history |
| Saving with no line items | Submit blocked | At least one charge line required |
### 3.9 Journal Entry

#### 3.9.1 Module Summary

| Aspect                     | Description |
|----------------------------|-------------|
| Purpose                    | Stores accounting postings linked to billing documents. Records line-level debit/credit movements with document references and balancing totals for finance reconciliation. |
| When it is created         | Created automatically by system during billing/payment events — invoice send/approval, debit note approval, payment received, and pro forma refund. Not created directly by users through a standalone workflow. |
| Created by (User / System) | System inserts journal entries on upstream document events; core fields are read-only when `Created_By_The_System` is true. |

#### 3.9.2 Business Rules

| Rule ID | When (condition) | System must (behavior) | Notes |
|---------|------------------|------------------------|-------|
| JNL-001 | System posting creates journal entry | Generate `Journal_Entry_No` using journal numbering function (`JO` + zero-padded sequence) | `thisapp.journal_entry.generate_journal_no()` |
| JNL-002 | `Payment_Received` is submitted | Create linked journal entry: debit `Paid_To` account, credit trade receivables for `Amount_Received` | `Successful payment received submission` |
| JNL-003 | `Invoice` posting path executes | Create three-line journal entry (`Sub_Total`, `Total_Tax`, `Grand_Total`) linked via `Document_No` and `Invoice` | Invoice send/approval posting scripts |
| JNL-004 | `Debit_Note` is approved | Create three-line journal entry linked via `Debit_Note` and `Document_No = Invoice_No` | `Debit_Note_Blueprint` approve script |
| JNL-005 | `Pro_Forma_Invoices` refund action runs | Create linked journal entry with `Deposits` reference | `Refund1` record action |
| JNL-006 | `Payment_Received` is deleted | Delete related journal entries by `Document_No = Payment_Received_No`; for deposits, also delete entries linked by `Deposits` | Payment deletion workflow |
| JNL-007 | `Invoice` or `Pro_Forma_Invoices` is deleted | Delete journal entries where `Document_No` matches source `Invoice_No` | Invoice and pro forma deletion workflows |
| JNL-008 | `Credit_Note` is deleted | Delete linked journal entries | Credit note deletion cleanup |
| JNL-009 | Journal entry form loads | Disable core reference/total fields; if system-created, line-item account/description/debit/credit and date are read-only | `Disable Fields` |

#### 3.9.3 Calculations

| What is calculated | How it is calculated | Notes |
|--------------------|----------------------|-------|
| Journal number | `"JO" + zero-padded running sequence` | `generate_journal_no()` |
| Sub-total debit/credit | Populated explicitly on system insert | `Sub_Total_Debit`, `Sub_Total_Credit` |
| Total debit/credit | Populated explicitly on system insert | `Total_Debit`, `Total_Credit` |
| Difference | `Total_Debit - Total_Credit` | Balancing check |
| Payment receipt entry | `Total_Debit = Total_Credit = Amount_Received` | Two-line balancing entry |

#### 3.9.4 Relationship to Other Documents

| Direction  | Related document | Relationship |
|------------|------------------|--------------|
| Upstream   | `Invoice` | Send/approval posting creates linked journal entry; deleted on invoice removal. |
| Upstream   | `Debit_Note` | Approval posting creates linked journal entry. |
| Upstream   | `Payment_Received` | Add creates receipt journal; delete removes it. |
| Upstream   | `Pro_Forma_Invoices` | Refund action creates deposit-linked journal entry. |
| Upstream   | `Credit_Note` | Linked entries removed on credit note deletion. |
| Upstream   | `Chart_Of_Account` | Account references on journal line items. |

#### 3.9.5 Status Lifecycle

| Status | Meaning | Moved by (User / System) | Allowed next statuses |
|--------|---------|--------------------------|-----------------------|
| Posted (implicit) | Journal entry created by system posting event | System | Removed (on source document delete/reversal) |
| Removed (implicit) | Journal entry deleted when source document is removed or payment reversed | System | — |

No dedicated blueprint for `Journal_Entry` in DS — lifecycle is event-driven from upstream module workflows.

#### 3.9.6 Exceptions and Restrictions

| Situation | What is not allowed | Notes |
|-----------|---------------------|-------|
| Editing system-created journal lines | Line accounts, amounts, and date are read-only | `Created_By_The_System = true` |
| Manual standalone journal creation | No traced record actions on `Journal_Entry` form | Entries are downstream artifacts of billing events |
| Unbalanced posting | System inserts set `Total_Debit = Total_Credit` | Explicit on payment path |
## 4. Cross-Cutting

### 4.1 Shared Business Rules

| Rule ID | Applies to | When (condition) | System must (behavior) | Notes |
|---------|------------|------------------|------------------------|-------|
| SHR-001 | `Subscription`, `Tenancy`, `Invoice` | Daily `Subscription_Schedule` runs | Query billable tenancies and active subscriptions; create invoices via `create_invoice_current_duration` or `create_invoice_previous_duration` based on `Bill_For` and billing cycle | `Subscription_Schedule` |
| SHR-002 | `Invoice` | 1 week after `Due_Date` and invoice is not `Draft` or paid | Send first payment reminder email using active `Email_Templates` (`Template_Type = Invoice Reminder`, `Reminder_Type = First`) with invoice PDF attachment | `W1st_Remainder_Invoice_Due`; attachment template varies by `Charge_Category` |
| SHR-003 | `Invoice` | 2 weeks after `Due_Date` and invoice is not `Draft` or `Paid` | Send final payment reminder email using active final reminder template with invoice PDF attachment | `Final_Invoice_Reminder` |
| SHR-004 | `Invoice` | `Due_Date` reached and stage is `Approved`, `Sent`, or `Partially Paid` | Move invoice blueprint stage to `Overdue` | `Change_status_to_Overdue_` (daily from due date) |
| SHR-005 | `Payment_Received` | User edits line `Allocation` | Require target document reference; block over-allocation; recompute `Amount_Received`, `Amount_Received_MYR`, and `Total_Still_Owing` | `Handle Payment Received Line Item Allocation` |
| SHR-006 | `Payment_Received`, `Invoice`, `Debit_Note`, `Pro_Forma_Invoices` | Payment is submitted successfully | Update target document `Amount_Paid`/`Amount_Due`; set blueprint stage (`Paid`, `Partially Paid`, `Sent`, or `Overdue`) by balance and due date | `Successful payment received submission` |
| SHR-007 | `Payment_Received`, linked documents, `Journal_Entry` | Payment record is deleted | Reverse allocations and blueprint stages on target documents; delete payment line items and linked journal entries | `_Successful payment received deletion` |
| SHR-008 | All charge-based billing documents | Document is validated on save | Require at least one line item across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`; block zero/negative quantity or unit price | Shared pattern across Invoice, Pro Forma, Credit Note, Debit Note, Refund Note, Subscription |
| SHR-009 | Documents with `Charge_Category` | `Charge_Category` includes telephone charges | Require at least one `Call_Charges` row on submit | Shared validation across billing document forms |
| SHR-010 | Billing documents with document numbers | Record is created (on add) | Assign module-specific document number via namespace generator (`invoice`, `credit_note`, `debit_note`, `refund_note`, `payment_received`, etc.) | Number assigned on add success per module |
| SHR-011 | `Invoice`, `Credit_Note`, `Debit_Note`, `Pro_Forma_Invoices` | Document is approved through blueprint | Validate supplier/customer identity via LHDN API before advancing approval transition | Blueprint `Approve` transition scripts |
| SHR-012 | `Credit_Note`, `Refund_Note`, apply-credit flow | Credit balance changes | Recompute `Credits_Used`, `Refund`, and `Credits_Remaining`; route `Credit_Note_Blueprint` to `Open` or `Closed` | Credit note save, refund save, apply-credit save |
| SHR-013 | `Invoice`, `Pro_Forma_Invoices`, `Credit_Note`, `Debit_Note`, `Refund_Note` | Document form loads on add | Default supplier fields from `Organization_Settings` | Form load initialization workflows |
| SHR-014 | `Journal_Entry` | Upstream billing/payment event posts or source document is deleted | Create balanced journal entry on post; remove linked entries when source document or payment is deleted | Event-driven from invoice, debit note, payment, pro forma refund flows |

### 4.2 Status Summary (All Modules)

| Module | Status | Meaning | Moved by (User / System) |
|--------|--------|---------|--------------------------|
| Tenancy | Active Billing Setup (implicit) | Tenancy in operational use for billing | User + System |
| Tenancy | Billing Settings Locked (implicit) | `Billing_Cycle` / `Bill_Every` / `Bill_For` locked when active subscriptions exist | System |
| Subscription | `Active` | Billable; participates in invoice generation | System (default on add); User |
| Subscription | `Inactive` | Final billing reached or no longer billable | System (billing-date update) |
| Subscription | `Terminated` | Contract explicitly ended | User (status field) |
| Pro Forma Invoice | `Draft` → `Pending Approval` → `Approved` → `Sent` / `Overdue` → `Partially Paid` / `Paid` | Standard approval and receivable lifecycle | User (blueprint); System (payment/overdue) |
| Pro Forma Invoice | `Rejected` | Approval declined | User (approver) |
| Pro Forma Invoice | `Closed` | Blueprint closed state (module-specific) | User / System |
| Invoice | `Draft` → `Pending Approval` → `Approved` → `Sent` / `Overdue` → `Partially Paid` / `Paid` | Primary tax invoice lifecycle | User (blueprint); System (payment, reminders, overdue schedule) |
| Invoice | `Rejected` | Approval declined | User (approver) |
| Payment Received | Posted (implicit) | Payment saved; allocations and journal applied | System |
| Payment Received | Reversed (implicit) | Payment deleted; downstream impacts restored | User + System |
| Payment Received | Receipt sent (`Receipt_Sent` field) | Customer receipt email dispatched | User |
| Credit Note | `Draft` → `Pending Approval` → `Approved` → `Open` / `Closed` | Credit issuance, utilisation, and LHDN eligibility | User (blueprint); System (on save by `Credits_Remaining`) |
| Credit Note | `Rejected` | Approval declined | User (approver) |
| Debit Note | `Draft` → `Pending Approval` → `Approved` → `Sent` / `Overdue` → `Partially Paid` / `Paid` | Additional charge lifecycle | User (blueprint); System (payment/overdue) |
| Debit Note | `Rejected` | Approval declined | User (approver) |
| Refund Note | Posted (implicit) | Refund saved; source credit note balances updated | System |
| Journal Entry | Posted (implicit) | Accounting entry created from upstream event | System |
| Journal Entry | Removed (implicit) | Entry deleted when source document/payment removed | System |

Blueprint references: `Pro_Forma_Invoices_Bluepr`, `Invoice_Blueprint`, `Credit_Note_Blueprint`, `Debit_Note_Blueprint`. Tenancy, Subscription, Payment Received, Refund Note, and Journal Entry use implicit or field-based state only.

### 4.3 Notifications and Emails

| Event | Module | When it is sent | Who receives it | Notes |
|-------|--------|-----------------|-----------------|-------|
| Document approval required | Invoice, Pro Forma Invoice, Credit Note, Debit Note | User sends document for approval | Approver role users (email + in-app notification) | `send_approval_notification` helper |
| Invoice approved | Invoice | Blueprint `Approve` transition succeeds | Finance/coordinator role list | Email + `zoho.pushNotification` with report link |
| Invoice sent to customer | Invoice | User runs send-invoice action / blueprint send path | Customer email (`Customer_E_mail`) | Uses `Email_Templates`; PDF attachment by `Charge_Category` |
| Pro forma sent to customer | Pro Forma Invoice | User runs send action | Customer email (with CC where configured) | Uses `Email_Templates`; pro forma PDF attachment |
| First payment reminder | Invoice | 1 week after `Due_Date` (09:00 Asia/Singapore) | Customer email | `W1st_Remainder_Invoice_Due`; active First reminder template |
| Final payment reminder | Invoice | 2 weeks after `Due_Date` (09:00 Asia/Singapore) | Customer email | `Final_Invoice_Reminder`; active Final reminder template |
| Credits available notice | Invoice | User marks invoice sent when customer has credit available | Customer email (via `Notify_Credits_Available` popup form) | Opened from invoice blueprint send path when credits exist |
| Payment receipt | Payment Received | User runs send receipt action | Customer email | `Receipt_Sent` field updated on success |
| Customer statement | Customer Statement | User submits statement request for date range | Per statement configuration | Aggregates invoices, payments, credits — not a fixed schedule |
| Overdue status change | Invoice | Daily from `Due_Date` at 18:25 (Asia/Singapore) | N/A (status change only) | `Change_status_to_Overdue_` — no customer email in this schedule |

Reminder schedules exclude `Draft` invoices. First reminder filter uses `"paid"` (lowercase); final reminder uses `"Paid"` — see §5.2 open question on stage casing.

### 4.4 Setup and Master Data

| Data item | Required before billing works | Used by module(s) | Notes |
|-----------|-------------------------------|-------------------|-------|
| `Organization_Settings` | Yes | All billing documents, LHDN flows | Supplier defaults, base currency, LHDN Client ID/Secret, portal environment, company/finance emails |
| `Customer_Profile` | Yes | Tenancy, all billing documents | Customer identity, TIN, addresses, portal access |
| `Tenancy` | Yes | Subscription, Invoice, Payment Received, statements | Billing cycle, bill-for, payment term, next billing date, payable account |
| `Tax` | Yes | Subscription, Invoice, Pro Forma, Credit Note, Debit Note, Refund Note | Line-item tax rates and tax types |
| `Payment_Term` | Yes | Tenancy, Subscription, Invoice, Pro Forma, Credit Note, Debit Note, Refund Note | `Due_Date = Invoice_Date + Payment_Term.Days` |
| `Chart_Of_Account` | Yes | Tenancy, Payment Received, Journal Entry | Payable/receivable and bank accounts for posting |
| `Bank` | Recommended | Payment Received (`Paid_To`), organization setup | Bank account context for receipts |
| `Email_Templates` | Yes (for automated comms) | Invoice reminders, send-document flows | `Template_Type`, `Reminder_Type`, `Status = Active`; placeholder merge on send |
| `Transaction_Type` | Yes | Line items on Subscription and billing documents | Item catalog for monthly rental, internet, call charges |
| `Business_Segment` | Recommended | Line items | Analytical segment on charge rows |
| `Business_Unit` | Recommended | Line items | Business unit on charge rows |
| `Circuit_ID` / `Circuit_ID_Type` | As needed | Line items (telecom/circuit services) | Circuit reference on applicable charge lines |
| `User` / roles | Yes | Approval notifications, access control | Administrator, Finance Manager, Finance Executive, Customer portal profiles |
## 5. Alignment and Ongoing Use

### 5.1 Assumptions and Dependencies

| #   | Assumption or dependency | Impact if not met | Owner |
|-----|--------------------------|-------------------|-------|
| 1   | `XMT___Billing_System.ds` export is kept in sync with live Zoho Creator before code or BRD changes are finalised | Local documentation and split files may not match production behaviour | Project owner / Administrator |
| 2   | `Organization_Settings` is configured with valid supplier details, base currency, and LHDN credentials (`Client_ID`, `Client_Secret`, portal environment) | Approval transitions, LHDN submission, and send/reference validations will fail | Administrator |
| 3   | Master data (`Customer_Profile`, `Tax`, `Payment_Term`, `Chart_Of_Account`, `Transaction_Type`, `Email_Templates`) exists before operational billing | Documents cannot be created correctly; reminders and journal posting may fail | Administrator / Finance Manager |
| 4   | Active `Email_Templates` exist for invoice reminders (`Template_Type = Invoice Reminder`, First/Final) and send-document flows | Scheduled reminders and customer send actions will not dispatch email | Administrator |
| 5   | Zoho Creator platform, Zoho mail (`zoho.adminuserid`), and LHDN MyInvois API endpoints remain available | Schedules, notifications, and e-invoicing actions will error at runtime | IT / Zoho platform |
| 6   | Finance users follow blueprint approval sequence (Draft → Pending Approval → Approved → Sent) before expecting payment or LHDN outcomes | Skipping stages may block send, LHDN submit, or reference-document validation | Finance Manager |
| 7   | `Subscription_Schedule` remains enabled and tenancy `Next_Billing_Date` is maintained accurately | Recurring invoices will not generate on expected dates | Operations / Finance Executive |
| 8   | Invoice `Invoice_UUID` and `QR_Invoice_Public_Link` are populated after LHDN-compliant approval before send or credit-reference use | Send actions, credit applications, and refund references may be blocked | Finance Manager |
| 9   | Users do not delete posted payments or approved documents without understanding reversal impacts | Balances, blueprint stages, and journal entries may become inconsistent | Finance Executive / Finance Manager |
| 10  | Customer portal profile (`Customer`) exposes only documents intended for self-service view | Customers may see more or less than business intends | Administrator |

### 5.2 Open Questions and Decisions Needed

| #   | Question | Decision needed from | Status (Open / Resolved) | Resolution |
|-----|----------|----------------------|--------------------------|------------|
| 1   | Invoice reminder schedules use different paid-stage casing (`"paid"` in `W1st_Remainder_Invoice_Due` vs `"Paid"` in `Final_Invoice_Reminder`). What is the canonical `Invoice_Blueprint` stage value, and should filters be normalised? | Finance Manager / Developer | Open | — |
| 2   | `Subscription_Status = Terminated` is available on the form, but traced billing logic only auto-transitions to `Inactive` on final billing completion. Should `Terminated` stop invoice generation immediately? | Finance Manager / Operations | Open | — |
| 3   | Pro forma success workflow `Handle_Submission_Form_an6` opens `#Report:Debit_Notes` after save. Is this intentional or should it redirect to the Pro Forma report? | Finance Manager / Project owner | Open | — |
| 4   | Overdue schedule `Change_status_to_Overdue_` condition mixes `||` and `&&` across stages and `Due_Date < today`. Confirm intended precedence — should due-date check apply to all eligible stages? | Developer / Finance Manager | Open | — |
| 5   | Credit note field `Invoice_No` is used as the credit note document number. Confirm whether reporting/LHDN labelling should display as “Credit Note No.” for customer-facing documents. | Finance Manager / Client | Open | — |

### 5.3 Implementation Status

| Module            | Status (Done / Partial / Not Started) | Notes |
|-------------------|---------------------------------------|-------|
| Tenancy           | Partial                               | Core validations, account numbering, billing-field locks, and Desk integration implemented; no dedicated blueprint — behaviour in form workflows |
| Subscription      | Partial                               | Line calculations, validations, work-order path, and invoice-generation triggers implemented; `Terminated` status behaviour not fully defined in code |
| Pro Forma Invoice | Partial                               | Validation, totals, approval/sending, deposit payments, and LHDN paths implemented; post-submit navigation to Debit Notes report needs confirmation |
| Invoice           | Partial                               | Full lifecycle, reminders, overdue schedule, payments, conversions, and journal posting implemented; logic distributed across blueprint, workflows, functions, and schedules |
| Payment Received  | Partial                               | Allocation, reversal, journal linkage, and apply-credit orchestration implemented; cross-module side effects spread across multiple workflows |
| Credit Note       | Partial                               | Lifecycle, calculations, credit/refund sync, conversion, and LHDN submit implemented; long validation/sync workflow blocks |
| Debit Note        | Partial                               | Validation, conversion, approval/sending, payment-state updates, and LHDN payload implemented across blueprint and payment flows |
| Refund Note       | Partial                               | Numbering, validation, credit-note sync, and LHDN submit implemented; no dedicated blueprint — workflow-driven state |
| Journal Entry     | Partial                               | System posting and cleanup paths implemented from upstream modules; limited standalone user lifecycle on journal form |

Overall system status: **Partial** — end-to-end billing is operational in Creator, but behaviour is distributed across large workflow blocks with open questions in §5.2 before declaring UAT-complete.

### 5.4 Related Documents

| Document | Location | Purpose | Primary audience |
|----------|----------|---------|------------------|
| XMT Billing System export (source of truth) | `XMT___Billing_System.ds` (repo root) | Authoritative Deluge/DSL export of live Creator application | Developer, QA |
| XMT Billing Requirements (technical) | `docs/XMT_Billing_Requirements.md` | Dev-focused requirements with `BR-xxx` rules, evidence citations, and confidence tags | Developer, QA |
| XMT End-to-End Flows | `docs/XMT_End_to_End_Flows.md` | Step-by-step UAT walkthrough with Manual / On Save / Schedule trigger labels | QA, Finance Manager |
| Split Deluge files | `application/` (repo) | Readable per-artifact exports for editing; must be verified against `.ds` before use | Developer |
| Cursor rules — billing gate | `.cursor/rules/billing-business-gate.mdc` | Requires explicit approval before billing logic code changes | Developer, AI-assisted editing |
| Cursor rules — Creator structure | `.cursor/rules/zoho-creator-structure.mdc` | Maps workflows, functions, schedules, and record actions to folder conventions | Developer |

## Appendix (Optional)

### Appendix A. Roles and Responsibilities

| Role | Responsibility | Related module(s) |
|------|----------------|-------------------|
| Administrator | Configure organization settings, taxes, payment terms, chart of accounts, email templates, LHDN environment, and user access | Organization Settings, Tax, Payment Term, Chart of Account, Email Templates, User |
| Finance Manager | Approve and send billing documents; submit to LHDN; review journal entries and customer statements; resolve billing exceptions | Invoice, Pro Forma Invoice, Credit Note, Debit Note, Refund Note, Journal Entry, Customer Statement |
| Finance Executive | Create tenancies and subscriptions; record payments; apply credits; create refund notes; maintain day-to-day billing data | Tenancy, Subscription, Payment Received, Apply Credit to Invoice, Invoice, Credit Note |
| Operations / Sales | Set up customer profiles, tenancies, subscriptions, and work orders; does not typically perform LHDN submission or journal review | Customer Profile, Tenancy, Subscription, Work Order |
| Customer (portal) | View own billing information exposed through portal profile | Portal-enabled invoice and related views |
| QA / UAT | Execute end-to-end test flows against this BRD and `XMT_End_to_End_Flows.md`; verify schedule and on-save automation | All billing modules |

### Appendix B. Revision History

| Version | Date | Author | Summary of changes |
|---------|------|--------|--------------------|
| 1.0 | 18 Jun 2026 | Hazrul | Initial BRD — document orientation, foundation, module requirements (§3.1–3.9), cross-cutting rules, alignment sections |
| 1.1 | 19 Jun 2026 | Hazrul | Renumbered to hierarchical structure (1.x, 2.x, 3.x.x); completed Payment Received through Journal Entry; filled cross-cutting and alignment sections |
