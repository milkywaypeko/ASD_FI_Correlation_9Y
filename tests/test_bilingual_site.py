"""Static bilingual UI contract. This feature must never recalculate OLS data."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_every_dashboard_has_korean_english_switch():
    pages = sorted(SITE.glob("*.html"))
    assert len(pages) >= 12
    for page in pages:
        content = page.read_text(encoding="utf-8")
        assert 'assets/js/i18n.js' in content, page.name
        assert 'lang="ko"' in content, page.name


def test_root_dashboard_matches_unified_and_has_language_switch():
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    unified = (SITE / "unified.html").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1) == unified
    assert 'assets/js/i18n.js' in root


def test_language_toggle_is_persistent_accessible_and_presentation_only():
    js = (SITE / "assets/js/i18n.js").read_text(encoding="utf-8")
    for expected in [
        "public-data-lab-language",
        "localStorage.getItem",
        "localStorage.setItem",
        "new URLSearchParams(location.search).get('lang')",
        "['ko','한국어']",
        "['en','English']",
        "aria-pressed",
        "document.documentElement.lang=code",
        "MutationObserver",
        "NodeFilter.SHOW_TEXT",
        "window.SiteLanguage",
        "data-no-translate",
        "'SCRIPT','STYLE','NOSCRIPT','TEXTAREA','PRE','CODE'",
    ]:
        assert expected in js
    # The i18n code must not edit numeric results, CSV payloads, regression
    # coefficients, observations, or source JSON.
    for forbidden in ["pearsonr(", "fetch(", "JSON.stringify(", "new Blob(", "download("]:
        assert forbidden not in js


def test_english_dictionary_covers_main_analysis_ui():
    js = (SITE / "assets/js/i18n.js").read_text(encoding="utf-8")
    for term in [
        "Final six-variable regression",
        "Simple linear regressions",
        "OLS slope β₁ p-value",
        "SciPy Pearson r",
        "Download trend CSV",
        "Regression results by year and region",
        "Data quality & methodology",
        "Select a model from the comparison table.",
    ]:
        assert term in js
