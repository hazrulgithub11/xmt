# Zoho Creator — Reference

## `.ds` file section map

`XMT___Billing_System.ds` is the monolithic export. Split files under `application/` mirror sections inside it.

| `.ds` section | Local path |
|---|---|
| `forms { form X { ... workflows ... } }` | `application/forms/{Form}/` |
| `functions { Deluge { ... } }` | `application/Custom Functions/` |
| `functions { ActionName { type = functions ... } }` | `application/forms/{Form}/workflow/actions/` |
| `schedules { ... }` | `application/Schedule/` |
| Blueprint transition scripts | `application/blueprints/` |

Grep `.ds` by link name (e.g. `Handle_Exchange_Rate`) to confirm a workflow exists before editing the split file.

## Form workflow trigger matrix

| `record event` | Valid triggers |
|---|---|
| `on add` | `on load`, `on user input`, `on validate`, `on success` |
| `on edit` | `on load`, `on user input`, `on validate`, `on success` |
| `on add or edit` | All of the above |
| `on delete` | `on validate` (and delete-specific actions) |

## Record action execution types

Seen in `workflow/actions/`:

- `execution type = for each record` — bulk action from report selection
- `on click` — the actual handler inside `on start > actions`

Criteria in `actions (Field == "value")` gate when the button is available.

## Custom function namespaces in this app

| Namespace folder | Example call |
|---|---|
| `Default/` | `thisapp.close_form()` |
| `invoice/` | `thisapp.invoice.calc_line_tax(...)` |
| `tenancy/` | `thisapp.tenancy.generate_tenancy_no(...)` |
| `subscription/` | `thisapp.subscription.createTicket(...)` |
| `credit_note/` | `thisapp.credit_note.generate_credit_note_no()` |

Namespace in folder name maps to `thisapp.{folder}` — function file name maps to the method name after the dot in the signature.

## Schedule types in this app

1. **Form-scoped** — `form = Invoice[criteria]`; `on load` runs per matching record when triggered
2. **App-scoped** — no `form` line; queries forms inside the Deluge body (see `Subscription_Schedule`)

## Blueprint folder structure

```
blueprints/{Blueprint_Name}/
  blueprint.json
  transitions/{Transition_Name}/
    transition.json
    before/phase_config.ds
    after/unconditional/script_01.deluge
    after/if_{criteria}/update_*.deluge
```

Scripts under `before/`, `after/`, `during/` are plain Deluge. `phase_config.ds` holds phase configuration — do not treat as workflow.

## Sync workflow (developer ↔ live Creator)

1. Developer exports or pulls from Zoho Creator → updates `XMT___Billing_System.ds` and split files
2. Before AI edits: confirm target exists in both local split file and `.ds`
3. AI edits split file under `application/`
4. Developer imports/pastes changes back into Creator UI

AI should not assume it can deploy to Creator — it edits local export files only.
