#!/usr/bin/env python3
"""
Create a DRAFT expense note (Opslaan als concept) on mijn.starterslabo.be.

Navigation: Aankoop → Nieuwe onkostennota → PurchaseForm.aspx?Type=E

Safety:
- Only clicks "Opslaan als concept" (btnSaveConcept), never "Verstuur" (BtnSubmit),
  unless --send is passed explicitly.
- Use --dry-run to fill the form and report values WITHOUT saving anything.
- Attachments use Telerik RadAsyncUpload: must wait for ruUploadSuccess before save.
"""

import argparse
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from starterslabo.purchase import (
    EXPENSE_FORM_URL,
    SEL,
    fill_radnumeric,
    find_expense_edit_url,
    save_draft,
    upload_attachment,
)
from starterslabo.session import load_credentials, login, new_page


def read_filled(page: Page) -> dict[str, str]:
    return {
        "title": page.input_value(SEL["title"]),
        "account": page.locator(SEL["account"]).evaluate(
            "el => el.options[el.selectedIndex]?.text ?? ''"
        ),
        "amount": page.input_value(SEL["amount"]),
        "date": page.input_value(SEL["date"]),
        "invoice_nr": page.input_value(SEL["invoice_nr"]),
        "description": page.input_value(SEL["description"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Onderwerp (short label)")
    parser.add_argument(
        "--account",
        required=True,
        help="Rekening code, e.g. 612125 for software/website",
    )
    parser.add_argument("--amount", required=True, help="Bedrag, e.g. 49,99")
    parser.add_argument("--date", required=True, help="Datum (YYYY-MM-DD)")
    parser.add_argument(
        "--invoice-nr",
        default="",
        help="Factuurnummer from receipt/invoice",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Motivatie beroepskosten (business justification)",
    )
    parser.add_argument(
        "--attachment",
        default="",
        help="Path to receipt PDF/image to upload as Bijlage",
    )
    parser.add_argument(
        "--upsert",
        action="store_true",
        help="Update the existing onkostennota with this --invoice-nr instead of creating another",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fill the form but do NOT save anything",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Click Verstuur (final submit) instead of saving a draft. Avoid.",
    )
    args = parser.parse_args()

    if args.attachment:
        attachment = Path(args.attachment).expanduser().resolve()
        if not attachment.is_file():
            print(f"Attachment not found: {attachment}", file=sys.stderr)
            return 1
    else:
        attachment = None

    email, password = load_credentials()

    with sync_playwright() as p:
        browser, page = new_page(p)
        try:
            login(page, email, password)
            form_url = EXPENSE_FORM_URL
            if args.upsert:
                if not args.invoice_nr:
                    print("--upsert requires --invoice-nr", file=sys.stderr)
                    return 1
                found = find_expense_edit_url(page, args.invoice_nr)
                if found:
                    form_url = found
                    print(f"Upsert: updating existing expense {found}")
                else:
                    print("Upsert: no matching expense, creating new concept")
            page.goto(form_url, wait_until="networkidle", timeout=60_000)
            save_btn = page.locator(SEL["save_draft"])
            is_concept = save_btn.count() > 0 and save_btn.is_enabled()
            if not is_concept:
                if args.send:
                    print("Already booked (not a concept). Nothing to close.")
                    return 0
                print(
                    "Existing onkostennota is not a concept anymore; "
                    "will not overwrite a booked note.",
                    file=sys.stderr,
                )
                return 2

            page.fill(SEL["title"], args.title)
            page.select_option(SEL["account"], args.account)
            fill_radnumeric(page, SEL["amount"], args.amount)
            page.fill(SEL["date"], args.date)
            if args.invoice_nr:
                page.fill(SEL["invoice_nr"], args.invoice_nr)
            page.fill(SEL["description"], args.description)

            if attachment:
                upload_attachment(page, attachment)

            filled = read_filled(page)
            print("Filled expense note:")
            print(f"  Onderwerp   : {filled['title']!r}")
            print(f"  Rekening    : {filled['account']}")
            print(f"  Bedrag      : {filled['amount']!r}")
            print(f"  Datum       : {filled['date']}")
            print(f"  Factuurnr   : {filled['invoice_nr']!r}")
            print(
                f"  Motivatie   : {filled['description'][:80]!r}"
                f"{'...' if len(filled['description']) > 80 else ''}"
            )
            if attachment:
                print(f"  Bijlage     : {attachment.name} (upload complete)")

            page.screenshot(path="draft-expense-filled.png", full_page=True)

            if args.dry_run:
                print("Dry run: nothing saved. Screenshot: draft-expense-filled.png")
                return 0

            if args.send:
                page.click(SEL["send"])
                page.wait_for_load_state("networkidle", timeout=60_000)
                action = "Verstuur (SENT)"
                blocked = ""
                summary = page.locator(SEL["validation_summary"])
                if summary.count() and summary.is_visible():
                    blocked = summary.inner_text().strip()
            else:
                action = "Opslaan als concept (DRAFT)"
                blocked = save_draft(page)

            page.screenshot(path="draft-expense-result.png", full_page=True)

            if blocked:
                print(f"\nValidation blocked the save:\n{blocked}", file=sys.stderr)
                print("Screenshot: draft-expense-result.png", file=sys.stderr)
                return 1

            print(f"\n{action} OK")
            print(f"  Final URL: {page.url}")
            print("  Screenshot: draft-expense-result.png")
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
