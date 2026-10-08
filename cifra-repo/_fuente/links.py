import asyncio
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/-home-claude/e24c0a24-9621-5317-8341-bf33f574e495/scratchpad/'
ok=[];bad=[]
def chk(c,m): (ok if c else bad).append(m)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    for esq in ('dark','light'):
      pg=await (await b.new_context(viewport={'width':1440,'height':900},color_scheme=esq)).new_page()
      errs=[];fall=[]
      pg.on('pageerror',lambda e:errs.append(str(e)))
      # el .mp4 queda afuera: el servidor de prueba no soporta pedidos por rango y Chromium
      # cancela la descarga. En Cloudflare anda bien.
      pg.on('requestfailed',lambda r:fall.append(r.url) if ('127.0.0.1' in r.url and not r.url.endswith('.mp4')) else None)
      await pg.goto('http://127.0.0.1:8899/index.html',wait_until='load'); await pg.wait_for_timeout(2500)
      chk(not errs,f'{esq}: sin errores de JS {errs}')
      chk(not fall,f'{esq}: ningun archivo falla {fall}')
      d=await pg.evaluate("""()=>({
        nav:[...document.querySelectorAll('.navlinks > a')].map(a=>a.getAttribute('href')),
        trig:!!document.getElementById('trig-serv'),
        exp:document.getElementById('trig-serv').getAttribute('aria-expanded'),
        menu:[...document.querySelectorAll('#menu-serv a')].map(a=>a.getAttribute('href')),
        menuVis:getComputedStyle(document.getElementById('menu-serv')).visibility,
        lp:document.querySelectorAll('.lp-links,.lp-card').length,
        cards:[...document.querySelectorAll('.cinta-grupo:not([data-copia]) a.plat-link')].map(a=>[a.getAttribute('href'),a.querySelector('.plat-logo').naturalWidth,Math.round(a.querySelector('.plat-logo').getBoundingClientRect().height),a.querySelector('.plat-logo').currentSrc.split('/').pop(),a.getAttribute('aria-label'),!!a.querySelector('.plat-ir')]),
        foot:[...document.querySelectorAll('footer a')].map(a=>a.getAttribute('href')).filter(h=>h&&h.includes('-ads'))})""")
      chk(d['nav']==['#experiencia','#metodo'], f'{esq}: menu {d["nav"]}')
      chk(d['trig'] and d['exp']=='false' and d['menuVis']=='hidden', f'{esq}: el desplegable arranca cerrado ({d["exp"]}, {d["menuVis"]})')
      chk(d['menu']==['/google-ads/','/meta-ads/','#servicios'], f'{esq}: opciones del desplegable {d["menu"]}')
      chk(d['lp']==0, f'{esq}: el bloque "Páginas por servicio" ya no está ({d["lp"]})')
      chk([c[0] for c in d['cards']]==['/google-ads/','/meta-ads/'], f'{esq}: las dos tarjetas del carrusel linkean {[c[0] for c in d["cards"]]}')
      chk(all(c[1]>0 and c[2]>=20 and c[4] and c[5] for c in d['cards']), f'{esq}: con logo, aria y flechita {d["cards"]}')
      if esq=='dark': chk(all('oscuro' in c[3] for c in d['cards']), f'oscuro: variantes {[c[3] for c in d["cards"]]}')
      chk(d['foot']==['/google-ads/','/meta-ads/'], f'{esq}: footer {d["foot"]}')
      await pg.evaluate("document.querySelector('#plataformas').scrollIntoView({block:'center',behavior:'instant'})"); await pg.wait_for_timeout(1600)
      await pg.hover('a.plat-link', force=True); await pg.wait_for_timeout(800)
      tr=await pg.evaluate("()=>{const a=document.querySelector('a.plat-link');return [getComputedStyle(a).transform, getComputedStyle(a.querySelector('.plat-ir')).opacity, getComputedStyle(a).cursor]}")
      chk('-6' in tr[0] and float(tr[1])>0.9, f'{esq}: la tarjeta se levanta y muestra la flechita {tr}')
      await pg.screenshot(path=f'{OUT}links-{esq}.png')
      # desborde en todos los anchos
      for w in (1440,1280,1100,1024,980,900,768,620,430,390,360,320):
        await pg.set_viewport_size({'width':w,'height':900}); await pg.wait_for_timeout(380)
        ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        chk(ov<=0, f'{esq}: sin desborde a {w}px ({ov})')
      await pg.close()
    # idiomas
    pg=await (await b.new_context(viewport={'width':1440,'height':900})).new_page()
    await pg.goto('http://127.0.0.1:8899/index.html',wait_until='load'); await pg.wait_for_timeout(2200)
    for idi,esperado in (('en','Google Ads — see the page'),('pt','Google Ads — ver a página'),('it','Google Ads — vedi la pagina'),('fr','Google Ads — voir la page')):
      await pg.click(f'#idiomas button[data-idioma="{idi}"]'); await pg.wait_for_timeout(700)
      t=await pg.get_attribute('.cinta-grupo:not([data-copia]) a.plat-link[href="/google-ads/"]','aria-label')
      vacias=await pg.evaluate("[...document.querySelectorAll('[data-i18n]')].filter(e=>!e.textContent.trim()).length")
      chk(t==esperado and vacias==0, f'{idi}: aria de la tarjeta traducido ({t!r}, {vacias} textos vacios)')
    await pg.click('#idiomas button[data-idioma="es"]'); await pg.wait_for_timeout(500)
    # el link lleva a la landing
    await pg.evaluate("document.querySelector('#plataformas').scrollIntoView({block:'center',behavior:'instant'})"); await pg.wait_for_timeout(1600)
    # dejar la tarjeta de Google Ads bien centrada en su casillero y recien ahi clickearla
    pt=await pg.evaluate("""()=>{const e=window.CIFRA_CINTAS[0],k=window.CIFRA_CINTA_CASILLEROS(e);
      const t=[...e.c.querySelectorAll('a.plat-link[href="/google-ads/"]')][0];
      e.pos=t.offsetLeft-(k.ini+k.paso*0); e.resto=0;
      e.pista.style.transform='translate3d('+(-e.pos)+'px,0,0)';
      const r=e.c.getBoundingClientRect(), s=r.width/e.c.clientWidth, izq=t.offsetLeft-e.pos;
      return {x:r.left+(izq+t.offsetWidth/2)*s, y:r.top+r.height/2}}""")
    await pg.mouse.move(pt['x'],pt['y']); await pg.wait_for_timeout(900)
    await pg.mouse.click(pt['x'],pt['y']); await pg.wait_for_timeout(1700)
    chk(pg.url.endswith('/google-ads/'), f'la tarjeta del carrusel abre la landing ({pg.url})')
    chk('Google Ads' in (await pg.title()), f'y la landing carga ({await pg.title()})')
    await pg.close()

    # --- desplegable de Servicios ---
    pg=await (await b.new_context(viewport={'width':1440,'height':900},color_scheme='dark')).new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://127.0.0.1:8899/index.html',wait_until='load'); await pg.wait_for_timeout(2200)
    # se abre al pasar el mouse
    await pg.hover('#trig-serv'); await pg.wait_for_timeout(500)
    v=await pg.evaluate("()=>{const m=document.getElementById('menu-serv');const s=getComputedStyle(m);return [s.visibility,s.opacity,Math.round(m.getBoundingClientRect().height)]}")
    chk(v[0]=='visible' and float(v[1])>0.9 and v[2]>100, f'se abre al pasar el mouse ({v})')
    await pg.screenshot(path=f'{OUT}menu-dark.png')
    # los logos cargan
    lg=await pg.evaluate("[...document.querySelectorAll('#menu-serv .menu-punto')].map(i=>[Math.round(i.getBoundingClientRect().height),getComputedStyle(i).backgroundColor])")
    chk(len(lg)==2 and all(x[0]>=9 for x in lg) and lg[0][1]!=lg[1][1], f'cada opcion con el punto de su marca {lg}')
    # clickeable de verdad (no queda tapado)
    enc=await pg.evaluate("""()=>{const a=document.querySelector('#menu-serv .menu-item');const r=a.getBoundingClientRect();
      const e=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return !!(e&&e.closest('.menu-item'))}""")
    chk(enc, 'la opcion se puede clickear (el panel esta por encima)')
    # clic en el boton abre y cierra
    await pg.mouse.move(5,5); await pg.wait_for_timeout(400)
    await pg.click('#trig-serv'); await pg.wait_for_timeout(400)
    chk(await pg.get_attribute('#trig-serv','aria-expanded')=='true', 'el clic lo abre')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
    chk(await pg.get_attribute('#trig-serv','aria-expanded')=='false', 'Escape lo cierra')
    await pg.click('#trig-serv'); await pg.wait_for_timeout(300)
    await pg.mouse.click(720,700); await pg.wait_for_timeout(400)
    chk(await pg.get_attribute('#trig-serv','aria-expanded')=='false', 'tocar afuera lo cierra')
    # teclado: con foco en el boton se ve el panel
    await pg.keyboard.press('Tab')
    await pg.evaluate("document.getElementById('trig-serv').focus()"); await pg.wait_for_timeout(400)
    vis=await pg.evaluate("getComputedStyle(document.getElementById('menu-serv')).visibility")
    chk(vis=='visible', f'con foco de teclado tambien se abre ({vis})')
    # navegar a la landing desde el desplegable
    await pg.click('#trig-serv'); await pg.wait_for_timeout(300)
    await pg.click('#menu-serv a[href="/meta-ads/"]'); await pg.wait_for_timeout(1500)
    chk(pg.url.endswith('/meta-ads/'), f'el desplegable lleva a la landing ({pg.url})')
    chk(not errs, f'desplegable sin errores de JS {errs}')
    await pg.close()
    # el ancla "ver todos" baja a Servicios y cierra el panel
    pg=await (await b.new_context(viewport={'width':1440,'height':900})).new_page()
    await pg.goto('http://127.0.0.1:8899/index.html',wait_until='load'); await pg.wait_for_timeout(2200)
    await pg.click('#trig-serv'); await pg.wait_for_timeout(300)
    await pg.click('#menu-serv a[href="#servicios"]'); await pg.wait_for_timeout(1500)
    y=await pg.evaluate("Math.round(document.getElementById('servicios').getBoundingClientRect().top)")
    chk(abs(y)<200 and await pg.get_attribute('#trig-serv','aria-expanded')=='false', f'"ver todos" baja a Servicios y cierra ({y}px)')
    # traduccion del desplegable
    for idi,esp in (('en','See all services'),('fr','Voir tous les services')):
      await pg.click(f'#idiomas button[data-idioma="{idi}"]'); await pg.wait_for_timeout(500)
      t=await pg.text_content('.menu-todos')
      lab=await pg.get_attribute('#trig-serv','aria-label')
      fl=await pg.evaluate("()=>{const s=document.querySelector('#trig-serv svg');return s?Math.round(s.getBoundingClientRect().width):0}")
      chk(t.strip()==esp and fl>=10, f'{idi}: desplegable traducido y con su flechita ({t.strip()!r}, aria {lab!r}, flecha {fl}px)')
    await pg.close()


    # --- tarjetas del carrusel: copias fuera del tabulado y tarjeta cortada ---
    pg=await (await b.new_context(viewport={'width':1440,'height':900})).new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://127.0.0.1:8899/index.html',wait_until='load'); await pg.wait_for_timeout(2600)
    cop=await pg.evaluate("""()=>{const c=[...document.querySelectorAll('.cinta-grupo[data-copia] a.plat-link')];
      return [c.length, c.filter(a=>a.getAttribute('tabindex')==='-1').length]}""")
    chk(cop[0]>0 and cop[0]==cop[1], f'las copias no entran en el tabulado ({cop})')
    # primer clic sobre una tarjeta cortada: la acomoda, no navega
    await pg.evaluate("document.querySelector('#plataformas').scrollIntoView({block:'center',behavior:'instant'})"); await pg.wait_for_timeout(1500)
    pos=await pg.evaluate("""()=>{const e=window.CIFRA_CINTAS[0],k=window.CIFRA_CINTA_CASILLEROS(e);
      const a=[...e.c.querySelectorAll('a.plat-link')].map(t=>({izq:t.offsetLeft-e.pos,w:t.offsetWidth}));
      // corre la fila a mano para dejar una tarjeta cortada contra el borde derecho
      const t=[...e.c.querySelectorAll('a.plat-link')][0];
      e.pos = t.offsetLeft - (k.ini + k.n*k.paso - GAPX - t.offsetWidth/2); e.resto=0;
      e.pista.style.transform='translate3d('+(-e.pos)+'px,0,0)';
      const r=e.c.getBoundingClientRect(), s=r.width/e.c.clientWidth;
      const izq=t.offsetLeft-e.pos;
      return {x:r.left+(izq+t.offsetWidth*0.35)*s, y:r.top+r.height/2, izq}}""".replace('GAPX','14'))
    antes=pg.url
    await pg.mouse.click(pos['x'],pos['y']); await pg.wait_for_timeout(1400)
    chk(pg.url==antes, f'la tarjeta cortada se acomoda en vez de abrirse ({pg.url})')
    ent=await pg.evaluate("""p=>{const e=window.CIFRA_CINTAS[0],k=window.CIFRA_CINTA_CASILLEROS(e);
      const el=document.elementFromPoint(p.x,p.y), t=el&&el.closest('.plat');
      if(!t) return null;
      const izq=t.offsetLeft-e.pos;
      return [Math.round(izq), Math.round(k.ini), Math.round(izq+t.offsetWidth), Math.round(k.ini+k.n*k.paso-14)]}""", pos)
    chk(ent and ent[0]>=ent[1]-3 and ent[2]<=ent[3]+3, f'y queda entera a la vista {ent}')
    # el segundo clic (ya entera) si navega
    await pg.mouse.click(pos['x'],pos['y']); await pg.wait_for_timeout(1600)
    chk('-ads/' in pg.url, f'el segundo clic abre la landing ({pg.url})')
    chk(not errs, f'carrusel sin errores de JS {errs}')
    await pg.close()

    # celular
    ctx=await b.new_context(**p.devices['iPhone 13']); pg=await ctx.new_page()
    await pg.goto('http://127.0.0.1:8899/index.html',wait_until='load'); await pg.wait_for_timeout(2200)
    await pg.evaluate("document.querySelector('#plataformas').scrollIntoView({block:'center',behavior:'instant'})"); await pg.wait_for_timeout(1800)
    await pg.screenshot(path=f'{OUT}links-mob.png')
    alto=await pg.evaluate("[...document.querySelectorAll('a.plat-link')].map(a=>Math.round(a.getBoundingClientRect().height))")
    chk(len(alto)>=2 and all(h>=100 for h in alto), f'celular: tarjetas con buen tamaño {alto}')
    ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    chk(ov<=0, f'celular: sin desborde ({ov})')
    await b.close()
asyncio.run(main())
print('\n'.join('  OK  '+m for m in ok)); print()
print('\n'.join('  FALLA  '+m for m in bad) if bad else 'TODO OK'); print(f'{len(ok)} ok / {len(bad)} fallas')
