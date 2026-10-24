const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();
for(const [f,h] of [['story',1920],['feed',1350]]){
const p=await b.newPage({viewport:{width:1080,height:h}});await p.goto('file://'+__dirname+'/timetable.html?f='+f);
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.screenshot({path:`FINAL/timetable/WARM_24oct_TIMETABLE_${f==='story'?'STORY_1080x1920':'FEED_1080x1350'}.png`});await p.close();}
await b.close();})();
