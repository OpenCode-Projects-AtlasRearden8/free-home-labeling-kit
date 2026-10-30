"""Tests for the free-home-labeling-kit build.

These verify the required contract: every sheet builds a valid, unbranded,
US-Letter PDF in printables/, and the build script detects corruption.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build as build_mod  # noqa: E402

PRINTABLES = ROOT / "printables"

EXPECTED_SLUGS = sorted(build_mod.REQUIRED_SHEET_SLUGS)


@pytest.fixture(scope="module")
def built_pdfs() -> dict[str, Path]:
    """Build every sheet once for the whole module; map slug -> PDF path."""
    results = build_mod.build_all()  # rows of (slug, status, problems)
    assert all(status == "OK" and not problems for _, status, problems in results)
    return {
        slug: build_mod.PRINTABLES_DIR / f"{slug}.pdf"
        for slug, _status, _problems in results
    }


# --------------------------------------------------------------------------
# source-level checks
# --------------------------------------------------------------------------

def test_every_required_sheet_html_exists() -> None:
    for slug in EXPECTED_SLUGS:
        path = ROOT / "src" / "sheets" / f"{slug}.html"
        assert path.exists(), f"missing sheet source: {path}"


def test_sheets_link_the_shared_stylesheet() -> None:
    for slug in EXPECTED_SLUGS:
        html = (ROOT / "src" / "sheets" / f"{slug}.html").read_text(encoding="utf-8")
        assert 'href="../css/print.css"' in html, f"{slug}.html does not use the shared CSS"


def test_stylesheet_sets_us_letter_page() -> None:
    css = (ROOT / "src" / "css" / "print.css").read_text(encoding="utf-8")
    assert "size: letter" in css


# --------------------------------------------------------------------------
# build contract: every sheet -> one valid PDF
# --------------------------------------------------------------------------

def test_every_sheet_builds_a_pdf(built_pdfs) -> None:
    assert sorted(built_pdfs) == EXPECTED_SLUGS
    for slug, pdf_path in built_pdfs.items():
        assert pdf_path.exists(), f"no PDF produced for {slug}"
        assert pdf_path.suffix == ".pdf"
        head = pdf_path.read_bytes()[:5]
        assert head == b"%PDF-", f"{slug}: bad magic bytes {head!r}"


def test_every_pdf_is_valid_and_has_text(built_pdfs) -> None:
    for slug, pdf_path in built_pdfs.items():
        assert build_mod.validate_pdf(pdf_path) == [], f"{slug}: validation problems"


def test_every_pdf_is_us_letter(built_pdfs) -> None:
    for slug, pdf_path in built_pdfs.items():
        assert build_mod.check_page_sizes(pdf_path) == [], f"{slug}: wrong page size"


def test_every_pdf_page_count_is_realistic(built_pdfs) -> None:
    for slug, pdf_path in built_pdfs.items():
        n = len(PdfReader(str(pdf_path)).pages)
        assert 1 <= n <= 8, f"{slug}: unrealistic page count {n}"


def test_pdfs_are_unbranded(built_pdfs) -> None:
    for slug, pdf_path in built_pdfs.items():
        assert build_mod.check_unbranded(pdf_path) == [], f"{slug}: PDF contains branding"


# --------------------------------------------------------------------------
# build script CLI + robustness
# --------------------------------------------------------------------------

def test_single_sheet_build(tmp_path, monkeypatch) -> None:
    out_dir = tmp_path / "printables"
    monkeypatch.setattr(build_mod, "PRINTABLES_DIR", out_dir)
    results = build_mod.build_all("cable-charger-tags")
    assert len(results) == 1
    slug, status, problems = results[0]
    assert (slug, status, problems) == ("cable-charger-tags", "OK", [])


def test_unknown_sheet_slug_fails(monkeypatch) -> None:
    monkeypatch.setattr(build_mod, "PRINTABLES_DIR", ROOT / "printables")
    with pytest.raises(SystemExit):
        build_mod.build_all("no-such-sheet")


def test_validate_pdf_detects_corruption(tmp_path) -> None:
    bad = tmp_path / "broken.pdf"
    bad.write_bytes(b"not a pdf at all")
    problems = build_mod.validate_pdf(bad)
    assert problems, "corrupt file should produce validation problems"

    good_path = PRINTABLES / "breaker-box-directory.pdf"
    if good_path.exists():
        assert build_mod.validate_pdf(good_path) == []


def test_validate_pdf_detects_missing_file(tmp_path) -> None:
    problems = build_mod.validate_pdf(tmp_path / "ghost.pdf")
    assert problems == ["file does not exist"]


def test_cli_builds_everything_and_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "build.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for slug in EXPECTED_SLUGS:
        assert slug in proc.stdout
    assert (ROOT / "printables" / f"{EXPECTED_SLUGS[0]}.pdf").exists()


def test_single_pdf_text_extraction_sanity() -> None:
    """One representative PDF must contain its own title text."""
    pdf = PRINTABLES / "where-is-it-index.pdf"
    if not pdf.exists():
        pytest.skip("printables not built yet")
    text = PdfReader(str(pdf)).pages[0].extract_text() or ""
    assert "Where Is It" in text


def test_no_secrets_in_source_tree() -> None:
    """Guardrail: source files must not embed credentials or personal data."""
    forbidden_tokens = ["api_key", "API_KEY", "password", "BEGIN PRIVATE KEY", "sk-"]
    scan_self = Path(__file__)  # holds the forbidden tokens themselves
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.parent.name == ".git":
            continue
        if path.suffix in {".pdf", ".png", ".jpg", ".pyc"} or "__pycache__" in path.parts:
            continue
        if path == scan_self:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden_tokens:
            assert token not in content, f"{path.relative_to(ROOT)} contains {token!r}"
