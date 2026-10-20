'use strict';
let dataset=null, shown=[];const el=id=>document.getElementById(id);
const metaLabel=(type,id)=> dataset?.meta?.[type]?.[String(id)] || String(id);
const dim=['diagnos','region','kon','alder'];
function fill(name){const s=el(name);s.replaceChildren();for(const [id,label] of Object.entries(dataset.meta[name]||{})){if(!dataset.data.some(r=>String(r[{diagnos:3,region:2,kon:4,alder:5}[name]])===id))continue;const o=document.createElement('option');o.value=id;o.textContent=label;s.append(o)}}
// Shares use raw counts, never rates; other breakdown dimensions must match exactly.
function codeBounds(code){const m=/^([A-Z])(\d\d)(?:-([A-Z])(\d\d))?$/.exec(code);if(!m)return null;return [m[1].charCodeAt(0)*100+Number(m[2]),(m[3]||m[1]).charCodeAt(0)*100+Number(m[4]||m[2])]}
function findParent(code){const a=codeBounds(code);if(!a)return null;const candidates=Object.keys(dataset.meta.diagnos).map(k=>[k,codeBounds(k)]).filter(([k,b])=>b&&k!==code&&b[0]<=a[0]&&b[1]>=a[1]&&(b[1]-b[0])>(a[1]-a[0]));candidates.sort((x,y)=>(x[1][1]-x[1][0])-(y[1][1]-y[1][0]));return candidates[0]?.[0]||null}
function info(row){const [measure,year,region,diag,sex,age,value]=row;const count=(code)=>dataset.data.find(r=>r[0]===1&&r[1]===year&&r[2]===region&&r[3]===code&&r[4]===sex&&r[5]===age)?.[6];const numerator=count(diag),total=count('99'),parent=findParent(diag),part=parent?count(parent):null;const fmt=v=>new Intl.NumberFormat('sv-SE',{maximumFractionDigits:2}).format(v);const pct=(n,d)=>Number.isFinite(n)&&Number.isFinite(d)&&d>0?fmt(100*n/d)+' %':'Ej beräkningsbar';return '<strong>'+year+' – '+metaLabel('diagnos',diag)+'</strong><br>Värde: '+fmt(value)+(measure===2?' per 100 000':' dödsfall')+'<br>Andel av samtliga dödsfall: '+(diag==='99'?'100 %':pct(numerator,total))+'<br>Andel inom delgrupp'+(parent?' ('+metaLabel('diagnos',parent)+')':'')+': '+(parent?pct(numerator,part):'Ingen entydig överordnad grupp')+'<br><small>Andelarna baseras på antal döda, inte per 100 000.</small>'}

const palette=['#9d1631','#1f77b4','#2ca02c','#9467bd','#ff7f0e','#17becf','#8c564b','#e377c2','#7f7f7f','#bcbd22','#164e63','#c2410c','#3f6212','#6d28d9','#9f1239','#0369a1','#15803d','#7c2d12','#a21caf','#334155','#be123c'];
function rankedCodes(){
 const region=el('region').value,sex=el('kon').value,age=el('alder').value,metric=el('rankmetric').value;
 const years=dataset.data.filter(r=>r[0]===1&&r[2]===region&&r[4]===sex&&r[5]===age&&r[3]==='99').map(r=>r[1]);
 const year=Math.max(...years);
 const total=dataset.data.find(r=>r[0]===1&&r[1]===year&&r[2]===region&&r[3]==='99'&&r[4]===sex&&r[5]===age)?.[6];
 // Only non-overlapping top-level ICD chapters; exclude supplementary overlapping codes.
 const chapters=new Set(['A00-B99','C00-D48','D50-D89','E00-E90','F00-F99','G00-G99','H00-H59','H60-H95','I00-I99','J00-J99','K00-K93','L00-L99','M00-M99','N00-N99','O00-O99','P00-P96','Q00-Q99','R00-R99','S00-T98','V01-Y98','U00-U99']);
 const m=metric==='rate'?2:1;
 const values=dataset.data.filter(r=>r[0]===m&&r[1]===year&&r[2]===region&&r[4]===sex&&r[5]===age&&chapters.has(r[3])&&Number.isFinite(r[6])).map(r=>({code:r[3],value:metric==='share'?(total>0?100*r[6]/total:NaN):r[6]}));
 values.sort((a,b)=>b.value-a.value||a.code.localeCompare(b.code));
 return {year,values};
}
function updateRank(){
 const pos=el('topprank').value;
 if(pos==='all')return;
 const r=rankedCodes();const slice=r.values.slice(Number(pos),Number(pos)+5);
 const sel=el('diagnos');sel.replaceChildren();
 for(const row of slice){const opt=document.createElement('option');opt.value=row.code;opt.textContent=metaLabel('diagnos',row.code);sel.append(opt)}
 el('diagnos-sok').value='';
 el('status').textContent='Rangordning för '+r.year+' efter '+(el('rankmetric').value==='share'?'andel av dödsfall':'dödsfall per 100 000')+'. Avser ICD-huvudkapitel, inte överlappande diagnosundergrupper.';
}
function drawRegions(){
 const svg=el('regional-chart'),legend=el('regional-legend');svg.replaceChildren();legend.replaceChildren();
 const ns='http://www.w3.org/2000/svg',metric=Number(el('matt').value),diagnosis=el('diagnos').value,sex=el('kon').value,age=el('alder').value;
 const regions=Object.keys(dataset.meta.region).filter(k=>k!=='0');
 const lines=regions.map(k=>({code:k,rows:dataset.data.filter(r=>r[0]===metric&&r[2]===k&&r[3]===diagnosis&&r[4]===sex&&r[5]===age&&Number.isFinite(r[6])).sort((a,b)=>a[1]-b[1])})).filter(x=>x.rows.length);
 const vals=lines.flatMap(l=>l.rows.map(r=>r[6]));if(!vals.length)return;
 const max=Math.max(1,...vals),lo=Math.min(...lines.flatMap(l=>l.rows.map(r=>r[1]))),hi=Math.max(...lines.flatMap(l=>l.rows.map(r=>r[1])));
 const X=t=>65+(t-lo)/(hi-lo||1)*895,Y=v=>315-v/max*275;
 function node(tag,attrs,text){const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;svg.append(n);return n}
 for(let i=0;i<=4;i++){const yy=315-i*275/4;node('line',{x1:65,y1:yy,x2:965,y2:yy,stroke:'#e6e9ef'});node('text',{x:6,y:yy+4},new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}).format(max*i/4))}
 for(let yr=lo;yr<=hi;yr+=Math.max(1,Math.ceil((hi-lo)/7)))node('text',{x:X(yr)-14,y:346},yr);
 lines.forEach((l,i)=>{const color=palette[i%palette.length];node('polyline',{points:l.rows.map(r=>X(r[1])+','+Y(r[6])).join(' '),fill:'none',stroke:color,'stroke-width':2,opacity:.88});const span=document.createElement('span');span.textContent='● '+metaLabel('region',l.code);span.style.color=color;legend.append(span);for(const r of l.rows){const dot=node('circle',{cx:X(r[1]),cy:Y(r[6]),r:3,fill:color,tabindex:0});const title=document.createElementNS(ns,'title');title.textContent=metaLabel('region',l.code)+' '+r[1]+': '+r[6];dot.append(title)}})
}


let ageDataset=null;
async function fetchAges(){
 try{const r=await fetch('data/dodsorsaker-alder.json');if(!r.ok)throw Error('Åldersfilen har ännu inte genererats');ageDataset=await r.json();drawComparisons()}catch(e){el('age-status').textContent=e.message+'. Kör arbetsflödet Bygg Socialstyrelsens data.'}
}
function chartCompare(chartId,legendId,lines){
 const svg=el(chartId),legend=el(legendId);svg.replaceChildren();legend.replaceChildren();
 const ns='http://www.w3.org/2000/svg',vals=lines.flatMap(l=>l.rows.map(r=>r[6])).filter(Number.isFinite);
 if(!vals.length){const t=document.createElementNS(ns,'text');t.setAttribute('x',60);t.setAttribute('y',160);t.textContent='Ingen tillgänglig statistik för detta urval';svg.append(t);return}
 const max=Math.max(...vals),min=chartId==='sex-chart'?Math.min(...vals):Math.min(0,...vals),span=max-min||1,all=lines.flatMap(l=>l.rows.map(r=>r[1])),lo=Math.min(...all),hi=Math.max(...all),X=t=>65+(t-lo)/(hi-lo||1)*890,Y=v=>315-(v-min)/span*275;
 function node(tag,attrs,label){const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(label!==undefined)n.textContent=label;svg.append(n);return n}
 for(let i=0;i<=4;i++){const y=315-i*275/4;node('line',{x1:65,y1:y,x2:955,y2:y,stroke:'#e5e7eb'});node('text',{x:5,y:y+4},new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}).format(min+span*i/4))}
 for(let yr=lo;yr<=hi;yr+=Math.max(1,Math.ceil((hi-lo)/7)))node('text',{x:X(yr)-15,y:346},yr);
 lines.forEach((l,i)=>{if(!l.rows.length)return;const color=palette[i%palette.length];node('polyline',{points:l.rows.map(r=>X(r[1])+','+Y(r[6])).join(' '),fill:'none',stroke:color,'stroke-width':2.3});const span=document.createElement('span');span.textContent='● '+l.label;span.style.color=color;legend.append(span);for(const r of l.rows){const dot=node('circle',{cx:X(r[1]),cy:Y(r[6]),r:3.5,fill:color,tabindex:0});const title=document.createElementNS(ns,'title');title.textContent=l.label+' – '+r[1]+': '+new Intl.NumberFormat('sv-SE',{maximumFractionDigits:2}).format(r[6]);dot.append(title)}})
}
function drawComparisons(){
 if(!dataset)return;
 const metric=Number(el('matt').value),diag=el('diagnos').value,region=el('region').value,age=el('alder').value,sex=el('kon').value;
 const sexes=['1','2'].map(k=>({label:metaLabel('kon',k),rows:dataset.data.filter(r=>r[0]===metric&&r[2]===region&&r[3]===diag&&r[4]===k&&r[5]===age).sort((a,b)=>a[1]-b[1])}));
 chartCompare('sex-chart','sex-legend',sexes);
 if(!ageDataset)return;
 const ages=Object.keys(ageDataset.meta.alder).filter(k=>k!=='99'&&ageDataset.data.some(r=>r[5]===k));
 const lines=ages.map(k=>({label:metaLabel('alder',k),rows:ageDataset.data.filter(r=>r[0]===metric&&r[2]===region&&r[3]===diag&&r[4]===sex&&r[5]===k).sort((a,b)=>a[1]-b[1])})).filter(l=>l.rows.length);
 el('age-status').textContent=lines.length?'Åldersspecifika årsvärden. Vid mått per 100 000 används respektive åldersgrupps befolkning som nämnare.':'Denna diagnos saknar ännu åldersuppdelade data i webbversionen.';
 chartCompare('age-chart','age-legend',lines);
}

function draw(){
 const keys=[el('matt').value,...['year','region','diagnos','kon','alder'].map(x=>x)]; // dimensions from imported rows
 shown=dataset.data.filter(r=> String(r[0])===keys[0]&&String(r[2])===el('region').value&&String(r[3])===el('diagnos').value&&String(r[4])===el('kon').value&&String(r[5])===el('alder').value).sort((a,b)=>a[1]-b[1]);
 el('chart-title').textContent=metaLabel('diagnos',el('diagnos').value)+' – '+metaLabel('region',el('region').value);
 const svg=el('chart');svg.replaceChildren();el('hoverinfo').hidden=true;const ns='http://www.w3.org/2000/svg';function node(tag,attrs,text){let n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;svg.append(n);return n}
 if(!shown.length){node('text',{x:50,y:160},'Inga data för urvalet');el('rows').replaceChildren();return}
 const v=shown.map(r=>Number(r[6])).filter(Number.isFinite),max=Math.max(1,...v),min=0;const x=y=>70+(y-1997)/28*895,y=z=>300-(z-min)/(max-min)*260;for(let j=0;j<=4;j++){const yy=300-j*65;node('line',{x1:70,y1:yy,x2:965,y2:yy,stroke:'#e5e7eb'});node('text',{x:8,y:yy+4},new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}).format(max*j/4))}for(let yr=1997;yr<=2025;yr+=4)node('text',{x:x(yr)-14,y:325},yr);
 const pts=shown.filter(r=>Number.isFinite(Number(r[6]))).map(r=>x(r[1])+','+y(Number(r[6]))).join(' ');node('polyline',{points:pts,fill:'none',stroke:'#a31d30','stroke-width':3,'stroke-linejoin':'round'});
 for(const r of shown){if(!Number.isFinite(Number(r[6])))continue;const c=node('circle',{cx:x(r[1]),cy:y(Number(r[6])),r:4,fill:'#a31d30'});const tip=el('hoverinfo');c.addEventListener('pointerenter',()=>{tip.innerHTML=info(r);tip.hidden=false});c.addEventListener('pointerleave',()=>{tip.hidden=true});c.addEventListener('focus',()=>{tip.innerHTML=info(r);tip.hidden=false});c.addEventListener('blur',()=>{tip.hidden=true});c.setAttribute('tabindex','0');c.setAttribute('aria-label',r[1]+': '+r[6]);c.setAttribute('r','6')}
 drawRegions();drawComparisons();
 el('rows').replaceChildren();for(const r of shown){const tr=document.createElement('tr');for(const val of [r[1],r[6]]){const td=document.createElement('td');td.textContent=val;tr.append(td)}el('rows').append(tr)}
}
async function start(){try{const response=await fetch('data/dodsorsaker.json');if(!response.ok)throw Error('Ingen publicerad sammanställning ännu');dataset=await response.json();for(const d of dim)fill(d);for(const [key,val]of Object.entries({diagnos:'99',region:'25',kon:'3',alder:'99'})){if([...el(key).options].some(x=>x.value===val))el(key).value=val}el('status').textContent='Årsvärden från Socialstyrelsens CSV-export. Filtrerbara data: '+dataset.data.length.toLocaleString('sv-SE')+' rader.';for(const d of [...dim,'matt'])el(d).addEventListener('change',()=>{if(['region','kon','alder'].includes(d)&&el('topprank').value!=='all')updateRank();draw()});el('topprank').addEventListener('change',()=>{if(el('topprank').value!=='all')updateRank();else{fill('diagnos');el('status').textContent='Visar alla tillgängliga diagnoser'}draw()});el('rankmetric').addEventListener('change',()=>{if(el('topprank').value!=='all')updateRank();draw()});const allOptions=[...el('diagnos').options].map(o=>[o.value,o.textContent]);el('diagnos-sok').addEventListener('input',()=>{const q=el('diagnos-sok').value.toLocaleLowerCase('sv-SE').trim();const previous=el('diagnos').value;el('diagnos').replaceChildren();for(const [id,label] of allOptions){if(q && !(id+' '+label).toLocaleLowerCase('sv-SE').includes(q))continue;const opt=document.createElement('option');opt.value=id;opt.textContent=label;el('diagnos').append(opt)}if([...el('diagnos').options].some(o=>o.value===previous))el('diagnos').value=previous;draw()});draw();}catch(err){el('status').textContent=err.message+'. Kör arbetsflödet för datagenerering i GitHub Actions.';el('explore').hidden=true;el('results').hidden=true}}

let maternity=null;
async function loadMaternity(){
 if(maternity)return;
 const resp=await fetch('data/graviditet.json');if(!resp.ok){el('maternity-status').textContent='Databearbetning återstår. Kör Inventera graviditetsdata i Actions på nytt.';return}
 maternity=await resp.json();
 for(const [field,dim] of [['maternity-region','region'],['maternity-var','variabel'],['maternity-measure','matt']]){
  const select=el(field);select.replaceChildren();for(const [code,label]of Object.entries(maternity.meta[dim])){const has=maternity.data.some(r=>String(r[dim==='matt'?0:dim==='region'?2:3])===code);if(!has)continue;const opt=document.createElement('option');opt.value=code;opt.textContent=label;select.append(opt)}
 }
 if([...el('maternity-region').options].some(o=>o.value==='00000'))el('maternity-region').value='00000';
 for(const d of ['maternity-region','maternity-var','maternity-measure'])el(d).addEventListener('change',drawMaternity);
 drawMaternity();
}
function drawMaternity(){
 const measure=el('maternity-measure').value,region=el('maternity-region').value,variable=el('maternity-var').value;
 const data=maternity.data.filter(r=>String(r[0])===measure&&r[2]===region&&r[3]===variable).sort((a,b)=>a[1]-b[1]);
 el('maternity-status').textContent=data.length?'Årsserie: '+data[0][1]+'–'+data[data.length-1][1]:'Inga observationer för detta urval';
 const svg=el('maternity-chart');svg.replaceChildren();const ns='http://www.w3.org/2000/svg';
 function n(tag,attr,t){const e=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attr))e.setAttribute(k,v);if(t!==undefined)e.textContent=t;svg.append(e);return e}
 if(!data.length)return;
 const max=Math.max(...data.map(r=>r[4]),0.01),min=Math.min(0,...data.map(r=>r[4]));
 const yr0=data[0][1],yr1=data[data.length-1][1],X=yr=>65+(yr-yr0)/(yr1-yr0||1)*880,Y=v=>300-(v-min)/(max-min||1)*250;
 for(let j=0;j<=4;j++){const v=min+(max-min)*j/4,yy=Y(v);n('line',{x1:65,y1:yy,x2:945,y2:yy,stroke:'#e2e8f0'});n('text',{x:3,y:yy+4},new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}).format(v))}
 for(let yr=yr0;yr<=yr1;yr+=Math.max(1,Math.ceil((yr1-yr0)/7)))n('text',{x:X(yr)-15,y:326},yr);
 n('polyline',{points:data.map(r=>X(r[1])+','+Y(r[4])).join(' '),stroke:'#991b2b','stroke-width':3,fill:'none'});
 for(const r of data){const dot=n('circle',{cx:X(r[1]),cy:Y(r[4]),r:5,fill:'#991b2b'}),tip=document.createElementNS(ns,'title');tip.textContent=r[1]+': '+new Intl.NumberFormat('sv-SE',{maximumFractionDigits:2}).format(r[4])+' ('+maternity.meta.matt[measure]+')';dot.append(tip)}
}



let verifiedGBD=[];
async function loadVerifiedGBD(){
 try{
  const response=await fetch('data/gbd-verified.json');
  if(!response.ok)return;
  const payload=await response.json();
  verifiedGBD=(payload.records||[]).filter(r=>r.mapping_review_status==='approved'&&r.license_review_status==='approved');
  renderRisk();
 }catch(e){console.warn('GBD estimates unavailable',e)}
}

const gbdReview={ 'C00-D48':'Neoplasms','I00-I99':'Cardiovascular diseases','J00-J99':'Respiratory diseases','A00-B99':'Communicable diseases','V01-Y98':'Injuries'};
function populateRisk(){
 if(!dataset)return;
 const select=el('risk-diagnos');select.replaceChildren();
 for(const [k,label] of Object.entries(dataset.meta.diagnos)){const opt=document.createElement('option');opt.value=k;opt.textContent=k+' – '+label;select.append(opt)}
 const selected=el('diagnos').value;if([...select.options].some(o=>o.value===selected))select.value=selected;
 renderRisk();
}
function renderRisk(){
 const diag=el('risk-diagnos').value;
 const candidate=gbdReview[diag];
 el('risk-connection').textContent=candidate?'ICD '+diag+' – möjlig tematisk motsvarighet i GBD: '+candidate+'. Ej verifierad kodmatchning. Risk–orsakssamband har ännu inte granskats.':'Ingen granskad GBD-koppling för ICD '+diag+'. Koppling och relevanta riskfaktorer återstår att utreda.';
 el('risk-estimates').textContent='Inga kvalitetssäkrade riskattribuerbara skattningar för denna ICD-kod har importerats. Andelar ska inte härledas ur dödsorsakens namn.';
}
function calcRisk(){
 const n=Number(el('risk-deaths').value),p=Number(el('risk-paf').value);
 el('risk-scenario').textContent=el('risk-deaths').value!==''&&el('risk-paf').value!==''&&Number.isFinite(n)&&Number.isFinite(p)&&n>=0&&p>=0&&p<=100?'Scenario: '+new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}).format(n*p/100)+' av '+n+' dödsfall vid ett hypotetiskt PAF om '+p+' %. Inte en prognos eller en validerad skattning.':'Ange ett antal och en andel mellan 0 och 100 %.';
}
el('risk-diagnos').addEventListener('change',renderRisk);
for(const id of ['risk-deaths','risk-paf'])el(id).addEventListener('input',calcRisk);


let scbEdu=null;
function renderSCBEducation(){
 if(!scbEdu)return;
 const svg=el('scb-education-chart'),legend=el('scb-education-legend');svg.replaceChildren();legend.replaceChildren();
 const dims=scbEdu.sources.education.dimensions;
 const dim=pattern=>dims.find(d=>pattern.test(d.text.toLowerCase()))||null;
 const cause=dim(/dödsorsak/),education=dim(/utbildning/),sex=dim(/kön/),year=dim(/år/);
 if(![cause,education,sex,year].every(Boolean)){el('scb-education-status').textContent='SCB-kodlistorna har ändrats. Kontrollera tabellens struktur.';return}
 const lookup=(dimension,value)=>{const i=dimension.values.indexOf(value);return dimension.valueTexts[i]||value};
 for(const [id,d] of [['scb-education-cause',cause],['scb-education-sex',sex]]){
  const s=el(id),previous=s.value;if(!s.options.length){for(const v of d.values){const opt=document.createElement('option');opt.value=v;opt.textContent=lookup(d,v);s.append(opt)}}if([...s.options].some(o=>o.value===previous))s.value=previous;
 }
 const cc=el('scb-education-cause').value,ss=el('scb-education-sex').value;
 const rows=scbEdu.observations.filter(r=>r.table==='education'&&r.dimensions[cause.code]===cc&&r.dimensions[sex.code]===ss);
 const series=education.values.map((v,i)=>({name:lookup(education,v),color:['#991b2b','#d09b22','#2563eb'][i%3],rows:rows.filter(r=>r.dimensions[education.code]===v).map(r=>({year:Number(r.dimensions[year.code]),value:r.value})).filter(r=>Number.isFinite(r.year)).sort((a,b)=>a.year-b.year)}));
 const values=series.flatMap(s=>s.rows.map(r=>r.value));if(!values.length){el('scb-education-status').textContent='Inga data för detta urval.';return}
 const last=Math.max(...rows.map(r=>Number(r.dimensions[year.code])));
 const latest=Object.fromEntries(education.values.map(v=>[v,rows.find(r=>r.dimensions[education.code]===v&&Number(r.dimensions[year.code])===last)?.value]));
 const loEdu=latest['10'],hiEdu=latest['30'],fmt=v=>new Intl.NumberFormat('sv-SE',{maximumFractionDigits:2}).format(v);
 const comparison=Number.isFinite(loEdu)&&Number.isFinite(hiEdu)&&hiEdu>0?' Skillnad förgymnasial–eftergymnasial '+fmt(loEdu-hiEdu)+' per 100 000; kvot '+fmt(loEdu/hiEdu)+'.':'';
 el('scb-education-status').textContent=lookup(cause,cc)+' – '+lookup(sex,ss)+'. Dödstal per 100 000, 35–84 år. Senaste år: '+last+'.'+comparison+' Ej verifierat åldersstandardiserade.';
 const max=Math.max(1,...values)*1.1,years=series.flatMap(s=>s.rows.map(r=>r.year)),lo=Math.min(...years),hi=Math.max(...years),ns='http://www.w3.org/2000/svg',X=x=>70+(x-lo)/(hi-lo||1)*860,Y=y=>310-y/max*260;
 function n(tag,attrs,label){const item=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))item.setAttribute(k,v);if(label!==undefined)item.textContent=label;svg.append(item);return item}
 for(let i=0;i<=4;i++){const y=310-i*260/4;n('line',{x1:70,y1:y,x2:935,y2:y,stroke:'#e5e7eb'});n('text',{x:5,y:y+4},new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}).format(i*max/4))}
 for(let yr=lo;yr<=hi;yr++)n('text',{x:X(yr)-15,y:342},yr);
 for(const s of series){if(!s.rows.length)continue;n('polyline',{points:s.rows.map(r=>X(r.year)+','+Y(r.value)).join(' '),fill:'none',stroke:s.color,'stroke-width':3});const label=document.createElement('span');label.textContent='● '+s.name+'  ';label.style.color=s.color;legend.append(label);
  for(const r of s.rows){const point=n('circle',{cx:X(r.year),cy:Y(r.value),r:4,fill:s.color});const title=document.createElementNS(ns,'title');title.textContent=s.name+' '+r.year+': '+r.value.toLocaleString('sv-SE');point.append(title)}}
}
async function loadSCBEducation(){
 if(scbEdu){renderSCBEducation();return}
 try{const r=await fetch('data/scb-mortality-education.json');if(!r.ok)throw Error('SCB-filen är ännu inte genererad. Kör GitHub-arbetsflödet.');scbEdu=await r.json();renderSCBEducation()}
 catch(e){el('scb-education-status').textContent=e.message}
}
for(const id of ['scb-education-cause','scb-education-sex'])el(id).addEventListener('change',renderSCBEducation);

document.querySelectorAll('[data-area]').forEach(b=>b.addEventListener('click',()=>{const a=b.dataset.area;for(const t of document.querySelectorAll('[data-area]'))t.setAttribute('aria-selected',t===b?'true':'false');el('explore').hidden=a!=='dodsorsaker';el('maternity').hidden=a!=='fodsel';el('risk-panel').hidden=a!=='risk';el('scb-education-panel').hidden=a!=='education';if(a==='education')loadSCBEducation();if(a==='risk')populateRisk();if(a==='fodsel')loadMaternity().catch(e=>{el('maternity-status').textContent='Kunde inte läsa graviditetsdata: '+e.message});el('results').hidden=a!=='dodsorsaker';let title={dodsorsaker:'Dödsorsaker 1997–2025',ekonomi:'Ekonomiskt bistånd 1990–2025',fodsel:'Graviditeter, förlossningar och nyfödda 1973–2024',metod:'Metod & data'};el('heading').textContent=title[a];el('status').textContent=a==='dodsorsaker'?(dataset?'Välj region, diagnos, kön, ålder och mått.':'Bearbetade dödsorsaksdata saknas ännu.'):a==='metod'?'Källa: Socialstyrelsens publicerade CSV-exporter. Bearbetningen görs i GitHub Actions. Årsdata; ingen kommunupplösning i dödsorsaksfilen. Dödstal per 100 000 är inte åldersstandardiserade. Diagnosgrupper kan överlappa.':'Detta statistikområde ansluts när respektive CSV-arkiv har granskats och bearbetats.'}));
el('csv').addEventListener('click',()=>{const txt='År;Värde\n'+shown.map(r=>r[1]+';'+String(r[6]).replace('.',',')).join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\ufeff'+txt],{type:'text/csv;charset=utf-8'}));a.download='socialstyrelsen-urval.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)});

let bmiData=null;
const bmiCodes={25:['övervikt (BMI mellan 25,0 och 29,9)','obesitas (BMI är 30,0 eller mer)'],30:['obesitas (BMI är 30,0 eller mer)']};
function renderBMI(){
 const svg=el('bmi-trend-chart');svg.replaceChildren();
 if(!bmiData)return;
 const threshold=el('bmi-threshold').value,scbAge=el('bmi-scb-age').value,mfrAge=el('bmi-mfr-age').value;
 const scb=new Map(),mfr=new Map();
 for(const r of bmiData.scb){
  if(r.age!==scbAge||r.measure!=='Body Mass Index (BMI)'||!bmiCodes[threshold].includes(r.bmi))continue;
  const v=scb.get(r.period)||{sum:0,n:0};
  v.sum+=r.value;v.n++;scb.set(r.period,v);
 }
 for(const r of bmiData.socialstyrelsen){
  if(r.age!==mfrAge||r.measure!=='Procent')continue;
  if((threshold==='25'&&['25 ≤ BMI < 30','BMI ≥ 30'].includes(r.bmi))||(threshold==='30'&&r.bmi==='BMI ≥ 30')){
   const v=mfr.get(r.year)||{sum:0,n:0};v.sum+=r.value;v.n++;mfr.set(r.year,v);
  }
 }
 const scbRows=[...scb].filter(([k,v])=>v.n===bmiCodes[threshold].length).map(([period,v])=>{const m=period.match(/^(\d{4})-(\d{4})$/);return m?{year:(+m[1]+ +m[2])/2,value:v.sum,label:period}:null}).filter(Boolean).sort((a,b)=>a.year-b.year);
 const socRows=[...mfr].filter(([k,v])=>v.n===(threshold==='25'?2:1)).map(([year,v])=>({year:+year,value:v.sum,label:String(year)})).sort((a,b)=>a.year-b.year);
 const lines=[{name:'SCB ULF, kvinnor '+scbAge,rows:scbRows,color:'#991b2b'},{name:'Socialstyrelsen MFR, '+mfrAge,rows:socRows,color:'#2563eb'}];
 const all=lines.flatMap(x=>x.rows),ns='http://www.w3.org/2000/svg';
 const status=el('bmi-load'),details=el('bmi-details');
 if(!all.length){status.textContent='Inga jämförbara uppgifter för urvalet.';details.textContent='';return}
 status.textContent='SCB: '+scbRows.length+' perioder; Socialstyrelsen: '+socRows.length+' år. Diagrammet visar separata serier med olika målpopulationer.';
 const minYear=Math.min(...all.map(x=>x.year)),maxYear=Math.max(...all.map(x=>x.year)), ymax=Math.max(10,...all.map(x=>x.value))*1.1;
 const X=yr=>65+(yr-minYear)/(maxYear-minYear||1)*885,Y=v=>315-v/ymax*265;
 function node(tag,attrs,label){const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(label!==undefined)n.textContent=label;svg.append(n);return n}
 for(let i=0;i<=4;i++){const y=315-i*265/4;node('line',{x1:65,y1:y,x2:950,y2:y,stroke:'#e5e7eb'});node('text',{x:10,y:y+4},(ymax*i/4).toFixed(1).replace('.',',')+' %')}
 for(let yr=Math.ceil(minYear/5)*5;yr<=maxYear;yr+=5)node('text',{x:X(yr)-16,y:345},String(yr));
 for(const line of lines){
  const rows=line.rows;if(!rows.length)continue;
  node('polyline',{points:rows.map(r=>X(r.year)+','+Y(r.value)).join(' '),fill:'none',stroke:line.color,'stroke-width':2.7});
  for(const r of rows){const dot=node('circle',{cx:X(r.year),cy:Y(r.value),r:4,fill:line.color});const t=document.createElementNS(ns,'title');t.textContent=line.name+' '+r.label+': '+r.value.toFixed(1).replace('.',',')+' %';dot.append(t)}
 }
 details.textContent='Röd: '+lines[0].name+'. Blå: '+lines[1].name+'. BMI ≥'+threshold+'. Urvalens nivåskillnad är deskriptiv, inte en beräknad fertilitetskorrelation.';
}
async function loadBMI(){
 try{const response=await fetch('data/bmi-comparison.json');if(!response.ok)throw Error('BMI-jämförelsefil saknas');bmiData=await response.json();renderBMI()}
 catch(e){el('bmi-load').textContent=e.message}
}
for(const id of ['bmi-threshold','bmi-scb-age','bmi-mfr-age'])el(id).addEventListener('change',renderBMI);


async function loadBMIFertilityCorrelations(){
 const result=el('bmi-correlation-results'),svg=el('bmi-fertility-scatter');
 try{
  const response=await fetch('data/bmi-fertility-exploratory.json');if(!response.ok)throw Error('Analysfilen har ännu inte publicerats.');
  const d=await response.json(),fmt=v=>v===null?'Ej beräkningsbart':new Intl.NumberFormat('sv-SE',{maximumFractionDigits:3}).format(v);
  result.replaceChildren();
  for(const [key,title] of [['overweight_or_obesity','BMI ≥25'],['obesity','BMI ≥30']]){
   const s=d.correlations[key],p=document.createElement('p');
   p.textContent=title+': '+s.n_periods+' perioder; korrelation mellan nivåer r = '+fmt(s.r_levels)+'; mellan periodförändringar r = '+fmt(s.r_consecutive_differences)+'.';
   result.append(p);
  }
  const rows=d.series.overweight_or_obesity;
  if(!rows?.length)return;
  const xs=rows.map(r=>r.bmi_pct),ys=rows.map(r=>r.births_per_1000),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys),ns='http://www.w3.org/2000/svg';
  const X=v=>75+(v-xmin)/(xmax-xmin||1)*860,Y=v=>310-(v-ymin)/(ymax-ymin||1)*250;
  svg.replaceChildren();
  function node(tag,attrs,label){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(label!==undefined)n.textContent=label;svg.append(n);return n}
  for(let i=0;i<=4;i++){
   const y=310-i*250/4;node('line',{x1:75,y1:y,x2:940,y2:y,stroke:'#e5e7eb'});
   node('text',{x:7,y:y+4},(ymin+(ymax-ymin)*i/4).toFixed(1).replace('.',','));
   node('text',{x:75+i*860/4-13,y:340},(xmin+(xmax-xmin)*i/4).toFixed(1).replace('.',','));
  }
  for(const r of rows){
   const dot=node('circle',{cx:X(r.bmi_pct),cy:Y(r.births_per_1000),r:5,fill:'#991b2b'});
   const title=document.createElementNS(ns,'title');title.textContent=r.period+': BMI ≥25 '+r.bmi_pct.toFixed(1).replace('.',',')+' %; födda per 1 000 kvinnor '+r.births_per_1000.toFixed(1).replace('.',',');dot.append(title);
  }
  node('text',{x:340,y:365},'Andel kvinnor med BMI ≥25 (%)');
 }catch(e){result.textContent='Kunde inte ladda korrelationerna: '+e.message}
}

start();fetchAges();loadVerifiedGBD();loadBMI();loadBMIFertilityCorrelations();