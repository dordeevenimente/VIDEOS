const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/overlay.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
for(const id of ['warm','s1','s2','s3','s4','end']){
 await p.evaluate(id=>{document.querySelectorAll('.L').forEach(e=>e.classList.toggle('on',e.id===id));},id);
 await p.screenshot({path:`ov_${id}.png`,omitBackground:true});}
await b.close();})();
