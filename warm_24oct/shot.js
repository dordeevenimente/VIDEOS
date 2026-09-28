const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/poster.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await p.screenshot({path:'WARM_directie_A.png'});await b.close();})();
