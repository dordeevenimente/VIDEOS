const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const jobs=[];
for(const t of ['promo','g1','g2','g3']) for(const f of ['feed','story']) jobs.push([`k=tier&t=${t}&f=${f}`,`WARM_ENTRADAS_${t}_${f}`]);
for(const f of ['feed','story']) jobs.push([`k=ladder&t=promo&f=${f}`,`WARM_ENTRADAS_calendario_${f}`]);
for(const t of ['promo','g1','g2']) jobs.push([`k=last&t=${t}&f=story`,`WARM_ENTRADAS_ultimas_horas_${t}_story`]);
for(const t of ['promo','g1','g2']) jobs.push([`k=soldout&t=${t}&f=story`,`WARM_ENTRADAS_soldout_${t}_story`]);
const only=process.argv[2];
(async()=>{const b=await chromium.launch();
for(const [qs,name] of jobs){ if(only && !name.includes(only)) continue;
 const story=qs.includes('f=story');
 const p=await b.newPage({viewport:{width:1080,height:story?1920:1350}});
 await p.goto('file://'+__dirname+'/ticket.html?'+qs);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
 await p.screenshot({path:`out/${name}.png`});await p.close();}
await b.close();})();
