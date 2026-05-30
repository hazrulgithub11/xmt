#!/usr/bin/env python3
"""Sync invoice, payment, and related modules from XMT___Billing_System.ds."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "sync_payment_received_workflows.py",
    "sync_invoice_workflows.py",
    "sync_custom_functions.py",
    "sync_notify_credits_workflows.py",
    "extract_blueprints.py",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    for name in SCRIPTS:
        print(f"\n=== {name} ===")
        subprocess.run([sys.executable, str(root / name)], check=True)


if __name__ == "__main__":
    main()
