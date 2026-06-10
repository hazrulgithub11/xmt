#!/usr/bin/env bash
# Phase 4 static verification for Journal Entry inline subform refactor.
# Run from repo root: bash scripts/verify_phase4_journal_entry.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

section() { echo ""; echo "== $1 =="; }

section "1. Inline subform on Journal_Entry form"
if grep -q 'type = grid' "application/forms/Journal Entry/Journal_Entry.deluge" \
   && grep -q 'values  = Journal_Entry_Line_Item.ID' "application/forms/Journal Entry/Journal_Entry.deluge"; then
  fail "Journal_Entry still uses linked grid (values = Journal_Entry_Line_Item.ID)"
elif grep -q 'Journal_Entry_Line_Item' "application/forms/Journal Entry/Journal_Entry.deluge" \
     && grep -q 'Account' "application/forms/Journal Entry/Journal_Entry.deluge" \
     && grep -q 'Description' "application/forms/Journal Entry/Journal_Entry.deluge" \
     && grep -q 'Debit' "application/forms/Journal Entry/Journal_Entry.deluge" \
     && grep -q 'Credit' "application/forms/Journal Entry/Journal_Entry.deluge"; then
  pass "Journal_Entry has inline subform with Account, Description, Debit, Credit"
else
  fail "Journal_Entry inline subform fields not found"
fi

section "2. Standalone form/report removed from repo"
if [ -d "application/forms/Journal Entry Line Item" ]; then
  fail "Standalone Journal Entry Line Item folder still exists"
else
  pass "Standalone form folder deleted"
fi

section "3. No obsolete standalone-form references"
if rg -q 'delete from Journal_Entry_Line_Item|Journal_Entry_Line_Item\[' application/ 2>/dev/null; then
  fail "Found delete/query against standalone Journal_Entry_Line_Item form"
else
  pass "No standalone Journal_Entry_Line_Item delete/query"
fi

if rg -q 'related field = Journal_Entry_Line_Item(\.|$)' application/ 2>/dev/null; then
  fail "Report still uses related field = Journal_Entry_Line_Item (linked lookup)"
else
  pass "No linked-form report lookup for Journal_Entry_Line_Item"
fi

if rg -q 'row[0-9]+\.(Invoice|Payment_Received|Deposits|Debit_Note|Credit_Note|Journal_Entry)' application/ 2>/dev/null; then
  fail "Creation workflow still assigns per-row source links"
else
  pass "No per-row source link assignments on line items"
fi

section "4. Five journal-entry creation paths"
CREATION_FILES=(
  "application/forms/Payment Received/workflow/Handle_Successful_Submiss.deluge:Payment_Received"
  "application/forms/Invoice/workflow/actions/Send_Invoice.deluge:Invoice"
  "application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge:Invoice"
  "application/forms/Pro Forma Invoices/workflow/actions/Refund.deluge:Deposits"
  "application/blueprints/Debit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge:Debit_Note"
)
for entry in "${CREATION_FILES[@]}"; do
  file="${entry%%:*}"
  header_link="${entry##*:}"
  if [ ! -f "$file" ]; then
    fail "Missing creation file: $file"
    continue
  fi
  if ! grep -q 'insert into Journal_Entry' "$file"; then
    fail "$file — no insert into Journal_Entry"
    continue
  fi
  if ! grep -q 'Journal_Entry.Journal_Entry_Line_Item()' "$file"; then
    fail "$file — missing inline subform row constructor"
    continue
  fi
  if ! grep -q "${header_link}=" "$file"; then
    fail "$file — missing header link $header_link"
    continue
  fi
  if ! grep -q 'Journal_Entry_Line_Item=journalEntryLineItem' "$file"; then
    fail "$file — missing Journal_Entry_Line_Item collection insert"
    continue
  fi
  pass "$file — creation path OK (header: $header_link)"
done

section "5. Deletion paths (parent Journal_Entry only)"
DELETION_FILES=(
  "application/forms/Invoice/workflow/Handle_Deletion_Of_Invoic.deluge"
  "application/forms/Payment Received/workflow/Handle_Successful_Deletio.deluge"
  "application/forms/Pro Forma Invoices/workflow/Handle_Deletion_Of_Record1.deluge"
)
for file in "${DELETION_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    fail "Missing deletion file: $file"
    continue
  fi
  if ! grep -q 'delete from Journal_Entry' "$file"; then
    fail "$file — no delete from Journal_Entry"
    continue
  fi
  pass "$file — deletes Journal_Entry parent"
done

section "6. Chart of Account deletion validation"
COA_FILE="application/forms/Chart Of Account/workflow/Validate_Record_Deletion7.deluge"
if grep -q 'Journal_Entry\[Journal_Entry_Line_Item.Account == input.ID\]' "$COA_FILE"; then
  pass "COA validation uses parent-form subform criteria"
else
  fail "COA validation missing Journal_Entry[Journal_Entry_Line_Item.Account == input.ID]"
fi

section "7. Reports show inline subform columns"
REPORT_FILES=(
  "application/forms/Journal Entry/All_Journal_Entries.deluge"
  "application/forms/Payment Received/Payment_Received_Report.deluge"
  "application/forms/Payment Received/Deposit_Payment_Received_Report.deluge"
)
for file in "${REPORT_FILES[@]}"; do
  if grep -q 'Journal_Entry_Line_Item.Account' "$file" \
     && grep -q 'Journal_Entry_Line_Item.Description' "$file" \
     && grep -q 'Journal_Entry_Line_Item.Debit' "$file" \
     && grep -q 'Journal_Entry_Line_Item.Credit' "$file"; then
    pass "$file — inline subform columns present"
  else
    fail "$file — missing inline subform columns"
  fi
done

if grep -q 'related field = Journal_Entry.Payment_Received' \
   "application/forms/Payment Received/Payment_Received_Report.deluge" \
   "application/forms/Payment Received/Deposit_Payment_Received_Report.deluge"; then
  pass "Payment Received reports use Journal_Entry.Payment_Received header link"
else
  fail "Payment Received reports missing Journal_Entry.Payment_Received related field"
fi

section "Summary"
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
  echo "STATIC VERIFICATION: FAILED"
  exit 1
fi
echo "STATIC VERIFICATION: PASSED"
echo ""
echo "Manual sandbox smoke tests still required in Zoho Creator (see Phase 4 checklist in plan)."
