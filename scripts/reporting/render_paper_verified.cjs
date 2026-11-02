// Pass node_modules as argv[2] and optionally a browser executable as argv[3].
const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');
const {chromium} = require(path.join(process.argv[2], 'playwright'));
const root=path.resolve(__dirname,'../..');
(async()=>{
 const executable=process.argv[3] || process.env.AGERE_BROWSER || [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe'
 ].find(p=>fs.existsSync(p));
 const browser=await chromium.launch({...(executable ? {executablePath:executable} : {}),headless:true,args:['--allow-file-access-from-files']});
 try {
 const page=await browser.newPage();
 await page.goto(pathToFileURL(path.join(root,'output/paper/RESEARCH_PAPER.html')).href);
 await page.waitForFunction(()=>window.__rendered===true,{timeout:60000});
 await page.evaluate(async()=>{await document.fonts.ready; await Promise.all([...document.images].map(i=>i.decode()));});
 const audit=await page.evaluate(()=>({images:document.images.length,brokenImages:[...document.images].filter(i=>!i.naturalWidth).length,mathErrors:document.querySelectorAll('.katex-error').length,headings:document.querySelectorAll('h2').length}));
 if(audit.brokenImages||audit.mathErrors) throw new Error(JSON.stringify(audit));
 await page.evaluate(()=>{
   document.title='Quantized Monoliths and Full Precision Specialist Teams';
   document.querySelectorAll('p > img').forEach(img=>{
     const p=img.parentElement, cap=p.nextElementSibling;
     const fig=document.createElement('figure'); p.before(fig); fig.append(p);
     if(cap?.classList.contains('caption'))fig.append(cap);
   });
   document.querySelectorAll('table').forEach(t=>{
     t.querySelectorAll('td').forEach(c=>{if(/^(SAS|MAS)$/.test(c.textContent.trim()))c.style.whiteSpace='nowrap';});
     if(t.rows.length<=17)t.classList.add('short-table');
     const caption=t.previousElementSibling;
     if(t.rows[0]?.cells.length>=9 || (caption?.tagName==='P' && caption.textContent.startsWith('Table E'))){
       const wrap=document.createElement('div');wrap.className='wide-table';t.before(wrap);
       if(t.rows.length<=17)wrap.style.breakInside='avoid';
       const prev=wrap.previousElementSibling;
       if(prev?.tagName==='P' && prev.textContent.startsWith('Table E'))wrap.append(prev);
       wrap.append(t);
     }
   });
   document.querySelectorAll('p').forEach(p=>{
     if(p.textContent.startsWith('Table E')){p.style.breakAfter='avoid';p.style.breakInside='avoid';}
     const next=p.nextElementSibling;
     if(/^T\d+\./.test(p.textContent) && next && (next.matches('.katex-display')||next.querySelector('.katex-display'))){
       const w=document.createElement('div');w.style.breakInside='avoid';p.before(w);w.append(p,next);
     }
   });
   const style=document.createElement('style');style.textContent=`
   @page { size:A4; margin:18mm 16mm 19mm; }
   @page wide { size:A4 landscape; margin:17mm 14mm 18mm; }
   body { max-width:none; font-size:10.5pt; line-height:1.42; color:#161616; }
   h1 { color:#111; font-size:20pt; } h2,h3 { color:#111; }
   h2 { border:0; } p,li { text-align:left; orphans:3; widows:3; }
   table { break-inside:auto; font-size:8.5pt; } table.short-table {break-inside:avoid;} thead {display:table-header-group;} tr {break-inside:avoid;}
   th {background:#e8edf0;color:#111;} th,td {overflow-wrap:anywhere;}
   figure {margin:10pt 0; break-inside:avoid;} figure img {max-height:145mm;object-fit:contain;}
   .caption {color:#333;} .wide-table {page:wide;}
   .wide-table table {font-size:9pt;line-height:1.3;} pre {font-size:7.6pt;break-inside:avoid;}
   pre code {font-size:inherit;} .katex {font-size:1em;} .katex-display {overflow:visible;}
   h2 {break-after:avoid;} a {color:#16324f;text-decoration:none;} hr {display:none;}
   `;document.head.append(style);
 });
 await page.pdf({path:path.join(root,'output/pdf/RESEARCH_PAPER.pdf'),preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#555"><span class="pageNumber"></span></div>'});
 fs.writeFileSync(path.join(root,'output/paper/render_audit.json'),JSON.stringify(audit,null,2));
 console.log(JSON.stringify(audit));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
