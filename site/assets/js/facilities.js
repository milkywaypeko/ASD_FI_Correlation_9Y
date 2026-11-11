'use strict';
/* Static-only facility-density explorer: statistical values come from Python. */
(async () => {
  const $ = id => document.getElementById(id);
  const set = (id, value) => { $(id).textContent = String(value); };
  const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));
  const fmt = (value, digits=7) => finite(value) ?
    Number(value).toLocaleString('ko-KR', {maximumFractionDigits:digits}) : '—';
  const fmtP = value => !finite(value) ? '—' : Number(value) === 0 ?
    '< 1e-323 (정밀도 한계)' : Math.abs(Number(value)) < 1e-9 ?
      Number(value).toExponential(3) : fmt(value, 9);
  const fmtCI = (low, high) => `${fmt(low, 9)} ~ ${fmt(high, 9)}`;
  const cache = new Map();
  const load = path => {
    if (!cache.has(path)) cache.set(path, fetch(path).then(async response => {
      if (!response.ok) throw Error(`${path}: HTTP ${response.status}`);
      if (!path.endsWith('.gz')) return response.json();
      if (!('DecompressionStream' in window)) throw Error('gzip 지원 브라우저가 필요합니다.');
      return new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();
    }).catch(error => {cache.delete(path);throw error;}));
    return cache.get(path);
  };
  const quote = value => '"' + String(value ?? '').replaceAll('"','""') + '"';
  function csvDownload(name, rows) {
    const blob = new Blob(['\uFEFF' + rows.map(row => row.map(quote).join(',')).join('\r\n')],
                          {type:'text/csv;charset=utf-8'});
    const url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  const state = {
    model:'facility_general',type:'자폐성',scope:'municipal',province:'전국',district:'',
    year:2022,pooled:false,search:'',indexScope:'all',allTypes:false,allRegions:false,
    sort:'year',descending:true,page:0
  };
  let manifest, index=[], filtered=[], selected=null;
  let mainChart=null,trendCharts=[],run=0,detailRun=0;
  const pageSize=30;
  const model=()=>manifest.models[state.model];
  const region=()=>state.scope==='provincial'?'전국':
    state.scope==='local_history'?`${state.province}|${state.district}`:state.province;
  const period=()=>state.pooled||state.scope==='local_history'?'전기간':state.year;
  const find=(type=state.type,year=period())=>index.find(item=>
    item.type===type && item.scope===state.scope && item.region===region() &&
    String(item.year)===String(year));
  const valid=item=>item && finite(item.intercept);
  const option=(select,value,label)=>select.add(new Option(label,value));
  const trendYears=()=>model().years;
  function refreshDistrict() {
    const sel=$('f-district'),prior=state.district;
    sel.replaceChildren();
    if (state.scope==='local_history' && state.province==='전국') state.province=manifest.provinces[0];
    if (state.province==='전국') {state.district='';sel.disabled=true;return;}
    const districts=(manifest.districts||{})[state.province]||[];
    for (const district of districts) option(sel,district,district);
    state.district=districts.includes(prior)?prior:(districts[0]||'');
    sel.value=state.district;
    sel.disabled=state.scope!=='local_history';
  }
  function refreshControls() {
    const years=trendYears();
    if (!years.includes(state.year))state.year=years[years.length-1];
    refreshDistrict();
    $('f-model').value=state.model;
    $('f-type').value=state.type;
    $('f-scope').value=state.scope;
    $('f-province').value=state.province;
    $('f-province').disabled=state.scope==='provincial';
    $('f-pooled').checked=state.pooled||state.scope==='local_history';
    $('f-pooled').disabled=state.scope==='local_history';
    $('f-year').min=String(years[0]);$('f-year').max=String(years[years.length-1]);
    $('f-year').value=String(state.year);
    $('f-year').disabled=state.pooled||state.scope==='local_history';
    set('f-year-label',period()==='전기간'?`${years[0]}~${years.at(-1)}년 통합`:`${state.year}년 1분기`);
    set('f-year-start',years[0]);set('f-year-end',years.at(-1));
    set('f-period-title',`${years[0]} — ${years.at(-1)}`);
    $('f-special-note').hidden=state.model!=='facility_psychiatric';
    $('f-total-note').hidden=state.model!=='facility_total';
  }
  function resetRaw() {
    $('f-ols-details').open=true;
    $('f-scipy-details').open=true;
    $('f-observations-details').open=false;
    $('f-scipy-observations-details').open=false;
  }
  function clearCharts() {
    if(mainChart){mainChart.destroy();mainChart=null;}
    for(const chart of trendCharts)chart.destroy();
    trendCharts=[];
  }
  function clearMainChart(){if(mainChart){mainChart.destroy();mainChart=null;}}
  function clearTrends(){for(const chart of trendCharts)chart.destroy();trendCharts=[];}
  function putCell(row,value,formatter=String) {
    const td=document.createElement('td');td.textContent=formatter(value);row.append(td);return td;
  }
  function drawCoefficients(item,detail) {
    const tbody=$('f-coeff-body');tbody.replaceChildren();
    if(!detail)return;
    const field=model().field,ols=detail.model.coefficients?.[field];
    const scipy=detail.correlations?.scipy?.[field];
    const tr=document.createElement('tr');
    [model().category,fmt(ols?.coef,9),fmtP(ols?.p),fmtCI(ols?.ci?.[0],ols?.ci?.[1]),
     fmt(ols?.se,9),fmt(scipy?.statistic,9),fmtP(scipy?.pvalue),
     fmtCI(scipy?.confidence_interval?.low,scipy?.confidence_interval?.high),item.n]
      .forEach(value=>putCell(tr,value));
    tbody.append(tr);
  }
  function renderObservations(detail,item) {
    const head=$('f-observation-head'),body=$('f-observation-body');
    head.replaceChildren();body.replaceChildren();
    const tr=document.createElement('tr');
    for(const field of detail.columns){const th=document.createElement('th');th.textContent=field;tr.append(th);}
    head.append(tr);
    for(const values of detail.observations.slice(0,150)) {
      const r=document.createElement('tr');
      values.forEach(value=>putCell(r,value, v=>typeof v==='number'?fmt(v,10):String(v??'')));
      body.append(r);
    }
    set('f-observation-count',`${detail.observations.length}개 완전관측치 · 화면에 최대 150개 표시 · CSV에는 전체 표본 포함`);
    $('f-observation-export').disabled=false;
    $('f-observation-export').onclick=()=>csvDownload(
      `facility_observations_${state.model}_${item.type}_${item.scope}_${item.year}.csv`,
      [detail.columns,...detail.observations]);
  }
  function showSciPy(detail,item) {
    const field=model().field,s=detail.correlations?.scipy?.[field];
    const tbody=$('f-scipy-body'),pairs=$('f-scipy-observation-body');
    tbody.replaceChildren();pairs.replaceChildren();
    if(!s)throw Error(`SciPy 결과 없음: ${field}`);
    const row=document.createElement('tr');
    [model().category,fmt(s.statistic,10),fmtP(s.pvalue),
     fmt(s.confidence_interval?.low,10),fmt(s.confidence_interval?.high,10),s.n,
     s.reason||(s.warnings?.length?s.warnings.join(' / '):'정상')]
       .forEach(v=>putCell(row,v));
    tbody.append(row);
    set('f-scipy-raw',[
      'scipy.stats.pearsonr(X, Y, alternative="two-sided")',
      `SciPy version: ${detail.correlations.scipy_version}`,
      `선택 모형: ${item.type} / ${model().category} / ${item.region} / ${item.year}`,
      `X: ${model().category} (개소/인구 10만 명)`,
      `Y: ${item.type} 장애인 등록률 (%)`,
      `완전관측치 n: ${s.n}`,
      `SciPy 반환 객체: ${s.raw??'계산 불가'}`,
      `95% 신뢰구간 반환 객체: ${s.raw_confidence_interval??'계산 불가'}`,
      `statistic (r): ${s.statistic??'null'}`,
      `pvalue (two-sided): ${fmtP(s.pvalue)}`,
      `confidence_interval(0.95): [${s.confidence_interval?.low??'null'}, ${s.confidence_interval?.high??'null'}]`,
      `경고: ${s.warnings?.length?s.warnings.join(' / '):'없음'}`,
      `계산 실패 사유: ${s.reason??'없음'}`
    ].join('\n'));
    const columns=['year','province','district',field,'registered_rate_percent'];
    const observations=detail.observations.map(r=>[r[0],r[1],r[2],r[4],r[3]]);
    for(const values of observations.slice(0,150)){
      const tr=document.createElement('tr');
      values.forEach(v=>putCell(tr,v,x=>typeof x==='number'?fmt(x,10):String(x??'')));
      pairs.append(tr);
    }
    set('f-scipy-observation-count',`${observations.length}개 X·Y 쌍 · 화면에 최대 150개 표시 · CSV에는 전체 포함`);
    $('f-scipy-export').disabled=false;
    $('f-scipy-export').onclick=()=>csvDownload(
      `scipy_pearson_pairs_${state.model}_${item.type}_${item.year}.csv`,
      [columns,...observations]);
  }
  function drawScatter(detail,item) {
    clearMainChart();
    if(!window.Chart||!valid(item)||!detail.observations.length)return;
    const points=detail.observations.map(r=>({x:r[4],y:r[3],label:`${r[1]} ${r[2]} (${r[0]})`}));
    const xs=points.map(p=>p.x);const lo=Math.min(...xs),hi=Math.max(...xs);
    const line=[{x:lo,y:item.intercept+item.coefficients[0]*lo},
                {x:hi,y:item.intercept+item.coefficients[0]*hi}];
    mainChart=new Chart($('f-scatter'),{
      type:'scatter',data:{datasets:[
        {label:'실제 등록률(%)',data:points,backgroundColor:'#159ba0',pointRadius:3},
        {label:'단순회귀 적합선',data:line,type:'line',showLine:true,pointRadius:0,
         borderColor:'#f28c28',borderWidth:2}
      ]},options:{responsive:true,maintainAspectRatio:false,parsing:false,
        scales:{x:{type:'linear',title:{display:true,text:`${model().category} (개소/인구 10만 명)`}},
                y:{title:{display:true,text:'장애인 등록률 (%)'}}},
        plugins:{tooltip:{callbacks:{label:context=>{
          const raw=context.raw;
          return `${raw.label||context.dataset.label}: X=${fmt(raw.x,7)}, Y=${fmt(raw.y,7)}`;
        }}}}}
    });
  }
  function trendRecords() {
    const r=region();
    return trendYears().map(year=>index.find(item=>item.year===year &&
      item.type===state.type && item.scope===state.scope && item.region===r)||null);
  }
  function drawTrends(detail=null) {
    clearTrends();
    const isHistory=state.scope==='local_history';
    $('f-annual-trends').hidden=isHistory;
    $('f-local-trend-wrap').hidden=!isHistory;
    if(isHistory){
      set('f-trend-note','개별 기초지자체에는 연도별 별도 단면 OLS가 없습니다. 아래는 해당 지역의 연도별 X·Y 실제 관측값이며, 기간 통합 OLS는 별도로 표시합니다.');
      $('f-trend-export').disabled=!detail;
      if(!detail)return;
      const rows=[...detail.observations].sort((a,b)=>a[0]-b[0]);
      $('f-trend-export').onclick=()=>csvDownload(`facility_local_history_${state.model}_${state.type}_${state.district}.csv`,
        [['year','province','district','facility_density_per_100k','registered_rate_percent','facility_count_q1','population'],
         ...rows.map(r=>[r[0],r[1],r[2],r[4],r[3],r[r.length-2],r[r.length-1]])]);
      if(!window.Chart)return;
      trendCharts.push(new Chart($('f-local-trend'),{type:'line',data:{labels:rows.map(r=>r[0]),datasets:[
        {label:'요양기관 수 (인구 10만 명당)',data:rows.map(r=>r[4]),yAxisID:'density',borderColor:'#159ba0',spanGaps:false},
        {label:'등록률 (%)',data:rows.map(r=>r[3]),yAxisID:'rate',borderColor:'#f28c28',spanGaps:false}
      ]},options:{responsive:true,maintainAspectRatio:false,
        scales:{density:{type:'linear',position:'left',title:{display:true,text:'기관 수/10만 명'}},
                rate:{type:'linear',position:'right',grid:{drawOnChartArea:false},title:{display:true,text:'등록률 (%)'}}}}}));
      return;
    }
    set('f-trend-note','동일한 분석 단위에 대해 연도별로 별도 OLS를 적합했습니다. 추정 불가 시점은 0으로 바꾸거나 보간하지 않습니다.');
    const rows=trendRecords(),years=trendYears();
    $('f-trend-export').disabled=false;
    $('f-trend-export').onclick=()=>csvDownload(`facility_trend_${state.model}_${state.type}_${state.scope}.csv`,[
      ['연도','장애유형','요양기관','scope','region','n','기울기 β₁','OLS β₁ p값','절편 β₀',
       'R²','수정 R²','모형 F p값','SciPy r','SciPy p값'],
      ...years.map((year,i)=>{const m=rows[i];return [year,state.type,model().category,state.scope,region(),
        m?.n??null,m?.coefficients?.[0]??null,m?.pvalues?.[0]??null,m?.intercept??null,
        m?.r2??null,m?.adj_r2??null,m?.p_model??null,m?.correlations?.[0]??null,
        m?.correlation_pvalues?.[0]??null];})
    ]);
    if(!window.Chart)return;
    const metrics=[
      ['coef',m=>m.coefficients?.[0],'β₁ (%p/개소·10만 명)'],
      ['intercept',m=>m.intercept,'절편 β₀ (%p)'],
      ['r2',m=>m.r2,'R²'],
      ['adjr2',m=>m.adj_r2,'수정 R²'],
      ['pcoef',m=>m.pvalues?.[0],'OLS 기울기 p값'],
      ['pmodel',m=>m.p_model,'모형 F검정 p값'],
      ['corr',m=>m.correlations?.[0],'SciPy 피어슨 r']
    ];
    for(const [key,getValue,label] of metrics) {
      const points=years.map((year,i)=>({x:year,y:rows[i]&&finite(getValue(rows[i]))?getValue(rows[i]):null}));
      trendCharts.push(new Chart($('f-trend-'+key),{
        type:'line',data:{datasets:[{label,data:points,showLine:true,spanGaps:false,
          borderColor:'#159ba0',backgroundColor:'#159ba0',pointRadius:3}]},
        options:{responsive:true,maintainAspectRatio:false,parsing:false,
          scales:{x:{type:'linear',min:years[0],max:years.at(-1),ticks:{stepSize:1},title:{display:true,text:'연도'}},
                  y:{title:{display:true,text:label}}},
          plugins:{tooltip:{callbacks:{label:c=>'실제 값: '+(key==='pcoef'||key==='pmodel'?fmtP(c.raw.y):fmt(c.raw.y,9))}}}}
      }));
    }
  }
  function scoped(item) {
    const nationwide=state.indexScope==='national_municipal';
    if(nationwide){if(item.scope!=='municipal'||item.region!=='전국')return false;}
    else if(state.indexScope!=='all' && item.scope!==state.indexScope)return false;
    if(!state.allTypes && item.type!==state.type)return false;
    if(!nationwide && !state.allRegions && state.province!=='전국' &&
       item.region!=='전국' && !item.region.includes(state.province))return false;
    const q=state.search.trim().toLocaleLowerCase();
    return !q || [item.year,item.type,item.scope,item.region,model().category]
      .some(v=>String(v??'').toLocaleLowerCase().includes(q));
  }
  const sortValue=(item,key)=>({
    year:()=>item.year==='전기간'?'9999':String(item.year),type:()=>item.type,
    scope:()=>item.scope,region:()=>item.region,n:()=>item.n,
    slope:()=>item.coefficients?.[0],pvalue:()=>item.pvalues?.[0],
    corr:()=>item.correlations?.[0],corrP:()=>item.correlation_pvalues?.[0],
    intercept:()=>item.intercept,r2:()=>item.r2,adj_r2:()=>item.adj_r2,p_model:()=>item.p_model
  })[key]?.();
  function sortIndex() {
    filtered=index.filter(scoped);
    filtered.sort((a,b)=>{
      const av=sortValue(a,state.sort),bv=sortValue(b,state.sort);
      if(av==null&&bv!=null)return 1;
      if(av!=null&&bv==null)return -1;
      const order=typeof av==='number'&&typeof bv==='number'?av-bv:
        String(av??'').localeCompare(String(bv??''),'ko',{numeric:true});
      return state.descending?-order:order;
    });
    state.page=Math.min(state.page,Math.max(0,Math.ceil(filtered.length/pageSize)-1));
  }
  const cols=[
    ['year','시점'],['type','장애유형'],['scope','분석 단위'],['region','광역/기초'],
    ['n','표본 n'],['slope','OLS β₁ 기울기'],['pvalue','OLS β₁ p값 (양측)'],
    ['corr','SciPy r'],['corrP','SciPy r p값'],['intercept','절편 β₀'],
    ['r2','R²'],['adj_r2','수정 R²'],['p_model','모형 F p값']
  ];
  function drawIndex() {
    sortIndex();
    const nationwide=state.indexScope==='national_municipal';
    set('f-index-definition',nationwide?
      '전국 기초지자체의 완전관측치를 모아 연도·장애유형별 1개 OLS만 적합한 결과입니다. 광역별 OLS나 개별 지자체 시계열은 포함하지 않습니다.':
      '전국·광역별 기초지자체 비교, 광역지자체 간 비교, 개별 기초지자체 시계열을 구분합니다. 전국 통합 OLS만 보려면 표 분석 단위를 변경하세요.');
    const head=$('f-index-head'),body=$('f-index-body');head.replaceChildren();body.replaceChildren();
    const tr=document.createElement('tr');
    for(const [key,title] of cols) {
      const th=document.createElement('th'),button=document.createElement('button');
      button.type='button';button.className='u-sort';
      button.textContent=title+(state.sort===key?(state.descending?' ▼':' ▲'):'');
      button.onclick=()=>{if(state.sort===key)state.descending=!state.descending;
        else{state.sort=key;state.descending=false;}state.page=0;drawIndex();};
      th.append(button);tr.append(th);
    }
    const th=document.createElement('th');th.textContent='상세';tr.append(th);head.append(tr);
    for(const item of filtered.slice(state.page*pageSize,(state.page+1)*pageSize)) {
      const row=document.createElement('tr');
      row.dataset.selected=String(selected?.id===item.id);
      for(const [key] of cols) {
        const v=sortValue(item,key);
        putCell(row,v,v=>v==null?'—':typeof v==='number'?
          ((key==='pvalue'||key==='corrP'||key==='p_model')?fmtP(v):fmt(v,8)):String(v));
      }
      const td=document.createElement('td'),button=document.createElement('button');
      button.type='button';button.className='outline-button';button.textContent='Raw·관측치';
      button.onclick=()=>selectIndexItem(item);
      td.append(button);row.append(td);body.append(row);
    }
    set('f-index-count',`${filtered.length}개 모형 / ${state.page+1} / ${Math.max(1,Math.ceil(filtered.length/pageSize))} 페이지`);
    $('f-prev').disabled=state.page===0;
    $('f-next').disabled=(state.page+1)*pageSize>=filtered.length;
    $('f-index-export').disabled=filtered.length===0;
  }
  function exportIndex() {
    csvDownload(`facility_index_${state.model}_filtered.csv`,[
      ['시점','장애유형','분석단위','지역','표본 n','OLS β₁','OLS β₁ p값',
       'SciPy r','SciPy r p값','절편 β₀','R²','수정 R²','모형 F p값','상세 파일'],
      ...filtered.map(item=>[
        item.year,item.type,item.scope,item.region,item.n,item.coefficients?.[0]??null,
        item.pvalues?.[0]??null,item.correlations?.[0]??null,item.correlation_pvalues?.[0]??null,
        item.intercept,item.r2,item.adj_r2,item.p_model,item.shard
      ])
    ]);
  }
  function clearSelected(message) {
    selected=null;
    clearMainChart();
    for(const id of ['f-n','f-slope','f-pvalue','f-intercept','f-r2','f-adjr2',
                     'f-pmodel','f-pearson','f-pearson-p'])set(id,'—');
    set('f-ols-raw',message);set('f-scipy-raw',message);
    $('f-coeff-body').replaceChildren();$('f-scipy-body').replaceChildren();
    $('f-observation-head').replaceChildren();$('f-observation-body').replaceChildren();
    $('f-scipy-observation-body').replaceChildren();
    $('f-observation-export').disabled=true;$('f-scipy-export').disabled=true;
    set('f-detail-title',message);
  }
  async function select(item) {
    const token=++detailRun;
    resetRaw();
    clearSelected('상세 모형을 불러오는 중…');
    selected=item;
    if(!item){clearSelected('해당 조건에 계산된 모형이 없습니다.');return;}
    set('f-caption',`${item.type} · ${model().category} · ${item.region.replace('|',' ')} · ${item.year}`);
    set('f-detail-title',`${item.type} / ${item.region.replace('|',' ')} / ${item.year} / n=${item.n}`);
    try {
      const packet=await load(item.shard);
      if(token!==detailRun)return;
      const detail=packet[item.id];
      if(!detail || detail.model.n!==item.n || detail.observations.length!==item.n ||
         detail.model.intercept!==item.intercept || detail.model.r2!==item.r2 ||
         detail.model.adj_r2!==item.adj_r2 || detail.model.p_model!==item.p_model ||
         (item.intercept!==null && detail.model.coefficients?.[model().field]?.coef!==item.coefficients?.[0]))
        throw Error('회귀 인덱스와 원시 통계 또는 표본 수가 일치하지 않습니다.');
      set('f-n',item.n);set('f-slope',fmt(item.coefficients?.[0],9));
      set('f-pvalue',fmtP(item.pvalues?.[0]));set('f-intercept',fmt(item.intercept,9));
      set('f-r2',fmt(item.r2,9));set('f-adjr2',fmt(item.adj_r2,9));
      set('f-pmodel',fmtP(item.p_model));set('f-pearson',fmt(item.correlations?.[0],9));
      set('f-pearson-p',fmtP(item.correlation_pvalues?.[0]));
      const message=item.warning || `X: ${model().category} 개소/인구 10만 명 · Y: ${item.type} 장애인 등록률(%) · 비가중 단순회귀로 인과관계가 아닙니다.`;
      set('f-status',message);
      set('f-ols-raw',detail.model.raw||detail.model.warning||'모형을 추정할 수 없습니다.');
      drawCoefficients(item,detail);showSciPy(detail,item);renderObservations(detail,item);
      drawScatter(detail,item);
      if(state.scope==='local_history')drawTrends(detail);
      drawIndex();
    } catch(error) {
      if(token!==detailRun)return;
      console.error(error);clearSelected('상세 로딩 실패: '+error.message);
      set('f-status','상세 로딩 실패: '+error.message);
    }
  }
  async function selectIndexItem(item) {
    state.type=item.type;state.scope=item.scope;
    if(item.scope==='local_history'){
      const parts=item.region.split('|');state.province=parts[0];state.district=parts[1];
      state.pooled=true;
    }else if(item.scope==='provincial'){
      state.province='전국';state.district='';state.pooled=item.year==='전기간';
    }else{
      state.province=item.region;state.district='';state.pooled=item.year==='전기간';
    }
    if(typeof item.year==='number')state.year=item.year;
    refreshControls();drawTrends();await select(item);
    $('f-detail-header').scrollIntoView({behavior:'smooth',block:'start'});
  }
  async function render(reloadIndex=false) {
    const token=++run;
    refreshControls();
    set('f-status','OLS 인덱스를 불러오는 중입니다.');
    try {
      if(reloadIndex)index=await load(`data/facility_index_${state.model}.json.gz`);
      if(token!==run)return;
      if(!index.length)throw Error('계산된 회귀 인덱스가 없습니다.');
      drawIndex();
      drawTrends();
      await select(find());
    }catch(error) {
      if(token!==run)return;
      console.error(error);clearSelected('회귀 인덱스 로딩 실패: '+error.message);
      set('f-status','회귀 인덱스를 불러오지 못했습니다: '+error.message+' · python build.py로 데이터를 생성하세요.');
    }
  }
  try {
    manifest=await load('data/facility_manifest.json');
    const query=new URLSearchParams(location.search);
    if(manifest.models[query.get('model')])state.model=query.get('model');
    if(manifest.types.includes(query.get('type')))state.type=query.get('type');
    for(const [id,item] of Object.entries(manifest.models))option($('f-model'),id,item.label);
    for(const name of manifest.types)option($('f-type'),name,name);
    option($('f-province'),'전국','전국');
    for(const name of manifest.provinces)option($('f-province'),name,name);
    refreshControls();
    $('f-model').onchange=e=>{
      state.model=e.target.value;state.year=2022;state.page=0;
      const url=new URL(location.href);url.searchParams.set('model',state.model);
      history.replaceState(null,'',url);window.SidebarNav?.updateActive();render(true);
    };
    $('f-type').onchange=e=>{state.type=e.target.value;state.page=0;render();};
    $('f-scope').onchange=e=>{state.scope=e.target.value;
      if(state.scope==='local_history')state.pooled=true;
      state.page=0;render();};
    $('f-province').onchange=e=>{state.province=e.target.value;state.page=0;render();};
    $('f-district').onchange=e=>{state.district=e.target.value;render();};
    $('f-year').oninput=e=>{state.year=Number(e.target.value);render();};
    $('f-pooled').onchange=e=>{state.pooled=e.target.checked;render();};
    $('f-search').oninput=e=>{state.search=e.target.value;state.page=0;drawIndex();};
    $('f-index-scope').onchange=e=>{state.indexScope=e.target.value;state.page=0;drawIndex();};
    $('f-all-types').onchange=e=>{state.allTypes=e.target.checked;state.page=0;drawIndex();};
    $('f-all-regions').onchange=e=>{state.allRegions=e.target.checked;state.page=0;drawIndex();};
    $('f-prev').onclick=()=>{state.page--;drawIndex();};
    $('f-next').onclick=()=>{state.page++;drawIndex();};
    $('f-index-export').onclick=exportIndex;
    await render(true);
  } catch(error) {
    console.error(error);set('f-status','초기화 실패: '+error.message);
  }
})();
