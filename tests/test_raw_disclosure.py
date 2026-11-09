"""Raw result summaries stay expanded; long observation tables stay collapsed."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "site/unified.html").read_text(encoding="utf-8")


def _details_tag(id_):
    found = re.search(r'<details\b[^>]*\bid="' + re.escape(id_) + r'"[^>]*>', HTML)
    assert found is not None, id_
    return found.group(0)


def _details_body(id_):
    return HTML.split(_details_tag(id_), 1)[1].split("</details>", 1)[0]


def test_statistical_raw_results_start_expanded():
    for id_, content_id in (("u-ols-raw-details", "u-raw"),
                            ("u-scipy-raw-details", "u-scipy-raw")):
        assert re.search(r"\bopen(?:\s|>)", _details_tag(id_))
        assert f'id="{content_id}"' in _details_body(id_)


def test_observation_raw_tables_start_collapsed():
    for id_, table_id, count_id in (
        ("u-observation-details", "u-observation-body", "u-observation-count"),
        ("u-scipy-observation-details", "u-scipy-observation-body", "u-scipy-observation-count"),
    ):
        assert not re.search(r"\bopen(?:\s|>)", _details_tag(id_))
        assert f'id="{table_id}"' in _details_body(id_)
        assert f'id="{count_id}"' in _details_body(id_)


def test_disclosure_resets_on_each_model_selection_and_export_remains():
    js = (ROOT / "site/assets/js/unified.js").read_text(encoding="utf-8")
    assert "function resetRawDetails()" in js
    assert "resetRawDetails();" in js
    assert "'u-observation-details', 'u-scipy-observation-details'" in js
    assert "'u-ols-raw-details', 'u-scipy-raw-details'" in js
    assert "u-observation-export" in js and "u-scipy-export" in js
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1) == HTML
