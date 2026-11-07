'use strict';
/* Python statsmodels generates all models. Browser only selects and draws them. */
(async () => {
 const $=id=>document.getElementById(id),fmt=(v,n=5)=>Lab.numeric(v,n),pf=v=>Lab.pvalue(v);
 const mode=document.body.dataset.analysis;
 const spec={
   multi:['demographic_multi_models','다중회귀',null],
   age65:['age65_ols_models','65세 이상 고령인구','age65_percent'],
   under15:['under15_ols_models','0~14세 저연령 인구','under15_percent'],
   medical:['medical_ols_models','1인당 진료비','medical_10k_per_person']
 }[mode];
 if(!spec)return;
 const isMulti=mode==='multi',prefix=spec[0];
 const labels={
   before:'재정자립도(개편 전, 0~1)',after:'재정자립도(개편 후, 0~1)',
   age65_percent:'65세 이상 인구비율(%)',under15_percent:'0~14세 인구비율(%)',
   fertility:'합계출산율(명/여성)',medical_10k_per_person:'1인당 진료비(만원)'
 };
 const state={scope:'municipal',province:'전국',district:'',year:2022,allYears:false,fiscal:'after',dtype:'전체'};
 let meta,municipal,provincial,pooled,history,yearly={},chart,selected,visible=[];
 let requestId=0;
 const vars=()=>isMulti?[state.fiscal,'age65_percent','under15_percent','fertility','medical_10k_per_person']:[spec[2]];
 const year=()=>state.scope==='local_history'||state.allYears?'전기간':state.year;
 const region=()=>state.scope==='provincial'?'전국':state.scope==='local_history'?state.province+'|'+state.district:state.province;
 const find=items=>items?.find(m=>m.scope===state.scope&&m.region===region()&&String(m.year)===String(year())&&(!isMulti||m.mode===state.fiscal)&&(!m.type||m.type===state.dtype));
 const outcome=()=>state.dtype==='전체'?'전체 장애인 등록률(%)':state.dtype+' 장애유형 등록률(%)';
 const valid=m=>m&&m.intercept!=null;
 const set=(id,value)=>Lab.text(id,value);
 const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function updateDistrict(){
   const select=$('an-district');select.replaceChildren();
   (meta.districts[state.province]||[]).forEach(d=>Lab.opt(select,d,d));
   if([...select.options].some(o=>o.value===state.district))select.value=state.district;
   state.district=select.value||'';
 }
 function observations(){
   const source=state.scope==='provincial'?provincial:municipal;
   return source.filter(r=>(year()==='전기간'||r.year===state.year)
     &&(state.scope==='provincial'||state.province==='전국'||r.province===state.province)
     &&(state.scope!=='local_history'||r.district===state.district)
     &&(state.scope!=='provincial'||!r.complete_types||r.complete_types.includes(state.dtype))
     &&r.rates?.[state.dtype]!=null&&vars().every(key=>r[key]!=null&&Number.isFinite(Number(r[key]))));
 }
 function formula(model){
   if(!valid(model))return '표본 부족 또는 설계행렬 특이성으로 추정 불가';
   return outcome()+' = '+fmt(model.intercept,7)+model.predictors.map(k=>' + ('+fmt(model.coefficients[k]?.coef,7)+' × '+labels[k]+')').join('');
 }
 function showCoefficients(model){
   if(!valid(model)){$('an-coefficients').textContent='추정 가능한 계수가 없습니다.';return;}
   let html='<table><thead><tr><th>독립변수</th><th>계수 β</th><th>p-값</th><th>95% 신뢰구간</th></tr></thead><tbody>';
   for(const k of model.predictors){
     const c=model.coefficients[k];
     html+='<tr><td>'+escape(labels[k])+'</td><td>'+fmt(c.coef,8)+'</td><td>'+escape(pf(c.p))+'</td><td>'+fmt(c.ci?.[0],6)+' ~ '+fmt(c.ci?.[1],6)+'</td></tr>';
   }
   $('an-coefficients').innerHTML=html+'</tbody></table>';
 }
 function predicted(row){
   if(!valid(selected))return null;
   return selected.intercept+vars().reduce((sum,k)=>sum+Number(row[k])*selected.coefficients[k].coef,0);
 }
 function showObservations(){
   const keys=vars();
   $('an-table-head').innerHTML='<tr><th>연도</th><th>광역</th><th>기초</th>'+keys.map(k=>'<th>'+escape(labels[k])+'</th>').join('')+'<th>'+escape(outcome())+'</th><th>예측(%)</th><th>잔차(%p)</th></tr>';
   const tbody=$('an-table-body');tbody.replaceChildren();
   for(const r of visible.slice(0,100)){
     const estimate=predicted(r);
     const tr=document.createElement('tr');
     [r.year,r.province,r.district,...keys.map(k=>fmt(r[k],4)),fmt(r.rates[state.dtype],5),fmt(estimate,5),fmt(estimate==null?null:r.rates[state.dtype]-estimate,5)].forEach(v=>{
       const td=document.createElement('td');td.textContent=String(v);tr.appendChild(td);
     });
     tbody.appendChild(tr);
   }
   set('an-table-count',visible.length+'개 유효 관측치 · 표에는 100개까지 표시 · 전체 CSV 다운로드 가능');
 }
 function showChart(){
   if(chart){chart.destroy();chart=null;}
   if(!window.Chart){set('an-chart-note','차트 라이브러리 로드 실패. 통계표는 확인할 수 있습니다.');return;}
   const key=isMulti?state.fiscal:vars()[0];
   const points=visible.map(r=>({x:r[key],y:r.rates[state.dtype],label:r.province+' '+r.district+' '+r.year}));
   const data=[{label:'실제 '+state.dtype+' 등록률',data:points,backgroundColor:'rgba(36,111,156,.7)',pointRadius:3.2}];
   if(valid(selected)&&visible.length){
     const xs=points.map(r=>r.x),lo=Math.min(...xs),hi=Math.max(...xs);
     const slope=selected.coefficients[key].coef;
     let base=selected.intercept;
     if(isMulti)for(const other of vars()){
       if(other!==key){base+=selected.coefficients[other].coef*visible.reduce((s,r)=>s+Number(r[other]),0)/visible.length;}
     }
     data.push({type:'line',label:isMulti?'다른 변수 평균 고정 예측선':'OLS 예측선',
       data:[{x:lo,y:base+slope*lo},{x:hi,y:base+slope*hi}],
       borderColor:'#bd6738',borderWidth:2,pointRadius:0,tension:0});
   }
   chart=new Chart($('an-chart'),{type:'scatter',data:{datasets:data},options:{
     responsive:true,maintainAspectRatio:false,
     scales:{x:{type:'linear',title:{display:true,text:labels[key]}},y:{title:{display:true,text:outcome()}}},
     plugins:{tooltip:{callbacks:{label:c=>c.raw.label?c.raw.label+' · '+fmt(c.raw.x,3)+' / '+fmt(c.raw.y,3)+'%':'예측 '+fmt(c.raw.y,3)+'%'}}}
   }});
   set('an-chart-note',isMulti?'실제 관측치 + 나머지 설명변수를 표본 평균에 고정한 조건부 예측선':'실제 관측치 + OLS 예측선');
 }
 async function render(){
   const request=++requestId;
   $('an-province').disabled=state.scope==='provincial';
   $('an-district-wrap').hidden=state.scope!=='local_history';
   $('an-all-years').checked=state.allYears||state.scope==='local_history';
   $('an-all-years').disabled=state.scope==='local_history';
   $('an-year').disabled=state.allYears||state.scope==='local_history';
   $('an-year').value=state.year;
   $('an-mode-wrap').hidden=!isMulti;
   set('an-year-caption',year()==='전기간'?'2014~2022년 통합':state.year+'년');
   set('an-outcome',outcome()+' = 해당 유형의 등록인원 ÷ 주민등록인구 × 100 (%)');
   set('an-caption',state.dtype+' · '+region().replace('|',' · ')+' · '+year()+' · '+(state.scope==='provincial'?'광역 간':state.scope==='local_history'?'개별 기초 시계열':'기초 간'));
   $('an-export').disabled=true;
   set('an-warning','선택한 장애유형의 사전 계산 모형을 불러오는 중입니다.');
   let items;
   try {
     if(state.dtype==='전체') {
       items=state.scope==='local_history'?history:state.allYears?pooled:yearly[String(state.year)+(isMulti?state.fiscal:'')];
     } else {
       const index=meta.types.indexOf(state.dtype);
       if(index<0)throw Error('지원하지 않는 장애유형: '+state.dtype);
       const filename='data/'+prefix+'_type_'+String(index).padStart(2,'0')+'.json';
       const payload=await Lab.load(filename);
       if(payload.type!==state.dtype)throw Error('선택한 장애유형과 파일 내용이 일치하지 않습니다.');
       items=payload.models;
     }
   } catch(error) {
     if(request!==requestId)return;
     console.error(error);
     selected=null;visible=[];
     set('an-warning','유형별 회귀 데이터를 불러오지 못했습니다: '+error.message);
     $('an-export').disabled=true;
     return;
   }
   if(request!==requestId)return; // An earlier type selection must never overwrite a newer one.
   selected=find(items);visible=observations();
   set('an-n',selected?.n??'—');
   set('an-r2',fmt(selected?.r2,5));set('an-adjr2',fmt(selected?.adj_r2,5));
   set('an-intercept',fmt(selected?.intercept,6));
   set('an-p',pf(selected?.p_model));
   set('an-formula',formula(selected));
   const special=state.dtype==='청각·언어'
     ? '※ 청각·언어는 2014~2017년 경기도 통합 집계만 포함합니다. 다른 유형 및 지역에 0으로 대체하지 않으며 전국 대표성을 갖지 않습니다. '
     : '';
   set('an-warning',special+(selected?.warning||(
     isMulti?'다른 설명변수들을 함께 고려한 조건부 연관성입니다.':'단순회귀는 공변량을 통제하지 않습니다.')));
   set('an-raw',selected?.raw||'해당 조건에서 추정 불가');
   showCoefficients(selected);showObservations();showChart();
   $('an-export').disabled=false;
 }
 function exportCsv(){
   const keys=vars(),quote=x=>'"'+String(x??'').replace(/"/g,'""')+'"';
   const header=['연도','광역','기초','장애유형',...keys.map(k=>labels[k]),outcome(),'예측(%)','잔차(%p)'];
   const records=visible.map(r=>{
     const estimate=predicted(r);
     return [r.year,r.province,r.district,state.dtype,...keys.map(k=>r[k]),r.rates[state.dtype],estimate,estimate==null?null:r.rates[state.dtype]-estimate];
   });
   const value='\uFEFF'+[header,...records].map(row=>row.map(quote).join(',')).join('\r\n');
   const url=URL.createObjectURL(new Blob([value],{type:'text/csv;charset=utf-8'}));
   const link=document.createElement('a');link.href=url;link.download=mode+'_'+meta.types.indexOf(state.dtype)+'_'+year()+'.csv';link.click();
   setTimeout(()=>URL.revokeObjectURL(url),500);
 }
 try {
   meta=await Lab.load('data/meta.json');
   [municipal,provincial,pooled,history]=await Promise.all([
     Lab.load('data/municipalities.json'),Lab.load('data/provinces.json'),
     Lab.load('data/'+prefix+'_pooled.json'),Lab.load('data/'+prefix+'_local_history.json')
   ]);
   const pending=[];
   for(let year=2014;year<=2022;year++)for(const fiscal of(isMulti?['before','after']:[''])){
     const key=String(year)+(isMulti?fiscal:'');
     pending.push(Lab.load('data/'+prefix+'_'+year+(isMulti?'_'+fiscal:'')+'.json').then(m=>{yearly[key]=m;}));
   }
   await Promise.all(pending);
   Lab.opt($('an-province'),'전국','전국');
   meta.provinces.forEach(value=>Lab.opt($('an-province'),value,value));
   meta.types.forEach(dtype=>Lab.opt($('an-type'),dtype,dtype));
   updateDistrict();
   $('an-scope').onchange=e=>{
     state.scope=e.target.value;
     if(state.scope==='local_history'&&state.province==='전국'){
       state.province=meta.provinces[0];$('an-province').value=state.province;
     }
     updateDistrict();render();
   };
   $('an-province').onchange=e=>{state.province=e.target.value;updateDistrict();render();};
   $('an-district').onchange=e=>{state.district=e.target.value;render();};
   $('an-mode').onchange=e=>{state.fiscal=e.target.value;render();};
   $('an-type').onchange=e=>{state.dtype=e.target.value;render();};
   $('an-year').oninput=e=>{state.year=Number(e.target.value);render();};
   $('an-all-years').onchange=e=>{state.allYears=e.target.checked;render();};
   $('an-export').onclick=exportCsv;
   render();
 } catch(error){console.error(error);set('an-warning','데이터를 불러오지 못했습니다: '+error.message+'. python build.py를 다시 실행해 주세요.');}
})();