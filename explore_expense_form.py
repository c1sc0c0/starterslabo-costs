#!/usr/bin/env python3
"""One-off explorer for PurchaseForm.aspx?Type=E — writes docs/onkostenform-raw.json."""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from starterslabo.session import load_credentials, login, new_page

EXPENSE_FORM_URL = "https://mijn.starterslabo.be/Views/PurchaseForm.aspx?Type=E"
OUTPUT = Path(__file__).parent / "docs" / "onkostenform-raw.json"

EXTRACT = """() => {
  function fieldMeta(el) {
    const tag = el.tagName.toLowerCase();
    const label = (() => {
      if (el.id) {
        const l = document.querySelector('label[for="' + el.id + '"]');
        if (l) return l.innerText.trim();
      }
      const parent = el.closest('.form-group, .row, td, th, .input-group');
      if (parent) {
        const lab = parent.querySelector('label');
        if (lab && lab !== el) return lab.innerText.trim();
      }
      const prev = el.previousElementSibling;
      if (prev && prev.tagName === 'LABEL') return prev.innerText.trim();
      return el.placeholder || '';
    })();
    const opts = tag === 'select'
      ? [...el.options].map(o => ({
          value: o.value,
          text: o.text.trim(),
          selected: o.selected,
          disabled: o.disabled,
        }))
      : undefined;
    return {
      tag,
      type: el.type || null,
      id: el.id || null,
      name: el.name || null,
      label,
      placeholder: el.placeholder || null,
      value: tag === 'select' ? el.value : (el.value ?? null),
      required: el.required || el.getAttribute('aria-required') === 'true',
      disabled: el.disabled,
      maxLength: el.maxLength > 0 ? el.maxLength : null,
      options: opts,
      classes: el.className || null,
      visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length),
    };
  }

  const fields = [];
  document.querySelectorAll('input, select, textarea, button').forEach((el) => {
    const tag = el.tagName.toLowerCase();
    if (el.type === 'hidden') {
      fields.push({ ...fieldMeta(el), hidden: true });
      return;
    }
    if (tag === 'button') {
      fields.push({
        tag: 'button',
        type: el.type,
        id: el.id || null,
        label: el.innerText.trim(),
        visible: !!(el.offsetWidth || el.offsetHeight),
      });
      return;
    }
    fields.push(fieldMeta(el));
  });

  return {
    url: location.href,
    title: document.title,
    fields,
  };
}"""


def main() -> None:
    email, password = load_credentials()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser, page = new_page(p)
        try:
            login(page, email, password)
            page.goto(EXPENSE_FORM_URL, wait_until="networkidle", timeout=60_000)
            page.screenshot(
                path=OUTPUT.parent / "onkosten-form-full.png", full_page=True
            )
            data = page.evaluate(EXTRACT)
            OUTPUT.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"Wrote {OUTPUT} ({len(data['fields'])} fields)")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
