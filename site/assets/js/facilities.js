'use strict';
/* Facility density and simple OLS are computed in Python; the browser only displays JSON. */
(async () => {
  const $ = id => document.getElementById(id);
  const fmt = (v, decimals=6) => v == null || !Number.isFinite(Number(v)) ? '—' :
    Number(v).toLocaleString('ko-KR', {maximumFractionDigits: decimals});
  const fmtP = v => v == null ? '—' : v === 0 ? '< 1e-323 (정밀도 한계)' :
    Number(v) < 1e-8 ? Number(v).toExponential(3) : fmt(v, 9);
  const set = (id, value) => { $(id).textContent = String(value); };
  const cache = new Map();
  function load(path) {
    if (!cache.has(path)) cache.set(path, fetch(path).then(async response => {
      if (!response.ok) throw Error(`${path}: HTTP ${response.status}`);
      if (!path.endsWith('.gz')) return response.json();
      if (!('DecompressionStream' in window)) throw Error('gzip을 지원하는 브라우저가 필요합니다.');
      return new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();
    }).catch(e => {cache.delete(path);throw e;}));
    return cache.get(path);
  }
  const quote = v => '"' + String(v ?? '').replaceAll('"', '""') + '"';
  function csvDownload(name, rows) {
    const blob = new Blob(['\uFEFF' + rows.map(row => row.map(quote).join(',')).join('\r\n')],
      {type: 'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url), 1000);
  }
  const state = {model:'facility_general',type:'자폐성',scope:'municipal',province:'전국',year:2022,pooled:false};
  let manifest, index = [], selected = null, charts = [], sequence=0;
  const entry = () => manifest.models[state.model];
  const period = () => state.pooled ? '전기간' : state.year;
  const region = () => state.scope === 'provincial' ? '전국' : state.province;
  const find = (type=state.type, year=period()) => index.find(row => row.type === type &&
    row.scope === state.scope && row.region === region() && String(row.year) === String(year));
  function clearCharts() { charts.forEach(c=>c.destroy());charts=[]; }
  function selectOptions(element, options, preserve) {
    element.replaceChildren();
    for (const [value,label] of options) element.add(new Option(label,value));
    if (options.some(([v])=>v === preserve)) element.value=preserve;
    return element.value;
  }
  function refreshControls() {
    const years=entry().years;
    if (!years.includes(state.year))state.year=years[years.length-1];
    state.year=Number(selectOptions($('f-year'),years.map(y=>[String(y),`${y}년 1분기`]),String(state.year)));
    $('f-year').disabled=state.pooled;
    $('f-pooled').checked=state.pooled;
    $('f-province').disabled=state.scope === 'provincial';
    $('f-model').value=state.model;
    $('f-type').value=state.type;
    $('f-scope').value=state.scope;
    $('f-province').value=state.province;
    $('f-special-note').hidden=state.model !== 'facility_psychiatric';
  }
  function renderObservations(detail) {
    const head=$('f-observation-head'),body=$('f-observation-body');
    head.replaceChildren();body.replaceChildren();
    const tr=document.createElement('tr');
    for (const label of detail.columns) {const th=document.createElement('th');th.textContent=label;tr.append(th);}
    head.append(tr);
    for (const obs of detail.observations.slice(0,150)) {
      const tr=document.createElement('tr');
      for (const value of obs) {const td=document.createElement('td');td.textContent=typeof value==='number'?fmt(value,10):String(value??'');tr.append(td);}
      body.append(tr);
    }
    set('f-observation-count',`${detail.observations.length}개 표본 중 화면 150개까지 표시 · CSV에는 전체 포함`);
    $('f-observation-export').disabled=false;
    $('f-observation-export').onclick=()=>csvDownload(`facility_observations_${state.model}_${state.type}_${period()}.csv`,[detail.columns,...detail.observations]);
  }
  function graph(detail, item) {
    clearCharts();
    if (!window.Chart || !item || item.intercept==null) return;
    const obs=detail.observations;
    if (!obs.length)return;
    const pts=obs.map(row=>({x:row[4],y:row[3]}));
    const xs=pts.map(p=>p.x),lo=Math.min(...xs),hi=Math.max(...xs);
    const field=entry().field;
    const slope=item.coefficients[0];
    const line=[{x:lo,y:item.intercept+slope*lo},{x:hi,y:item.intercept+slope*hi}];
    charts.push(new Chart($('f-scatter'),{
      type:'scatter',data:{datasets:[
        {label:'실제 장애인 등록률(%)',data:pts,pointRadius:3,backgroundColor:'#159ba0'},
        {label:'OLS 단순회귀 적합선',data:line,type:'line',showLine:true,pointRadius:0,borderColor:'#f28c28',borderWidth:2}
      ]},options:{responsive:true,maintainAspectRatio:false,parsing:false,
        scales:{x:{type:'linear',title:{display:true,text:`${entry().category} (인구 10만 명당 개소)`}},
                y:{title:{display:true,text:'장애인 등록률 (%)'}}}}}
    ));
  }
  function graphTrends() {
    const years=entry().years,records=years.map(y=>find(state.type,y));
    $('f-trend-export').disabled=false;
    $('f-trend-export').onclick=()=>csvDownload(`facility_trend_${state.model}_${state.type}.csv`,[
      ['연도','장애유형','요양기관','scope','region','n','OLS slope','OLS slope p','R2','adj R2','Pearson r','SciPy p'],
      ...years.map((y,i)=>[y,state.type,entry().category,state.scope,region(),records[i]?.n??null,
        records[i]?.coefficients?.[0]??null,records[i]?.pvalues?.[0]??null,
        records[i]?.r2??null,records[i]?.adj_r2??null,records[i]?.correlations?.[0]??null,records[i]?.correlation_pvalues?.[0]??null])
    ]);
    if (!window.Chart)return;
    // A separate y-axis is required because slope (percentage points per
    // facility/100k) and Pearson r (unitless) are not commensurate.
    const data=years.map((y,i)=>({year:y,slope:records[i]?.coefficients?.[0]??null,r:records[i]?.correlations?.[0]??null}));
    charts.push(new Chart($('f-trend'),{
      type:'line',data:{labels:years,datasets:[
        {label:'OLS 기울기 β₁ (%p/개소·10만명)',data:data.map(d=>d.slope),yAxisID:'slope',spanGaps:false,borderColor:'#f28c28'},
        {label:'SciPy 피어슨 r',data:data.map(d=>d.r),yAxisID:'r',spanGaps:false,borderColor:'#159ba0'}
      ]},options:{responsive:true,maintainAspectRatio:false,
        scales:{slope:{type:'linear',position:'left',title:{display:true,text:'OLS 기울기 β₁'}},
                r:{type:'linear',position:'right',min:-1,max:1,grid:{drawOnChartArea:false},title:{display:true,text:'Pearson r'}}}}}
    ));
  }
  function resetRaw() {
    $('f-ols-details').open=true;$('f-scipy-details').open=true;
    $('f-observations-details').open=false;
  }
  async function render(reloadIndex=false) {
    const token=++sequence;
    refreshControls();resetRaw();
    $('f-observation-export').disabled=true;
    set('f-status','OLS 결과를 불러오는 중입니다.');
    try {
      if (reloadIndex) index=await load(`data/facility_index_${state.model}.json.gz`);
      if (token!==sequence)return;
      const item=find();selected=item;
      set('f-caption',`${state.type} · ${entry().category} · ${region()} · ${period()}`);
      if(!item)throw Error('해당 분석 단위의 결과가 없습니다.');
      const detail=(await load(item.shard))[item.id];
      if(token!==sequence)return;
      if (!detail || item.n !== detail.observations.length || item.n !== detail.model.n)
        throw Error('표본 수와 RAW 상세 결과가 일치하지 않습니다.');
      set('f-n',item.n);set('f-slope',fmt(item.coefficients?.[0],9));set('f-pvalue',fmtP(item.pvalues?.[0]));
      set('f-intercept',fmt(item.intercept,9));set('f-r2',`${fmt(item.r2,6)} / ${fmt(item.adj_r2,6)}`);
      set('f-pearson',fmt(item.correlations?.[0],9));set('f-pearson-p',fmtP(item.correlation_pvalues?.[0]));
      set('f-status',item.warning || `X: ${entry().category} 인구 10만 명당 개소 · Y: ${state.type} 장애인 등록률(%) · 1분기 스냅샷과 연간 통계를 결합한 비가중 단순회귀이며 인과관계가 아닙니다.`);
      set('f-ols-raw',detail.model.raw || detail.model.warning || 'OLS 추정 불가');
      const scipy=detail.correlations.scipy[entry().field];
      set('f-scipy-raw',[
        'scipy.stats.pearsonr(X, Y, alternative="two-sided")',
        'SciPy '+detail.correlations.scipy_version,
        'X: '+entry().category+' (개소/인구 10만 명)',
        'Y: '+state.type+' 장애인 등록률(%)',
        'n: '+scipy.n,
        'PearsonRResult: '+(scipy.raw||'정의되지 않음'),
        'ConfidenceInterval: '+(scipy.raw_confidence_interval||'정의되지 않음'),
        'r: '+scipy.statistic,
        'two-sided p: '+fmtP(scipy.pvalue),
        '95% CI: ['+scipy.confidence_interval.low+', '+scipy.confidence_interval.high+']',
        'warnings: '+scipy.warnings.join('; '),
        'reason: '+(scipy.reason||'없음')
      ].join('\n'));
      renderObservations(detail);
      graph(detail,item);graphTrends();
    }catch(error){
      if(token!==sequence)return;
      console.error(error);clearCharts();
      set('f-status','분석 로딩 실패: '+error.message);
      for(const id of ['f-n','f-slope','f-pvalue','f-intercept','f-r2','f-pearson','f-pearson-p'])set(id,'—');
      set('f-ols-raw',error.message);set('f-scipy-raw',error.message);
    }
  }
  try {
    manifest=await load('data/facility_manifest.json');
    selectOptions($('f-model'),Object.entries(manifest.models).map(([id,v])=>[id,v.label]),state.model);
    selectOptions($('f-type'),manifest.types.map(v=>[v,v]),state.type);
    selectOptions($('f-province'),[['전국','전국'],...manifest.provinces.map(v=>[v,v])],state.province);
    const query=new URLSearchParams(location.search);
    if(manifest.models[query.get('model')])state.model=query.get('model');
    if(manifest.types.includes(query.get('type')))state.type=query.get('type');
    for(const [id,field] of [['f-model','model'],['f-type','type'],['f-scope','scope'],['f-province','province']]){
      $(id).onchange=e=>{
        state[field]=e.target.value;
        if(field==='model'){
          const url=new URL(location.href);url.searchParams.set('model',state.model);history.replaceState(null,'',url);
        }
        render(field==='model');
      };
    }
    $('f-year').onchange=e=>{state.year=Number(e.target.value);render();};
    $('f-pooled').onchange=e=>{state.pooled=e.target.checked;render();};
    $('f-index-export').disabled=false;
    $('f-index-export').onclick=()=>csvDownload(`facility_index_${state.model}.csv`,[
      ['장애유형','분석단위','지역','연도','n','절편','OLS slope','OLS p','R2','adj R2','SciPy r','SciPy p'],
      ...index.map(r=>[r.type,r.scope,r.region,r.year,r.n,r.intercept,r.coefficients?.[0],r.pvalues?.[0],r.r2,r.adj_r2,r.correlations?.[0],r.correlation_pvalues?.[0]])
    ]);
    await render(true);
  }catch(error){console.error(error);set('f-status','초기화 실패: '+error.message);}
})();
