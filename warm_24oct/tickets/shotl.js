const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/ladder.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.screenshot({path:'out/WARM_ENTRADAS_calendario_v2_feed.png'});await b.close();})();
