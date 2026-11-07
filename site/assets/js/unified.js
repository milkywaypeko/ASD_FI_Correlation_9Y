'use strict';
/* Static-only browser: never estimates regressions; displays Python statsmodels output. */
(async function () {
  const $ = id => document.getElementById(id);
  const parse = x => x === null || x === undefined || !Number.isFinite(Number(x)) ? null : Number(x);
  const fmt = (x, digits = 6) => parse(x) === null ? '—' : Number(x).toLocaleString('ko-KR', {maximumFractionDigits: digits});
  const text = (id, value) => { $(id).textContent = String(value); };
  const opt = (element, value, label) => element.add(new Option(label, value));
  const cache = new Map();
  const load = path => {
    if (!cache.has(path)) cache.set(path, fetch(path).then(async response => {
      if (!response.ok) throw Error(path + ' HTTP ' + response.status);
      if (!path.endsWith('.gz')) return response.json();
      // GitHub Pages serves .gz as a binary asset, not Content-Encoding:gzip.
      // Decompress on demand: this preserves exact statsmodels summaries and
      // observations without shipping 1,258 uncompressed JSON documents.
      if (!('DecompressionStream' in window)) {
        throw Error('gzip 지원 브라우저가 필요합니다 (최신 Chrome/Edge/Firefox/Safari).');
      }
      const readable = response.body.pipeThrough(new DecompressionStream('gzip'));
      return new Response(readable).json();
    }).catch(error => {cache.delete(path);throw error;}));
    return cache.get(path);
  };
  const quote = value => '"' + String(value === null || value === undefined ? '' : value).replace(/"/g, '""') + '"';
  function download(filename, rows) {
    const blob = new Blob(['\uFEFF' + rows.map(row => row.map(quote).join(',')).join('\r\n')],
                          {type: 'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob), anchor = document.createElement('a');
    anchor.href = url; anchor.download = filename; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  const escaped = s => String(s ?? '').replace(/[&<>"']/g, char => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[char]));
  const params = new URLSearchParams(location.search);
  const initial = params.get('model');
  const state = {
    model: 'six', dtype: '전체', scope: 'municipal', province: '전국',
    district: '', fiscal: 'after', year: 2022, pooled: false,
    search: '', indexScope: 'all', allTypes: false, allRegions: false,
    sort: 'year', descending: true, page: 0, trendVar: 0
  };
  let manifest, index = [], filtered = [], selected = null, current = null;
  let charts = [], trendCharts = [], run = 0;
  const pageSize = 30;
  const spec = () => manifest.models[state.model];
  const fields = () => spec().fiscal ?
    [state.fiscal, ...spec().fields] : [...spec().fields];
  const modelFields = item => item && item.mode && spec().fiscal ?
    [item.mode, ...spec().fields] : [...spec().fields];
  const region = () => state.scope === 'provincial' ? '전국' :
    state.scope === 'local_history' ? state.province + '|' + state.district : state.province;
  const period = () => state.pooled || state.scope === 'local_history' ? '전기간' : state.year;
  const findSelected = () => index.find(item => item.type === state.dtype &&
    item.scope === state.scope && item.region === region() &&
    String(item.year) === String(period()) &&
    (!spec().fiscal || item.mode === state.fiscal));
  const label = field => manifest.labels[field] || field;
  const valid = item => item && item.intercept !== null && item.intercept !== undefined;
  function updateDistrict() {
    const control = $('u-district'), old = state.district;
    control.replaceChildren();
    if (state.province === '전국') {state.district='';control.disabled=true;return;}
    (manifest.districts[state.province] || []).forEach(value => opt(control, value, value));
    control.value = [...control.options].some(o => o.value === old) ? old : control.options[0]?.value || '';
    state.district = control.value;
    control.disabled = state.scope !== 'local_history';
  }
  function updateControls() {
    const years = spec().years;
    if (!years.includes(state.year)) state.year = years.at(-1);
    $('u-year').min = String(years[0]);
    $('u-year').max = String(years.at(-1));
    $('u-year').value = String(state.year);
    $('u-year').disabled = state.pooled || state.scope === 'local_history';
    $('u-all-years').checked = state.pooled || state.scope === 'local_history';
    $('u-all-years').disabled = state.scope === 'local_history';
    $('u-mode-wrap').hidden = !spec().fiscal;
    $('u-province').disabled = state.scope === 'provincial';
    $('u-district').disabled = state.scope !== 'local_history';
    text('year-start', years[0]);
    text('page-period', years[0] + ' — ' + years.at(-1));
    text('u-year-label', period() === '전기간' ? years[0] + '–' + years.at(-1) + '년 통합' : state.year + '년');
    text('page-title', spec().label);
    $('u-model').value = state.model;
    // Keep the shared sidebar highlight synchronized with the active model,
    // including model changes made through the select control.
    document.querySelectorAll('.navigation a[data-unified-model]').forEach(link => {
      const isActive = link.dataset.unifiedModel === state.model;
      link.classList.toggle('active', isActive);
      if (isActive) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    $('u-type').value = state.dtype;
    $('u-scope').value = state.scope;
    $('u-mode').value = state.fiscal;
    $('u-province').value = state.province;
    $('u-index-scope').value = state.indexScope;
    $('u-all-types').checked = state.allTypes;
    $('u-all-regions').checked = state.allRegions;
    const vars = fields();
    $('u-trend-var').replaceChildren();
    vars.forEach((field, i) => opt($('u-trend-var'), String(i), label(field)));
    state.trendVar = Math.min(state.trendVar, vars.length - 1);
    $('u-trend-var').value = String(state.trendVar);
    // Every source with a healthcare component excludes 2014, including trend and CSV.
    document.title = spec().label + ' | 장애인 등록률 연구';
  }
  async function loadDetail(item) {
    const details = await load(item.shard);
    if (!details[item.id]) throw Error('모형 상세 누락: ' + item.id);
    const result = details[item.id];
    if (result.model.n !== item.n ||
        result.model.intercept !== item.intercept ||
        result.model.r2 !== item.r2 ||
        result.model.adj_r2 !== item.adj_r2 ||
        result.model.p_model !== item.p_model) {
      throw Error('경량 인덱스와 원문 모형이 일치하지 않습니다.');
    }
    if (result.observations.length !== item.n) throw Error('원문과 관측치 표본 수 불일치');
    return result;
  }
  function clearCharts(collection) {collection.forEach(c => c.destroy()); collection.length = 0;}
  function showCoefficients(item, detail) {
    const body = $('u-coefficients'); body.replaceChildren();
    const model = detail?.model;
    for (const field of modelFields(item)) {
      const c = model?.coefficients?.[field] || {};
      const tr = document.createElement('tr');
      for (const value of [label(field), fmt(c.coef, 10), fmt(c.p, 9),
                            fmt(c.ci?.[0], 9), fmt(c.ci?.[1], 9)]) {
        const td = document.createElement('td'); td.textContent = value; tr.appendChild(td);
      }
      body.appendChild(tr);
    }
  }
  function graph(canvas, data, xLabel, yLabel) {
    if (!window.Chart) return null;
    return new Chart(canvas, {type:'scatter', data:{datasets:data}, options:{
      responsive:true,maintainAspectRatio:false,
      parsing:false,
      scales:{x:{type:'linear',title:{display:true,text:xLabel}},
              y:{title:{display:true,text:yLabel}}},
      plugins:{tooltip:{callbacks:{label:context => {
        const r = context.raw;
        return (r.place ? r.place + ' · ' : '') + fmt(r.x, 5) + ' / ' + fmt(r.y, 5);
      }}}}
    }});
  }
  function scatter(detail, item) {
    clearCharts(charts);
    const container = $('u-scatters');container.replaceChildren();
    if (!valid(item) || !detail || !detail.observations.length) {
      text('u-scatter-status', item?.warning || '이 조건에서 표시할 유효한 관측치가 없습니다.');
      return;
    }
    const predictors = modelFields(item);
    for (let i=0;i<predictors.length;i++) {
      const field = predictors[i], box = document.createElement('div');
      box.className = 'u-scatter';
      const h = document.createElement('h3');
      h.textContent = label(field) + ' × ' + item.type + ' 등록률(%)';
      const canvas = document.createElement('canvas');
      box.append(h, canvas);container.appendChild(box);
      const observations = detail.observations;
      const points = observations.map(row => ({
        x:row[4 + i], y:row[3], place:row[1] + ' ' + row[2] + ' ' + row[0]
      }));
      const xs = points.map(v => v.x).filter(Number.isFinite);
      if (!xs.length) continue;
      const otherMean = predictors.map((p, idx) =>
        observations.reduce((sum, obs) => sum + obs[4+idx], 0) / observations.length
      );
      const coefficient = item.coefficients[i];
      const baseline = item.intercept + item.coefficients.reduce((s, beta, idx) =>
        s + (idx === i ? 0 : beta * otherMean[idx]), 0);
      const low = Math.min(...xs), high = Math.max(...xs);
      const condition = predictors.length > 1;
      const datasets = [
        {label:'실제 등록률(%)',data:points,backgroundColor:'rgba(32,104,158,.65)',pointRadius:3.1},
        {type:'line',label:condition?'나머지 다섯 변수 평균 고정 조건부 예측선':'단순 OLS 예측선',
         data:[{x:low,y:baseline + coefficient*low},{x:high,y:baseline + coefficient*high}],
         borderColor:'#bd6738',borderWidth:2,pointRadius:0}
      ];
      const instance = graph(canvas,datasets,label(field),item.type+' 등록률(%)');
      if(instance) charts.push(instance);
    }
    text('u-scatter-status', window.Chart ? '실제 관측치와 ' +
      (predictors.length > 1 ? '나머지 다섯 설명변수 평균 고정 조건부 예측선' : '단순회귀 적합선') +
      '을 구별해 표시합니다.' : 'Chart.js CDN을 불러오지 못했습니다. 계수와 관측치는 아래 표에서 확인할 수 있습니다.');
  }
  function observedDetail(detail, item) {
    const body = $('u-observation-body'),head = $('u-observation-head');
    body.replaceChildren();head.replaceChildren();
    const tr = document.createElement('tr');
    detail.columns.forEach(field => {
      const th = document.createElement('th');th.textContent = label(field);tr.appendChild(th);
    });head.appendChild(tr);
    for(const row of detail.observations.slice(0, 150)) {
      const r = document.createElement('tr');
      row.forEach(value => {const td=document.createElement('td');td.textContent =
        typeof value === 'number' ? fmt(value, 9) : String(value);r.appendChild(td);});
      body.appendChild(r);
    }
    text('u-observation-count', detail.observations.length +
      '개 완전관측치 · 화면에서 150개 표시 · CSV에는 전체 관측치 포함');
    text('u-detail-title', item.type+' / '+item.region.replace('|',' ')+' / '+item.year+
      (item.mode ? ' / '+item.mode : '')+' / n='+item.n);
    text('u-raw',detail.model.raw || detail.model.warning || '모형을 추정할 수 없습니다.');
    $('u-observation-export').disabled=false;
    $('u-observation-export').onclick=()=>download(
      'observations_'+state.model+'_'+item.id+'.csv',
      [detail.columns,...detail.observations]
    );
  }
  async function select(item) {
    const token=++run;
    selected=item;current=null;
    text('u-raw','상세 모형을 불러오는 중…');
    $('u-observation-export').disabled=true;
    if (!item) {
      showCoefficients(null,null);
      text('u-raw','해당 선택의 모형이 없습니다.');
      scatter(null,null);
      return;
    }
    try {
      const detail=await loadDetail(item);
      if (token!==run) return;
      current=detail;
      text('u-intercept',fmt(item.intercept));
      text('u-r2',fmt(item.r2));
      text('u-adjr2',fmt(item.adj_r2));
      text('u-pmodel',fmt(item.p_model,9));
      text('u-n',item.n);
      text('u-caption',item.type+' · '+item.region.replace('|',' ')+' · '+item.year);
      text('u-warning',item.warning || '해당 계수는 인과효과가 아니라 관측자료의 통계적 연관성입니다.');
      showCoefficients(item,detail);
      scatter(detail,item);
      observedDetail(detail,item);
    } catch(error) {
      if (token!==run) return;
      console.error(error);
      text('u-warning',error.message);
      text('u-raw','상세 모델 로딩 실패: '+error.message);
    }
  }
  function scoped(item) {
    // This is ONE OLS per year / disability / fiscal mode fitted over all
    // complete-case basic municipalities nationwide. Never mix it up with
    // 17 separate metropolitan OLS fits or local time-series regressions.
    const nationwide = state.indexScope === 'national_municipal';
    if (nationwide) {
      if (item.scope !== 'municipal' || item.region !== '전국') return false;
    } else if (state.indexScope !== 'all' && item.scope !== state.indexScope) {
      return false;
    }
    if (!state.allTypes && item.type!==state.dtype) return false;
    // Province restrictions must not exclude nationwide rows in the preset.
    if (!nationwide && !state.allRegions && state.province!=='전국' &&
        !item.region.includes(state.province) && item.region!=='전국') return false;
    if (spec().fiscal && item.mode!==state.fiscal) return false;
    const q=state.search.trim().toLocaleLowerCase();
    return !q || [item.year,item.region,item.type,item.scope,item.mode]
      .some(value=>String(value??'').toLocaleLowerCase().includes(q));
  }
  const sortKeys = {
    year: item=>String(item.year).replace('전기간','9999'),
    type: item=>item.type, scope: item=>item.scope, region: item=>item.region,
    n: item=>item.n, intercept: item=>item.intercept,
    r2: item=>item.r2,adj_r2: item=>item.adj_r2,p_model: item=>item.p_model
  };
  function order() {
    filtered = index.filter(scoped);
    filtered.sort((a,b)=>{
      const av=sortKeys[state.sort]?.(a),bv=sortKeys[state.sort]?.(b);
      const aNull=av==null,bNull=bv==null;
      if(aNull!==bNull) return aNull?1:-1;
      let compare=typeof av==='number'&&typeof bv==='number'?av-bv:
        String(av).localeCompare(String(bv),'ko',{numeric:true});
      return state.descending?-compare:compare;
    });
    const maxPage=Math.max(0,Math.ceil(filtered.length/pageSize)-1);
    state.page=Math.min(maxPage,state.page);
  }
  const col = (key,label,sortable=true) => ({key,label,sortable});
  function drawIndex() {
    order();
    const national = state.indexScope === 'national_municipal';
    text('u-index-definition', national
      ? '전국 기초지자체 전체를 하나의 표본으로 합친 OLS만 표시합니다. 행마다 연도(또는 전체기간) × 장애유형 × 재정자립도 기준별 1개 모형이며, 표본 n은 해당 조건에서 실제 사용된 기초지자체·연도 관측치 수입니다. 광역별 회귀나 기초지자체 개별 시계열은 포함하지 않습니다. 검색·정렬·CSV·Raw·관측치도 이 결과만 따릅니다.'
      : '표 분석 단위에 따라 전국·광역별 기초지자체 횡단면 OLS, 광역지자체 간 OLS, 기초지자체 시계열 OLS를 구분합니다. 전국 기초지자체 통합 OLS만 보려면 위 선택기를 변경하세요.');
    const columns=[
      col('year','시점'),col('type','장애유형'),col('scope','분석 단위'),
      col('region','광역/기초'),col('n','표본 n'),
      col('intercept','절편 β₀'),col('r2','R²'),col('adj_r2','수정 R²'),
      col('p_model','모형 F p값')
    ];
    const maxVariables = spec().fiscal ? spec().fields.length+1 : spec().fields.length;
    for(let i=0;i<maxVariables;i++) {
      columns.push(col('beta'+i,'β'+(i+1),false));
      columns.push(col('p'+i,'β'+(i+1)+' p값',false));
    }
    columns.push(col('action','상세',false));
    const head=$('u-index-head'),body=$('u-index-body');
    head.replaceChildren();body.replaceChildren();
    const tr=document.createElement('tr');
    columns.forEach(column=>{
      const th=document.createElement('th'),button=document.createElement('button');
      button.type='button';button.className='u-sort';
      button.textContent=column.label+(state.sort===column.key?(state.descending?' ▼':' ▲'):'');
      button.disabled=!column.sortable;
      if(column.sortable)button.onclick=()=>{
        if(state.sort===column.key)state.descending=!state.descending;
        else {state.sort=column.key;state.descending=false;}
        state.page=0;drawIndex();
      };
      th.append(button);tr.append(th);
    });head.append(tr);
    for(const item of filtered.slice(state.page*pageSize,(state.page+1)*pageSize)) {
      const row=document.createElement('tr');
      columns.forEach(column=>{
        const td=document.createElement('td');
        if(column.key==='action') {
          const button=document.createElement('button');
          button.className='outline-button';button.textContent='Raw·관측치';
          button.onclick=()=>{select(item);$('u-raw').scrollIntoView({behavior:'smooth',block:'center'});};
          td.append(button);
        } else {
          let value=item[column.key];
          if(column.key.startsWith('beta'))value=item.coefficients[Number(column.key.slice(4))];
          if(/^p\d+$/.test(column.key))value=item.pvalues[Number(column.key.slice(1))];
          td.textContent=typeof value==='number'?fmt(value,8):String(value??'—');
        }
        row.append(td);
      });body.append(row);
    }
    text('u-index-count',filtered.length+'개 모형 / '+(state.page+1)+' / '+
      Math.max(1,Math.ceil(filtered.length/pageSize))+' 페이지');
    $('u-prev').disabled=state.page===0;
    $('u-next').disabled=(state.page+1)*pageSize>=filtered.length;
  }
  function trendRows() {
    return spec().years.map(year => index.find(item =>
      item.year===year && item.type===state.dtype &&
      item.scope===state.scope && item.region===region() &&
      (!spec().fiscal || item.mode===state.fiscal)
    ) || null);
  }
  function trendDatasets(rows, metric) {
    const points=spec().years.map((year,i)=>{
      const item=rows[i];
      const val = item && valid(item) ? metric(item) : null;
      return {x:year,y:parse(val)};
    });
    return [{label:'연도별 OLS',data:points,borderColor:'#226b97',
      backgroundColor:'#226b97',spanGaps:false,tension:0.15,pointRadius:3}];
  }
  function drawTrends() {
    clearCharts(trendCharts);
    const rows=trendRows(),i=state.trendVar;
    const configs=[
      ['coef',m=>m.coefficients[i],'β (%p/X 1단위)'],
      ['intercept',m=>m.intercept,'절편 (%p)'],
      ['r2',m=>m.r2,'R²'],
      ['adjr2',m=>m.adj_r2,'수정 R²'],
      ['pcoef',m=>m.pvalues[i],'기울기 p값'],
      ['pmodel',m=>m.p_model,'모형 F p값']
    ];
    for(const [id,value,title] of configs) {
      if(!window.Chart) continue;
      const instance=new Chart($('u-trend-'+id),{type:'line',
        data:{datasets:trendDatasets(rows,value)},
        options:{responsive:true,maintainAspectRatio:false,parsing:false,
          scales:{x:{type:'linear',min:spec().years[0],max:spec().years.at(-1),
            ticks:{stepSize:1},title:{display:true,text:'연도'}},
            y:{title:{display:true,text:title}}},
          plugins:{tooltip:{callbacks:{label:c=>'실제 값: '+fmt(c.raw.y,10)}}}}
      });
      trendCharts.push(instance);
    }
    $('u-trend-export').onclick=()=>download(
      'yearly_regression_'+state.model+'_'+state.dtype+'.csv',
      [['연도','장애유형','광역/기초','재정자립도 기준','설명변수','기울기 β','절편 β₀','R²','수정 R²','기울기 p값','F검정 모형 p값','표본 n'],
       ...spec().years.map((year,j)=>{
         const m=rows[j];
         return [year,state.dtype,region(),state.fiscal,fields()[i],
           valid(m)?m.coefficients[i]:null,valid(m)?m.intercept:null,
           valid(m)?m.r2:null,valid(m)?m.adj_r2:null,
           valid(m)?m.pvalues[i]:null,valid(m)?m.p_model:null,m?.n??null];
       })]
    );
  }
  async function render(changeModel=false) {
    const token=++run;
    updateControls();
    text('u-warning','OLS 인덱스를 불러오는 중입니다.');
    try {
      const items=await load('data/unified_index_'+state.model+'.json.gz');
      if(token!==run)return;
      index=items;
      drawIndex();
      drawTrends();
      const chosen=findSelected();
      await select(chosen);
      if(changeModel) {
        const url=new URL(location.href);url.searchParams.set('model',state.model);
        history.replaceState(null,'',url);
        window.SidebarNav?.updateActive();
      }
    } catch(error) {
      if(token!==run)return;
      console.error(error);
      text('u-warning','회귀 인덱스를 불러오지 못했습니다: '+error.message+
        ' · python build.py로 데이터가 생성됐는지 확인하세요.');
    }
  }
  try {
    manifest=await load('data/unified_manifest.json');
    const mainMeta=await load('data/meta.json');
    manifest.districts=mainMeta.districts;
    if(initial && manifest.models[initial])state.model=initial;
    for(const [id,value] of Object.entries(manifest.models))opt($('u-model'),id,value.label);
    manifest.types.forEach(v=>opt($('u-type'),v,v));
    opt($('u-province'),'전국','전국');
    manifest.provinces.forEach(v=>opt($('u-province'),v,v));
    updateDistrict();
    $('u-model').onchange=e=>{state.model=e.target.value;state.year=2022;state.trendVar=0;state.page=0;render(true);};
    $('u-type').onchange=e=>{state.dtype=e.target.value;state.page=0;render();};
    $('u-scope').onchange=e=>{
      state.scope=e.target.value;
      if(state.scope==='local_history'&&state.province==='전국') {
        state.province=manifest.provinces[0];$('u-province').value=state.province;
      }
      updateDistrict();render();
    };
    $('u-province').onchange=e=>{state.province=e.target.value;updateDistrict();render();};
    $('u-district').onchange=e=>{state.district=e.target.value;render();};
    $('u-mode').onchange=e=>{state.fiscal=e.target.value;render();};
    $('u-year').oninput=e=>{state.year=Number(e.target.value);render();};
    $('u-all-years').onchange=e=>{state.pooled=e.target.checked;render();};
    $('u-trend-var').onchange=e=>{state.trendVar=Number(e.target.value);drawTrends();};
    $('u-search').oninput=e=>{state.search=e.target.value;state.page=0;drawIndex();};
    $('u-index-scope').onchange=e=>{state.indexScope=e.target.value;state.page=0;drawIndex();};
    $('u-all-types').onchange=e=>{state.allTypes=e.target.checked;state.page=0;drawIndex();};
    $('u-all-regions').onchange=e=>{state.allRegions=e.target.checked;state.page=0;drawIndex();};
    $('u-prev').onclick=()=>{state.page--;drawIndex();};
    $('u-next').onclick=()=>{state.page++;drawIndex();};
    $('u-index-export').onclick=()=> {
      const width=spec().fiscal?spec().fields.length+1:spec().fields.length;
      download('regression_index_'+state.model+'.csv',
        [['시점','장애유형','분석 단위','광역/기초','재정자립도 기준','표본 n',
          '절편 β₀','R²','수정 R²','모형 F p값',
          ...Array.from({length:width},(_,i)=>['β'+(i+1),'β'+(i+1)+' p값']).flat(),'상세 파일'],
          ...filtered.map(item=>[item.year,item.type,item.scope,item.region,item.mode,
            item.n,item.intercept,item.r2,item.adj_r2,item.p_model,
            ...item.coefficients.flatMap((beta,i)=>[beta,item.pvalues[i]]),item.shard])]);
    };
    render();
  } catch(error) {
    console.error(error);
    text('u-warning','초기화 실패: '+error.message);
  }
})();
