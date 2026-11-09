"""Load Starters Labo portal credentials without printing them."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def phoenix_root(start: Path | None = None) -> Path | None:
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / "nexus" / "starterslabo" / "starterslabo.yaml").is_file():
            return parent
        if (parent / "AGENTS.md").is_file() and (parent / "nexus").is_dir():
            return parent
    return None


def env_files(start: Path | None = None) -> list[Path]:
    here = (start or Path(__file__)).resolve()
    files: list[Path] = []
    files.append(here.parent / ".env")
    files.append(here.parent.parent / ".env")
    files.append(here.parent.parent / "scripts" / ".env")
    root = phoenix_root(here)
    if root:
        files.append(root / "data" / "raw" / "StartersLabo" / "skills" / ".env")
        files.append(root / ".cursor" / "skills" / "starterslabo-export" / "scripts" / ".env")
        files.append(root / "nexus" / "starterslabo" / ".env")
    seen: set[Path] = set()
    out: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def load_portal_env(start: Path | None = None) -> None:
    for path in env_files(start):
        load_dotenv(path)
    load_dotenv()


def credentials() -> tuple[str, str]:
    load_portal_env()
    email = os.environ.get("STARTERSLABO_EMAIL")
    password = os.environ.get("STARTERSLABO_PASSWORD")
    if not email or not password:
        raise SystemExit(
            "Missing STARTERSLABO_EMAIL or STARTERSLABO_PASSWORD. "
            "Copy .env.example to .env in this skill folder, or export the vars. "
            "Never print the password."
        )
    return email, password
