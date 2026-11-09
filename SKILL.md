---
name: starterslabo-costs
description: >-
  Enter expense notes (onkostennota / costs) on mijn.starterslabo.be via
  Playwright automation. Use when the user mentions onkosten, onkostennota,
  kosten invoeren, expense note, Aankoop, PurchaseForm Type=E, starterslabo-costs,
  or wants to log a business expense/receipt on Starters Labo.
---

# Starters Labo — Nieuwe onkostennota (`starterslabo-costs`)

Help the user enter business expenses on [mijn.starterslabo.be](https://mijn.starterslabo.be) under **Aankoop → Nieuwe onkostennota** (`PurchaseForm.aspx?Type=E`).

Not affiliated with Starterslabo. Credentials stay in `.env` at this skill’s root — never commit or print them.

**Supplier invoice (leverancier, nog te betalen)?** Use skill **starterslabo-expenses** and `create_draft_purchase.py` instead — not this form.

## Setup (first run)

From this skill’s clone root:

```bash
uv sync
uv run playwright install chromium
cp .env.example .env   # STARTERSLABO_EMAIL, STARTERSLABO_PASSWORD
```

## Workflow

```
Progress:
- [ ] 1. Gather receipt fields + rekening
- [ ] 2. Check Aankoop list for duplicate Factuurnummer
- [ ] 3. Dry-run with --attachment
- [ ] 4. User confirms → save concept (omit --dry-run)
```

1. **Gather** from the user (ask if missing):
   - Receipt/invoice PDF or image path (**required** — always pass `--attachment` when a receipt exists)
   - **Onderwerp** — short label (e.g. "SaaS abonnement juni 2026")
   - **Bedrag** — amount incl. VAT as shown on receipt
   - **Datum** — invoice/receipt date (`YYYY-MM-DD`)
   - **Factuurnummer** — supplier order/invoice number (dedup key)
   - **Motivatie beroepskosten** — why this is a business expense
   - **Rekening** — GL account (suggest from table below; confirm with user)

2. **Check for duplicates** before creating — scan Aankoop for the same Factuurnummer or same date+amount+subject. Skip or use the attach script if it already exists without PDF. To **rewrite** an existing concept with the same `--invoice-nr`, pass `--upsert` (refuses a booked/non-concept note).

3. **Dry run first** unless the user explicitly says to save:

```bash
uv run python create_draft_expense.py \
  --title "..." \
  --account 612125 \
  --amount "49,99" \
  --date 2026-06-15 \
  --invoice-nr "INV-123" \
  --description "..." \
  --attachment /path/to/receipt.pdf \
  --dry-run
```

4. **Save as concept** only after the user confirms the dry-run screenshot/values (omit `--dry-run`).

5. **Never** pass `--send` (Verstuur) unless the user explicitly asks to submit for coach review.

## Attachments (critical)

Bijlagen use **Telerik RadAsyncUpload**. The file must finish uploading **before** save. `create_draft_expense.py` waits for `.ruUploadSuccess` and `fileUploader_ClientState`. **Always pass `--attachment`** when a receipt exists.

Verify in the Aankoop list: rows with a PDF show a download icon (`DynamicDownload.aspx`). No icon = attachment missing.

### Add PDF to an existing concept

```bash
uv run python attach_expense_receipt.py \
  --invoice-nr INV-123 \
  --attachment /path/to/receipt.pdf
```

Use `--dry-run` to upload without saving. Use `--edit-url` to skip Factuurnummer lookup.

## Safety rules

- Default action: **Opslaan als concept** (draft), not Verstuur.
- Credentials: `.env` or `STARTERSLABO_EMAIL` / `STARTERSLABO_PASSWORD` — never commit or print them.
- Debug: `HEADED=1 uv run python create_draft_expense.py ...`
- Leverancier fields are pre-filled with the user’s own company — do not change unless asked.

## Rekening picker (common accounts)

| User says… | Code | Label |
|------------|------|-------|
| software, SaaS, hosting | `612125` | software, website en onderhoud |
| telefoon, gsm, internet | `612105` | telefoon, gsm, internet |
| abonnement, tijdschrift | `612115` | abonnementen boeken tijdschriften |
| kantoor, drukwerk | `612300` | bureelbenodigdheden en drukwerk |
| opleiding, cursus | `613265` | opleiding, seminaries en begeleidingen |
| restaurant, eten | `614345` | restaurantkosten |
| openbaar vervoer, trein | `614330` | openbaar vervoer |
| kilometer, wagen | `614317` or `614324` | kilometervergoeding |
| verzekering | `613160` | verzekering BA en andere |
| lidgeld | `613220` | lidgelden en bijdragen |
| reclame | `614100` | publiciteitskosten |
| onduidelijk | `610999` | andere kostencategorie — ask user |

Full account list: [docs/onkostennota-form.schema.json](docs/onkostennota-form.schema.json)

## Motivatie template

Write a clear, business-linked justification in Dutch:

> [Product/dienst] voor [bedrijfsactiviteit]. Gebruikt voor [concrete taak].

Example: *SaaS-abonnement voor softwareontwikkeling. AI-assistentie bij code review en prototyping.*

## Form reference

| Field | CLI flag | Notes |
|-------|----------|-------|
| Onderwerp | `--title` | Short label |
| Rekening | `--account` | 6-digit code |
| Bedrag | `--amount` | Comma decimal: `49,99` |
| Datum | `--date` | `YYYY-MM-DD` |
| Factuurnummer | `--invoice-nr` | Optional but recommended |
| Motivatie | `--description` | Required textarea |
| Bijlage | `--attachment` | Receipt PDF/image |

Detailed form spec: [docs/onkostennota-form.md](docs/onkostennota-form.md)

## When the user provides a receipt

1. Read the PDF/image for amount, date, invoice number, supplier, description.
2. Map expense type → rekening code (confirm if ambiguous).
3. Check Aankoop for a duplicate Factuurnummer.
4. Propose field values in a summary table before running the script.
5. Run `--dry-run` with `--attachment`; confirm the screenshot shows upload success.
6. Save only on confirmation.

## Related scripts

| Script | Purpose |
|--------|---------|
| `create_draft_expense.py` | Fill, upload receipt, save expense note |
| `attach_expense_receipt.py` | Add PDF to existing expense by Factuurnummer |
| `explore_expense_form.py` | Re-crawl form fields (writes gitignored JSON) |
