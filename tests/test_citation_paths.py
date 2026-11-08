"""The user-supplied KOSIS citation register links every source CSV to the source page."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]


def test_all_30_kosis_sources_are_mapped_to_real_repository_files():
    sources = (ROOT / "KOSIS_SOURCES.md").read_text(encoding="utf-8")
    section = sources.split("## 사용자 제공 KOSIS 인용문", 1)[1].split("\n---\n", 1)[0]
    paths = re.findall(r"\x60(Statistics/[^\x60]+\.csv)\x60", section)
    ids = re.findall(r"https://kosis\.kr/statHtml/statHtml\.do\?orgId=\d+&tblId=[\w_]+&conn_path=I2", section)
    assert len(paths) == 30 and len(set(paths)) == 30
    assert len(ids) == 30 and len(set(ids)) == 30
    assert all((ROOT / path).is_file() for path in paths)


def test_all_sources_are_visible_on_methodology_page_with_file_paths():
    page = html.unescape((ROOT / "site/quality.html").read_text(encoding="utf-8"))
    sources = (ROOT / "KOSIS_SOURCES.md").read_text(encoding="utf-8")
    register = sources.split("## 사용자 제공 KOSIS 인용문", 1)[1].split("\n---\n", 1)[0]
    paths = re.findall(r"\x60(Statistics/[^\x60]+\.csv)\x60", register)
    assert 'id="kosis-citations"' in page
    for path in paths:
        assert path in page
    assert page.count('https://kosis.kr/statHtml/statHtml.do?orgId=') >= 30
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "KOSIS 출처 30건" in readme
