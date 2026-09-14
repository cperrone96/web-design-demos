#!/usr/bin/env python3
"""Run dependency-free integrity and accessibility smoke checks for the demos."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
SITES = {
    "green-horizons": 8,
    "climate-pro": 16,
    "shield-pest": 4,
}
FORBIDDEN = (
    re.compile(r"@gmail\.com\b", re.I),
    re.compile(r"@yahoo\.com\b", re.I),
    re.compile(r"@outlook\.com\b", re.I),
    re.compile(r"BEGIN (?:RSA|OPENSSH|EC|PGP) PRIVATE KEY"),
    re.compile(r"(?:^|[\s=:/])(?:sk|pk)_(?:live|test)_[A-Za-z0-9]+"),
    re.compile(r"(?:/Users/|/home/)[^\s\"']+"),
)


class PageParser(HTMLParser):
    """Capture only the attributes needed for static quality checks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.title = ""
        self.in_title = False
        self.viewport = False
        self.description = False
        self.images: list[tuple[str, str]] = []
        self.references: list[tuple[str, str]] = []
        self.fragments: list[str] = []
        self.ids: set[str] = set()
        self.label_for: set[str] = set()
        self.status_ids: set[str] = set()
        self.forms: list[dict[str, str]] = []
        self.controls: list[tuple[str, str, int]] = []
        self.current_form = -1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if values.get("id"):
            self.ids.add(values["id"])
        if values.get("role") == "status" or values.get("aria-live"):
            if values.get("id"):
                self.status_ids.add(values["id"])
        if tag == "html":
            self.html_lang = values.get("lang", "").strip()
        elif tag == "form":
            self.forms.append(
                {
                    "action": values.get("action", ""),
                    "demo": values.get("data-demo-form", "").lower(),
                    "status": values.get("data-demo-status", ""),
                }
            )
            self.current_form = len(self.forms) - 1
        elif tag == "label":
            if values.get("for"):
                self.label_for.add(values["for"])
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = values.get("name", "").lower()
            if name == "viewport":
                self.viewport = bool(values.get("content"))
            elif name == "description":
                self.description = bool(values.get("content", "").strip())
        elif tag == "img":
            self.images.append((values.get("src", ""), values.get("alt", "")))
            if values.get("src"):
                self.references.append(("img", values["src"]))
        elif tag in {"script", "link", "video", "audio", "source"}:
            for attr in ("src", "href", "poster"):
                if values.get(attr):
                    self.references.append((tag, values[attr]))
        elif tag == "a" and values.get("href"):
            self.references.append(("a", values["href"]))
            if values["href"].startswith("#") and values["href"] != "#":
                self.fragments.append(values["href"][1:].split("?")[0])
        elif tag in {"input", "select", "textarea"}:
            input_type = values.get("type", "").lower()
            if input_type not in {"hidden", "submit", "button", "reset", "image"}:
                self.controls.append((values.get("id", ""), input_type or tag, self.current_form))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "form":
            self.current_form = -1

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def css_references(path: Path) -> list[str]:
    """Return url() values from a stylesheet, excluding inline data URLs."""
    text = path.read_text(encoding="utf-8")
    return [
        value.strip().strip("\"'")
        for value in re.findall(r"url\(\s*([^)]*?)\s*\)", text, flags=re.I)
        if not value.strip().lower().startswith("data:")
    ]


def local_target(page: Path, value: str) -> Path | None:
    """Return a local path for a relative reference, or None for external refs."""
    value = unquote(value.strip())
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return None
    target = (page.parent / parsed.path).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return page.parent / "__outside_repository__"
    if parsed.path.endswith("/"):
        target = target / "index.html"
    return target


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN:
        match = pattern.search(text)
        if match:
            errors.append(f"{path.relative_to(ROOT)} contains a forbidden secret/path pattern near {match.group(0)!r}")

    parser = PageParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:  # pragma: no cover - defensive parser guard
        errors.append(f"{path.relative_to(ROOT)} is not parseable HTML: {exc}")
        return errors

    rel = path.relative_to(ROOT)
    if not parser.html_lang:
        errors.append(f"{rel} is missing <html lang=...>")
    if not parser.title.strip():
        errors.append(f"{rel} is missing a non-empty <title>")
    if not parser.viewport:
        errors.append(f"{rel} is missing a viewport meta tag")
    if not parser.description:
        errors.append(f"{rel} is missing a non-empty meta description")
    for fragment in parser.fragments:
        if fragment not in parser.ids:
            errors.append(f"{rel} has a broken in-page anchor: #{fragment}")
    for src, alt in parser.images:
        if not alt.strip():
            errors.append(f"{rel} has an image without alt text: {src}")
    for form in parser.forms:
        if form["action"]:
            errors.append(f"{rel} demo form must omit action so it cannot transmit data")
        if form["demo"] != "true":
            errors.append(f"{rel} form is missing data-demo-form=\"true\"")
        if not form["status"] or form["status"] not in parser.status_ids:
            errors.append(f"{rel} demo form is missing a status target with role=status/aria-live")
    for control_id, control_type, form_index in parser.controls:
        if form_index < 0:
            continue
        if not control_id:
            errors.append(f"{rel} {control_type} control is missing an id for label association")
        elif control_id not in parser.label_for:
            errors.append(f"{rel} control #{control_id} is missing an associated <label for=...>")
    for kind, reference in parser.references:
        target = local_target(path, reference)
        if target is not None and not target.is_file():
            errors.append(f"{rel} has a broken local {kind} reference: {reference}")
    return errors


def check_stylesheet(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN:
        match = pattern.search(text)
        if match:
            errors.append(f"{path.relative_to(ROOT)} contains a forbidden secret/path pattern near {match.group(0)!r}")
    for reference in css_references(path):
        target = local_target(path, reference)
        if target is not None and not target.is_file():
            errors.append(f"{path.relative_to(ROOT)} has a broken local asset reference: {reference}")
    return errors


def main() -> int:
    errors: list[str] = []
    for site, expected_pages in SITES.items():
        pages = sorted((ROOT / site).glob("*.html"))
        if len(pages) != expected_pages:
            errors.append(f"{site} expected {expected_pages} HTML pages, found {len(pages)}")
        if not (ROOT / site / "index.html").is_file():
            errors.append(f"{site} is missing index.html")
        for page in pages:
            errors.extend(check_file(page))
        for stylesheet in sorted((ROOT / site).glob("*.css")):
            errors.extend(check_stylesheet(stylesheet))

    for unwanted in (".ipynb_checkpoints", "__pycache__", ".pytest_cache"):
        if any(path.name == unwanted for path in ROOT.rglob(unwanted)):
            errors.append(f"generated cache directory should not be committed: {unwanted}")

    if errors:
        print("Static-site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    for site, expected_pages in SITES.items():
        print(f"PASS {site}: {expected_pages} HTML pages; metadata, assets, links, and privacy scan clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
