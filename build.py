#!/usr/bin/env python3
"""Build the free-home-labeling-kit printables.

Renders every HTML sheet in src/sheets/ to an unbranded PDF in printables/
using WeasyPrint, then validates each PDF with pypdf (magic bytes, page
count, US Letter page size, and extractable text).

Usage:
    python3 build.py                              # build all sheets + validate
    python3 build.py --sheet cable-charger-tags   # build a single sheet
    python3 build.py --clean                      # delete printables/*.pdf first
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
SHEETS_DIR = ROOT / "src" / "sheets"
PRINTABLES_DIR = ROOT / "printables"

LETTER_W_IN, LETTER_H_IN = 8.5, 11.0
PT_PER_IN = 72.0
SIZE_TOLERANCE_IN = 0.15  # renderer slack for letter pages

REQUIRED_SHEET_SLUGS = (
    "cable-charger-tags",
    "breaker-box-directory",
    "water-shutoff-valve-labels",
    "kit-contents-labels",
    "seasonal-storage-labels",
    "remote-cheat-cards",
    "where-is-it-index",
)

# Strings that must never appear inside the printable PDFs (they stay unbranded).
FORBIDDEN_TEXT_IN_PDFS = ("asdale", "dylan", "copyright", "(c) 2026")


def discover_sheets(slug: str | None = None) -> list[Path]:
    if slug:
        return [SHEETS_DIR / f"{slug}.html"]
    return sorted(SHEETS_DIR.glob("*.html"))


def render_sheet(html_path: Path, out_path: Path) -> None:
    from weasyprint import HTML

    HTML(filename=str(html_path)).write_pdf(str(out_path))


def validate_pdf(path: Path) -> list[str]:
    """Return a list of problems for one PDF; an empty list means valid."""
    issues: list[str] = []

    if not path.exists():
        return [f"file does not exist"]

    size = path.stat().st_size
    if size < 1000:
        issues.append(f"suspiciously small file ({size} bytes)")

    head = path.read_bytes()[:8]
    if not head.startswith(b"%PDF-"):
        issues.append(f"missing %PDF- magic bytes (got {head[:5]!r})")
        return issues

    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # corrupt PDF / bad xref / unsupported structure
        issues.append(f"pypdf could not open the file ({exc})")
        return issues

    n_pages = len(reader.pages)
    if n_pages < 1:
        issues.append("PDF has zero pages")
        return issues

    for i in range(n_pages):
        try:
            if not (reader.pages[i].extract_text() or "").strip():
                issues.append(f"page {i + 1}: no extractable text")
        except Exception as exc:
            issues.append(f"page {i + 1}: text extraction failed ({exc})")

    return issues


def check_page_sizes(path: Path) -> list[str]:
    """Every page must be US Letter (portrait) within tolerance."""
    out: list[str] = []
    for i, page in enumerate(PdfReader(str(path)).pages):
        box = page.mediabox
        w_in, h_in = float(box.width) / PT_PER_IN, float(box.height) / PT_PER_IN
        if (
            abs(w_in - LETTER_W_IN) > SIZE_TOLERANCE_IN
            or abs(h_in - LETTER_H_IN) > SIZE_TOLERANCE_IN
        ):
            out.append(
                f"page {i + 1}: size {w_in:.2f}x{h_in:.2f}in is not "
                f"US Letter ({LETTER_W_IN}x{LETTER_H_IN}in)"
            )
    return out


def check_unbranded(path: Path) -> list[str]:
    """The printable PDFs must not carry any brand/authoring text."""
    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    text = text.lower()
    return [f"forbidden token {token!r} found in PDF text" for token in FORBIDDEN_TEXT_IN_PDFS if token in text]


def check_sheets() -> None:
    found = {p.stem for p in discover_sheets()}
    expected = set(REQUIRED_SHEET_SLUGS)
    if found != expected:
        missing = expected - found
        extra = found - expected
        extras = f", unexpected: {sorted(extra)}" if extra else ""
        raise SystemExit(
            f"Sheet set mismatch under {SHEETS_DIR}: "
            f"missing {sorted(missing)}{extras}"
        )


def build_all(slug: str | None = None, clean: bool = False) -> list[tuple[str, str, list[str]]]:
    """Render sheets to PDFs; returns (slug, status, problems) tuples."""
    if slug:
        sheets = discover_sheets(slug)
        if not sheets or not sheets[0].exists():
            raise SystemExit(f"Unknown sheet slug: {slug}.html (see src/sheets/)")
    else:
        check_sheets()
        sheets = discover_sheets()

    PRINTABLES_DIR.mkdir(exist_ok=True)
    if clean:
        for old in PRINTABLES_DIR.glob("*.pdf"):
            old.unlink()

    results: list[tuple[str, str, list[str]]] = []
    for html_path in sheets:
        pdf_path = PRINTABLES_DIR / f"{html_path.stem}.pdf"
        render_sheet(html_path, pdf_path)
        problems = validate_pdf(pdf_path)
        problems += check_page_sizes(pdf_path)
        problems += check_unbranded(pdf_path)
        status = "OK" if not problems else "FAIL"
        results.append((html_path.stem, status, problems))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build free-home-labeling-kit printables (HTML -> PDF)."
    )
    parser.add_argument("--sheet", help="build a single sheet by slug (e.g. cable-charger-tags)")
    parser.add_argument("--clean", action="store_true", help="remove old PDFs before building")
    args = parser.parse_args(argv)

    try:
        results = build_all(args.sheet, clean=args.clean)
    except SystemExit as exc:
        parser.error(str(exc))
        return 2  # pragma: no cover - parser.error exits first

    widest = max(len(name) for name, _, _ in results)
    failures = 0
    for name, status, problems in sorted(results):
        print(f"{name:<{widest}}  {status}")
        for problem in problems:
            print(f"  - {problem}")
            failures += 1

    if failures:
        print(f"\nBuild finished with {failures} problem(s).", file=sys.stderr)
        return 1
    print(f"\nAll sheets built and validated -> {PRINTABLES_DIR.name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
