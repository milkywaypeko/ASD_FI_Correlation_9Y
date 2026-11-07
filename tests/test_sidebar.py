"""Sidebar navigation regression checks for all static GitHub Pages entrypoints."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = ("index.html", "unified.html", "multivariate.html",
         "fiscal-birth.html", "results.html", "quality.html")
SIMPLE = ("age65", "under15", "medical", "premium", "fertility", "fiscal")
LEGACY = ("multivariate.html", "fiscal-birth.html", "results.html")


def test_one_shared_sidebar_on_all_pages():
    for name in PAGES:
        page = (SITE / name).read_text(encoding="utf-8")
        nav = re.search(r'<nav class="navigation"[^>]*>(.*?)</nav>', page, re.S)
        assert nav is not None, name
        assert page.count('assets/js/sidebar.js') == 1, name
        assert nav.group(1).count('<a ') == 2, name
        assert 'age-medical-multi.html' not in nav.group(1), name
        assert 'household-premium-ols.html' not in nav.group(1), name
        assert 'birth-ols.html' not in nav.group(1), name


def test_root_homepage_contains_same_navigation_script():
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    homepage = (SITE / "unified.html").read_text(encoding="utf-8")
    explorer = (SITE / "index.html").read_text(encoding="utf-8")
    assert '<base href="./site/">' in root
    assert root.replace('<base href="./site/">', '', 1) == homepage
    assert 'assets/js/dashboard.js' in explorer
    assert 'assets/js/unified.js' in root


def test_unique_models_and_legacy_analysis_entries():
    script = (SITE / "assets" / "js" / "sidebar.js").read_text(encoding="utf-8")
    for key in SIMPLE:
        assert script.count(f"['{key}',") == 1, key
    for page in LEGACY:
        assert script.count(f"['{page}',") == 1, page
    assert "a.dataset.navKey = key" in script
    assert "aria-current" in script
    assert "window.location.pathname.endsWith('/')" in script
    assert "window.SidebarNav" in script
    assert "has-active" in script


def test_grouped_menu_does_not_alter_analysis():
    script = (SITE / "assets" / "js" / "sidebar.js").read_text(encoding="utf-8")
    assert "fit_extended_ols" not in script
    assert "fetch(" not in script
    unified = (SITE / "assets" / "js" / "unified.js").read_text(encoding="utf-8")
    assert "window.SidebarNav?.updateActive()" in unified
    assert "history.replaceState(null,'',url)" in unified
