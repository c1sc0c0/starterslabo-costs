"""Purchase form helpers — onkostennota (Type=E) and aankoopfactuur SL (Type=P)."""

from pathlib import Path

from playwright.sync_api import Page

P = "ctl00_ContentPlaceLabo_PurchaseForm_"

EXPENSE_FORM_URL = "https://mijn.starterslabo.be/Views/PurchaseForm.aspx?Type=E"
PURCHASE_FORM_URL = "https://mijn.starterslabo.be/Views/PurchaseForm.aspx"

SEL = {
    "title": f"#{P}TxtBoxTitle",
    "account": f"#{P}SelectPurchaseAccount",
    "amount": f"#{P}TxtBoxAmount",
    "date": f"#{P}InputInvoiceDate",
    "invoice_nr": f"#{P}InputPurchaseNr",
    "description": f"#{P}TxtBoxDescription",
    "to_be_paid": f"#{P}CheckBoxToBePaid",
    "supplier": f"#{P}InputSupplierSelector",
    "supplier_name": f"#{P}InputSupplierName",
    "supplier_phone": f"#{P}InputSupplierPhone",
    "supplier_email": f"#{P}InputSupplierEmail",
    "supplier_address": f"#{P}InputSupplierAdres",
    "supplier_city": f"#{P}InputSupplierCity",
    "supplier_postal": f"#{P}InputSupplierPostCode",
    "supplier_country": f"#{P}InputCountryType",
    "supplier_bic": f"#{P}InputSupplierBicCode",
    "supplier_iban": f"#{P}InputSupplierIban",
    "supplier_vat": f"#{P}InputSupplierTax",
    "supplier_tax_regime": f"#{P}InputSupplierTaxRegime",
    "supplier_contact": f"#{P}InputSupplierContactPerson",
    "supplier_contact_email": f"#{P}InputSupplierContactPersoonEmail",
    "attachment": f"#{P}fileUploaderfile0",
    "save_draft": f"#{P}btnSaveConcept",
    "send": f"#{P}BtnSubmit",
    "validation_summary": "[id*=ValidationSummary]",
}


def fill_radnumeric(page: Page, selector: str, value: str) -> None:
    """Fill a Telerik RadNumericTextBox; blur triggers a postback, so wait for it."""
    el = page.locator(selector)
    el.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Delete")
    el.type(value)
    page.keyboard.press("Tab")
    page.wait_for_load_state("networkidle", timeout=30_000)


def upload_attachment(page: Page, path: Path) -> None:
    """Upload a file via Telerik RadAsyncUpload and wait until the server has it."""
    filename = path.name
    page.set_input_files(SEL["attachment"], str(path))
    page.locator(".ruUploadSuccess").filter(has_text=filename).wait_for(
        state="visible", timeout=60_000
    )
    page.wait_for_function(
        """(name) => {
            const el = document.querySelector('[id*="fileUploader_ClientState"]');
            if (!el || !el.value) return false;
            return el.value.includes('uploadedFiles') && el.value.includes(name);
        }""",
        arg=filename,
        timeout=60_000,
    )


def open_purchase_list(page: Page) -> None:
    page.locator("#ctl00_dashboardBtns_Purchase").click()
    page.wait_for_url("**/Views/Purchase.aspx", timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=30_000)


def open_purchase_invoice_form(page: Page) -> None:
    """Aankoop → Nieuwe aankoopfactuur SL."""
    open_purchase_list(page)
    page.locator('a[href="/Views/PurchaseForm.aspx"]').first.click()
    page.wait_for_url("**/Views/PurchaseForm.aspx", timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=30_000)


def fill_supplier(
    page: Page,
    *,
    supplier_id: str = "",
    name: str = "",
    vat: str = "",
    tax_regime: str = "Standaard",
    phone: str = "",
    email: str = "",
    address: str = "",
    city: str = "",
    postal: str = "",
    country: str = "BE",
    iban: str = "",
    bic: str = "",
    contact: str = "",
    contact_email: str = "",
) -> None:
    """Select leverancier and fill supplier block (postback when selector changes)."""
    page.select_option(SEL["supplier"], supplier_id)
    page.wait_for_load_state("networkidle", timeout=30_000)

    def fill_if(selector: str, value: str) -> None:
        if value:
            page.fill(selector, value)

    fill_if(SEL["supplier_name"], name)
    fill_if(SEL["supplier_vat"], vat)
    if tax_regime:
        page.select_option(SEL["supplier_tax_regime"], tax_regime)
    fill_if(SEL["supplier_phone"], phone)
    fill_if(SEL["supplier_email"], email)
    fill_if(SEL["supplier_address"], address)
    fill_if(SEL["supplier_city"], city)
    fill_if(SEL["supplier_postal"], postal)
    if country:
        page.select_option(SEL["supplier_country"], country)
    fill_if(SEL["supplier_iban"], iban)
    fill_if(SEL["supplier_bic"], bic)
    fill_if(SEL["supplier_contact"], contact)
    fill_if(SEL["supplier_contact_email"], contact_email)


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
        "supplier": page.input_value(SEL["supplier_name"]),
        "supplier_vat": page.input_value(SEL["supplier_vat"]),
    }


def fetch_purchase_rows(page: Page) -> list[dict[str, str | bool | None]]:
    """Return rows from the Aankoop list."""
    return page.evaluate(
        """() => {
            return [...document.querySelectorAll('table tbody tr')].map(tr => {
                const tds = [...tr.querySelectorAll('td')].map(td => td.innerText.trim());
                if (tds.length < 5) return null;
                const edit = tr.querySelector('a[href*="PurchaseForm.aspx?ID="]');
                const att = tr.querySelector('a[href*="DynamicDownload"]');
                return {
                    type: tds[0] || '',
                    date: tds[2] || '',
                    supplier: tds[3] || '',
                    subject: tds[4] || '',
                    amount: tds[5] || '',
                    account: tds[6] || '',
                    editHref: edit ? edit.href : null,
                    hasAttachment: !!att,
                };
            }).filter(Boolean);
        }"""
    )


def find_purchase_edit_url(page: Page, invoice_nr: str) -> str | None:
    """Find edit URL by factuurnummer (prefer matching list rows, then concepts)."""
    open_purchase_list(page)
    needle = invoice_nr.strip().upper()
    month_hint = ""
    compact = needle.replace("-", "")
    if "SHOPIFY-FEE-" in compact:
        yyyymm = compact.split("SHOPIFY-FEE-")[-1][:6]
        if len(yyyymm) == 6 and yyyymm.isdigit():
            month_hint = f"{yyyymm[:4]}-{yyyymm[4:]}"

    hits: list[str] = []
    for row in fetch_purchase_rows(page):
        edit_href = row.get("editHref")
        if not edit_href:
            continue
        blob = " ".join(
            str(row.get(k) or "") for k in ("type", "subject", "supplier", "date")
        ).upper()
        href_s = str(edit_href)
        if needle and needle in blob:
            hits.append(href_s)
        elif month_hint and month_hint in blob and "SHOPIFY" in blob:
            hits.append(href_s)
        elif month_hint and month_hint in blob and "FEE" in blob:
            hits.append(href_s)
    for href in hits:
        page.goto(href, wait_until="networkidle", timeout=60_000)
        nr = page.input_value(SEL["invoice_nr"])
        if nr.strip().upper() == invoice_nr.strip().upper():
            return href
        title = ""
        try:
            title = page.input_value(SEL["title"])
        except Exception:  # noqa: BLE001
            title = ""
        if (
            month_hint
            and month_hint in title
            and "shopify" in title.lower()
            and "fee" in title.lower()
        ):
            return href
    return None


# Backwards-compatible aliases
fetch_expense_rows = fetch_purchase_rows
find_expense_edit_url = find_purchase_edit_url


def save_draft(page: Page) -> str:
    """Click Opslaan als concept; return validation summary text if blocked."""
    page.click(SEL["save_draft"])
    page.wait_for_load_state("networkidle", timeout=60_000)
    summary = page.locator(SEL["validation_summary"])
    if summary.count() and summary.is_visible():
        return summary.inner_text().strip()
    return ""
