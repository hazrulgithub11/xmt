---
name: zoho-creator-deluge
description: >-
  Guides editing Zoho Creator Deluge exports — custom functions, form workflows,
  record actions, schedules, blueprints, forms, and reports. Use when writing or
  modifying Zoho Creator code, when the user mentions workflows, functions,
  schedules, Deluge, Creator, or asks where automation should live.
---

# Zoho Creator Deluge — Project Guide

Read this before writing or moving Deluge in this repo.

## Repo layout

```
XMT___Billing_System.ds          # Full app export — source of truth for what exists in live Creator
application/
  Custom Functions/{ns}/{fn}   # Reusable Deluge functions (namespaced)
  forms/{Form Name}/
    {Form}.deluge                # Form field definitions (form block)
    {Report}.deluge              # Report/list definitions (list block)
    workflow/*.deluge            # Form workflows (type = form)
    workflow/actions/*.deluge    # Record actions / buttons (type = functions)
  Schedule/*                     # Scheduled workflows (type = schedule)
  blueprints/{Blueprint}/        # Blueprint JSON + transition Deluge scripts
  Pages/*.zml                    # ZML pages (not Deluge)
```

## The #1 confusion: two kinds of "functions"

Zoho Creator UI and casual speech use "function" for two different things.

### 1. Custom Functions (reusable Deluge)

**Purpose:** Shared business logic — calculations, number generation, API helpers.

**Path:** `application/Custom Functions/{namespace}/{function_name}` (no file extension)

**Format:** Plain Deluge only. Namespace in the signature:

```deluge
// application/Custom Functions/invoice/calc_line_tax
Map invoice.calc_line_tax(decimal subTotal, decimal taxPct, bool nullSafeTotal)
{
	taxAmount = subTotal * taxPct / 100;
	// ...
	return lineTax;
}
```

**Invocation:** `thisapp.{namespace}.{function_name}(args)` — e.g. `thisapp.invoice.calc_line_tax(sub, pct, true)`

**Default namespace** (`Custom Functions/Default/`): functions without a prefix in signature — e.g. `void close_form()`. Called as `thisapp.close_form()`.

**In `.ds`:** Lives under top-level `functions { Deluge { ... } }`.

### 2. Record Actions (workflow DSL, `type = functions`)

**Purpose:** Buttons and bulk actions on forms/reports — send email, approve, record payment.

**Path:** `application/forms/{Form}/workflow/actions/{Name}.deluge`

**Format:** Workflow wrapper — NOT plain Deluge:

```deluge
Send_Invoice as "Send Invoice"
{
	type =  functions
	form = Invoice
	execution type = for each record
	on start
	{
		actions (Blueprint.Current_Stage == "Sent")
		{
			on click
			(
				// Deluge script body here
			)
		}
	}
}
```

**Never** create these in `Custom Functions/`. **Never** wrap custom functions in `type = functions` blocks.

---

## Form Workflows (`type = form`)

**Purpose:** Automation tied to form lifecycle — prefill on load, react to field input, block submit, post-save side effects.

**Path:** `application/forms/{Form}/workflow/{Name}.deluge`

**Shell:**

```deluge
Workflow_Link_Name as "Display Name"
{
	type =  form
	form = Form_Link_Name
	record event = on add | on edit | on add or edit | on delete
	on load | on user input of Field | on validate | on success
	{
		actions (optional_criteria)
		{
			custom deluge script
			(
				// Deluge body
			)
		}
	}
}
```

**Trigger cheat sheet:**

| Trigger | When it runs |
|---|---|
| `on load` | Form opens (add or edit) |
| `on user input of Field` | Field value changes in the UI |
| `on validate` | Before save — use `cancel submit` to block |
| `on success` | After successful save |
| `record event = on delete` | Record deletion |

**Subform fields:** `on user input of Subform.Field_Name`

---

## Schedules (`type = schedule`)

**Purpose:** Time-based jobs — reminders, overdue status, subscription billing.

**Path:** `application/Schedule/{Name}` (extension varies in export)

**Shell:**

```deluge
Schedule_Link_Name as "Display Name"
{
	type =  schedule
	form = Form[optional_criteria]   // omit for app-wide schedules
	start = "2026-01-01 00:00:00" | after 1 weeks from Due_Date at "09:00:00"
	frequency = daily                // when recurring
	time zone = "Asia/Singapore"
	on start
	{
		actions (optional_criteria)
		{
			on load
			(
				// Deluge body — runs per matching record when form-scoped
			)
		}
	}
}
```

---

## Blueprint transitions

**Purpose:** Logic when a record moves between blueprint stages (Approve, Reject, Send, etc.).

**Path:** `application/blueprints/{Blueprint}/transitions/{Transition}/before|after|during/.../*.deluge`

**Format:** Plain Deluge only — no workflow wrapper. Example calls:

```deluge
thisapp.blueprint.changeStage("Invoice","Invoice_Blueprint","Overdue",input.ID);
thisapp.blueprint.executeTransition("Invoice","Invoice_Blueprint","Send_For_Approval",input.ID);
```

Transition metadata (from/to stage) is in sibling `transition.json` files.

---

## Forms and reports

**Form definition** — `form Form_Name { ... fields, subforms, sections ... }`

**Report/list** — `list Report_Link_Name { show all rows from Form_Name ... }`

Reports live alongside forms in `application/forms/{Form Name}/`, not a separate top-level folder.

---

## Workflow before writing

1. **Classify the request** using the decision table in `.cursor/rules/zoho-creator-structure.mdc`.
2. **Find an existing sibling** in the target folder; copy its structure.
3. **Verify in `.ds`:** grep `XMT___Billing_System.ds` for the workflow/function link name. If absent locally or in `.ds`, stop and ask the user to sync from live Creator.
4. **Edit only the Deluge body** inside `custom deluge script (...)` or transition files unless the user explicitly asked to change trigger configuration.
5. **Do not mix artifact types** — e.g. do not put `on user input` logic in a custom function, or put `Map invoice.foo()` signatures in workflow files.

---

## Common mistakes (do not do these)

| Mistake | Correct approach |
|---|---|
| Writing `type = form` workflow in `Custom Functions/` | Put in `forms/{Form}/workflow/` |
| Writing `void my_helper()` in `workflow/` | Put in `Custom Functions/{ns}/my_helper` |
| Adding button logic as a custom function | Use `workflow/actions/` with `type = functions` |
| Using `function` keyword (JavaScript/Python style) | Deluge uses `void`, `string`, `Map`, etc. for return types |
| Inventing `on submit` trigger | Use `on validate` (before save) or `on success` (after save) |
| Editing `.ds` directly for routine changes | Edit the split file under `application/`; `.ds` is the sync reference |

---

## Naming conventions in this project

- **Link names** use underscores: `Handle_Exchange_Rate`, `Send_Invoice`
- **Display names** are in quotes after `as`: `as "Handle Exchange Rate"`
- **Form link names** in code use underscores: `Invoice`, `Refund_Note`, `Pro_Forma_Invoices`
- **Folder names** may contain spaces matching Creator display names: `Refund Note`, `Pro Forma Invoices`
- Export truncates long names in filenames: `Handle_Validation_Submiss2.deluge` — preserve the existing filename when editing

---

## Additional resources

- [reference.md](reference.md) — trigger matrix and `.ds` section map
