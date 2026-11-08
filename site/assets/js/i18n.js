'use strict';
/* Site-wide presentation-only Korean/English switch. Data keys, numeric values,
 * raw statsmodels/SciPy outputs, CSV exports and URL parameters stay unchanged. */
(() => {
  const STORAGE_KEY = 'public-data-lab-language';
  const searchLang = new URLSearchParams(location.search).get('lang');
  const saved = (() => { try { return localStorage.getItem(STORAGE_KEY); } catch { return null; } })();
  let language = ['ko', 'en'].includes(searchLang) ? searchLang : (saved === 'en' ? 'en' : 'ko');
  const dictionary = Object.entries({
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
  const skipped = new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','PRE','CODE','OPTION']);
  function translate(source) {
    if (language === 'ko' || !/[가-힣]/.test(source)) return source;
    let value = source;
    for (const [ko,en] of dictionary) {
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
    button.addEventListener('click',()=>setLanguage(code));
    switcher.append(button);
    buttons[code]=button;
  }
  function setLanguage(code) {
    if (!['ko','en'].includes(code)) return;
    language=code;
    try { localStorage.setItem(STORAGE_KEY,code); } catch { /* private browsing */ }
    document.documentElement.lang=code;
    document.documentElement.dataset.language=code;
    buttons.ko.setAttribute('aria-pressed',String(code==='ko'));
    buttons.en.setAttribute('aria-pressed',String(code==='en'));
    document.title=translate(document.titleKo || (document.titleKo=document.title));
    translateTree(document.body);
    window.dispatchEvent(new CustomEvent('site-language-change',{detail:{language:code}}));
  }
  const sidebar=document.querySelector('.sidebar');
  (sidebar?.querySelector('.sidebar-bottom') || sidebar || document.querySelector('.page-header') || document.body).prepend(switcher);
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