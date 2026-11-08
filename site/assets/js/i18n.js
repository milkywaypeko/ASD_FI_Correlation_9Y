'use strict';
/* Site-wide presentation-only Korean/English switch. Data keys, numeric values,
 * raw statsmodels/SciPy outputs, CSV exports and URL parameters stay unchanged. */
(() => {
  const STORAGE_KEY = 'public-data-lab-language';
  const searchLang = new URLSearchParams(location.search).get('lang');
  const saved = (() => { try { return localStorage.getItem(STORAGE_KEY); } catch { return null; } })();
  let language = ['ko', 'en'].includes(searchLang) ? searchLang : (saved === 'en' ? 'en' : 'ko');
  const dictionary = Object.entries({
    "X가 1단위 증가할 때 등록률 Y의 예상 변화량은 %p입니다. 다중회귀의 계수 β는 나머지 변수를 일정하게 유지한 조건부 연관성입니다.": "A one-unit increase in X corresponds to an expected change in registration rate Y measured in percentage points. Multivariable β coefficients hold other predictors constant.",
    "피어슨 r은 동일 완전관측 표본의 Y와 각 X 사이의 이변량 선형 상관계수": "Pearson r measures the bivariate linear correlation between Y and each X using the same complete-case sample",
    "로, 다른 변수를 통제한 편상관이나 β가 아닙니다. 계산이 불가능한 r은 —로 표시합니다.": " rather than partial correlation or an OLS coefficient. Undefined correlations are shown as —.",
    "산점도 Y는 실제 등록률(%). 다중회귀선은 해당 X를 제외한 나머지 다섯 설명변수를 현재 완전관측 표본 평균으로 고정한": "Scatterplot Y shows the observed registration rate (%). The multivariable line holds the other five predictors at their complete-case sample means and shows a",
    "조건부 예측선": "conditional prediction line",
    "이며 단순회귀선이 아닙니다.": " rather than a simple regression line.",
    "연도별 별도 회귀 결과입니다. 모형 추정이 불가능한 시점은 보간하지 않습니다. 피어슨 r은 같은 완전관측치에서 계산하며 OLS 추정 불가 시에도 계산 가능할 수 있습니다.": "Separate regressions are fitted by year. Years without an estimable model are not interpolated. Pearson r uses the same complete cases and may still be available when OLS is not.",
    "계수의 X 단위가 서로 다르므로 숫자 크기를 변수 간 직접 비교하지 마세요. p값 그래프와 CSV는 실제 p값입니다.": "Predictors have different units; do not directly compare coefficient magnitudes. The p-value charts and CSV retain actual p-values.",
    "전국 기초지자체 통합 OLS는 광역별로 나누지 않고, 한 연도의 모든 기초지자체 유효 관측치를 합쳐 하나의 statsmodels OLS를 적합한 결과입니다.": "Nationwide pooled municipal OLS fits one statsmodels model to all valid municipality observations in a year, without splitting by province.",
    "각 분석은 동일한 회귀 완전관측치에서": "Each analysis uses the same complete cases as the regression and calls",
    "로 계산합니다. r은 이변량 상관으로, 다중회귀의 편상관 또는 OLS β가 아닙니다.": "to compute its confidence interval. Pearson r is bivariate, not partial correlation or an OLS coefficient.",
    "아래 출력은 SciPy가 반환한": "The output below preserves the SciPy",
    "의 실제 표현입니다. 계산 불가능한 경우에는 사유를 표시합니다.": "objects as returned. If the computation is undefined, the reason is shown.",
    "선택한 모형의 Raw 출력과 관측자료": "Raw model output and observations",
    "선택 모형 · Raw·관측치": "Selected model · Raw & observations",
    "비교표 행을 선택하세요.": "Select a row from the comparison table.",
    "모형 선택 후 원문이 표시됩니다.": "The original output appears after selecting a model.",
    "완전관측치 · 적합값 · 잔차": "Complete cases · fitted values · residuals",
    "변수의 정의·관측 범위·해석 유의사항": "Variable definitions, observation coverage and interpretation",
    "2014년은 재정자립도 세입과목 개편 시점이고, 2022년은 일부 장애 등록통계의 자료 가용성 한계입니다. 따라서 전체 연구 기간은 2014~2022년입니다.": "2014 marks the fiscal-accounting reform, while disability registration data availability ends in 2022. The study therefore covers 2014–2022.",
    "건강보험료 또는 진료비를 포함한 회귀는 예외 없이 2015~2022년": "Regressions including health insurance premiums or medical spending use only 2015–2022",
    "만 이용합니다. 원본 2014년 CSV는 보존합니다.": ". The original 2014 CSV is retained.",
    "변수": "Variable",
    "계산식/단위": "Formula / unit",
    "분모": "Denominator",
    "장애유형별 등록률": "Disability-specific registration rate",
    "선택 장애유형 등록인원 ÷ 주민등록인구 × 100 (%)": "Registered persons in selected category ÷ registered population × 100 (%)",
    "해당 연도·지역 주민등록인구": "Registered population for the year and region",
    "원본 0~100 (%) ÷ 100 → 0~1, 개편 전·후 선택": "Original 0–100 (%) ÷ 100 → 0–1; choose pre/post reform",
    "공식 지방재정 통계": "Official local-government fiscal statistics",
    "65세 이상·0~14세 인구비율": "Population aged 65+ and 0–14 (%)",
    "해당 연령 주민등록연앙인구 ÷ 전체 주민등록연앙인구 × 100 (%)": "Midyear registered population in age group ÷ total midyear population × 100 (%)",
    "주민등록연앙인구": "Midyear registered population",
    "여성 1명당 출생아 수 (명/여성)": "Births per woman",
    "출산율 공식 기간지표": "Official period fertility indicator",
    "연간 총진료비(천원) ÷ 주민등록연앙인구 ÷ 10 (만원/인/년)": "Annual medical expenditure (KRW 1,000) ÷ midyear population ÷ 10 (KRW 10,000/person/year)",
    "연간 총보험료(천원) ÷ 주민등록세대수 ÷ 10 (만원/세대/년)": "Annual premiums (KRW 1,000) ÷ registered households ÷ 10 (KRW 10,000/household/year)",
    "주민등록세대수": "Registered households",
    "기울기 β₁은 X가 1단위 증가할 때 등록률 Y의 예상 변화(%p)입니다. 피어슨 r은 동일 완전관측치에서 계산한 이변량 상관으로 β₁과 다릅니다.": "Slope β₁ is the expected percentage-point change in registration rate Y for a one-unit increase in X. Pearson r is the bivariate correlation on the same complete cases and is distinct from β₁.",
    "다중회귀에서 각 β는 다른 다섯 설명변수를 일정하게 유지할 때 X가 1단위 증가하는 경우 등록률 Y의 예상 변화(%p)입니다. 단위가 다른 계수 크기를 직접 비교하지 마세요.": "In multivariable regression, each β is the expected percentage-point change in Y for a one-unit increase in X holding the other five predictors constant. Do not compare coefficients with different units directly.",
    "연도별 단순회귀 결과입니다. 모형을 추정할 수 없는 시점은 보간하지 않습니다. SciPy r은 동일 완전관측치로 계산합니다.": "Annual simple regression results. Years without an estimable model are not interpolated. SciPy r uses the same complete cases.",
    "연도별 6변수 다중회귀 결과입니다. β·절편·R²·수정 R²·OLS 계수 p값·모형 F p값을 표시하며 추정 불가 시점은 보간하지 않습니다.": "Annual six-variable regression results. β, intercept, R², adjusted R², OLS coefficient p-values and model F-test p-values are shown without interpolation.",
    "전국 기초지자체 전체를 하나의 표본으로 합친 OLS만 표시합니다.": "Show only OLS fitted to all municipalities nationwide as one sample.",
    "표 분석 단위에 따라 전국·광역별 기초지자체 횡단면 OLS, 광역지자체 간 OLS, 기초지자체 시계열 OLS를 구분합니다.": "The selected unit distinguishes nationwide/provincial municipal cross-sections, provincial cross-sections, and municipality time-series OLS.",
    "단순 OLS 예측선": "Simple OLS fit",
    "실제 등록률(%)": "Observed registration rate (%)",
    "나머지 다섯 변수 평균 고정 조건부 예측선": "Conditional fit holding five other predictors at their means",
    "단순회귀 적합선": "Simple regression fit",
    "상세 모형을 불러오는 중…": "Loading detailed model…",
    "SciPy 결과를 불러오는 중…": "Loading SciPy results…",
    "해당 선택의 모형이 없습니다.": "No model is available for this selection.",
    "해당 선택의 SciPy 분석이 없습니다.": "No SciPy analysis is available for this selection.",
    "해당 계수는 인과효과가 아니라 관측자료의 통계적 연관성입니다.": "This coefficient represents an observed statistical association, not a causal effect.",
    "계산 불가": "Unavailable",
    "정밀도 한계 가능": "Possible numerical precision limit",
    "완전관측치 n": "Complete-case n",
    "경고": "Warning",
    "계산 실패 사유": "Reason for calculation failure",
    "상태": "Status",
    "실제 X·Y 관측자료 CSV 저장": "Download observed X–Y pairs CSV",
    "상관분석 관측치 CSV 저장": "Download correlation observations CSV",
    "비교표에서 분석 모형을 선택하세요.": "Select a model from the comparison table.",
    "모형을 추정할 수 없습니다.": "Model cannot be estimated.",
    "상관분석 관측치": "Correlation observations",
    "광역": "Province",
    "기초": "Municipality",
    "X 설명변수 실제값": "Observed predictor X",
    "Y 장애유형 등록률(%)": "Disability registration rate Y (%)",
    "검색 결과 CSV 저장": "Download search results CSV",
    "전체 장애유형 결과 함께 비교": "Compare all disability categories",
    "모든 광역지자체 결과 포함": "Include all provinces",
    "표에서 모든 광역지자체 결과 포함": "Include all provinces in table",
    "모든 장애유형 결과 함께 비교": "Compare all disability categories",
    "전체 장애유형 함께 비교": "Compare all disability categories",
    "실제 관측치와": "Observed data and",
    "전국": "Nationwide",
    "강원특별자치도": "Gangwon State",
    "경기도": "Gyeonggi",
    "서울특별시": "Seoul",
    "부산광역시": "Busan",
    "대구광역시": "Daegu",
    "인천광역시": "Incheon",
    "광주광역시": "Gwangju",
    "대전광역시": "Daejeon",
    "울산광역시": "Ulsan",
    "세종특별자치시": "Sejong",
    "충청북도": "North Chungcheong",
    "충청남도": "South Chungcheong",
    "전북특별자치도": "Jeonbuk State",
    "전라남도": "South Jeolla",
    "경상북도": "North Gyeongsang",
    "경상남도": "South Gyeongsang",
    "제주특별자치도": "Jeju",
    '최종 6변수 다중회귀': 'Final six-variable regression',
    '개별 단순회귀': 'Simple linear regressions',
    '기타 기존 분석': 'Other analyses',
    '데이터 품질·연구 방법': 'Data quality & methodology',
    '데이터 탐색': 'Explore data',
    '65세 이상 인구비율': 'Population aged 65+ (%)',
    '0~14세 인구비율': 'Population aged 0–14 (%)',
    '1인당 진료비': 'Medical spending per person',
    '가구당 건강보험료': 'Health premium per household',
    '합계출산율': 'Total fertility rate',
    '재정자립도': 'Fiscal independence',
    '재정·출산율 2변수 회귀': 'Fiscal & fertility regression',
    '재정자립도 → 출산율': 'Fiscal independence → fertility',
    '기존 회귀 결과표': 'Previous regression results',
    '자료 가용성': 'Data availability',
    '전체 2014–2022': 'Full data: 2014–2022',
    '건강보험 포함 모형 2015–2022': 'Health-insurance models: 2015–2022',
    '주요 분석 메뉴': 'Main analysis navigation',
    '등록률 회귀분석': 'Disability registration rate regression',
    '장애인 등록률 통합 회귀 연구': 'Disability registration rate regression study',
    '지역별 장애유형 등록률과 사회·인구·건강보험 지표의 통계적 연관성을 탐색합니다. 인과관계를 입증하지 않습니다.': 'Explore statistical associations between disability registration rates and socioeconomic, demographic, and health-insurance indicators across regions. These results do not establish causality.',
    '01 / 분석 조건': '01 / Analysis settings',
    '분석 조건': 'Analysis settings',
    '분석값은 Python에서 사전 계산됩니다.': 'Results are precomputed in Python.',
    '회귀모형': 'Regression model',
    '장애유형': 'Disability category',
    '장애 유형': 'Disability category',
    '분석 단위': 'Unit of analysis',
    '광역지자체': 'Province / metropolitan city',
    '기초지자체': 'Municipality',
    '재정자립도 기준': 'Fiscal independence definition',
    '기초지자체 간 비교': 'Across municipalities',
    '광역지자체 간 비교': 'Across provinces',
    '기초지자체 연도별 변화': 'Municipality over time',
    '전국 기초지자체 통합 OLS만': 'Nationwide pooled municipal OLS only',
    '기초지자체 간 비교 (전국·광역별)': 'Municipal comparison (national / provincial)',
    '기초지자체 시계열': 'Municipality time series',
    '전체 분석 단위': 'All analysis units',
    '개편 후': 'After accounting reform',
    '개편 전': 'Before accounting reform',
    '세입과목 개편 후': 'After accounting reform',
    '세입과목 개편 전': 'Before accounting reform',
    '전체 기간 통합': 'Pool all years',
    '전체 기간': 'Full period',
    '전기간': 'All years',
    '단일 시점': 'Single year',
    '년 통합': ' pooled',
    '년': '',
    'OLS 회귀 결과': 'OLS regression results',
    '핵심 회귀 결과': 'Key regression results',
    '절편 β₀': 'Intercept β₀',
    'R² 결정계수': 'R² (coefficient of determination)',
    'Adjusted R² 수정 결정계수': 'Adjusted R²',
    '수정 R²': 'Adjusted R²',
    'F검정 모형 p값': 'Model F-test p-value',
    '표본 수 n': 'Sample size n',
    '단순회귀 기울기 β₁': 'Simple OLS slope β₁',
    '피어슨 상관계수 r': 'Pearson correlation r',
    'OLS 기울기 β₁ p값': 'OLS slope β₁ p-value',
    'β₁ = 0에 대한 양측 검정 · F검정 모형 p값과 별도': 'Two-sided test of β₁ = 0 · distinct from model F-test',
    'X 1단위 증가당 등록률 변화 (%p)': 'Change in registration rate per unit X (percentage points)',
    '설명변수별 회귀계수 β와 SciPy 피어슨 상관계수 r': 'Regression coefficients β and SciPy Pearson correlations r',
    '단순회귀 기울기 β₁와 SciPy 피어슨 상관계수 r': 'Simple regression slope β₁ and SciPy Pearson r',
    '6변수 다중회귀 · 설명변수별 회귀계수 β': 'Six-variable regression · coefficients by predictor',
    '설명변수 / 단위': 'Predictor / unit',
    '설명변수': 'Predictor',
    '기울기 β': 'Slope β',
    'OLS β p값': 'OLS coefficient p-value',
    'SciPy r p값(양측)': 'SciPy r p-value (two-sided)',
    'OLS β 95% CI 하한': 'OLS β 95% CI lower',
    'OLS β 95% CI 상한': 'OLS β 95% CI upper',
    '실제 장애유형별 등록률과 회귀 예측선': 'Observed registration rates and regression fits',
    '연도별 회귀지표 추이': 'Yearly regression trends',
    '연도별 회귀계수 추이': 'Yearly coefficient trends',
    '추이 CSV 저장': 'Download trend CSV',
    '다중회귀 설명변수 계수/기울기 선택': 'Select coefficient / predictor',
    '기울기 p값': 'Slope p-value',
    '기울기 p': 'Slope p',
    '피어슨 상관계수 r (선택한 X–Y)': 'Pearson r (selected X–Y)',
    '시점·광역·기초지자체별 회귀 통계표': 'Regression results by year and region',
    '행의 「Raw·관측치」를 선택하면 해당 모형의 statsmodels 출력과 실제 관측자료를 아래에서 확인할 수 있습니다.': 'Select “Raw & observations” in a row to view the statsmodels output and observed data below.',
    '연도·지역·장애유형 검색': 'Search year, region, category',
    '연도, 지역, 장애유형': 'Year, region, category',
    '표 분석 단위': 'Table analysis unit',
    '전체 장애유형 함께 비교': 'Compare all disability categories',
    '전체 지역 함께 비교': 'Include all regions',
    '전국 기초지자체 전체 회귀만 보기': 'Nationwide pooled municipal OLS only',
    '결과 CSV 저장': 'Download results CSV',
    'CSV 저장': 'Download CSV',
    'Raw·관측치': 'Raw & observations',
    '상세': 'Details',
    '시점': 'Year / period',
    '광역 / 기초': 'Province / municipality',
    '광역/기초': 'Province / municipality',
    '연도': 'Year',
    '지역': 'Region',
    '전체': 'Total',
    '전국': 'Nationwide',
    '표본 n': 'Sample n',
    '모형 F p값': 'Model F p-value',
    '모형 F검정 p값': 'Model F-test p-value',
    '선택한 모형의 Raw 출력과 관측자료': 'Selected model raw output and observations',
    '실제 statsmodels.OLS(...).fit().summary() 출력': 'Raw statsmodels.OLS(...).fit().summary()',
    'SciPy Raw 결과 및 실제 X·Y 관측자료': 'SciPy raw results and observed X–Y pairs',
    'SciPy Pearson r · p값 · 95% 신뢰구간': 'SciPy Pearson r · p-value · 95% confidence interval',
    '실제 X·Y 관측자료 CSV 저장': 'Download observed X–Y CSV',
    '원본 관측자료 CSV 저장': 'Download raw observations CSV',
    '관측치': 'Observations',
    '불러오는 중…': 'Loading…',
    '로딩 중…': 'Loading…',
    '집계 중': 'Computing…',
    '이전': 'Previous',
    '다음': 'Next',
    '결과 없음': 'No results',
    '자료 검증 및 분석 방법': 'Data validation and methodology',
    '병합 방식, 분모 설정, 행정구역 표준화 및 모델 계산에 관한 공개 기록입니다.': 'Public documentation of data joins, denominators, regional standardization, and model computation.',
    '기초지자체 × 연도': 'Municipality × year',
    '광역지자체 × 연도': 'Province × year',
    '인구·재정 결측 점검': 'Population / fiscal missing-data audit',
    '인구분모 확인 관측치': 'Records with population denominators',
    '시도 합계 관측치': 'Provincial aggregate records',
    '중복 없이 분석·검증': 'Checked without duplication',
    '장애인 비율의 분모·분자': 'Disability registration rate: numerator and denominator',
    '지역명 정규화와 예외 처리': 'Region name standardization and exceptions',
    '장애인 등록률과 설명변수의 피어슨 상관계수': 'Pearson correlation between registration rate and predictors',
    '자료 누락·매칭 점검': 'Missing-data and join audit',
    '장애인 비율 × 재정자립도': 'Disability registration rate × fiscal independence',
    '기초·광역지자체의 장애유형별 등록률과 재정자립도 사이의 선형적 관계를 탐색합니다.': 'Explore linear associations between disability registration rates and fiscal independence across municipalities and provinces.',
    '선형회귀 결과 비교': 'Compare linear regression results',
    '모든 지역 결과 보기 ↗': 'View all regional results ↗',
    '관측치 누락 및 특이사항은 자동 생성': 'Missing observations and anomalies are generated automatically',
    '결측': 'Missing',
    '표시': 'Display',
    '다운로드': 'Download',
    '선택': 'Select',
    '합계': 'Total',
    '남성': 'Male',
    '여성': 'Female',
    '지체': 'Physical disability',
    '뇌병변': 'Brain lesion',
    '시각': 'Visual disability',
    '청각': 'Hearing disability',
    '언어': 'Speech disability',
    '지적': 'Intellectual disability',
    '자폐성': 'Autism spectrum',
    '정신': 'Psychosocial disability',
    '신장': 'Kidney disability',
    '심장': 'Cardiac disability',
    '호흡기': 'Respiratory disability',
    '간': 'Liver disability',
    '안면': 'Facial disability',
    '장루·요루': 'Ostomy / urostomy',
    '뇌전증': 'Epilepsy',
    '장애유형별': 'By disability category',
    '양측': 'Two-sided',
    '모형을 추정할 수 없습니다.': 'Model cannot be estimated.',
    '통계적 연관성은 인과관계를 의미하지 않습니다.': 'Statistical association does not imply causation.',
    '통계적 연관성': 'Statistical association',
    '인과관계': 'Causality',
    '확인': 'View'
  }).sort((a,b)=>b[0].length-a[0].length);

  const originals = new WeakMap();
  const rendered = new WeakMap();
  const skipped = new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','PRE','CODE']);
  function translate(source) {
    if (language === 'ko' || !/[가-힣]/.test(source)) return source;
    let value = source;
    for (const [ko,en] of dictionary) {
      if (ko.length <= 3 && value.trim() !== ko) continue;
      if (value.includes(ko)) value = value.split(ko).join(en);
    }
    return value;
  }
  function shouldSkip(node) {
    let element = node.parentElement;
    while (element) {
      if (skipped.has(element.tagName) || element.hasAttribute('data-no-translate') ||
          element.closest?.('[data-no-translate]')) return true;
      element = element.parentElement;
    }
    return false;
  }
  function updateText(node) {
    if (shouldSkip(node)) return;
    const current = node.nodeValue;
    if (current !== rendered.get(node)) originals.set(node,current);
    const original = originals.get(node) ?? current;
    const desired = translate(original);
    if (current !== desired) node.nodeValue = desired;
    rendered.set(node,desired);
  }
  function translateTree(root) {
    if (root.nodeType === Node.TEXT_NODE) { updateText(root); return; }
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE &&
        (skipped.has(root.tagName) || root.closest('[data-no-translate]'))) return;
    const walker = document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) updateText(walker.currentNode);
    if (root.nodeType === Node.ELEMENT_NODE || root.nodeType === Node.DOCUMENT_NODE) {
      const elements = root.querySelectorAll('[placeholder],[aria-label],[title]');
      for (const element of elements) {
        for (const attribute of ['placeholder','aria-label','title']) {
          if (!element.hasAttribute(attribute)) continue;
          const key = 'data-i18n-ko-' + attribute;
          if (!element.hasAttribute(key)) element.setAttribute(key,element.getAttribute(attribute));
          const original = element.getAttribute(key);
          const desired = translate(original);
          if (element.getAttribute(attribute)!==desired) element.setAttribute(attribute,desired);
        }
      }
    }
  }
  const switcher = document.createElement('div');
  switcher.className = 'language-switcher';
  switcher.setAttribute('role','group');
  switcher.setAttribute('aria-label','Language / 언어');
  const buttons = {};
  for (const [code,name] of [['ko','한국어'],['en','English']]) {
    const button=document.createElement('button');
    button.type='button';
    button.textContent=name;
    button.dataset.language=code;
    button.addEventListener('click',()=>setLanguage(code,true));
    switcher.append(button);
    buttons[code]=button;
  }
  function setLanguage(code,fromClick=false) {
    if (!['ko','en'].includes(code)) return;
    language=code;
    if (fromClick && new URLSearchParams(location.search).has('lang')) {
      const url=new URL(location.href);
      url.searchParams.set('lang',code);
      history.replaceState(history.state,'',url);
    }
    try { localStorage.setItem(STORAGE_KEY,code); } catch { /* private browsing */ }
    document.documentElement.lang=code;
    document.documentElement.dataset.language=code;
    buttons.ko.setAttribute('aria-pressed',String(code==='ko'));
    buttons.en.setAttribute('aria-pressed',String(code==='en'));
    document.title=language==='ko' ? (document.titleKo || (document.titleKo=document.title)) : translate(document.titleKo || (document.titleKo=document.title));
    translateTree(document.body);
    window.dispatchEvent(new CustomEvent('site-language-change',{detail:{language:code}}));
  }
  const sidebar=document.querySelector('.sidebar');
  if (sidebar) sidebar.insertBefore(switcher,sidebar.querySelector('.navigation') || sidebar.firstChild);
  else (document.querySelector('.page-header') || document.body).prepend(switcher);
  const observer=new MutationObserver(records=>{
    for (const record of records) {
      if (record.type==='characterData') updateText(record.target);
      else for (const node of record.addedNodes) translateTree(node);
    }
  });
  observer.observe(document.body,{subtree:true,childList:true,characterData:true});
  window.SiteLanguage=Object.freeze({get:()=>language,set:setLanguage,translate});
  setLanguage(language);
})();