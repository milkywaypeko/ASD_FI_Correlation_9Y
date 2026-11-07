'use strict';
/**
 * One sidebar for every static research page, including the Pages root entry.
 * This is navigation only: no statistical inputs, model calculations, or
 * regression JSON are changed here.
 */
(() => {
  const nav = document.querySelector('.sidebar .navigation');
  if (!nav) return;

  const groups = [
    {title: '개별 단순회귀', key: 'simple', items: [
      ['age65', '65세 이상 인구비율', '◷'],
      ['under15', '0~14세 인구비율', '◴'],
      ['medical', '1인당 진료비', '▤'],
      ['premium', '가구당 건강보험료', '◉'],
      ['fertility', '합계출산율', '↗'],
      ['fiscal', '재정자립도', '◇']
    ]},
    {title: '기타 기존 분석', key: 'legacy', items: [
      ['multivariate.html', '재정·출산율 2변수 회귀', '∑'],
      ['fiscal-birth.html', '재정자립도 → 출산율', '◈'],
      ['results.html', '기존 회귀 결과표', '≋']
    ]}
  ];

  function currentPage() {
    // The project root "/" uses a <base href="./site/"> for its assets.
    // Compare the actual location to avoid treating / as a different page.
    return window.location.pathname.endsWith('/') ? 'index.html' :
      (window.location.pathname.split('/').pop() || 'index.html');
  }

  function unifiedModel() {
    return new URLSearchParams(window.location.search).get('model') || 'six';
  }

  function isActive(key) {
    const page = currentPage();
    // The project root now renders the six-variable explorer directly.
    // site/index.html remains the original fiscal data exploration page.
    const rootLanding = !window.location.pathname.includes('/site/') &&
      (window.location.pathname.endsWith('/') || page === 'index.html');
    if (key === 'index.html') return page === 'index.html' && !rootLanding;
    if (key === 'quality.html') return page === 'quality.html';
    if (key.endsWith('.html')) return page === key;
    return (page === 'unified.html' || rootLanding) && unifiedModel() === key;
  }

  function link(key, title, icon, nested = false) {
    const href = key.endsWith('.html') ? key : 'unified.html?model=' + key;
    const a = document.createElement('a');
    a.href = href;
    a.dataset.navKey = key;
    if (nested) a.classList.add('nav-subitem');

    const pictogram = document.createElement('span');
    pictogram.className = 'nav-icon';
    pictogram.setAttribute('aria-hidden', 'true');
    pictogram.textContent = icon;
    a.append(pictogram, document.createTextNode(title));
    return a;
  }

  // Replace old hardcoded/redirected menus, not their underlying URLs.
  const home = link('index.html', '데이터 탐색', '▦');
  const six = link('six', '최종 6변수 다중회귀', '∑');
  nav.replaceChildren(home, six);

  const groupElements = [];
  for (const group of groups) {
    const details = document.createElement('details');
    details.className = 'nav-group';
    details.dataset.navGroup = group.key;
    const summary = document.createElement('summary');
    summary.textContent = group.title;
    const links = document.createElement('div');
    links.className = 'nav-children';
    for (const [key, title, icon] of group.items) {
      links.append(link(key, title, icon, true));
    }
    details.append(summary, links);
    nav.append(details);
    groupElements.push(details);
  }
  nav.append(link('quality.html', '데이터 품질·연구 방법', 'ⓘ'));

  function updateActive() {
    let active = null;
    nav.querySelectorAll('a[data-nav-key]').forEach(a => {
      const match = isActive(a.dataset.navKey);
      a.classList.toggle('active', match);
      if (match) {
        a.setAttribute('aria-current', 'page');
        active = a;
      } else {
        a.removeAttribute('aria-current');
      }
    });
    for (const details of groupElements) {
      const containsActive = Boolean(details.querySelector('a.active'));
      details.classList.toggle('has-active', containsActive);
      // Do not collapse a group the reader opened manually. Automatically
      // expand only the group containing the current analysis.
      if (containsActive) details.open = true;
    }
    return active;
  }

  window.SidebarNav = Object.freeze({updateActive});
  window.addEventListener('popstate', updateActive);
  updateActive();
})();
