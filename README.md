# starterslabo-costs

Unofficial [Cursor](https://cursor.com) / [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill plus Playwright scripts to enter **Nieuwe onkostennota** on [mijn.starterslabo.be](https://mijn.starterslabo.be) (`PurchaseForm.aspx?Type=E`).

For supplier invoices (aankoopfactuur SL), use [starterslabo-expenses](https://github.com/c1sc0c0/starterslabo-expenses).

Not affiliated with Starterslabo.

## Install

Clone this repo **as the skill folder** (`SKILL.md` at the root):

```bash
git clone https://github.com/c1sc0c0/starterslabo-costs.git .cursor/skills/starterslabo-costs
git clone https://github.com/c1sc0c0/starterslabo-costs.git ~/.cursor/skills/starterslabo-costs
git clone https://github.com/c1sc0c0/starterslabo-costs.git .claude/skills/starterslabo-costs
git clone https://github.com/c1sc0c0/starterslabo-costs.git ~/.claude/skills/starterslabo-costs
```

Then:

```bash
cd .cursor/skills/starterslabo-costs   # or your clone path
uv sync
uv run playwright install chromium
cp .env.example .env
# Edit .env — never commit it
```

Restart the agent chat so the skill is discovered.

**Claude.ai:** zip this repo so `SKILL.md` is at the zip root and upload as a custom skill. You still run the Python scripts locally with `uv`.

## Usage

Dry run (fill form, no save):

```bash
uv run python create_draft_expense.py \
  --title "SaaS abonnement Q2" \
  --account 612125 \
  --amount "49,99" \
  --date 2026-06-15 \
  --invoice-nr "INV-2026-001" \
  --description "Software abonnement voor productontwikkeling." \
  --attachment ~/Downloads/receipt.pdf \
  --dry-run
```

Save as concept after confirming output: same command without `--dry-run`.

Visible browser: `HEADED=1 uv run python create_draft_expense.py ...`

## Security

- **No credentials in git.** Only `.env.example` is tracked.
- Put secrets in `.env` or export `STARTERSLABO_EMAIL` / `STARTERSLABO_PASSWORD`.
- Do not paste passwords into agent chat.
- `explore_expense_form.py` output under `docs/` is gitignored.

## Related

Index of all skills: [starterslabo-skills](https://github.com/c1sc0c0/starterslabo-skills).

- [starterslabo-expenses](https://github.com/c1sc0c0/starterslabo-expenses) — aankoopfactuur SL
- [starterslabo-km](https://github.com/c1sc0c0/starterslabo-km) — kilometervergoeding Excel
- [starterslabo-faq](https://github.com/c1sc0c0/starterslabo-faq) — portal FAQ crawl

## License

MIT — see [LICENSE](LICENSE). Starterslabo’s portal and templates remain their property.
