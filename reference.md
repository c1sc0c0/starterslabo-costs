# Onkostennota — field reference

Portal form: `https://mijn.starterslabo.be/Views/PurchaseForm.aspx?Type=E`

Human guide: [docs/onkostennota-form.md](docs/onkostennota-form.md)  
Account options: [docs/onkostennota-form.schema.json](docs/onkostennota-form.schema.json)

Default action is **Opslaan als concept**. Do not click Verstuur unless the user asks.

| CLI | Form |
|-----|------|
| `--title` | Onderwerp |
| `--account` | Rekening (6-digit GL) |
| `--amount` | Bedrag (European comma decimal) |
| `--date` | Datum `YYYY-MM-DD` |
| `--invoice-nr` | Factuurnummer |
| `--description` | Motivatie beroepskosten |
| `--attachment` | Bijlage (wait for Telerik upload) |
| `--dry-run` | Fill + screenshot, no save |
| `--upsert` | Update existing concept with the same Factuurnummer |
| `--send` | Verstuur — only when explicitly requested |

Leverancier is pre-filled as `KO <Achternaam> <Voornaam>`. Leave it unless asked.
