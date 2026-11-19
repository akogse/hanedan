// Bölüm simülasyonu: çizimden bağımsız, oyun mantığını 0.05 sn adımlarla çalıştırır; basit bir oyuncu botu kule kurar.
const { chromium } = require('playwright');
const stageId=+process.argv[2], plan=JSON.parse(process.argv[3]), out=process.argv[4];
(async () => {
  const b = await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
  const p = await b.newPage({viewport:{width:1280,height:720}});
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERR '+e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text().slice(0,200)); });
  await p.addInitScript(()=>{ let G; Object.defineProperty(window,'Phaser',{configurable:true,get(){return G},set(v){ const O=v.Game; v.Game=function(c){const g=new O(c); window.__g=g; return g}; v.Game.prototype=O.prototype; G=v; }});
    localStorage.setItem('hanedan-kusatmasi-save-v1',JSON.stringify({version:1,lang:'tr',identity:'commander',kingdom:'Test',bestStars:{1:5,2:5,3:5,4:5,5:5,6:5,7:5,8:5,9:5,10:5,11:5,12:5,13:5,14:5,15:5},tutorialDone:{basics:true,burn:true,combo:true,spell:true,hero:true,mine:true,flying:true,branch:true}}));});
  await p.goto('http://localhost:8765/index.html');
  for(let i=0;i<60;i++){ await p.waitForTimeout(3000); if(await p.evaluate(()=>window.__g&&['Opening','Intro','Map'].some(k=>window.__g.scene.isActive(k)))) break; } await p.waitForTimeout(5000);
  await p.evaluate((id)=>{ const g=window.__g; g.scene.scenes.forEach(s=>{ const k=s.sys.settings.key; if(k!=='Battle'&&k!=='Hud'&&s.sys.isActive()) g.scene.stop(k)}); const H=g.scene.getScene('Hud'); Object.getPrototypeOf(H).modal=function(){return Promise.resolve();}; g.scene.start('Battle',{stageId:id}); },stageId);
  await p.waitForTimeout(6000);
  const res=await p.evaluate((plan)=>{
    const sc=window.__g.scene.getScene('Battle'); const log={mineGold:0,bolt:0,boltDmg:0,kills:0,events:[]};
    const fc=sc.fx.coin.bind(sc.fx); sc.fx.coin=(x,y,a)=>{ if(sc.towers.some(t=>t&&t.def.id==="mine"&&t.x===x&&t.y-110===y)) log.mineGold+=a; return fc(x,y,a); };
    const oh=sc.combat.hit.bind(sc.combat); sc.combat.hit=(e,d,o)=>{ const r=oh(e,d,o); if(o.pierce!==undefined){log.bolt++; log.boltDmg+=r;} if(o.element==="lightning"){log.zap=(log.zap||0)+1; log.zapDmg=(log.zapDmg||0)+r;} if(e.flying){log.airHits=(log.airHits||0)+1;} if(o.element==="poison"){log.poisonHits=(log.poisonHits||0)+1; if(e.status.armorBrokenT>0) log.armorBroken=(log.armorBroken||0)+1;} return r; };
    const cf=sc.fx.comboFlash.bind(sc.fx); sc.fx.comboFlash=(a,b,c)=>{ log.combo=log.combo||{}; log.combo[c]=(log.combo[c]||0)+1; return cf(a,b,c); }; const ek=sc.enemyKilled.bind(sc); sc.enemyKilled=(e)=>{ log.kills++; if(e.flying) log.ravenKills=(log.ravenKills||0)+1; return ek(e); }; const er=sc.enemyReachedCastle.bind(sc); sc.enemyReachedCastle=(e)=>{ log.leak=(log.leak||[]); log.leak.push(e.def.id); return er(e); };
    sc.game.loop.sleep && sc.game.loop.sleep();
    let step=0, pi=0; const dt=50;
    sc.setPaused && sc.setPaused(false); sc.paused=false;
    const act=()=>{ while(pi<plan.length){ const [kind,spot,tower]=plan[pi];
        if(kind==='build'){ const c=sc.constructor; const cost= (sc.towers[spot]?null: window.__oe?0:0); }
        const t=sc.towers[spot];
        if(kind==='build'){ const lv1=sc.availableTowers? null:null; }
        // maliyeti kulenin kendisinden oku
        let cost;
        if(kind==='build'){ if(t){pi++;continue;} const tmp=sc.placeTower(spot,tower,1); cost=tmp.def.levels[0].cost; tmp.destroy(); sc.towers[spot]=null; sc.spotImgs[spot]?.setVisible(true);
          if(sc.gold<cost) return; sc.gold-=cost; sc.placeTower(spot,tower,1); log.events.push(`${(step*dt/1000).toFixed(0)}s kur ${tower}@${spot}`); pi++; }
        else if(kind==='dal'){ const DC={sniper:190,arrowRain:180,guards:190,berserkers:190,hellCatapult:230,flameBreath:220,iceSeal:200,blizzard:210,piercingSpear:240,hook:230,mint:200,treasureGuard:210,chainLightning:250,thunder:250,griffinRiders:220,eagleFlock:210,plague:220,acid:220,warRune:240,quakeRune:240};
          if(!t||t.level!==3||t.branch){pi++;continue;} cost=DC[tower]; if(sc.gold<cost) return; sc.gold-=cost; t.takeBranch(tower); log.events.push(`dal ${tower}`); pi++; }
        else { if(!t||t.level>=3){pi++;continue;} cost=t.def.levels[t.level].cost; if(sc.gold<cost) return; sc.gold-=cost; t.upgrade(); log.events.push(`${(step*dt/1000).toFixed(0)}s yükselt ${t.def.id}@${spot}->${t.level}`); pi++; } } };
    while(step<24000 && !sc.ended){
      act();
      if(!sc.waves.spawning && !sc.enemies.length && sc.waves.index+1<sc.waves.total) { try{ sc.startNextWave(); log.events.push(`${(step*dt/1000).toFixed(0)}s dalga ${sc.waves.index+1}`);}catch(e){log.events.push('wave err '+e.message);} }
      sc.paused=false; sc.speed=1/(window.OYUN_TEMPO||1); sc.update(0,dt); step++;
    }
    const hp=sc.castleHp; log.wave=sc.waves.index+1; log.alive=sc.enemies.length;
    return {ended:sc.ended, victory:sc.victory, time:(step*dt/1000).toFixed(0), castle:hp, gold:sc.gold, ...log};
  },plan);
  if(res.leak){const c={};res.leak.forEach(x=>c[x]=(c[x]||0)+1);res.leak=c;} res.events=res.events.filter(x=>x.includes("dalga")); console.log(JSON.stringify(res));
  await p.screenshot({path:out});
  console.log('errors:',errs.length?errs.join('\n'):'none'); await b.close();
})();
