# Nieuwe onkostennota — form guide

Explored on **PurchaseForm.aspx?Type=E** via Playwright (read-only unless explicitly saving).

Machine-readable spec: [onkostennota-form.schema.json](onkostennota-form.schema.json)  
Raw crawl: [onkostenform-raw.json](onkostenform-raw.json)

## How to reach the form

1. Log in at `/login.aspx`.
2. Open **Aankoop** in the left dashboard (`#ctl00_dashboardBtns_Purchase` → `/Views/Purchase.aspx`).
3. Click **Nieuwe onkostennota** → `/Views/PurchaseForm.aspx?Type=E`.

Direct URL (after login): `https://mijn.starterslabo.be/Views/PurchaseForm.aspx?Type=E`

## Platform behaviour

- **ASP.NET WebForms** with `__VIEWSTATE` postbacks (less aggressive than verkoopfactuur).
- **Bedrag** uses **Telerik RadNumericTextBox** (European formatting: `,` decimal, `.` thousands). Use click → select-all → type → Tab; plain `fill()` may not sync `*_ClientState`.
- Hidden field `hfInvoiceType` = `E` marks this as an onkostennota (expense note), not an aankoopfactuur.
- **Leverancier** is pre-filled with your own company (expense reimbursement to yourself). The selector is disabled; supplier fields are editable but usually left as-is.
- **Bijlagen**: Telerik RadAsyncUpload — attach receipt via `fileUploaderfile0`, then **wait for `.ruUploadSuccess`** before save. Saving too early drops the attachment.

## Form layout (top → bottom)

### Expense details

| Label | Control ID suffix | Required | Notes |
|-------|-------------------|----------|-------|
| Onderwerp | `TxtBoxTitle` | Yes (validation) | Short label, e.g. "SaaS abonnement juni 2026" |
| Rekening | `SelectPurchaseAccount` | Yes | GL account code — see account list below |
| Bedrag | `TxtBoxAmount` | Yes | RadNumeric currency |
| Datum | `InputInvoiceDate` | Yes | `type=date`, receipt/invoice date |
| Factuurnummer | `InputPurchaseNr` | Recommended | Number from supplier invoice/receipt |
| Motivatie beroepskosten | `TxtBoxDescription` | Yes | Business justification for the expense |

### Leverancier (pre-filled)

| Placeholder | Control ID suffix | Notes |
|-------------|-------------------|-------|
| Naam | `InputSupplierName` | Your company name |
| Telefoon | `InputSupplierPhone` | |
| Email | `InputSupplierEmail` | |
| Adres | `InputSupplierAdres` | |
| Plaats | `InputSupplierCity` | |
| Postcode | `InputSupplierPostCode` | |
| Land | `InputCountryType` | Default BE |
| Bic code | `InputSupplierBicCode` | Optional |
| IBAN | `InputSupplierIban` | Optional |
| BTW-regime | `InputSupplierTaxRegime` | Geen / Standaard / … |
| Contactpersoon | `InputSupplierContactPerson` | |
| Email contactpersoon | `InputSupplierContactPersoonEmail` | |

### Bijlagen

| Control | Notes |
|---------|-------|
| `fileUploaderfile0` | File input for receipt attachment (PDF, image) |

### Actions

| Button | ID suffix | Effect |
|--------|-----------|--------|
| **Opslaan als concept** | `btnSaveConcept` | Saves draft — **use this by default** |
| **Verstuur** | `BtnSubmit` | Submits for coach review — only when user confirms |

Prefix for all IDs: `ctl00_ContentPlaceLabo_PurchaseForm_`

## Rekening (account) options

| Code | Description | Typical use |
|------|-------------|-------------|
| 612125 | software, website en onderhoud | SaaS, Cursor, hosting, domains |
| 612105 | telefoon, gsm, internet | Mobile, broadband |
| 612115 | abonnementen boeken tijdschriften | Subscriptions, magazines |
| 612300 | bureelbenodigdheden en drukwerk | Office supplies, printing |
| 612095 | diverse kosten en klein materiaal | Miscellaneous small purchases |
| 613265 | opleiding, seminaries en begeleidingen | Training, courses |
| 614100 | publiciteitskosten | Advertising |
| 614330 | openbaar vervoer | Public transport |
| 614345 | restaurantkosten | Restaurant (business meals) |
| 614350 | kosten van onthaal | Hospitality |
| 614317 | kilometervergoeding 0% verworpen | Mileage (electric/light freight) |
| 614324 | kilometervergoeding 60% verworpen | Mileage (60% rejected) |
| 613160 | verzekering BA en andere | Insurance |
| 613220 | lidgelden en bijdragen | Membership fees |
| 610999 | andere kostencategorie dan vermeld | Other (when nothing fits) |
| 499000 | wachtrekening vaste en variabele kosten | Holding account (ask coach) |
| 230999 | wachtrekening investeringen | Investments holding account |

Full list in [onkostennota-form.schema.json](onkostennota-form.schema.json).

## Automation script

```bash
cd data/raw/StartersLabo/skills

# Dry run — fills form, takes screenshot, does NOT save
uv run python create_draft_expense.py \
  --title "SaaS abonnement juni 2026" \
  --account 612125 \
  --amount "20,00" \
  --date 2026-06-15 \
  --invoice-nr "INV-12345" \
  --description "SaaS-abonnement voor softwareontwikkeling" \
  --attachment ~/Downloads/cursor-receipt.pdf \
  --dry-run

# Save as concept (default safe action)
uv run python create_draft_expense.py \
  --title "SaaS abonnement juni 2026" \
  --account 612125 \
  --amount "20,00" \
  --date 2026-06-15 \
  --invoice-nr "INV-12345" \
  --description "SaaS-abonnement voor softwareontwikkeling" \
  --attachment ~/Downloads/cursor-receipt.pdf
```

### Add PDF to existing expense (edit form)

```bash
uv run python attach_expense_receipt.py \
  --invoice-nr KBFQE5XU \
  --attachment ~/Downloads/receipt.pdf
```

Credentials: `STARTERSLABO_EMAIL` and `STARTERSLABO_PASSWORD` in `skills/.env`.

Debug with visible browser: `HEADED=1 uv run python create_draft_expense.py ...`
