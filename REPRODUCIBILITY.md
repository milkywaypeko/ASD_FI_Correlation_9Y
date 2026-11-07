# 통계 재현성 점검: 보존할 원본과 삭제 가능한 산출물

이 문서는 `python build.py`의 **출력 파일을 삭제한 뒤 재생성**할 때의 기준입니다.
파일을 삭제하기 전에는 연구 시점의 `main` 커밋 SHA와 원본 CSV 체크섬을 남기고,
필요한 경우 산출물을 별도로 보관하세요. 삭제 자체는 자동으로 수행하지 않습니다.

## 절대 삭제하면 안 되는 자료·코드

| 경로 | 이유 |
| --- | --- |
| `Statistics/` 전체 (모든 하위 CSV 및 `Statistics/README.md`) | KOSIS에서 받은 원본 통계, 2014년 포함. 재현성의 출발점이며 재생성이 불가능합니다. |
| `build.py`, `expanded_analysis.py`, `insurance_premiums.py`, `unified_analysis.py` | 원본 읽기·지역 결합·정의·statsmodels OLS 계산 코드 |
| `requirements.txt` | Python 의존성 버전 범위 |
| `site/` 아래 `*.html`, `assets/js/`, `assets/css/` | 대시보드 템플릿·분석 단위·그래프·검색 및 데이터 로더 코드 |
| `tests/` | 수식·기간·원문·UI·재현성 회귀 테스트 |
| `AGENTS.md`, `.agents/`, `.github/` | 저장소 작업 지침·검증 및 Pages 배포 자동화 |
| `README.md`, `REPRODUCIBILITY.md`, `KOSIS_SOURCES.md`, `.gitignore`(존재 시) | 출처와 재현 절차의 감사기록 |
| `.git/` | 소스 버전·정확한 기준 커밋·원격 저장소 이력 |

**주의:** `Statistics/`의 2014년 건강보험 원본은 연구 결과에서 해당 연도를
제외하더라도 **원본 보존 대상으로 유지**합니다. 원자료 결측도 0으로 바꾸지 않습니다.

## 재생성 가능하므로 삭제해도 되는 산출물

| 경로 | 의미 / 삭제 조건 |
| --- | --- |
| `__pycache__/` 및 하위 Python `__pycache__/`, `*.pyc` | Python 바이트코드 캐시. 실행 시 다시 생성됩니다. |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | 테스트·검사 캐시. 있으면 삭제할 수 있습니다. |
| `site/data/` **전체** | 사전 계산된 JSON 및 gzip 인덱스·상세 통계. `python build.py`로 다시 생성되지만, 삭제 직후 사이트의 그래프·통계표는 동작하지 않습니다. |
| `site/raw/` **전체** | 분석 시 만들어진 `statsmodels` 원문 텍스트. 빌드로 다시 생성됩니다. |
| 프로젝트 루트 `index.html` | `site/unified.html`을 기반으로 빌드가 다시 생성하는 GitHub Pages 진입 파일. 삭제 중에는 루트 사이트를 열 수 없습니다. |
| 프로젝트 루트 `.nojekyll` | `build.py`가 다시 생성. GitHub Pages에 필요한 설정 파일이므로 배포 전에 복원되어야 합니다. |

**`site/` 폴더 전체는 삭제하지 마세요.** 같은 폴더에 재생성 가능한
`data/`·`raw/`와 보존할 HTML·CSS·JS가 섞여 있습니다.
`Statistics/`와 `site/`의 의미가 완전히 다릅니다.

## 정해진 재현 절차

아래 명령은 연구 코드가 설치된 프로젝트 루트에서 실행합니다.

```bash
# 1) 먼저 출처/원본 CSV를 보관하고 Git 커밋을 기록
git rev-parse HEAD
git status --short

# 2) 분석에 사용할 패키지와 테스트 러너 설치
python -m pip install -r requirements.txt
python -m pip install pytest

# 3) 삭제는 산출물만 대상으로 실행 (데이터 CSV는 대상에 없음)
python - <<'PY'
from pathlib import Path
import shutil
for name in ("site/data", "site/raw", "__pycache__", ".pytest_cache"):
    path = Path(name)
    if path.is_dir():
        shutil.rmtree(path)
PY

# 4) 한 번의 명령으로 전체 정적 웹사이트 재생성
python build.py

# 5) 파일과 회귀 통계 검증
python -m pytest tests -q

# 6) 정적 로컬 서버에서 연구 화면 확인
python -m http.server 8000
```

`site/data/unified_manifest.json`과
`site/data/unified_index_{six,age65,under15,medical,premium,fertility,fiscal}.json.gz`
및 `site/data/unified_detail/` 아래 gzip은 모두 생성 산출물입니다.
인덱스 통계량·OLS 원문·실제 관측치·예측값·잔차가 일치하는지 CI에서 확인합니다.

Python 계산은 원본 CSV와 사전 설치된 라이브러리만 사용하고 네트워크는
요청하지 않습니다. Chart.js는 외부 CDN을 사용하므로 **완전한 브라우저
오프라인 실행에는 별도로 라이브러리 제공이 필요합니다**.
GitHub Pages 배포 전 `index.html`, `.nojekyll` 및 생성된
`site/data/`가 준비되어 있어야 합니다.

## 결과 비교의 주의사항

동일한 입력 CSV·동일한 분석 코드·같은 NumPy/statsmodels 환경을 사용해야
계수/잔차/표본을 신뢰성 있게 비교할 수 있습니다. NumPy·statsmodels 버전 범위
내에서 패치 버전 차이는 출력 진단 형식이나 마지막 소수점에 영향을 줄 수 있으므로
`python -m pip freeze`로 실제 설치 버전을 보존하는 것이 좋습니다.
gzip 압축은 통계 값을 반올림하거나 바꾸지 않습니다.

KOSIS 출처 인용 규칙과 현재 검증된 표 링크는
[`KOSIS_SOURCES.md`](KOSIS_SOURCES.md)에 기록합니다.
