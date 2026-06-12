# XMT Module Map (DS Source-of-Truth)

Use `XMT___Billing_System.ds` as the primary reference for BRD authoring.

- Do not trust `application/forms/**` as authoritative when it diverges.
- Use local split files only for convenience after confirming behavior in `XMT___Billing_System.ds`.

---

## Core Anchors in `XMT___Billing_System.ds`

| Concern | DS anchor |
|---|---|
| Form definitions | `form <Form_Name>` near lines `182..9836` |
| Workflow definitions | `workflow { form { ... type = form; form = <Form_Name> ... } }` starting near line `17171` |
| Schedules | `schedule { ... type = schedule ... }` starting near line `32813` |
| Blueprints | `blueprint { ... type = Blueprint ... }` starting near line `33044` |
| Record actions | `type = functions; form = <Form_Name>` around `36490..37353` |
| Functions used in calculations | `thisapp.<namespace>.*` calls across function/workflow/schedule blocks |

---

## 5.1 Subscription & Tenancy

### Tenancy
| Type | DS reference |
|---|---|
| Form declaration | `form Tenancy` (line ~`9836`) |
| Workflows | search `form = Tenancy` within workflow block (starts ~`17171`) |
| Record actions | search `type =  functions` + `form = Tenancy` |
| Schedule linkage | `Subscription_Schedule` (starts ~`32980`), plus calls to `thisapp.tenancy.*` |
| Namespace | `thisapp.tenancy.*` |

### Subscription
| Type | DS reference |
|---|---|
| Form declaration | `form Subscription` (line ~`9018`) |
| Line item form | `form Subscription_Line_Item` |
| Workflows | search `form = Subscription` within workflow block |
| Record actions | search `type =  functions` + `form = Subscription` |
| Schedule linkage | `Subscription_Schedule` (starts ~`32980`) |
| Namespace | `thisapp.subscription.*` |

---

## 5.2 Pro Forma Invoice

| Type | DS reference |
|---|---|
| Form declaration | `form Pro_Forma_Invoices` (line ~`6507`) |
| Workflows | search `form = Pro_Forma_Invoices` within workflow block |
| Record actions | search `type =  functions` + `form = Pro_Forma_Invoices` |
| Blueprint | `Pro_Forma_Invoices_Bluepr as "Pro Forma Invoices Blueprint"` (starts ~`34215`) |
| Namespace | search `thisapp` usage directly in Pro Forma workflow/action blocks |

---

## 5.3 Invoice

| Type | DS reference |
|---|---|
| Form declaration | `form Invoice` (line ~`4052`) |
| Workflows | search `form = Invoice` within workflow block |
| Record actions | search `type =  functions` + `form = Invoice` |
| Blueprint | `Invoice_Blueprint as "Invoice Blueprint"` (starts ~`33238`) |
| Schedules | `W1st_Remainder_Invoice_Due` (~`32815`), `Final_Invoice_Reminder` (~`32889`), `Change_Status_To_Overdue` (~`32963`) |
| Namespace | `thisapp.invoice.*` |

---

## 5.4 Credit Note

| Type | DS reference |
|---|---|
| Form declaration | `form Credit_Note` (line ~`705`) |
| Workflows | search `form = Credit_Note` within workflow block |
| Record actions | search `type =  functions` + `form = Credit_Note` |
| Blueprint | `Credit_Note_Blueprint as "Credit Note Blueprint"` (starts ~`33046`) |
| Namespace | search for `thisapp` usage in Credit Note workflow/action blocks |

---

## 5.5 Debit Note

| Type | DS reference |
|---|---|
| Form declaration | `form Debit_Note` (line ~`2608`) |
| Workflows | search `form = Debit_Note` within workflow block |
| Record actions | search `type =  functions` + `form = Debit_Note` |
| Blueprint | `Debit_Note_Blueprint as "Debit Note Blueprint"` (starts ~`34756`) |
| Namespace | search for `thisapp` usage in Debit Note workflow/action blocks |

---

## 5.6 Refund Note

| Type | DS reference |
|---|---|
| Form declaration | `form Refund_Note` (line ~`7763`) |
| Workflows | search `form = Refund_Note` within workflow block |
| Record actions | search `type =  functions` + `form = Refund_Note` |
| Blueprint | no dedicated refund blueprint found in DS blueprint block |
| Namespace | search for `thisapp` usage in Refund Note workflow/action blocks |

---

## 5.7 Payment Received & Credit Application

### Payment Received
| Type | DS reference |
|---|---|
| Form declaration | `form Payment_Received` (line ~`5990`) |
| Line item form | `form Payment_Received_Line_Item` (line ~`6302`) |
| Workflows | search `form = Payment_Received` within workflow block |
| Record actions | search `type =  functions` + `form = Payment_Received` |
| Namespace | search for `thisapp` usage in Payment Received workflow/action blocks |

### Apply Credit To Invoices
| Type | DS reference |
|---|---|
| Form declaration | `form Apply_Credit_To_Invoices` (line ~`182`) |
| Line item form | `form Apply_Credit_To_Invoice_Line` (line ~`107`) |
| Workflows | search `form = Apply_Credit_To_Invoices` within workflow block |
| Record actions | search `type =  functions` + `form = Apply_Credit_To_Invoices` |

---

## 5.8 Journal Entry

| Type | DS reference |
|---|---|
| Form declaration | `form Journal_Entry` (line ~`5413`) |
| Workflows | search `form = Journal_Entry` within workflow block |
| Record actions | search `type =  functions` + `form = Journal_Entry` |
| Namespace | search `thisapp.journal` and `thisapp.journal_entry` |

---

## Supporting / Master Data (DS identifiers)

`Customer_Profile`, `Tax`, `Payment_Term`, `Chart_Of_Account`, `Organization_Settings`, `Business_Segment`, `Business_Unit`, `Email_Templates`, `Work_Order_Creation`, `Circuit_ID`.

Use DS search pattern:

`form (Customer_Profile|Tax|Payment_Term|Chart_Of_Account|Organization_Settings|Business_Segment|Business_Unit|Email_Templates|Work_Order_Creation|Circuit_ID)`

---

## Schedule Inventory in DS

The DS `schedule` block currently includes:

1. `W1st_Remainder_Invoice_Due` (~`32815`)
2. `Final_Invoice_Reminder` (~`32889`)
3. `Change_Status_To_Overdue` (~`32963`)
4. `Subscription_Schedule` (~`32980`)

If local `application/Schedule/*.deluge` contains extra files, treat DS as authoritative.
