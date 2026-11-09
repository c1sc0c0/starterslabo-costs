"""Browser session helpers for mijn.starterslabo.be."""

import os
import sys

from playwright.sync_api import Browser, Page, Playwright

from starterslabo.env import credentials as _credentials

LOGIN_URL = "https://mijn.starterslabo.be/login.aspx"


def load_credentials() -> tuple[str, str]:
    try:
        return _credentials()
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        raise


def is_headed() -> bool:
    return os.environ.get("HEADED", "").lower() in ("1", "true", "yes")


def new_page(playwright: Playwright) -> tuple[Browser, Page]:
    browser = playwright.chromium.launch(headless=not is_headed())
    return browser, browser.new_page()


def login(page: Page, email: str, password: str) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    page.fill("#InputUsername", email)
    page.fill("#InputPassword", password)
    page.click("#BtnSubmit")
    page.wait_for_url(lambda url: "login.aspx" not in url.lower(), timeout=30_000)
    if "login.aspx" in page.url.lower():
        raise RuntimeError(f"Login failed; still on {page.url}")
