import asyncio, json
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/-home-claude/e24c0a24-9621-5317-8341-bf33f574e495/scratchpad/'
IDI=['es','en','pt','it','fr']
ok=[];bad=[]
def chk(c,m): (ok if c else bad).append(m)
ES=json.load(open('i18n/es.json',encoding='utf-8'))
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    for slug,pref in (('google-ads','ga'),('meta-ads','ma')):
      # --- ?lang= en la URL ---
      for l in IDI:
        ctx=await b.new_context(viewport={'width':1440,'height':900},color_scheme='dark')
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        url=f'http://127.0.0.1:8899/{slug}/' + ('' if l=='es' else f'?lang={l}')
        await pg.goto(url,wait_until='load'); await pg.wait_for_timeout(1500)
        d=await pg.evaluate("""()=>({lang:document.documentElement.lang,t:document.title,
          desc:document.querySelector('meta[name=description]').content,
          h1:document.querySelector('h1').textContent,
          vacias:[...document.querySelectorAll('[data-i18n],[data-i18n-html]')].filter(e=>!e.textContent.trim()).map(e=>e.getAttribute('data-i18n')||e.getAttribute('data-i18n-html')),
          ph:[...document.querySelectorAll('[data-i18n-ph]')].filter(e=>!e.placeholder).length,
          fila:[...document.querySelectorAll('#idiomas button')].map(x=>x.textContent),
          activo:(document.querySelector('#idiomas button[aria-pressed=true]')||{}).textContent,
          dot:!!document.querySelector('h1 .dot'),
          ov:document.documentElement.scrollWidth-document.documentElement.clientWidth})""")
        esp_t=json.load(open(f'i18n/{l}.json',encoding='utf-8'))[f'{pref}.meta.title']
        esp_h1=json.load(open(f'i18n/{l}.json',encoding='utf-8'))[f'{pref}.hero.h1']
        chk(d['lang']==l, f'{slug} ?lang={l}: atributo lang ({d["lang"]})')
        chk(d['t']==esp_t, f'{slug} {l}: title traducido ({d["t"][:40]}…)')
        chk(esp_h1 in d['h1'] and d['dot'], f'{slug} {l}: h1 traducido y con el punto rojo ({d["h1"][:45]}…)')
        chk(not d['vacias'] and d['ph']==0, f'{slug} {l}: ninguna clave sin texto {d["vacias"][:4]}')
        chk(d['fila']==['ES','EN','PT','IT','FR'] and (d['activo'] or '').lower()==l, f'{slug} {l}: fila de idiomas marcando {d["activo"]}')
        chk(d['ov']<=0, f'{slug} {l}: sin desborde ({d["ov"]})')
        chk(not errs, f'{slug} {l}: sin errores de JS {errs}')
        await ctx.close()
      # --- cambiar de idioma con los botones + persistencia ---
      ctx=await b.new_context(viewport={'width':1440,'height':900}); pg=await ctx.new_page()
      await pg.goto(f'http://127.0.0.1:8899/{slug}/',wait_until='load'); await pg.wait_for_timeout(1500)
      await pg.click('#idiomas button[data-idioma="fr"]'); await pg.wait_for_timeout(700)
      fr=json.load(open('i18n/fr.json',encoding='utf-8'))
      d=await pg.evaluate("""()=>({t:document.title,btn:document.querySelector('#contact-form button').textContent,
        faq:document.querySelector('.faq-item summary').textContent,
        lbl:document.querySelector('label[for=f-desafio]').textContent,
        ph:document.querySelector('#f-desafio').placeholder})""")
      chk(d['t']==fr[f'{pref}.meta.title'] and d['btn']==fr['comun.form.btn'], f'{slug}: botones cambian el idioma ({d["btn"]})')
      chk(d['faq']==fr[f'{pref}.faq1.q'] and d['lbl']==fr[f'{pref}.form.desafio'] and d['ph']==fr[f'{pref}.form.ph4'],
          f'{slug}: preguntas y formulario en frances ({d["faq"][:30]}…)')
      await pg.reload(wait_until='load'); await pg.wait_for_timeout(1400)
      chk(await pg.evaluate("document.documentElement.lang")=='fr', f'{slug}: el idioma elegido sobrevive al recargar')
      # ?lang manda sobre lo guardado
      await pg.goto(f'http://127.0.0.1:8899/{slug}/?lang=pt',wait_until='load'); await pg.wait_for_timeout(1300)
      chk(await pg.evaluate("document.documentElement.lang")=='pt', f'{slug}: ?lang manda sobre lo guardado')
      # el WhatsApp sale en el idioma activo
      await pg.hover('.wa-float'); await pg.wait_for_timeout(400)
      h=await pg.get_attribute('.wa-float','href')
      chk(h and 'wa.me' in h and 'proposta' in h, f'{slug}: mensaje de WhatsApp en portugues ({h[-40:] if h else h})')
      await ctx.close()
      # --- frances en celular, que es el idioma mas largo ---
      ctx=await b.new_context(**p.devices['iPhone 13'],color_scheme='dark'); pg=await ctx.new_page()
      await pg.goto(f'http://127.0.0.1:8899/{slug}/?lang=fr',wait_until='load'); await pg.wait_for_timeout(1600)
      ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
      chk(ov<=0, f'{slug} celular en frances: sin desborde ({ov})')
      if slug=='google-ads': await pg.screenshot(path=OUT+'lp-fr-mob.png')
      await ctx.close()
    # captura de las dos en ingles
    for slug in ('google-ads','meta-ads'):
      ctx=await b.new_context(viewport={'width':1440,'height':900},color_scheme='dark'); pg=await ctx.new_page()
      await pg.goto(f'http://127.0.0.1:8899/{slug}/?lang=en',wait_until='load'); await pg.wait_for_timeout(1600)
      await pg.screenshot(path=OUT+f'lp-{slug}-en.png')
      await ctx.close()
    await b.close()
asyncio.run(main())
print('\n'.join('  OK  '+m for m in ok)); print()
print('\n'.join('  FALLA  '+m for m in bad) if bad else 'TODO OK'); print(f'{len(ok)} ok / {len(bad)} fallas')
