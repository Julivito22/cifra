import asyncio
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/-home-claude/e24c0a24-9621-5317-8341-bf33f574e495/scratchpad/'
PAGS=['google-ads','meta-ads']
ok=[];bad=[]
def chk(c,m): (ok if c else bad).append(m)

async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    for slug in PAGS:
      for esq in ('light','dark'):
        ctx=await b.new_context(viewport={'width':1440,'height':900}, color_scheme=esq)
        pg=await ctx.new_page()
        errs=[];fallos=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('requestfailed',lambda r:fallos.append(r.url) if '127.0.0.1' in r.url else None)
        await pg.goto(f'http://127.0.0.1:8899/{slug}/',wait_until='load'); await pg.wait_for_timeout(1800)
        chk(not errs, f'{slug} {esq}: sin errores de JS {errs}')
        chk(not fallos, f'{slug} {esq}: ningun archivo propio falla {fallos}')
        # logo de la plataforma
        lg=await pg.evaluate("()=>{const i=document.querySelector('.lp-sello img');return [i.naturalWidth, i.currentSrc.split('/').pop(), Math.round(i.getBoundingClientRect().height)]}")
        chk(lg[0]>0 and lg[2]>=18, f'{slug} {esq}: logo cargado ({lg[1]}, {lg[2]}px)')
        if esq=='dark': chk('oscuro' in lg[1], f'{slug}: en oscuro usa la variante -oscuro ({lg[1]})')
        # desborde horizontal en varios anchos
        for w in (1440,1280,1024,900,768,600,430,390,360,320):
          await pg.set_viewport_size({'width':w,'height':900}); await pg.wait_for_timeout(350)
          ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
          chk(ov<=0, f'{slug} {esq}: sin desborde a {w}px ({ov})')
        await pg.set_viewport_size({'width':1440,'height':900}); await pg.wait_for_timeout(400)
        if esq=='dark':
          await pg.screenshot(path=f'{OUT}lp-{slug}-hero.png')
          await pg.evaluate("document.querySelector('#incluye').scrollIntoView({block:'start',behavior:'instant'})"); await pg.wait_for_timeout(1200)
          await pg.screenshot(path=f'{OUT}lp-{slug}-incluye.png')
          await pg.evaluate("document.querySelector('#honestidad').scrollIntoView({block:'center',behavior:'instant'})"); await pg.wait_for_timeout(1200)
          await pg.screenshot(path=f'{OUT}lp-{slug}-nope.png')
        else:
          await pg.evaluate("document.querySelector('#preguntas').scrollIntoView({block:'start',behavior:'instant'})"); await pg.wait_for_timeout(900)
          await pg.click('.faq-item:nth-child(2) summary'); await pg.wait_for_timeout(600)
          abierto=await pg.evaluate("document.querySelectorAll('.faq-item[open]').length")
          chk(abierto==1, f'{slug}: las preguntas abren ({abierto})')
          await pg.screenshot(path=f'{OUT}lp-{slug}-faq.png')
        await ctx.close()

      # contenido y SEO
      ctx=await b.new_context(viewport={'width':1440,'height':900}); pg=await ctx.new_page()
      await pg.goto(f'http://127.0.0.1:8899/{slug}/',wait_until='load'); await pg.wait_for_timeout(1200)
      d=await pg.evaluate("""()=>({
        h1:document.querySelectorAll('h1').length, h1t:document.querySelector('h1').textContent,
        canon:document.querySelector('link[rel=canonical]').href,
        titulo:document.title, desc:document.querySelector('meta[name=description]').content.length,
        ld:[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>JSON.parse(s.textContent)['@type']),
        form:!!document.getElementById('contact-form'),
        formid:window.CIFRA_FORM_ID,
        pagina:document.querySelector('input[name="Página"]').value,
        key:document.querySelector('input[name=access_key]').value.length,
        wa:document.querySelectorAll('a[data-wa]').length,
        waHref:[...document.querySelectorAll('a[data-wa]')].map(a=>a.getAttribute('href')),
        num:document.documentElement.innerHTML.includes('1178173247'),
        secs:[...document.querySelectorAll('section[id]')].map(s=>s.id),
        faqs:document.querySelectorAll('.faq-item').length,
        cards:document.querySelectorAll('#incluye .serv').length,
        inicio:document.querySelector('nav .wm').getAttribute('href'),
        gtag:typeof gtag})""")
      chk(d['h1']==1, f'{slug}: un solo h1 ({d["h1"]})')
      chk(d['canon']==f'https://cifragrowth.com/{slug}/', f'{slug}: canonical correcto ({d["canon"]})')
      chk(40<len(d['titulo'])<65, f'{slug}: largo del title {len(d["titulo"])} — "{d["titulo"]}"')
      chk(120<=d['desc']<=165, f'{slug}: largo de la meta description {d["desc"]}')
      chk(d['ld']==['Service','FAQPage'], f'{slug}: datos estructurados {d["ld"]}')
      chk(d['form'] and d['key']==36, f'{slug}: formulario con su clave')
      chk(d['formid']=='lp_'+slug.replace('-','_'), f'{slug}: id de formulario propio ({d["formid"]})')
      chk(d['pagina'] and d['pagina'] in ('Google Ads','Meta Ads'), f'{slug}: el mail dice de qué página vino ({d["pagina"]})')
      chk(d['wa']>=2 and all(h=='#contacto' for h in d['waHref']) and not d['num'],
          f'{slug}: el numero de WhatsApp no esta en el HTML ({d["waHref"]})')
      chk(d['secs']==['inicio','incluye','arranque','honestidad','preguntas','contacto'], f'{slug}: secciones {d["secs"]}')
      chk(d['faqs']>=5 and d['cards']==6, f'{slug}: {d["cards"]} bloques y {d["faqs"]} preguntas')
      chk(d['inicio']=='/', f'{slug}: el logo vuelve al inicio ({d["inicio"]})')
      chk(d['gtag']=='function', f'{slug}: gtag cargado')
      # el WhatsApp se arma al pasar por encima
      await pg.hover('.wa-float'); await pg.wait_for_timeout(300)
      h=await pg.get_attribute('.wa-float','href')
      chk(h and 'wa.me' in h and 'text=' in h, f'{slug}: el link de WhatsApp se arma al tocarlo')
      # la conversión se dispara al enviar (Web3Forms interceptado)
      await pg.route('https://api.web3forms.com/**', lambda r: asyncio.ensure_future(r.fulfill(status=200, content_type='application/json', body='{"success":true}')))
      await pg.evaluate("window.__ev=[];window.gtag=function(){window.__ev.push([...arguments])}")
      await pg.fill('#f-nombre','Prueba'); await pg.fill('#f-email','prueba@ejemplo.com')
      await pg.click('#contact-form button[type=submit]'); await pg.wait_for_timeout(1200)
      ev=await pg.evaluate("window.__ev")
      lead=[e for e in ev if len(e)>1 and e[1]=='generate_lead']
      conv=[e for e in ev if len(e)>1 and e[1]=='conversion']
      ud=[e for e in ev if e[0]=='set' and e[1]=='user_data']
      chk(lead and lead[0][2].get('form_id')=='lp_'+slug.replace('-','_'), f'{slug}: generate_lead con el id de la landing ({lead})')
      chk(conv and conv[0][2]['send_to'].startswith('AW-18430783545/'), f'{slug}: conversión de Ads disparada')
      chk(bool(ud), f'{slug}: conversiones avanzadas (mail hasheado por gtag)')
      txt=await pg.text_content('#form-status')
      chk('Listo' in txt, f'{slug}: mensaje de ok al enviar ({txt!r})')
      await ctx.close()

      # celular
      ctx=await b.new_context(**p.devices['iPhone 13'], color_scheme='dark'); pg=await ctx.new_page()
      await pg.goto(f'http://127.0.0.1:8899/{slug}/',wait_until='load'); await pg.wait_for_timeout(1600)
      await pg.screenshot(path=f'{OUT}lp-{slug}-mob.png')
      t=await pg.evaluate("""()=>{const r=[];document.querySelectorAll('.btn, .navcta, .faq-item summary').forEach(e=>{
        const b=e.getBoundingClientRect(); if(b.height<40) r.push([e.textContent.trim().slice(0,18), Math.round(b.height)])});return r}""")
      chk(not t, f'{slug} celular: todo lo tocable mide 40px o mas {t}')
      ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
      chk(ov<=0, f'{slug} celular: sin desborde ({ov})')
      await ctx.close()
    await b.close()

asyncio.run(main())
print('\n'.join('  OK  '+m for m in ok)); print()
print('\n'.join('  FALLA  '+m for m in bad) if bad else 'TODO OK')
print(f'{len(ok)} ok / {len(bad)} fallas')
