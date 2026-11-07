# 장애인 등록률 통합 회귀분석 대시보드

**연구 기간 2014–2022 · 건강보험 관련 회귀 2015–2022 · Python statsmodels OLS · GitHub Pages 정적 사이트**

[**대시보드 바로가기**](https://milkywaypeko.github.io/ASD_FI_Correlation_9Y/) · [원본 데이터 설명](Statistics/README.md) · [데이터 품질·연구 방법](site/quality.html)

지역별 재정자립도, 인구구조, 합계출산율, 1인당 진료비, 가구당 건강보험료와 **선택한 장애유형의 등록률(%)** 사이의 통계적 연관성을 탐색하는 연구용 사이트입니다. 계산은 Python에서 사전 실행하며 브라우저에서는 생성된 정적 데이터만 읽습니다. **OLS는 인과관계를 입증하지 않습니다.**

## 홈페이지와 분석 화면

| 주소 | 내용 |
| --- | --- |
| [프로젝트 최상위 `index.html`](index.html) | **최종 6변수 다중회귀**를 기본값으로 여는 통합 대시보드 |
| [`site/unified.html?model=six`](site/unified.html?model=six) | 동일한 통합 회귀 화면, 최종 6변수 모형 직접 열기 |
| [`site/index.html`](site/index.html) | 기존 재정자립도 × 장애유형별 등록률 **데이터 탐색** 화면 (보존) |
| `site/unified.html?model=age65` | 65세 이상 인구비율 단순회귀 |
| `site/unified.html?model=under15` | 0–14세 인구비율 단순회귀 |
| `site/unified.html?model=medical` | 1인당 진료비 단순회귀 |
| `site/unified.html?model=premium` | 가구당 건강보험료 단순회귀 |
| `site/unified.html?model=fertility` | 합계출산율 단순회귀 |
| `site/unified.html?model=fiscal` | 재정자립도 단순회귀 |
| [`site/multivariate.html`](site/multivariate.html) | 기존 재정자립도·출산율 **2변수 다중회귀** (최종 6변수 모형과 별개) |
| [`site/fiscal-birth.html`](site/fiscal-birth.html) | 기존 재정자립도 → 출산율 회귀 |
| [`site/results.html`](site/results.html) | 기존 분석 결과표 |
| [`site/quality.html`](site/quality.html) | 데이터 품질 및 연구 방법 |

사이드바는 공통 `site/assets/js/sidebar.js`를 사용합니다. `개별 단순회귀`와 `기타 기존 분석`을 펼쳐 선택할 수 있습니다. 과거 주소(`age-medical-multi.html`, `age65-ols.html`, `under15-ols.html`, `medical-ols.html`, `household-premium-ols.html`, `birth-ols.html`)는 관련 통합 탭으로 이동합니다. **옛 5변수 선택기를 최종 화면에 남겨 두지 않습니다.**

## 분석 기간을 정한 이유

- **2014년 시작:** 재정자립도 세입과목 개편이 이루어진 시점이므로 연구 시작 연도로 정했습니다.
- **2022년 종료:** 여러 지자체의 장애인 등록통계가 2022년까지 확보되는 자료 가용성을 반영했습니다.
- **건강보험 포함 모형(진료비·보험료):** 2014년 자료는 **모든 관련 회귀에서 배제**합니다. 연도 선택, 2015–2022년 통합 회귀, 추이, 비교표, 관측치 CSV에도 동일한 제한을 적용합니다.
- **그 외 개별 단순회귀:** 재정자립도·출산율·인구구조 모형은 2014–2022년을 사용합니다. **2014년 원본 CSV는 삭제하지 않습니다.**

## 최종 6변수 회귀모형

**종속변수(Y):** 선택한 장애유형 등록률(%).

```text
Y = β₀ + β₁·X₁ + β₂·X₂ + β₃·X₃ + β₄·X₄ + β₅·X₅ + β₆·X₆ + ε
```

| 변수 | 계산식 / 의미 | 회귀 단위 |
| --- | --- | --- |
| Y 장애유형별 등록률 | 해당 유형 등록인원 ÷ 해당 연도·지역 주민등록인구 × 100 | % |
| X₁ 재정자립도 | 개편 전/후 선택. 원본 0–100%이면 내부에서 ÷ 100 | 0–1 |
| X₂ 65세 이상 비율 | 65세 이상 주민등록연앙인구 ÷ 전체 주민등록연앙인구 × 100 | % |
| X₃ 0–14세 비율 | 0–14세 주민등록연앙인구 ÷ 전체 주민등록연앙인구 × 100 | % |
| X₄ 합계출산율 | 지역별 공식 합계출산율 | 명/여성 |
| X₅ 1인당 진료비 | 연간 지역 총진료비(천원) ÷ 주민등록연앙인구 ÷ 10 | **만원/인/년** |
| X₆ 가구당 건강보험료 | 연간 지역 총보험료(천원) ÷ 주민등록세대수 ÷ 10 | **만원/세대/년** |

모든 X를 사용하는 최종 다중회귀는 **2015–2022년**에 한정합니다. 재정자립도는 개편 전·후 중 하나만 사용하고, 다른 변수의 정의는 바꾸지 않습니다.

**분모를 혼동하지 마세요.** 진료비는 해당 지역의 연간 총진료비를 연앙인구로 나눈 환산치로, 실제 개인 본인부담액이나 모든 비급여를 포함한 의료비가 아닙니다. 건강보험료는 **절대 1인당 금액이 아닙니다.** 지역 총보험료를 주민등록세대수로 나눈 **세대당 연간 환산액**이며 개별 가구에 실제 고지된 금액의 단순평균이라고 단정하지 않습니다.

### 장애유형 및 결측

선택 가능한 17종: **전체, 지체, 뇌병변, 시각, 청각, 언어, 청각·언어, 지적, 자폐성, 정신, 신장, 심장, 호흡기, 간, 안면, 장루·요루, 뇌전증**.

경기도 2014–2017년의 **청각·언어 통합 집계**는 별도 유형으로 보존하고 청각/언어에 임의로 분배하지 않습니다. 원본의 공란·누락·불일치 값은 **0으로 대체하거나 보간하지 않습니다.** 모델마다 종속변수와 필요한 설명변수가 모두 있는 완전관측치만 사용합니다. 추정할 수 없는 경우 표본 부족·공선성·결측 등 사유를 표시합니다.

## 화면의 통계와 해석

- 독립변수별 **기울기 β**, 절편 β₀, **R²와 수정 R² 각각**, 설명변수별 p값 및 95% 신뢰구간, 모형 F검정 p값, 표본 수 n
- 최종 6변수 모형의 **6개 실제 등록률 산점도**. 각 주황색 선은 나머지 다섯 설명변수를 현재 표본 평균으로 고정한 **다중회귀 조건부 예측선**입니다. 단순회귀선이 아닙니다.
- 연도별 기울기, 절편, R², 수정 R², 설명변수 p값, 모형 F검정 p값 추이. 결측 연도는 보간하지 않습니다.
- **04 / COMPLETE REGRESSION INDEX**에서 연도·지역·장애유형 검색, 분석 단위 선택, 정렬, 페이지 이동, 검색 결과 CSV 다운로드
- **Raw·관측치**에서 실제 `statsmodels.OLS(...).fit().summary()` 전체 출력, 모형에 사용한 원 관측치, 예측값, 잔차 및 관측치 CSV 다운로드

설명변수가 **1 분석 단위** 증가할 때의 회귀계수 β는 등록률의 예상 변화량을 **퍼센트포인트(%p)**로 표시합니다. 단순회귀는 다른 변수를 통제하지 않고, 다중회귀는 나머지 설명변수를 고정한 조건부 연관성입니다. X의 단위가 서로 다르므로 계수 크기를 직접 비교하면 안 됩니다. 재정자립도는 0–1로 정규화하므로 **원래 1%p 증가 = X₁ 0.01 증가**입니다.

이 분석의 한계에는 지자체 반복관측·연도효과를 따로 통제하지 않은 통합 OLS, 다중공선성, 행정구역 개편, 집계 기준 차이, 결측에 따른 n 변화가 포함됩니다. 진료비·보험료는 지역의 고령화나 질병 부담의 *결과*일 수도 있으며 인과적 효과로 해석할 수 없습니다.

## 원본 출처 및 디렉터리

| 폴더 | 자료 | 원본 출처 안내 |
| --- | --- | --- |
| `Statistics/인구/` | 주민등록인구, 5세별 연앙인구, 주민등록세대수 | 행정안전부 주민등록통계·KOSIS |
| `Statistics/재정/` | Financial Independence.csv | 지방재정365 재정자립도 |
| `Statistics/출산율/` | Birth rate.csv | KOSIS 합계출산율 |
| `Statistics/장애인등록/Disability/` | 17개 시도별 등록통계 CSV | 보건복지부·KOSIS |
| `Statistics/국가건강정보/진료비/` | 지역별 연령별 진료현황 CSV 4개 | 국민건강보험공단 통계 |
| `Statistics/국가건강정보/보험료/` | 지역별 건강보험료 현황 CSV 4개 | 국민건강보험공단 통계 |

출처, 기간, 분모, 원본 단위, 행정구역 처리와 결측 규칙은 [**Statistics/README.md**](Statistics/README.md)에 기록합니다. 원본 CSV는 그대로 두고 계산 및 정규화는 Python에서만 합니다.

## 재현 실행

Python과 `requirements.txt`에 명시된 라이브러리가 준비된 환경에서:

```bash
python -m pip install -r requirements.txt
python -m pip install pytest  # 테스트용 도구(분석 필수 의존성에는 포함되지 않음)
python -m pytest tests -q
python build.py
python -m http.server 8000
```

- [`http://localhost:8000/`](http://localhost:8000/) — **최종 6변수 통합 화면** (`index.html`).
- [`http://localhost:8000/site/index.html`](http://localhost:8000/site/index.html) — 기존 **데이터 탐색** 화면.
- [`http://localhost:8000/site/unified.html?model=six`](http://localhost:8000/site/unified.html?model=six) — 통합 화면 직접 주소.

`python build.py`는 통계 결과와 정적 웹사이트를 재생성하며, `site/unified.html`을 기반으로 **프로젝트 최상위 `index.html`을 다시 생성**합니다. 이때 `<base href="./site/">`를 넣어 리소스 경로를 맞춥니다. `site/index.html`은 데이터 탐색 화면으로 **변경하지 않고 보존**합니다. **따라서 최상위 `index.html`만 수동 수정해도 다음 빌드에서 덮어쓰므로 빌드 규칙도 함께 관리해야 합니다.**

```text
build.py                   전체 분석 + 정적 사이트 생성
expanded_analysis.py       인구·진료비 및 기존 분석
insurance_premiums.py      보험료 정합성·세대수 결합
unified_analysis.py        최종 6변수 및 6개 단순회귀 JSON 생성
site/unified.html          통합 분석 화면
site/index.html            기존 데이터 탐색 화면
site/assets/js/sidebar.js  공통 사이드바
site/data/unified_manifest.json
site/data/unified_index_<모형>.json.gz
site/data/unified_detail/<모형>/<장애유형번호>.json.gz
index.html                 GitHub Pages 루트 (빌드 산출물)
tests/                     기존·추가 분석 및 화면 계약 테스트
```

통합 화면은 경량 인덱스를 먼저 읽고 상세 OLS JSON은 선택 시에만 가져옵니다. `*.json.gz`는 브라우저의 `DecompressionStream('gzip')`으로 해제합니다. Python에 설치된 필수 패키지와 원본 CSV가 있으면 분석 계산은 인터넷 없이도 가능하지만, 차트는 외부 **Chart.js CDN**을 사용하므로 오프라인에서 별도 차트 라이브러리 제공이 필요합니다.

## GitHub Pages 배포와 검증

이 프로젝트는 정적 GitHub Pages 사이트입니다. 저장소의 **`main` 브랜치 / `/(root)`** 를 배포 소스로 사용하고 `.nojekyll`을 유지합니다. 배포 주소는 [https://milkywaypeko.github.io/ASD_FI_Correlation_9Y/](https://milkywaypeko.github.io/ASD_FI_Correlation_9Y/) 입니다.

분석 코드·페이지를 바꾼 후에는 테스트 → `python build.py` → 생성 JSON 일치 검증 → PR 병합 → Pages 배포 작업 성공 확인 순서로 진행합니다. `site/data/`의 원문·관측치가 포함된 gzip 자료는 정적 배포 파일 수를 줄이기 위해 모형 및 유형별로 묶으며, **압축 자체는 통계값을 바꾸지 않습니다.** 과거 배포에서 대량 파일의 `syncing_files` 시간 초과가 있어 압축을 도입했습니다.

**연구 해석에 관한 주의:** 본 저장소의 회귀 결과는 기술적·탐색적 연관성 분석입니다. 인과추론 또는 정책효과 추정으로 오해하지 마세요.
