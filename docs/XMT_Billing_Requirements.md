# XMT Billing System — Business Requirements Document (BRD)

> **Audience:** Development Team
> **Purpose:** Single source of truth for expected system behavior. Used for team alignment and to verify Deluge implementation correctness.
> **Status:** Draft — Pending Manager Approval

---

## Table of Contents

1. [Overview & Scope](#1-overview--scope)
2. [Glossary](#2-glossary)
3. [Module Map](#3-module-map)
4. [Shared Business Rules](#4-shared-business-rules)
5. [Per-Module Requirements](#5-per-module-requirements)
   - [5.1 Subscription & Tenancy](#51-subscription--tenancy)
   - [5.2 Pro Forma Invoice](#52-pro-forma-invoice)
   - [5.3 Invoice](#53-invoice)
   - [5.4 Credit Note](#54-credit-note)
   - [5.5 Debit Note](#55-debit-note)
   - [5.6 Refund Note](#56-refund-note)
   - [5.7 Payment Received & Credit Application](#57-payment-received--credit-application)
   - [5.8 Journal Entry](#58-journal-entry)
6. [Document Conversion Matrix](#6-document-conversion-matrix)
7. [Status Lifecycle Summary](#7-status-lifecycle-summary)
8. [Implementation Status Matrix](#8-implementation-status-matrix)
9. [Open Questions](#9-open-questions)

---

## 1. Overview & Scope

This BRD defines the expected billing behavior implemented in the Zoho Creator application, using `XMT___Billing_System.ds` as the primary source of truth. It aligns business expectations with actual Deluge implementation across forms, workflows, schedules, blueprints, and record actions that drive billing documents and accounting-impacting transactions.

### 1.1 Objectives

- Establish one shared reference for how billing records are created, validated, updated, and converted.
- Make module behavior traceable to concrete Deluge evidence so implementation review and QA can verify correctness.
- Identify confirmed behavior, inferred behavior, and unresolved gaps that need stakeholder clarification.

### 1.2 In Scope

This document covers billing-domain modules and their interactions:

- `Tenancy`
- `Subscription`
- `Pro_Forma_Invoices`
- `Invoice`
- `Credit_Note`
- `Debit_Note`
- `Refund_Note`
- `Payment_Received`
- `Apply_Credit_To_Invoices`
- `Journal_Entry`

For each module, scope includes:

- Form structure and key fields that drive behavior
- Form workflows (for example: `on load`, `on user input`, `on add`, `on edit`, `on success`)
- Record actions (`type = functions`) executed from module records
- Scheduled jobs relevant to billing outcomes (for example invoice reminders, overdue transitions, subscription invoicing)
- Blueprint lifecycle states and transitions where defined
- Cross-module document conversion and balance impact

### 1.3 Out of Scope

The following are outside this BRD unless they directly affect billing document behavior:

- UI styling/layout decisions that do not change data or workflow logic
- Non-billing modules and reports with no billing-side effects
- Infrastructure-level concerns (hosting, network, platform administration) not expressed in Deluge logic

### 1.4 Evidence Baseline and Traceability

- Primary authority: `XMT___Billing_System.ds`
- Secondary references: split local files under `application/forms`, `application/Schedule`, and related folders, only when consistent with DS
- Requirement confidence is tagged as `[Confirmed]`, `[Inferred]`, or `[Open Question]`
- Any unresolved or ambiguous behavior is recorded in `§9 Open Questions` rather than assumed

---

## 2. Glossary

### 2.1 Platform Terms

- **form** — Zoho Creator data schema and UI definition for a record type.
- **workflow** — Event-triggered Deluge logic executed on form events such as `on load`, `on user input`, `on add`, `on edit`, and `on success`.
- **schedule** — Time-triggered Deluge logic executed on configured date/time or recurring frequency.
- **blueprint** — State machine that defines allowed stages and transitions for a form record.
- **record action** — User-triggered function (`type = functions`) executed from a record context.
- **subform** — Embedded child row structure used for line items in a parent form.
- **Deluge** — Zoho Creator scripting language used for business logic implementation.

### 2.2 Canonical Module/Form Names

Use these names exactly throughout this BRD:

- `Tenancy`
- `Subscription`
- `Subscription_Line_Item`
- `Invoice`
- `Pro_Forma_Invoices`
- `Credit_Note`
- `Debit_Note`
- `Refund_Note`
- `Payment_Received`
- `Apply_Credit_To_Invoices`
- `Journal_Entry`
- `Customer_Profile`
- `Work_Order_Creation`

### 2.3 Evidence and Requirement Terms

- **[Confirmed]** — Requirement traced directly to specific Deluge implementation in DS or equivalent source file.
- **[Inferred]** — Requirement strongly implied by code structure or naming, but not exhaustively traced through all branches.
- **[Open Question]** — Behavior not conclusively traceable in code; requires stakeholder clarification and logging in `§9 Open Questions`.
- **Source** — Citation line that follows each `[Confirmed]` or `[Inferred]` rule, referencing concrete artifacts such as `thisapp.{module}.{function}`, workflow file, schedule, blueprint, or form field.

---

## 3. Module Map

This section maps each billing module to its primary anchor points in `XMT___Billing_System.ds` for traceability during requirement authoring and verification.

| BRD Module | Canonical Form(s) | Primary DS Anchors | Key Runtime Anchors |
|---|---|---|---|
| Subscription & Tenancy | `Subscription`, `Subscription_Line_Item`, `Tenancy` | `form Subscription`, `form Subscription_Line_Item`, `form Tenancy` | `Subscription_Schedule`; `thisapp.subscription.*`; `thisapp.tenancy.*` |
| Pro Forma Invoice | `Pro_Forma_Invoices` | `form Pro_Forma_Invoices` | `Pro_Forma_Invoices_Bluepr`; record actions for `Pro_Forma_Invoices` |
| Invoice | `Invoice` | `form Invoice` | `Invoice_Blueprint`; schedules `W1st_Remainder_Invoice_Due`, `Final_Invoice_Reminder`, `Change_Status_To_Overdue`; `thisapp.invoice.*` |
| Credit Note | `Credit_Note` | `form Credit_Note` | `Credit_Note_Blueprint`; record actions for `Credit_Note` |
| Debit Note | `Debit_Note` | `form Debit_Note` | `Debit_Note_Blueprint`; record actions for `Debit_Note` |
| Refund Note | `Refund_Note` | `form Refund_Note` | Record actions for `Refund_Note`; no dedicated refund blueprint found in DS blueprint block |
| Payment Received & Credit Application | `Payment_Received`, `Payment_Received_Line_Item`, `Apply_Credit_To_Invoices`, `Apply_Credit_To_Invoice_Line` | Corresponding `form ...` declarations | Workflow and record actions for both forms; blueprint stage updates are triggered against related billing documents |
| Journal Entry | `Journal_Entry` | `form Journal_Entry` | Workflow and record actions for `Journal_Entry`; namespace search target `thisapp.journal*` |

### 3.1 Shared Supporting Forms Referenced by Billing Logic

- `Customer_Profile`
- `Tax`
- `Payment_Term`
- `Chart_Of_Account`
- `Organization_Settings`
- `Business_Segment`
- `Business_Unit`
- `Email_Templates`
- `Work_Order_Creation`
- `Circuit_ID`

### 3.2 Source-of-Truth Rule for Mapping

- If split local files differ from DS, treat `XMT___Billing_System.ds` as authoritative.
- Use split files only as secondary references after DS behavior is confirmed.
- Current branch file-change check for tenancy/invoice/subscription/payment-received scope: no new or deleted files detected; only modifications to `XMT___Billing_System.ds` and `application/forms/Payment Received/Payment_Received_Report.deluge`.

---

## 4. Shared Business Rules

**BR-SHR-001** When an `Invoice` is not in `Draft` or paid stage, system must send the first reminder email at one week after `Due_Date` using an active "Invoice Reminder / First" template, with attachment template selected by `Charge_Category`. [Confirmed]  
Source: `XMT___Billing_System.ds` schedule `W1st_Remainder_Invoice_Due`, form filter `Invoice[Blueprint.Current_Stage != "paid" && Blueprint.Current_Stage != "Draft"]`, form `Email_Templates`.

**BR-SHR-002** When an `Invoice` is not in `Draft` or `Paid` stage, system must send the final reminder email at two weeks after `Due_Date` using an active "Invoice Reminder / Final" template, with attachment template selected by `Charge_Category`. [Confirmed]  
Source: `XMT___Billing_System.ds` schedule `Final_Invoice_Reminder`, form filter `Invoice[Blueprint.Current_Stage != "Paid" && Blueprint.Current_Stage != "Draft"]`, form `Email_Templates`.

**BR-SHR-003** When an `Invoice` is selected by the overdue schedule query and passes due date threshold logic, system must transition the record to `Overdue` through `Invoice_Blueprint`. [Confirmed]  
Source: `XMT___Billing_System.ds` schedule `Change_status_to_Overdue_`, `thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint","Overdue",...)`.

**BR-SHR-004** When `Subscription_Schedule` runs daily, system must query billable `Tenancy` and `Subscription` records and create invoices using `thisapp.invoice.create_invoice_current_duration` or `thisapp.invoice.create_invoice_previous_duration` based on `Bill_For` and billing cycle context. [Confirmed]  
Source: `XMT___Billing_System.ds` schedule `Subscription_Schedule`, `thisapp.tenancy.convert_bill_cycle_to_int`, `thisapp.tenancy.get_monthly_billing_date_from_actual`, `thisapp.invoice.create_invoice_current_duration`, `thisapp.invoice.create_invoice_previous_duration`.

**BR-SHR-005** When a `Payment_Received` line allocation is edited, system must require a target document reference and cap allocation at outstanding balance before recalculating `Amount_Received`, `Amount_Received_MYR`, and `Total_Still_Owing`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Payment_Received_L` (`form = Payment_Received`, `on user input of Payment_Received_Line_Item.Allocation`).

**BR-SHR-006** When `Payment_Received` is submitted with allocations, system must update target document `Amount_Paid` and `Amount_Due` and then set blueprint stage (`Paid`, `Partially Paid`, `Sent`, or `Overdue`) for `Invoice`, `Debit_Note`, or `Pro_Forma_Invoices` based on resulting balances and due date. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Submissio` (`form = Payment_Received`, `on success`), `thisapp.blueprint.changeStage(...)`.

**BR-SHR-007** When a `Payment_Received` record is deleted, system must reverse prior allocation impacts, recompute affected billing document status stages, remove linked payment line items, and delete linked `Journal_Entry` records. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Deletio` (`form = Payment_Received`, `on delete`), deletes on `Payment_Received_Line_Item` and `Journal_Entry`.

---

## 5. Per-Module Requirements

> Each module follows the same structure:
> - **Purpose**
> - **When and how it is created**
> - **Business rules and validations**
> - **Calculations** (line total, tax, balance impact)
> - **Relationship to other modules**
> - **Status lifecycle**
> - **Current implementation status** (Done / Partial / Not Started)

---

### 5.1 Subscription & Tenancy

#### Purpose
`Tenancy` defines customer billing cadence and account context (billing cycle, bill timing, payment term, reminder preference, payable accounts), while `Subscription` defines contracted charge lines and service period details that the system uses to generate recurring invoices.

#### When and How It Is Created
- `Tenancy` is created manually through the `Tenancy` form; account number is auto-generated during validation using `thisapp.tenancy.generate_tenancy_no(...)` when missing.
- `Subscription` is created manually through the `Subscription` form, with default initialization (base currency and `Subscription_Status = "Active"`).
- Initial and recurring invoice creation is triggered from subscription/tenancy billing logic:
  - immediate or near-term creation inside subscription success workflows
  - daily schedule creation through `Subscription_Schedule`

#### Business Rules and Validations
**BR-SUB-001** When a `Tenancy` record is submitted without `Account_Number`, system must require `Account_Type` and generate `Account_Number` using `thisapp.tenancy.generate_tenancy_no(Account_Type)`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validation_on_form_submis` (`form = Tenancy`, `on validate`), `thisapp.tenancy.generate_tenancy_no`.

**BR-SUB-002** When a `Tenancy` has active linked subscriptions, system must lock `Bill_Every`, `Bill_For`, and `Billing_Cycle` on tenancy edit. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Disable_Fields1` (`form = Tenancy`, `on load`), query `Subscription[Subscription_Status == "Active" && Customer_Code == input.ID]`.

**BR-SUB-003** When validating `Tenancy`, system must require `Bill_Every` for monthly billing cycle. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validation_on_form_submis` (`form = Tenancy`, `on validate`).

**BR-SUB-004** When `Subscription.Customer_Code` is selected, system must copy tenancy billing/payment context and reset subscription contract/prorate fields before recalculation. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Tenant_Code_Change` (`form = Subscription`, `on user input of Customer_Code`).

**BR-SUB-005** When validating `Subscription`, system must block submission if no line items exist or if any line quantity/unit price is less than or equal to zero. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss5` (`form = Subscription`, `on validate`).

**BR-SUB-006** When `Create_Work_Order` is true on `Subscription`, system must require `Work_Order_Type`; when unchecked, system must clear and hide `Work_Order_Type`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Validation_Submiss5` and `show_work_order_type_fiel` (`form = Subscription`).

**BR-SUB-007** When subscription line item or charge-category inputs change, system must toggle `User_Input_Trigger` and recalculate line totals and subscription totals. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow group `Handle_*` for `Subscription` and `User_Input_Trigger_Workfl5`.

**BR-SUB-008** When billing reaches final billing date during subscription update flow, system must clear `Next_Billing_Date`, set `Latest_Billing_Date`, and set `Subscription_Status = "Inactive"`. [Confirmed]  
Source: `XMT___Billing_System.ds` function `thisapp.subscription.update_subscription_next_and_last_billing_date`.

**BR-SUB-009** When deleting `Subscription` or `Tenancy`, system must block deletion if dependent billing/work-order records exist. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Validate_Record_Deletion2` (`form = Subscription`) and `Validate_Record_Deletion13` (`form = Tenancy`).

**BR-SUB-010** When `Subscription_Status` is set to `Terminated`, system must define explicit billing and invoice-generation behavior. [Open Question]

#### Calculations
- Subscription line calculations are performed on `User_Input_Trigger`:
  - `Sub_Total_* = Quantity_* * Unit_Price_*`
  - `Tax_Amount_* = Sub_Total_* * Tax_Pct_* / 100`
  - `Total_* = Sub_Total_* + Tax_Amount_*`
- Aggregated totals:
  - `Grand_Total = sum(Total_Monthly_Rental, Total_Internet_Charges, Total_Call_Charges)`
  - `Grand_Total_Base_Currency = sum(each line total * Exchange_Rate)`
- Tenant billing-cycle conversion (`thisapp.tenancy.convert_bill_cycle_to_int`) is used to default line quantities from tenancy cadence.
Source: `XMT___Billing_System.ds` workflow `User_Input_Trigger_Workfl5` (`form = Subscription`), workflows `Handle_*_Item` for subscription line items.

#### Relationships to Other Modules
- Upstream:
  - `Customer_Profile` and `Organization_Settings` provide customer and currency defaults.
  - `Tenancy` drives subscription billing cadence and payment context (`Billing_Cycle`, `Bill_For`, `Bill_Every`, `Payment_Term`, `Payable_To`).
- Downstream:
  - `Invoice` is generated from subscription lifecycle workflows and the `Subscription_Schedule`.
  - `Work_Order_Creation` is initiated from subscription work-order flow and can trigger ticket creation (`thisapp.subscription.create_ticket_for_work_order`).
  - Zoho Desk account/contact synchronization is performed from tenancy create/edit flows (`thisapp.tenancy.create_account_desk`, `thisapp.tenancy.sync_desk_technical_contact_on_edit`).

#### Status Lifecycle
- `Subscription` lifecycle is field-driven (no blueprint found for `Subscription` in DS):
  - Defined statuses in form: `Active`, `Inactive`, `Terminated`
  - Create flow initializes `Subscription_Status` to `Active`
  - Billing-update function sets `Subscription_Status` to `Inactive` when final billing is reached
- `Tenancy` has no explicit status lifecycle field; billing state is represented operationally through `Latest_Billing_Date`, `Next_Billing_Date`, and `Final_Billing_Date`.
Source: `XMT___Billing_System.ds` form `Subscription` field `Subscription_Status`; workflow `Initialize_Form_Defaults_`; function `thisapp.subscription.update_subscription_next_and_last_billing_date`; forms `Subscription` and `Tenancy`.

#### Implementation Status
`Partial` — Core tenancy/subscription defaults, validations, and billing-driven invoice generation are implemented; lifecycle behavior remains distributed across large workflow blocks and schedule/function paths with limited explicit handling for `Terminated` subscriptions.  
Latest DS delta: billing-generation paths were refactored to helper-based calculations (`thisapp.invoice.create_invoice_current_duration_helper`, `thisapp.invoice.create_invoice_previous_duration_helper`, `thisapp.invoice.calculate_subtotal_item_line`, `thisapp.invoice.calculate_tax_item_line`) and normalized tenancy-cycle variable usage (`tenancy_billing_cycle_int`) in subscription/tenancy-driven invoice creation calls.

---

### 5.2 Pro Forma Invoice

#### Purpose
`Pro_Forma_Invoices` represents deposit/pro-forma billing documents used to request payment before or alongside downstream billing flows. It captures charge lines, tax totals, amount due, approval/sending lifecycle, and deposit-payment linkage.

#### When and How It Is Created
- Manual creation through the `Pro_Forma_Invoices` form (`record event = on add`), with supplier defaults loaded from `Organization_Settings`.
- On create success, the document number is generated via `thisapp.deposit.generate_proforma_invoice_no()`.
- Sending actions are performed through blueprint transition (`Send_Invoice`) and record actions (`Send_Proforma_Invoice1`, `Mark_As_Sent_Invoice1`).
- Deposit collection is initiated from record action `Record_Payment_Deposit1`, which opens prefilled `Payment_Received` in deposit mode.

#### Business Rules and Validations
**BR-PFI-001** When a `Pro_Forma_Invoices` record is created, system must generate `Invoice_No` using `thisapp.deposit.generate_proforma_invoice_no()`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Invoice_Creation4` (`form = Pro_Forma_Invoices`, `on add`, `on success`); function `deposit.generate_proforma_invoice_no`.

**BR-PFI-002** When validating `Pro_Forma_Invoices`, system must block submission if no line items exist across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss4` (`form = Pro_Forma_Invoices`, `on validate`).

**BR-PFI-003** When `Charge_Category` includes telephone charges, system must block submission unless `Call_Charges` contains at least one row. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss4` (`form = Pro_Forma_Invoices`, `on validate`).

**BR-PFI-004** When validating line items for `Pro_Forma_Invoices`, system must block submission if any quantity or unit price is less than or equal to zero. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss4` (`form = Pro_Forma_Invoices`, `on validate`) and line input workflows `Handle_*_Quantity` / `Handle_*_Unit_Price`.

**BR-PFI-005** When line-item, tax, exchange-rate, or charge-category inputs change, system must toggle `User_Input_Trigger` and recalculate form totals and `Amount_Due`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_*` for `Pro_Forma_Invoices` plus `User_Input_Trigger_Workfl4`.

**BR-PFI-006** When `Invoice_Date` or `Payment_Term` changes and both are available, system must recompute `Due_Date` as `Invoice_Date + Payment_Term.Days`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Invoice_Date4` and tenant-context update block before `Handle_Submission_Form_an6`.

**BR-PFI-007** When a user selects `Reference_Invoice` for `Pro_Forma_Invoices`, system must reject references missing `Invoice_UUID` or `Invoice_Public_Link`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_reference_invoice_1` (`form = Pro_Forma_Invoices`, `on user input of Reference_Invoice`).

**BR-PFI-008** When sending an approved `Pro_Forma_Invoices`, system must move lifecycle to `Sent` if `Due_Date` is in the future, otherwise to `Overdue`. [Confirmed]  
Source: `XMT___Billing_System.ds` blueprint `Pro_Forma_Invoices_Bluepr` transition `Send_Invoice` and functions `Send_Proforma_Invoice1`, `Mark_As_Sent_Invoice1`.

**BR-PFI-009** When `Pro_Forma_Invoices` has payment allocations in `Payment_Received_Line_Item`, system must block deletion. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validation_Of_Deletion1` (`form = Pro_Forma_Invoices`, `on delete`, `on validate`).

**BR-PFI-010** When a `Pro_Forma_Invoices` record is deleted successfully, system must remove linked `Journal_Entry` records by matching `Document_No = Invoice_No`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Deletion_Of_Record1` (`form = Pro_Forma_Invoices`, `on delete`, `on success`).

**BR-PFI-011** When Pro Forma is submitted, system opens `Debit_Notes` report by default; confirm intended post-submit navigation for this module. [Open Question]

#### Calculations
- Line-level formulas are recalculated on `User_Input_Trigger`:
  - `Sub_Total_* = Quantity_* * Unit_Price_*`
  - `Tax_Amount_* = Sub_Total_* * Tax_Pct_* / 100`
  - `Total_* = Sub_Total_* + Tax_Amount_*`
- Document-level formulas:
  - `Sub_Total = Sub_Total_Monthly_Rental + Sub_Total_Internet_Charges + Sub_Total_Call_Charges`
  - `Total_Tax = Total_Tax_Monthly_Rental + Total_Tax_Internet_Charges + Total_Tax_Call_Charges`
  - `Grand_Total = Grand_Total_Monthly_Rental + Grand_Total_Internet_Charges + Grand_Total_Call_Charges`
  - `Grand_Total_Base_Currency = Exchange_Rate * Grand_Total` (or `0` if exchange rate is null)
  - `Amount_Due = Grand_Total` (before payment updates)
Source: `XMT___Billing_System.ds` workflow `User_Input_Trigger_Workfl4` (`form = Pro_Forma_Invoices`).

#### Relationships to Other Modules
- Upstream:
  - `Organization_Settings`, `Customer_Profile`, `Tenancy`, `Payment_Term`, and `Transaction_Type` drive default values, due-date setup, and line metadata.
  - `Invoice` can be linked as `Reference_Invoice` with UUID/public-link constraints.
- Downstream:
  - `Payment_Received` in deposit mode updates `Amount_Paid`, `Amount_Due`, and stage outcomes (`Paid`, `Partially Paid`, `Sent`, `Overdue`).
  - `Journal_Entry` can be created from refund flow (`Refund1`) and is cleaned up on pro-forma deletion.
  - Email templates and notification flows are triggered during approval/sending stages and record actions.

#### Status Lifecycle
`Pro_Forma_Invoices` lifecycle is managed by `Pro_Forma_Invoices_Bluepr`.

- Declared stages: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Paid`, `Partially Paid`, `Overdue`.
- Core transitions include:
  - `Send_For_Approval` (`Draft` -> `Pending Approval`)
  - `Approve` / `Reject` / `Resubmit` approval loop
  - `Send_Invoice` (`Approved` -> `Sent`, with due-date path to `Overdue`)
  - payment-result transitions between `Sent`, `Partially Paid`, `Paid`, and `Overdue`
Source: `XMT___Billing_System.ds` blueprint `Pro_Forma_Invoices_Bluepr`; payment workflows calling `thisapp.blueprint.changeStage("Pro_Forma_Invoices","Pro_Forma_Invoices_Bluepr",...)`.

#### Implementation Status
`Partial` — Core calculations, validations, approval/sending lifecycle, and deposit-payment integration are implemented; behavior is distributed across extensive workflows/blueprint/actions and includes at least one navigation ambiguity needing confirmation.

---

### 5.3 Invoice

#### Purpose
`Invoice` is the primary receivable document for billed charges. It consolidates line-based charges, applies taxes and credits, tracks payment impact (`Amount_Paid`, `Amount_Due`), and drives downstream customer communication, blueprint lifecycle changes, and accounting entries.

#### When and How It Is Created
- Manual creation through the `Invoice` form (`record event = on add`), with default supplier and date initialization.
- System-generated from subscription billing logic through schedule-driven calls to `thisapp.invoice.create_invoice_current_duration(...)` and `thisapp.invoice.create_invoice_previous_duration(...)`.
- Invoice number assignment is finalized post-create by workflow (`thisapp.invoice.generate_invoice_number()` in on-success create flow).

#### Business Rules and Validations
**BR-INV-001** When an `Invoice` record is created, system must generate and persist `Invoice_No` using `thisapp.invoice.generate_invoice_number()`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Invoice_Creation` (`form = Invoice`, `record event = on add`, `on success`), `thisapp.invoice.generate_invoice_number`.

**BR-INV-002** When validating an `Invoice`, system must block submission if no line item exists across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss` (`form = Invoice`, `on validate`).

**BR-INV-003** When `Charge_Category` includes telephone charges, system must block submission unless at least one `Call_Charges` row is present. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss` (`form = Invoice`, `on validate`).

**BR-INV-004** When validating `Invoice` line rows, system must block submission if any quantity or unit price is less than or equal to zero. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss` (`form = Invoice`, `on validate`); workflows `Handle_*_Quantity` and `Handle_*_Unit_Price`.

**BR-INV-005** When `Credits_Applied_Total` exceeds `Grand_Total`, system must block submission. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss` (`form = Invoice`, `on validate`).

**BR-INV-006** When `Invoice_Date` or `Customer_Code` context changes, system must recompute `Due_Date`, `Previous_Balance`, and `Total_Amount_Due` using payment terms and `thisapp.invoice.invoice_balance_updates(...)`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Invoice_Date`, `Handle_Customer_Code_Chan`, `Load_of_the_form_Initiali`; `thisapp.invoice.invoice_balance_updates`.

**BR-INV-007** When line item fields or tax selections change, system must toggle `User_Input_Trigger` to recalculate subtotals, tax amounts, grand totals, and `Amount_Due`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Monthly_Rental_*`, `Handle_Internet_Charges_*`, `Handle_Call_Charges_*`, `Handle_Exchange_Rate`, `User_Input_Trigger_Workfl`.

**BR-INV-008** When an `Invoice` is approved through `Invoice_Blueprint`, system must validate supplier/customer identity and address data and attempt LHDN API submission before advancing lifecycle routing. [Confirmed]  
Source: `XMT___Billing_System.ds` blueprint `Invoice_Blueprint` transition `Approve` (after script with token retrieval, taxpayer validation, and submission payload preparation).

**BR-INV-009** When sending an approved invoice, system must enforce `Invoice_UUID` and `QR_Invoice_Public_Link` presence and set lifecycle to `Sent` or `Overdue` based on `Due_Date`. [Confirmed]  
Source: `XMT___Billing_System.ds` blueprint `Invoice_Blueprint` transition `Send_Invoice`; record action `Send_Invoice`; `thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint",...)`.

**BR-INV-010** When an `Invoice` is deleted, system must remove linked `Journal_Entry` records and recalculate balances from the next later invoice for the same customer context when present. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Deletion_Of_Invoic` (`form = Invoice`, `record event = on delete`, `on success`).

#### Calculations
- Line calculations are performed per subform row:  
  - `Sub_Total_* = Quantity_* * Unit_Price_*`  
  - `Tax_Amount_* = Sub_Total_* * Tax_Pct_* / 100`  
  - `Total_* = Sub_Total_* + Tax_Amount_*`
- Section totals aggregate row totals independently for `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`.
- Document totals are derived as:
  - `Sub_Total = Sub_Total_Monthly_Rental + Sub_Total_Internet_Charges + Sub_Total_Call_Charges`
  - `Total_Tax = Total_Tax_Monthly_Rental + Total_Tax_Internet_Charges + Total_Tax_Call_Charges`
  - `Grand_Total = Grand_Total_Monthly_Rental + Grand_Total_Internet_Charges + Grand_Total_Call_Charges`
  - `Grand_Total_Base_Currency = Grand_Total * Exchange_Rate`
  - `Amount_Due = Grand_Total - Amount_Paid - Credits_Applied_Total`
  - `Total_Amount_Due = Amount_Due + Previous_Balance`
Source: `XMT___Billing_System.ds` workflow `User_Input_Trigger_Workfl` (`form = Invoice`, `on user input of User_Input_Trigger`).

#### Relationships to Other Modules
- Upstream:
  - `Subscription`/`Tenancy` schedule flow creates invoices (`thisapp.invoice.create_invoice_current_duration`, `thisapp.invoice.create_invoice_previous_duration`).
  - `Organization_Settings`, `Customer_Profile`, `Tax`, `Business_Segment`, and `Business_Unit` provide defaulting and line metadata.
- Downstream:
  - `Payment_Received` allocations update `Invoice.Amount_Paid`, `Invoice.Amount_Due`, and stage outcomes.
  - `Apply_Credit_To_Invoices` updates `Credits_Applied` and `Credits_Applied_Total`.
  - `Journal_Entry` entries are created during send/approval flows and removed on invoice deletion.
  - Reminder schedules and overdue schedules operate on `Invoice` stage/date conditions.

#### Status Lifecycle
`Invoice` lifecycle is governed by `Invoice_Blueprint`.

- Declared stages: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Partially Paid`, `Paid`, `Overdue`.
- Core transitions observed in blueprint and record actions include:
  - `Send_For_Approval` (`Draft` -> `Pending Approval`)
  - `Approve` / `Reject` / `Resubmit` around approval loop
  - `Send_Invoice` (`Approved` -> `Sent`, with due-date path to `Overdue`)
  - payment-result transitions to `Partially Paid` / `Paid`
  - due-date-based movement to `Overdue`
Source: `XMT___Billing_System.ds` blueprint `Invoice_Blueprint`, functions `Bulk_Send_For_Approval_In`, `Bulk_Approve_Invoices`, workflow/schedule calls to `thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint",...)`.

#### Implementation Status
`Partial` — Core invoice lifecycle, validations, calculations, reminders, and posting logic are implemented; some lifecycle behavior is split across blueprint, workflows, functions, and schedules and should be consolidated during refactoring.  
Latest DS delta: overdue schedule anchor moved from `Change_Status_To_Overdue` to `Change_status_to_Overdue_`, and schedule filter logic now includes `Approved` stage with updated condition expression.

---

### 5.4 Credit Note

#### Purpose
`Credit_Note` records post-issuance credits for customer billing adjustments. It supports approval routing, credit application to invoices, refund tracking, remaining-credit management, and controlled submission to LHDN.

#### When and How It Is Created
- Manual creation through the `Credit_Note` form (`record event = on add`), with supplier defaults loaded from `Organization_Settings`.
- Conversion from `Invoice` through record action `Convert_To_Credit_Note`, which creates a new credit note and copies invoice header/line data.
- On create success, system assigns `Invoice_No` using `thisapp.credit_note.generate_credit_note_no()`.
- Post-submit flow recalculates credit balances and routes blueprint stage to `Open` or `Closed` based on `Credits_Remaining`.

#### Business Rules and Validations
**BR-CN-001** When a `Credit_Note` is created, system must generate `Invoice_No` using `thisapp.credit_note.generate_credit_note_no()`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Invoice_Creation1` (`form = Credit_Note`, `on add`, `on success`); function `credit_note.generate_credit_note_no`.

**BR-CN-002** When validating `Credit_Note`, system must block submission if no line items exist across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss2` (`form = Credit_Note`, `on validate`).

**BR-CN-003** When `Charge_Category` includes telephone charges, system must block submission unless `Call_Charges` contains at least one row. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss2` (`form = Credit_Note`, `on validate`).

**BR-CN-004** When validating credit-note line rows, system must block submission if any quantity or unit price is less than or equal to zero. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss2` (`form = Credit_Note`, `on validate`) and line input workflows `Handle_*` for `Credit_Note`.

**BR-CN-005** When `Credit_Applied_Invoices` includes invoice references, system must block submission if any referenced `Invoice` has empty `Invoice_UUID`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss2` (`form = Credit_Note`, validation block for applied invoices).

**BR-CN-006** When `Credits_Remaining` is negative, system must block submission. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss2` (`form = Credit_Note`, `on validate`).

**BR-CN-007** When refund-history rows or applied-credit rows are removed from `Credit_Note`, system must delete orphaned `Refund_Note`/`Apply_Credit_To_Invoice_Line` records and recompute affected `Invoice` credit totals. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss2` (`form = Credit_Note`, synchronization blocks for `Refund_History` and `Credit_Applied_Invoices`).

**BR-CN-008** When `Credit_Note` submission succeeds, system must set `Credit_Note_Blueprint` stage to `Open` if `Credits_Remaining > 0` and to `Closed` if `Credits_Remaining == 0`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Submission_Form_an4` (`form = Credit_Note`, `on success`), `thisapp.blueprint.changeStage("Credit_Note","Credit_Note_Blueprint",...)`.

**BR-CN-009** When deleting `Credit_Note`, system must block deletion if it is linked to `Apply_Credit_To_Invoice_Line` or linked `Refund_Note` records. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validate_Record_Deletion4` (`form = Credit_Note`, `on delete`, `on validate`).

**BR-CN-010** When submitting a `Credit_Note` to LHDN via record action, system must allow submission only when current blueprint stage is `Closed`. [Confirmed]  
Source: `XMT___Billing_System.ds` function `Submit_Credit_Note_to_LHD1` (`form = Credit_Note`), guard `if(input.Blueprint.Current_Stage != "Closed")`.

#### Calculations
- Line-level formulas are recalculated on `User_Input_Trigger`:
  - `Sub_Total_* = Quantity_* * Unit_Price_*`
  - `Tax_Amount_* = Sub_Total_* * Tax_Pct_* / 100`
  - `Total_* = Sub_Total_* + Tax_Amount_*`
- Document totals:
  - `Sub_Total = Sub_Total_Monthly_Rental + Sub_Total_Internet_Charges + Sub_Total_Call_Charges`
  - `Total_Tax = Total_Tax_Monthly_Rental + Total_Tax_Internet_Charges + Total_Tax_Call_Charges`
  - `Grand_Total = Grand_Total_Monthly_Rental + Grand_Total_Internet_Charges + Grand_Total_Call_Charges`
  - `Grand_Total_Base_Currency = Exchange_Rate * Grand_Total` (or `0` when exchange rate is null)
- Credit-balance formulas:
  - `Refund = sum(Refund_History.Refund_History_Amount_Refunded)`
  - `Credits_Used = sum(Credit_Applied_Invoices.CAI_Amount_Credited)`
  - `Credits_Remaining = Grand_Total - Refund - Credits_Used`
Source: `XMT___Billing_System.ds` workflow `User_Input_Trigger_Workfl2` (`form = Credit_Note`).

#### Relationships to Other Modules
- Upstream:
  - `Invoice` can be converted to `Credit_Note` through `Convert_To_Credit_Note`.
  - `Organization_Settings`, `Customer_Profile`, `Tenancy`, and `Payment_Term` provide default and due-date context.
- Downstream:
  - `Apply_Credit_To_Invoices` applies available credits to invoices and writes `Apply_Credit_To_Invoice_Line`.
  - `Refund_Note` can be created from a credit note via `Create_Refund_Note_From_C`.
  - `Invoice` balances are updated when credit applications are added/removed.
  - LHDN submission for `Credit_Note` depends on applied-invoice references and closed-stage eligibility.

#### Status Lifecycle
`Credit_Note` lifecycle is managed by `Credit_Note_Blueprint`.

- Declared stages: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Open`, `Closed`.
- Core transitions include:
  - `Send_For_Approval` (`Draft` -> `Pending Approval`)
  - `Approve` / `Reject` / `Resubmit` approval loop
  - `Converted_to_Open` (`Approved` -> `Open`) when UUID/public-link criteria are satisfied
  - `Converted_to_Closed` (`Open` -> `Closed`)
  - `Revert_to_Pending_Approva` (`Approved` -> `Pending Approval`) when UUID/public-link criteria are not met
Source: `XMT___Billing_System.ds` blueprint `Credit_Note_Blueprint` and workflow `Handle_Submission_Form_an4`.

#### Implementation Status
`Partial` — Core credit-note lifecycle, calculations, credit/refund synchronization, conversion, and validation controls are implemented; behavior remains distributed across long workflow blocks and multiple module interactions.

---

### 5.5 Debit Note

#### Purpose
`Debit_Note` records upward billing adjustments for customer charges after initial billing context exists. It supports approval and sending lifecycle, due-date-driven status movement, payment allocation tracking, and optional LHDN submission with reference linkage.

#### When and How It Is Created
- Manual creation through the `Debit_Note` form (`record event = on add`), with supplier defaults loaded from `Organization_Settings`.
- Conversion from `Invoice` through record action `Convert_To_Debit_Note1`, which creates a debit note by copying invoice header/line values.
- On create success, system assigns `Invoice_No` using `thisapp.debit_note.generate_debit_note_no()`.
- Form success route currently navigates to `#Report:Debit_Notes`.

#### Business Rules and Validations
**BR-DN-001** When a `Debit_Note` is created, system must generate `Invoice_No` using `thisapp.debit_note.generate_debit_note_no()`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Invoice_Creation2` (`form = Debit_Note`, `on add`, `on success`); function `debit_note.generate_debit_note_no`.

**BR-DN-002** When validating `Debit_Note`, system must block submission if no line items exist across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss1` (`form = Debit_Note`, `on validate`).

**BR-DN-003** When `Charge_Category` includes telephone charges, system must block submission unless `Call_Charges` contains at least one row. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss1` (`form = Debit_Note`, `on validate`).

**BR-DN-004** When validating debit-note line rows, system must block submission if any quantity or unit price is less than or equal to zero. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss1` (`form = Debit_Note`, `on validate`) and line input workflows `Handle_*` for `Debit_Note`.

**BR-DN-005** When `Customer` changes on `Debit_Note`, system must load candidate `Reference_Invoice` records for that customer and show a warning if none exist. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Customer_Name_Chan2` (`form = Debit_Note`, `on user input of Customer`).

**BR-DN-006** When `Customer_Code` context changes and `Payment_Term` is available, system must recompute `Due_Date` as `Invoice_Date + Payment_Term.Days`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Customer_Code_Chan3`, `Handle_Invoice_Date1` (`form = Debit_Note`).

**BR-DN-007** When line-item, tax, exchange-rate, or charge-category inputs change, system must toggle `User_Input_Trigger` and recompute totals and `Amount_Due`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_*` for `Debit_Note` and `User_Input_Trigger_Workfl1`.

**BR-DN-008** When `Debit_Note` is submitted to LHDN through record action, system must build reference payload from `Reference_Invoice.Invoice_No` and `Reference_Invoice.Invoice_UUID` before calling debit-note submission routine. [Confirmed]  
Source: `XMT___Billing_System.ds` function `Submit_Debit_Note_to_LHDN` (`form = Debit_Note`), payload fields `reference_invoice_number`, `reference_invoice_uuid`, call `thisapp.debit_note_submit_lhdn(...)`.

**BR-DN-009** When payment is posted or reversed through `Payment_Received`, system must update `Debit_Note.Amount_Paid`, `Debit_Note.Amount_Due`, and set `Debit_Note_Blueprint` stage (`Paid`, `Partially Paid`, `Sent`, `Overdue`) based on resulting balance and due-date context. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Successful_Submissio` and `Handle_Successful_Deletio` (`form = Payment_Received`), `thisapp.blueprint.changeStage("Debit_Note","Debit_Note_Blueprint",...)`.

**BR-DN-010** When deleting a `Debit_Note`, system must block deletion if linked `Payment_Received_Line_Item` records exist. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validation_Of_Deletion2` (`form = Debit_Note`, `on delete`, `on validate`).

#### Calculations
- Line-level formulas are recalculated on `User_Input_Trigger`:
  - `Sub_Total_* = Quantity_* * Unit_Price_*`
  - `Tax_Amount_* = Sub_Total_* * Tax_Pct_* / 100`
  - `Total_* = Sub_Total_* + Tax_Amount_*`
- Document totals:
  - `Sub_Total = Sub_Total_Monthly_Rental + Sub_Total_Internet_Charges + Sub_Total_Call_Charges`
  - `Total_Tax = Total_Tax_Monthly_Rental + Total_Tax_Internet_Charges + Total_Tax_Call_Charges`
  - `Grand_Total = Grand_Total_Monthly_Rental + Grand_Total_Internet_Charges + Grand_Total_Call_Charges`
  - `Grand_Total_Base_Currency = Exchange_Rate * Grand_Total` (or `0` when exchange rate is null)
  - `Amount_Due = Grand_Total` (before payment allocation updates)
Source: `XMT___Billing_System.ds` workflow `User_Input_Trigger_Workfl1` (`form = Debit_Note`).

#### Relationships to Other Modules
- Upstream:
  - `Invoice` can be converted to `Debit_Note` through `Convert_To_Debit_Note1` and linked via `Reference_Invoice`.
  - `Organization_Settings`, `Customer_Profile`, `Tenancy`, and `Payment_Term` provide defaults and due-date context.
- Downstream:
  - `Payment_Received` updates debit-note paid/due amounts and stage outcomes.
  - LHDN submission flow writes UUID/public-link data and related-list records.

#### Status Lifecycle
`Debit_Note` lifecycle is managed by `Debit_Note_Blueprint`.

- Declared stages: `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Paid`, `Partially Paid`, `Overdue`.
- Core transitions observed include:
  - `Send_For_Approval` (`Draft` -> `Pending Approval`)
  - `Approve` / `Reject` / `Resubmit` approval loop
  - send-path movement from approved to `Sent` or `Overdue` based on due-date logic
  - payment-result transitions to `Partially Paid` / `Paid` and due-date-based `Overdue`
Source: `XMT___Billing_System.ds` blueprint `Debit_Note_Blueprint`; approval/send routing in blueprint scripts; payment-driven stage updates in `Payment_Received` workflows.

#### Implementation Status
`Partial` — Core debit-note validation, calculation, conversion, approval/sending, payment-state updates, and LHDN submission payloading are implemented; behavior remains distributed across blueprint, workflows, and cross-module payment flows.

---

### 5.6 Refund Note

#### Purpose
`Refund_Note` records refund amounts issued against a referenced `Credit_Note`, while preserving customer/supplier billing context, recalculating refund line totals, and synchronizing refund balances back to the source `Credit_Note`.

#### When and How It Is Created
- Creation is initiated from `Credit_Note` using record action `Create_Refund_Note_From_C`, which opens `Refund_Note` with prefilled customer/address/currency context and `Reference_Credit_Note`.
- On add success, `Invoice_No` is assigned through `thisapp.refund_note.generate_refund_note_no()`.
- Form success route navigates to `#Report:Refund_Notes`.
- Direct manual creation is effectively blocked by validation requiring `Is_Refund_Note_Created_from_Credit_Note = true`.

#### Business Rules and Validations
**BR-RN-001** When a `Refund_Note` is created, system must generate `Invoice_No` using `thisapp.refund_note.generate_refund_note_no()`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Invoice_Creation3` (`form = Refund_Note`, `on add`, `on success`); function `refund_note.generate_refund_note_no`.

**BR-RN-002** When validating `Refund_Note`, system must block submission if no line items exist across `Monthly_Rental`, `Internet_Charges`, and `Call_Charges`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss3` (`form = Refund_Note`, `on validate`).

**BR-RN-003** When `Charge_Category` includes telephone charges, system must block submission unless at least one `Call_Charges` row exists. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss3` (`form = Refund_Note`, `on validate`).

**BR-RN-004** When validating refund-note line rows, system must block submission if any quantity or unit price is less than or equal to zero. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss3` (`form = Refund_Note`, `on validate`).

**BR-RN-005** When `Reference_Credit_Note.Credits_Remaining` is lower than refund `Grand_Total`, system must block submission. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss3` (`form = Refund_Note`, `on validate`).

**BR-RN-006** When `Refund_Note` is not created through the credit-note conversion path (`Is_Refund_Note_Created_from_Credit_Note = false`), system must block submission. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Validation_Submiss3` (`form = Refund_Note`, `on validate`) and function `Create_Refund_Note_From_C` (`form = Credit_Note`).

**BR-RN-007** When `Customer` changes on `Refund_Note`, system must populate `Reference_Credit_Note` options using customer credit notes with positive `Credits_Remaining` and warn if none exist. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Customer_Name_Chan4` (`form = Refund_Note`, `on user input of Customer`).

**BR-RN-008** When `Reference_Credit_Note` is selected, system must enforce LHDN reference readiness by requiring UUID/public link and validating LHDN document status before allowing use as reference. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_reference_credit_n` (`form = Refund_Note`, `on user input of Reference_Credit_Note`).

**BR-RN-009** When `Refund_Note` saves successfully, system must recalculate source `Credit_Note` refund history, applied-credit history, and `Credits_Remaining`, then set `Credit_Note_Blueprint` stage to `Open` or `Closed` based on remaining credit. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Successful_form_submissio1` (`form = Refund_Note`, `on success`), `thisapp.blueprint.changeStage("Credit_Note","Credit_Note_Blueprint",...)`.

**BR-RN-010** When deleting a `Refund_Note`, system must block deletion and instruct user to delete through credit-note refund history handling. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validate_Record_Deletion5` (`form = Refund_Note`, `on delete`, `on validate`).

#### Calculations
- Line-level formulas on `User_Input_Trigger`:
  - `Sub_Total_* = Quantity_* * Unit_Price_*`
  - `Tax_Amount_* = Sub_Total_* * Tax_Pct_* / 100`
  - `Total_* = Sub_Total_* + Tax_Amount_*`
- Document totals:
  - `Sub_Total = Sub_Total_Monthly_Rental + Sub_Total_Internet_Charges + Sub_Total_Call_Charges`
  - `Total_Tax = Total_Tax_Monthly_Rental + Total_Tax_Internet_Charges + Total_Tax_Call_Charges`
  - `Grand_Total = Grand_Total_Monthly_Rental + Grand_Total_Internet_Charges + Grand_Total_Call_Charges`
  - `Grand_Total_Base_Currency = Exchange_Rate * Grand_Total` (or `0` when exchange rate is null)
- Upstream credit impact on success:
  - `Credit_Note.Refund = sum(Refund_Note.Grand_Total where Reference_Credit_Note = current credit note)`
  - `Credit_Note.Credits_Used = sum(Apply_Credit_To_Invoice_Line.Amount_Applied for the credit note)`
  - `Credit_Note.Credits_Remaining = Credit_Note.Grand_Total - Refund - Credits_Used`
Source: `XMT___Billing_System.ds` workflows `User_Input_Trigger_Workfl3` and `Successful_form_submissio1` (`form = Refund_Note`).

#### Relationships to Other Modules
- Upstream:
  - `Credit_Note` launches refund creation through `Create_Refund_Note_From_C` and acts as mandatory reference (`Reference_Credit_Note`).
  - `Organization_Settings`, `Customer_Profile`, `Tenancy`, and `Payment_Term` provide supplier defaults, customer details, and due-date context.
- Downstream:
  - `Credit_Note` is updated on refund save (refund history, applied-credit history sync, `Credits_Remaining`, and `Credit_Note_Blueprint` stage).
  - LHDN submission action `Submit_Refund_Note_to_LHD1` sends refund-note payload and stores returned UUID/public-link metadata.

#### Status Lifecycle
`Refund_Note` does not have a dedicated blueprint lifecycle in `XMT___Billing_System.ds`; operational state is enforced through validation gates and cross-module credit-note stage updates. [Inferred]  
Source: `XMT___Billing_System.ds` record action `Create_Refund_Note_From_C`, workflows `Handle_Validation_Submiss3` and `Successful_form_submissio1`, and no `Refund_Note_Blueprint` declaration in DS blueprint block.

#### Implementation Status
`Partial` — Core refund-note numbering, validation, totals, reference checks, credit-note synchronization, and LHDN payload submission are implemented; lifecycle control is distributed across workflows without a dedicated refund-note blueprint.

---

### 5.7 Payment Received & Credit Application

#### Purpose
`Payment_Received` captures customer receipt allocation against `Invoice`, `Debit_Note`, or `Pro_Forma_Invoices`, while `Apply_Credit_To_Invoices` allocates `Credit_Note` balances to unpaid invoices through a controlled credit-application flow.

#### When and How It Is Created
- `Payment_Received` is created manually or opened prefilled via record actions:
  - `Record_Payment_Invoice` (`Invoice` -> `Payment_Received`, single-record invoice mode)
  - `Record_Payment_Deposit1` (`Pro_Forma_Invoices` -> `Payment_Received`, single-record deposit mode)
- `Payment_Received` numbering is assigned on add success using type-specific generators:
  - `thisapp.payment_received.generate_payment_received_no_invoice_and_debit_note()`
  - `thisapp.payment_received.generate_payment_received_no_deposit()`
- `Apply_Credit_To_Invoices` is opened from `Credit_Note` record action `Apply_Credits_to_Invoices`, and submits by writing `Apply_Credit_To_Invoice_Line` rows before self-cleanup.

#### Business Rules and Validations
**BR-PAY-001** When `Payment_Received` is saved, system must assign `Payment_Received_No` using generator prefix rules based on `Payment_Type` (`Invoice/Debit Note` vs `Deposit`). [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Submiss` (`form = Payment_Received`, `on add`, `on success`); functions `payment_received.generate_payment_received_no_invoice_and_debit_note`, `payment_received.generate_payment_received_no_deposit`.

**BR-PAY-002** When creating `Payment_Received`, system must prefill `Payment_Received_Line_Item` rows for selected single-record document mode (`Invoice`, `Debit Note`, `Pro Forma Invoice`) and initialize received totals. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Pre_fill_Fields1` (`form = Payment_Received`, `on add`, `on load`).

**BR-PAY-003** When `Customer_Name` is selected, system must load open receivables into `Payment_Received_Line_Item` based on `Payment_Type` and compute `Amount_Received`, `Amount_Received_MYR`, and `Total_Still_Owing`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Customer_Name2` (`form = Payment_Received`, `on user input of Customer_Name`).

**BR-PAY-004** When editing `Payment_Received_Line_Item.Allocation`, system must reject over-allocation, require a document reference (`Invoice_No`, `Debit_Note_No`, or `Pro_Forma_Invoice_No`), and recompute allocation totals in both transaction currency and MYR. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Payment_Received_L` (`form = Payment_Received`, `on user input of Payment_Received_Line_Item.Allocation`).

**BR-PAY-005** When validating `Payment_Received`, system must block submit if no allocatable line item exists for the chosen payment type. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Validate_Payment_Received` (`form = Payment_Received`, `on validate`).

**BR-PAY-006** When `Payment_Received` add succeeds, system must insert a balancing `Journal_Entry` linked to the receipt (`Payment_Received`) with debit to `Paid_To` account and credit to trade receivables account. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Submiss` (`form = Payment_Received`, `on add`, `on success`), insert into `Journal_Entry`.

**BR-PAY-007** When invoice/debit allocations are posted, system must update source document `Amount_Paid`/`Amount_Due` and transition blueprint stages (`Paid`, `Partially Paid`, `Sent`, `Overdue`) based on remaining due and due-date context. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Submiss` (`form = Payment_Received`, condition `Payment_Type == "Invoice/Debit Note"`).

**BR-PAY-008** When deposit allocations are posted, system must update `Pro_Forma_Invoices.Amount_Paid`/`Amount_Due` and transition `Pro_Forma_Invoices_Bluepr` stage (`Paid`, `Partially Paid`, `Sent`, `Overdue`) by resulting balance and due-date context. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Submiss` (`form = Payment_Received`, condition `Payment_Type == "Deposit"`).

**BR-PAY-009** When a `Payment_Received` record is deleted, system must reverse allocated amounts/stages on linked documents and delete related `Journal_Entry` records. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Deletio` (`form = Payment_Received`, `on delete`, `on success`).

**BR-PAY-010** When `Apply_Credit_To_Invoices` loads without selected credit note, system must constrain selectable credit notes to records in `Approved`/`Open` stage with positive `Credits_Remaining`, excluding notes currently used in active apply-credit forms. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Apply_Credit_To_Invoices_` (`form = Apply_Credit_To_Invoices`, `on load`).

**BR-PAY-011** When validating `Apply_Credit_To_Invoices`, system must block submission if no invoice is targeted, if any `Credits_To_Apply` exceeds invoice `Amount_Due`, or if total applied exceeds selected credit note `Credits_Remaining`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Credits_To_Apply` and `Apply_Credit_To_Invoices_1` (`form = Apply_Credit_To_Invoices`).

**BR-PAY-012** When `Apply_Credit_To_Invoices` saves, system must insert `Apply_Credit_To_Invoice_Line` rows, update invoice credit totals/amount due, recompute source `Credit_Note` balances, transition `Credit_Note_Blueprint` (`Open`/`Closed`), and delete the transient apply-credit record. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Form_Submission` (`form = Apply_Credit_To_Invoices`, `on success`).

#### Calculations
- Receipt-allocation totals (`Payment_Received`):
  - `Amount_Received = sum(Payment_Received_Line_Item.Allocation)`
  - `Amount_Received_MYR = sum(Payment_Received_Line_Item.Allocation_MYR)`
  - `Total_Still_Owing = sum(Outstanding_Balance - Allocation)`
- Line conversion:
  - `Allocation_MYR = Allocation * document Exchange_Rate` (document = `Invoice`, `Debit_Note`, or `Pro_Forma_Invoices`)
- Document impact formulas:
  - On payment add: `Amount_Paid += Allocation`, `Amount_Due -= Allocation`
  - On payment delete: `Amount_Paid -= Allocation`, `Amount_Due += Allocation`
  - On credit apply: `Invoice.Amount_Due = Invoice.Grand_Total - Invoice.Amount_Paid - Invoice.Credits_Applied_Total`
  - Credit note rollup: `Credits_Remaining = Grand_Total - Refund - Credits_Used`
Source: `XMT___Billing_System.ds` workflows `Handle_Payment_Received_L`, `Handle_Payment_Received_T`, `Handle_Successful_Submiss`, `Handle_Successful_Deletio`, and `Handle_Form_Submission`.

#### Relationships to Other Modules
- Upstream:
  - `Invoice` and `Pro_Forma_Invoices` launch `Payment_Received` via record actions (`Record_Payment_Invoice`, `Record_Payment_Deposit1`).
  - `Credit_Note` launches `Apply_Credit_To_Invoices` via `Apply_Credits_to_Invoices`.
- Downstream:
  - `Payment_Received` updates `Invoice`, `Debit_Note`, and `Pro_Forma_Invoices` balances and lifecycle stages.
  - `Payment_Received` writes/deletes system-created `Journal_Entry` records.
  - `Apply_Credit_To_Invoices` writes `Apply_Credit_To_Invoice_Line`, updates `Invoice.Credits_Applied*`, and updates `Credit_Note` balance fields and blueprint stage.

#### Status Lifecycle
`Payment_Received` and `Apply_Credit_To_Invoices` do not have dedicated blueprint definitions in `XMT___Billing_System.ds`; lifecycle effects are implemented by workflow-driven updates on related documents (`Invoice`, `Debit_Note`, `Pro_Forma_Invoices`, `Credit_Note`). [Inferred]  
Source: `XMT___Billing_System.ds` workflow blocks for `Payment_Received` and `Apply_Credit_To_Invoices`, plus absence of module-specific blueprint declarations.

#### Implementation Status
`Partial` — Receipt numbering/allocation, journal posting, reversal logic, and credit-application propagation are implemented, but orchestration is spread across multiple workflow paths and cross-module side effects.  
Latest DS delta: payment receipt/report output removed several system metadata fields (`Added_Time`, `Added_User`, `Customer_Name.Modified_Time`, `Customer_Code.Modified_User`) and relabeled report `Modified_Time` to `Payment Received Modified Time`; payment posting blocks also include explicit stage updates and opening-balance recalculation calls in updated script paths.

---

### 5.8 Journal Entry

#### Purpose
`Journal_Entry` stores accounting postings linked to billing documents (`Invoice`, `Debit_Note`, `Payment_Received`, `Pro_Forma_Invoices`) and records line-level debit/credit movements with document references and balancing totals.

#### When and How It Is Created
- System-generated insertions occur during billing/payment events:
  - `Invoice` send/approval posting flows insert `Journal_Entry`.
  - `Debit_Note` approval flow inserts `Journal_Entry`.
  - `Payment_Received` add flow inserts `Journal_Entry`.
  - `Pro_Forma_Invoices` refund action inserts `Journal_Entry`.
- Journal number generation uses `thisapp.journal_entry.generate_journal_no()` in system-created paths.
- There are no traced `type = functions` record actions directly bound to `Journal_Entry`.

#### Business Rules and Validations
**BR-JNL-001** When a system posting creates `Journal_Entry`, system must generate `Journal_Entry_No` using `thisapp.journal_entry.generate_journal_no()`. [Confirmed]  
Source: `XMT___Billing_System.ds` function `journal_entry.generate_journal_no`; insert paths in `Payment_Received`, `Invoice`, `Debit_Note`, and `Pro_Forma_Invoices` workflows/actions.

**BR-JNL-002** When `Payment_Received` is submitted, system must create a linked `Journal_Entry` with debit to `Paid_To` account and credit to trade receivables account for `Amount_Received`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Submiss` (`form = Payment_Received`, `on add`, `on success`), insert into `Journal_Entry`.

**BR-JNL-003** When `Invoice` posting path executes, system must create a three-line `Journal_Entry` (`Sub_Total`, `Total_Tax`, `Grand_Total`) linked to the invoice via `Document_No` and `Invoice`. [Confirmed]  
Source: `XMT___Billing_System.ds` invoice posting script (insert near `newJournalEntryRecord = insert into Journal_Entry` with `Invoice=getInvoice.ID`), and send-invoice action insert path.

**BR-JNL-004** When `Debit_Note` is approved in blueprint flow, system must create a three-line `Journal_Entry` linked to `Debit_Note` and `Document_No = Invoice_No`. [Confirmed]  
Source: `XMT___Billing_System.ds` `Debit_Note_Blueprint` approve script, insert near `newJournalEntryRecord = insert into Journal_Entry` with `Debit_Note=input.ID`.

**BR-JNL-005** When `Pro_Forma_Invoices` refund action runs, system must create a linked `Journal_Entry` with `Deposits=input.ID`. [Confirmed]  
Source: `XMT___Billing_System.ds` function `Refund1` (`form = Pro_Forma_Invoices`), insert into `Journal_Entry`.

**BR-JNL-006** When `Payment_Received` is deleted, system must delete related `Journal_Entry` records by `Document_No = Payment_Received_No`; for deposit reversals, system additionally deletes `Journal_Entry` rows linked by `Deposits`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Handle_Successful_Deletio` (`form = Payment_Received`, `on delete`, `on success`).

**BR-JNL-007** When `Invoice` or `Pro_Forma_Invoices` records are deleted, system must delete related `Journal_Entry` records where `Document_No` matches source `Invoice_No`. [Confirmed]  
Source: `XMT___Billing_System.ds` workflows `Handle_Deletion_Of_Invoic` (`form = Invoice`) and `Handle_Deletion_Of_Pro_F` (`form = Pro_Forma_Invoices`).

**BR-JNL-008** When `Journal_Entry` is loaded, system must disable core reference/total fields; if `Created_By_The_System` is true, line-item account/description/debit/credit and date are also read-only. [Confirmed]  
Source: `XMT___Billing_System.ds` workflow `Disable_Fields5` (`form = Journal_Entry`, `on load`).

#### Calculations
- Numbering formula:
  - `Journal_Entry_No = "JO" + zero-padded running sequence`
- System posting totals are populated explicitly on insert, including:
  - `Sub_Total_Debit`, `Sub_Total_Credit`
  - `Total_Debit`, `Total_Credit`
  - `Difference = Total_Debit - Total_Credit` (or equivalent expanded expression)
- For payment-received generated entries:
  - `Total_Debit = Amount_Received`
  - `Total_Credit = Amount_Received`
Source: `XMT___Billing_System.ds` function `journal_entry.generate_journal_no`; `Journal_Entry` insert blocks in payment/invoice/debit/refund flows.

#### Relationships to Other Modules
- Upstream creators:
  - `Invoice` posting paths create linked `Journal_Entry`.
  - `Debit_Note` blueprint approval creates linked `Journal_Entry`.
  - `Payment_Received` add flow creates linked `Journal_Entry`.
  - `Pro_Forma_Invoices` refund action creates linked `Journal_Entry`.
- Downstream dependencies:
  - `Journal_Entry` rows are deleted when source records are removed/reversed in invoice, payment, and pro-forma flows.

#### Status Lifecycle
`Journal_Entry` has no dedicated blueprint lifecycle in `XMT___Billing_System.ds`; behavior is operational and event-driven from upstream module workflows/actions. [Inferred]  
Source: `XMT___Billing_System.ds` workflow coverage for `Journal_Entry` and absence of `Journal_Entry_Blueprint` declaration.

#### Implementation Status
`Partial` — System-driven posting and cleanup paths are implemented across invoice/debit/payment/deposit flows, while `Journal_Entry` behavior is mostly consumed as a target ledger artifact rather than a standalone lifecycle module.

---

## 6. Document Conversion Matrix

| From | To | Mechanism | Evidence |
|---|---|---|---|
| `Subscription` / `Tenancy` | `Invoice` | Daily schedule creates invoices for current or previous duration | `Subscription_Schedule`, `thisapp.invoice.create_invoice_current_duration`, `thisapp.invoice.create_invoice_previous_duration` |
| `Subscription` | `Work_Order_Creation` | Work-order flow creates/opens work-order records and can trigger desk ticket creation | `Create_Work_Order` flow, `thisapp.subscription.create_ticket_for_work_order` |
| `Pro_Forma_Invoices` | `Payment_Received` | Record action opens prefilled payment form in deposit mode | Function `Record_Payment_Deposit1` (`form = Pro_Forma_Invoices`) |
| `Pro_Forma_Invoices` | `Journal_Entry` | Refund action posts deposit-related journal entry lines | Function `Refund1` (`form = Pro_Forma_Invoices`) |
| `Invoice` | `Credit_Note` | Record action converts invoice into credit note with copied header and line-item data | Function `Convert_To_Credit_Note` (`form = Invoice`) |
| `Invoice` | `Debit_Note` | Record action converts invoice into debit note with copied header and line-item data | Function `Convert_To_Debit_Note1` (`form = Invoice`) |
| `Credit_Note` | `Refund_Note` | Record action opens prefilled refund-note form linked to source credit note | Function `Create_Refund_Note_From_C` (`form = Credit_Note`) |
| `Credit_Note` | `Apply_Credit_To_Invoices` | Record action opens credit application flow that writes `Apply_Credit_To_Invoice_Line` | Function `Apply_Credits_to_Invoices` (`form = Credit_Note`) |
| `Invoice` | `Payment_Received` | Record action opens prefilled payment form for invoice settlement | Function `Record_Payment_Invoice` (`form = Invoice`) |
| `Payment_Received` | `Journal_Entry` | Payment posting writes journal entry rows; payment deletion removes linked journal entries | Workflows `Handle_Successful_Submiss`, `Handle_Successful_Deletio` (`form = Payment_Received`) |
| `Debit_Note` | `Journal_Entry` | Blueprint approval posts debit-note journal lines linked by `Document_No` and `Debit_Note` | `Debit_Note_Blueprint` approve script (insert into `Journal_Entry`) |
| `Invoice` | `Journal_Entry` | Send/approval path inserts accounting journal lines for subtotal, tax, and grand total | Function `Send_Invoice`, workflow `Notify_Credits_Available` button script |

---

## 7. Status Lifecycle Summary

| Module | Lifecycle Mechanism | Key States / Outcomes | Notes |
|---|---|---|---|
| `Subscription` / `Tenancy` | Workflow + schedule + field-driven status updates | `Subscription`: `Active`, `Inactive` (with `Terminated` present as a status value to confirm behavior); `Tenancy` operational billing fields drive invoice cadence | No dedicated blueprint traced; lifecycle is distributed. |
| `Pro_Forma_Invoices` | `Pro_Forma_Invoices_Bluepr` + payment workflows | `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Partially Paid`, `Paid`, `Overdue` | Payment and delete flows in `Payment_Received` adjust stage outcomes. |
| `Invoice` | `Invoice_Blueprint` + schedule + payment workflows | `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Partially Paid`, `Paid`, `Overdue` | Reminder and overdue schedules, plus payment/credit adjustments, influence runtime state. |
| `Credit_Note` | `Credit_Note_Blueprint` + refund/credit-application synchronization | `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Open`, `Closed` | `Open`/`Closed` driven by `Credits_Remaining` recalculation. |
| `Debit_Note` | `Debit_Note_Blueprint` + payment workflows | `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Sent`, `Partially Paid`, `Paid`, `Overdue` | Approval/send and payment events both change stage. |
| `Refund_Note` | Workflow-gated lifecycle (no dedicated blueprint) | Operational progression via validation + successful posting against `Credit_Note` | State is inferred from workflow behavior and reference constraints. |
| `Payment_Received` | Workflow-gated lifecycle (no dedicated blueprint) | Add/update/delete allocation events; receipt sent flag (`Receipt_Sent`) | Lifecycle effects are propagated to `Invoice`, `Debit_Note`, and `Pro_Forma_Invoices`. |
| `Apply_Credit_To_Invoices` | Workflow-gated transient form (no dedicated blueprint) | Selection -> validation -> posting -> cleanup (`delete from Apply_Credit_To_Invoices`) | Acts as execution wrapper for creating `Apply_Credit_To_Invoice_Line`. |
| `Journal_Entry` | Event-driven target ledger (no dedicated blueprint) | Insert/update/delete as created by upstream modules | Primarily system-created and reference-linked (`Invoice`, `Debit_Note`, `Payment_Received`, `Deposits`). |

Source: `XMT___Billing_System.ds` blueprints (`Invoice_Blueprint`, `Pro_Forma_Invoices_Bluepr`, `Credit_Note_Blueprint`, `Debit_Note_Blueprint`) and module workflows/actions documented in `§5.1`–`§5.8`.

---

## 8. Implementation Status Matrix

| Module | Status | Note |
|---|---|---|
| `Subscription` / `Tenancy` | `Partial` | Billing cadence and invoice generation remain implemented, with recent DS refactor to helper-based invoice amount calculations and tenancy-cycle parameter normalization. |
| `Pro_Forma_Invoices` | `Partial` | Core validation, totals, approval/sending, and deposit-payment flows are implemented, with workflow/navigation inconsistencies to confirm. |
| `Credit_Note` | `Partial` | Core credit lifecycle, calculations, and credit/refund interactions are implemented across workflows, blueprint transitions, and record actions. |
| `Debit_Note` | `Partial` | Core validation, totals, conversion, blueprint routing, payment-state updates, and LHDN submission are implemented across multiple execution paths. |
| `Refund_Note` | `Partial` | Core refund validation, totaling, credit-note synchronization, and LHDN submission are implemented, but lifecycle is workflow-driven without a dedicated blueprint. |
| `Payment_Received` | `Partial` | Allocation/reversal and journal linkage remain implemented, with current DS/report cleanup removing system metadata columns and relabeling receipt modified-time output. |
| `Journal_Entry` | `Partial` | Ledger posting and cleanup are implemented through upstream module flows, with limited standalone lifecycle logic on the journal form itself. |
| `Invoice` | `Partial` | End-to-end behavior exists, with current DS schedule update using `Change_status_to_Overdue_` and revised overdue selection condition alongside existing distributed workflow/blueprint logic. |

---

## 9. Open Questions

1. `Invoice` schedule filters use both `"paid"` and `"Paid"` stage values in different places. Confirm canonical paid-stage casing in `Invoice_Blueprint` and whether normalization is required. (Observed in `W1st_Remainder_Invoice_Due` vs `Final_Invoice_Reminder` filters.)
2. `Subscription` supports status value `Terminated`, but traced billing-update logic only transitions to `Inactive` on final billing completion. Confirm required behavior for `Terminated` and whether invoice generation must stop immediately on that status.
3. `Pro_Forma_Invoices` workflow `Handle_Submission_Form_an6` opens `#Report:Debit_Notes` on success. Confirm whether this is intentional or should redirect to Pro Forma report.
4. Overdue schedule condition in `Change_status_to_Overdue_` is currently expressed as `Blueprint.Current_Stage == "Approved" || Blueprint.Current_Stage == "Sent" || Blueprint.Current_Stage == "Partially Paid" && Due_Date < today`; confirm intended precedence and whether `Due_Date < today` should apply to all included stages.
