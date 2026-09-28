const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const L={
 photo:['.halo','.photo'], warm:['.head'], j2:['.lineup .j2'],
 n1:['.lineup .n:nth-of-type(1)'], n2:['.lineup .n:nth-of-type(2)'], n3:['.lineup .n:nth-of-type(3)'],
 venue:['.fvenue'], date:['.fdate'], l1:['.finfo .l1'], l2:['.finfo .l2'], l3:['.finfo .l3']};
const ALL=Object.values(L).flat();
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/layers_feed.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
for(const [k,sel] of Object.entries(L)){
  await p.evaluate(([all,show,k])=>{document.querySelectorAll(all.join(',')).forEach(e=>e.classList.add('hid'));
    document.querySelectorAll(show.join(',')).forEach(e=>e.classList.remove('hid'));
    document.body.classList.toggle('noscrim',k!=='photo');},[ALL,sel,k]);
  await p.screenshot({path:`layerF_${k}.png`,omitBackground:true});}
await b.close();})();
