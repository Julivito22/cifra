# Genera las landings por servicio (google-ads, meta-ads) reutilizando el CSS, los
# scripts y el motor de idiomas de index.html. No se copia nada a mano: si manana
# cambia el diseno del sitio, se vuelve a correr este script y las landings quedan
# iguales al sitio.
#
# Los textos salen de i18n/<idioma>.json (es, en, pt, it, fr). El espanol es la
# fuente y vive en lp_es.py; las otras cuatro lenguas tienen que tener las mismas
# claves. Prefijos: comun.* va en las dos paginas, ga.* Google Ads, ma.* Meta Ads.
import re, os, json, datetime

IDIOMAS = ['es', 'en', 'pt', 'it', 'fr']
TXT = {l: json.load(open('i18n/%s.json' % l, encoding='utf-8')) for l in IDIOMAS}
for l in IDIOMAS[1:]:
    faltan = set(TXT['es']) - set(TXT[l])
    if faltan:
        raise SystemExit('a %s le faltan %d claves: %s' % (l, len(faltan), sorted(faltan)[:5]))

SRC = 'index.html'
s = open(SRC, encoding='utf-8').read()


def script_con(txt):
    """Devuelve el <script>...</script> que contiene ese texto."""
    i = s.index(txt)
    ini = s.rindex('<script', 0, i)
    fin = s.index('</script>', i) + len('</script>')
    return s[ini:fin]


GTM       = s[s.index('<!-- Google Tag Manager -->'):s.index('<!-- End Google Tag Manager -->')+len('<!-- End Google Tag Manager -->')]
GTM_NS    = s[s.index('<!-- Google Tag Manager (noscript) -->'):s.index('<!-- End Google Tag Manager (noscript) -->')+len('<!-- End Google Tag Manager (noscript) -->')]
CFG       = script_con('window.CIFRA_TRACKING = {')
GTAG      = script_con("gtag('config', window.CIFRA_TRACKING.ADS_ID)")
FUENTES   = re.search(r'<link href="https://fonts\.googleapis[^>]*/?>', s).group(0)
STYLE     = re.search(r'<style>.*?</style>', s, re.S).group(0)

SC_FORM   = script_con('// Conversión: se dispara una sola vez')
SC_WA     = script_con('// El numero de WhatsApp no esta escrito')
SC_MAIL   = script_con('// El mail: mailto: no hace NADA')
SC_WACLIC = script_con('// Marca los clics a WhatsApp como evento')
SC_FONDO  = script_con('// Fondo de puntos en 3D')
SC_TILT   = script_con('// Inclinacion 3D al scrollear')
SC_CARTAS = script_con('// Tarjetas vivas.')
SC_SUBIR  = script_con('// Volver arriba')
SC_REVEAL = script_con('// Entrada al scrollear')
SC_FILA   = script_con('// Idiomas en fila.')      # arma los botones ES EN PT IT FR
SC_I18N   = script_con('window.CIFRA_SET_IDIOMA = aplicar;')

# el id del formulario se vuelve configurable, asi en GA4 se ve de que pagina vino el lead
SC_FORM = SC_FORM.replace("'contacto_landing'", "(window.CIFRA_FORM_ID || 'contacto_landing')")
# el reveal mira selectores del sitio; las landings reusan .sec-head/.serv/.fase y suman el FAQ
SC_REVEAL = SC_REVEAL.replace(".contacto-grid > div'", ".contacto-grid > div, .faq-item'")

BOTONES = '''<button aria-label="Volver arriba" class="subir" data-i18n-aria="aria.subir" id="subir" type="button">↑</button>
<a aria-label="Escribinos por WhatsApp" class="wa-float" data-i18n-aria="aria.wa" href="#contacto" data-wa rel="noopener" target="_blank">
''' + re.search(r'<svg aria-hidden="true" viewbox="0 0 24 24"><path d="M17\.472.*?</svg>', s, re.S).group(0) + '''
<span>WhatsApp</span>
</a>'''

CSS_LP = '''
<style>
/* ---- Landings por servicio ---------------------------------------------- */
/* Hereda todo el diseno del sitio. Lo unico propio: el sello de la plataforma,
   la linea de confianza del hero, la lista de "lo que no" y el acordeon de preguntas. */
.lp-sello{display:inline-flex;align-items:center;gap:12px;background:color-mix(in srgb, var(--papel-raised) 88%, transparent);
  border:1px solid var(--line);border-radius:999px;padding:9px 18px 9px 14px;margin-bottom:22px;box-shadow:var(--sombra)}
.lp-sello img{height:22px;width:auto;display:block}
.lp-sello span{font-family:'IBM Plex Mono',monospace;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--tinta-soft)}
.lp-sello::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--marca);flex:none}
.lp-trust{display:flex;flex-wrap:wrap;gap:10px 22px;margin:26px 0 0;padding:0;list-style:none;
  font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:var(--tinta-soft)}
.lp-trust li{display:flex;align-items:center;gap:9px}
.lp-trust li::before{content:"";width:14px;height:2px;border-radius:2px;background:var(--rojo);flex:none}
.lp-serv-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
@media(max-width:1040px){.lp-serv-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:680px){.lp-serv-grid{grid-template-columns:minmax(0,1fr)}}
.lp-serv-grid .serv{padding:28px}
.lp-serv-grid .serv h3{font-size:19px}
/* lo que no hacemos */
.nope{background:color-mix(in srgb, var(--papel-raised) 88%, transparent);border:1px solid var(--line);
  border-radius:var(--r-lg);padding:38px 40px;display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);
  gap:34px;align-items:start;box-shadow:var(--sombra)}
@media(max-width:860px){.nope{grid-template-columns:minmax(0,1fr);padding:30px 24px;gap:22px}}
.nope h2{font-weight:800;font-size:clamp(24px,2.8vw,32px);line-height:1.12;margin:0;max-width:18ch}
.nope ul{margin:0;padding:0;list-style:none;display:grid;gap:16px}
.nope li{display:grid;grid-template-columns:22px minmax(0,1fr);gap:14px;align-items:start;color:var(--tinta-soft);font-size:15.5px}
.nope li b{color:var(--tinta);font-weight:600;display:block;margin-bottom:2px}
.nope .x{width:22px;height:22px;border-radius:50%;border:1px solid var(--line);display:grid;place-items:center;
  color:var(--rojo);font-size:12px;line-height:1;margin-top:2px}
/* preguntas */
.faq{display:grid;gap:12px;max-width:860px}
.faq-item{background:color-mix(in srgb, var(--papel-raised) 88%, transparent);border:1px solid var(--line);
  border-radius:var(--r);overflow:hidden;transition:border-color .18s ease,box-shadow .18s ease}
.faq-item[open]{border-color:color-mix(in srgb, var(--rojo) 38%, var(--line));box-shadow:var(--sombra)}
.faq-item summary{list-style:none;cursor:pointer;padding:20px 24px;display:flex;align-items:center;gap:16px;
  font-weight:600;font-size:16.5px}
.faq-item summary::-webkit-details-marker{display:none}
.faq-item summary::after{content:"+";margin-left:auto;color:var(--rojo);font-family:'IBM Plex Mono',monospace;
  font-size:19px;line-height:1;transition:transform .2s ease}
.faq-item[open] summary::after{content:"–"}
.faq-item summary:hover{color:var(--rojo)}
.faq-item summary:focus-visible{outline:2px solid var(--rojo);outline-offset:-2px;border-radius:var(--r)}
.faq-item p{margin:0;padding:0 24px 22px;color:var(--tinta-soft);font-size:15.5px;max-width:72ch}
@media (prefers-reduced-motion: reduce){.faq-item{transition:none}}
</style>'''


def dic_pagina(pref):
    """Diccionario de la pagina: las claves comun.* y las del prefijo, sin el prefijo."""
    d = {}
    for k in TXT['es']:
        if k.startswith('comun.'):
            corta = k[len('comun.'):]
        elif k.startswith(pref + '.'):
            corta = k[len(pref) + 1:]
        else:
            continue
        d[corta] = {l: TXT[l][k] for l in IDIOMAS}
    # El h1 y el titulo de "lo que no" llevan el punto rojo de la marca, y se aplican
    # con data-i18n-html (reemplaza el innerHTML). Si el texto fuera plano, al cambiar
    # de idioma el punto desaparecia: se lo agregamos a cada traduccion.
    for clave in ('hero.h1', 'nope.h2'):
        if clave in d:
            d[clave] = {l: v.rstrip('.').rstrip() + '<span class="dot">.</span>'
                        for l, v in d[clave].items()}
    return d


def t(pref, clave, idioma='es'):
    """Texto en espanol de una clave (para el HTML servido sin JS y el JSON-LD)."""
    k = clave if clave.startswith('comun.') else pref + '.' + clave
    return TXT[idioma][k]


def pagina(p):
    pref = p['pref']
    anio = datetime.date.today().year
    E = lambda c: t(pref, c)                      # texto en espanol
    K = lambda c: c if c.startswith('comun.') else c   # la clave va sin prefijo en el DIC
    corta = lambda c: c[len('comun.'):] if c.startswith('comun.') else c

    def i18n(c, attr='data-i18n'):
        return '%s="%s"' % (attr, corta(c))

    inc = '\n'.join(
        '<div class="serv"><h3 %s>%s</h3><p %s>%s</p><ul><li %s>%s</li><li %s>%s</li><li %s>%s</li></ul></div>' % (
            i18n('inc%d.t' % n), E('inc%d.t' % n), i18n('inc%d.p' % n), E('inc%d.p' % n),
            i18n('inc%d.a' % n), E('inc%d.a' % n), i18n('inc%d.b' % n), E('inc%d.b' % n),
            i18n('inc%d.c' % n), E('inc%d.c' % n))
        for n in range(1, 7))
    fases = '\n'.join(
        '<div class="fase"><div class="n">0%d</div><h3 %s>%s</h3><p %s>%s</p></div>' % (
            n, i18n('fase%d.t' % n), E('fase%d.t' % n), i18n('fase%d.d' % n), E('fase%d.d' % n))
        for n in range(1, 5))
    nope = '\n'.join(
        '<li><span class="x" aria-hidden="true">✕</span><span><b %s>%s</b><span %s>%s</span></span></li>' % (
            i18n('nope%d.t' % n), E('nope%d.t' % n), i18n('nope%d.d' % n), E('nope%d.d' % n))
        for n in range(1, 5))
    faq = '\n'.join(
        '<details class="faq-item"><summary %s>%s</summary><p %s>%s</p></details>' % (
            i18n('faq%d.q' % n), E('faq%d.q' % n), i18n('faq%d.a' % n), E('faq%d.a' % n))
        for n in range(1, 7))

    ld = {
      "@context": "https://schema.org",
      "@type": "Service",
      "name": p['servicio'],
      "serviceType": p['servicio'],
      "url": "https://cifragrowth.com/%s/" % p['slug'],
      "areaServed": {"@type": "Country", "name": "Argentina"},
      "provider": {"@type": "ProfessionalService", "name": "Cifra",
                   "url": "https://cifragrowth.com/",
                   "email": "cifra@cifragrowth.com",
                   "address": {"@type": "PostalAddress", "addressLocality": "Buenos Aires",
                               "addressCountry": "AR"}},
      "description": E('meta.desc')
    }
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": E('faq%d.q' % n),
                              "acceptedAnswer": {"@type": "Answer", "text": E('faq%d.a' % n)}}
                             for n in range(1, 7)]}

    # el motor de idiomas del sitio, con el diccionario de esta pagina
    dic = json.dumps(dic_pagina(pref), ensure_ascii=False, sort_keys=True)
    motor = re.sub(r'var DIC = \{.*?\};', 'var DIC = %s;' % dic.replace('\\', '\\\\'), SC_I18N, count=1, flags=re.S)
    assert dic[:40] in motor, 'no se pudo inyectar el diccionario'

    # alternativas por idioma: misma URL con ?lang=
    alternos = '\n'.join(
        '<link rel="alternate" hreflang="%s" href="https://cifragrowth.com/%s/%s"/>' % (
            l, p['slug'], '' if l == 'es' else '?lang=' + l) for l in IDIOMAS) + \
        '\n<link rel="alternate" hreflang="x-default" href="https://cifragrowth.com/%s/"/>' % p['slug']

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
{GTM}
{CFG}
<script>window.CIFRA_FORM_ID = '{p["form_id"]}';</script>
{GTAG}
{motor}
<title>{E('meta.title')}</title>
<meta content="{E('meta.desc')}" name="description"/>
<link href="https://cifragrowth.com/{p["slug"]}/" rel="canonical"/>
{alternos}
<meta content="index, follow, max-image-preview:large" name="robots"/>
<meta content="#FAF8F4" media="(prefers-color-scheme: light)" name="theme-color"/>
<meta content="#17140F" media="(prefers-color-scheme: dark)" name="theme-color"/>
<meta content="website" property="og:type"/>
<meta content="Cifra" property="og:site_name"/>
<meta content="es_AR" property="og:locale"/>
<meta content="https://cifragrowth.com/{p["slug"]}/" property="og:url"/>
<meta content="{p["og_title"]}" property="og:title"/>
<meta content="{E('meta.desc')}" property="og:description"/>
<meta content="https://cifragrowth.com/og-cifra.jpg" property="og:image"/>
<meta content="1200" property="og:image:width"/>
<meta content="630" property="og:image:height"/>
<meta content="image/jpeg" property="og:image:type"/>
<meta content="{p["og_title"]}" property="og:image:alt"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="{p["og_title"]}" name="twitter:title"/>
<meta content="{E('meta.desc')}" name="twitter:description"/>
<meta content="https://cifragrowth.com/og-cifra.jpg" name="twitter:image"/>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, indent=1)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False, indent=1)}</script>
<link rel="icon" href="/icon-32.png" sizes="32x32"/>
<link rel="apple-touch-icon" href="/apple-touch-icon.png"/>
{FUENTES}
{STYLE}
{CSS_LP}
</head>
<body style="--marca:{p["marca"]}">
<canvas id="fondo" aria-hidden="true"></canvas>
{GTM_NS}
<nav>
<div class="inner">
<a aria-label="Cifra — ir al inicio" data-i18n-aria="aria.inicio" class="wm" href="/" style="text-decoration:none">cifra<span class="dot">.</span></a>
<div class="navlinks">
<a data-i18n="nav.inc" href="#incluye">{E('comun.nav.inc')}</a>
<a data-i18n="nav.arr" href="#arranque">{E('comun.nav.arr')}</a>
<a data-i18n="nav.faq" href="#preguntas">{E('comun.nav.faq')}</a>
</div>
<div class="nav-der">
<div class="idiomas" role="group" aria-label="Elegir idioma" data-i18n-aria="aria.idioma" id="idiomas"></div>
<select aria-label="Elegir idioma" class="idioma" data-i18n-aria="aria.idioma" id="idioma">
<option value="es">ES</option>
<option value="en">EN</option>
<option value="pt">PT</option>
<option value="it">IT</option>
<option value="fr">FR</option>
</select>
<a class="navcta" data-i18n="nav.cta" href="#contacto">{E('comun.nav.cta')}</a>
</div>
</div>
</nav>
<div class="lienzo">
<section class="hero" id="inicio">
<div class="hero__grilla" aria-hidden="true"></div>
<div class="hero__inner">
<div class="lp-sello"><picture><source media="(prefers-color-scheme: dark)" srcset="../logos/{p["logo"]}-oscuro.png"><img src="../logos/{p["logo"]}.png" alt="" aria-hidden="true" decoding="async"/></picture><span>{p["servicio"]}</span></div>
<h1 class="hero__title display" data-i18n-html="hero.h1">{E('hero.h1')}<span class="dot">.</span></h1>
<p class="hero__sub" data-i18n="hero.sub">{E('hero.sub')}</p>
<div class="hero__actions">
<a class="btn btn-primary" data-i18n="hero.cta1" href="#contacto">{E('comun.hero.cta1')}</a>
<a class="btn btn-hero-ghost" data-i18n="hero.cta2" href="#incluye">{E('comun.hero.cta2')}</a>
</div>
<ul class="lp-trust">
<li data-i18n="hero.t1">{E('comun.hero.t1')}</li>
<li data-i18n="hero.t2">{E('comun.hero.t2')}</li>
<li data-i18n="hero.t3">{E('comun.hero.t3')}</li>
</ul>
</div>
</section>

<section id="incluye">
<div class="inner">
<div class="sec-head">
<div class="sec-eyebrow" data-i18n="inc.eyebrow">{E('comun.inc.eyebrow')}</div>
<h2 class="display" data-i18n="inc.h2">{E('inc.h2')}</h2>
<p data-i18n="inc.p">{E('inc.p')}</p>
</div>
<div class="lp-serv-grid">
{inc}
</div>
</div>
</section>

<section class="metodo" id="arranque">
<div class="inner">
<div class="sec-head">
<div class="sec-eyebrow" data-i18n="arr.eyebrow">{E('comun.arr.eyebrow')}</div>
<h2 class="display" data-i18n="arr.h2">{E('comun.arr.h2')}</h2>
<p data-i18n="arr.p">{E('comun.arr.p')}</p>
</div>
<div class="fase-grid">
{fases}
</div>
</div>
</section>

<section id="honestidad">
<div class="inner">
<div class="nope">
<h2 class="display" data-i18n-html="nope.h2">{E('comun.nope.h2')}<span class="dot">.</span></h2>
<ul>
{nope}
</ul>
</div>
</div>
</section>

<section id="preguntas">
<div class="inner">
<div class="sec-head">
<div class="sec-eyebrow" data-i18n="faq.eyebrow">{E('comun.faq.eyebrow')}</div>
<h2 class="display" data-i18n="faq.h2">{E('comun.faq.h2')}</h2>
<p data-i18n="faq.p">{E('comun.faq.p')}</p>
</div>
<div class="faq">
{faq}
</div>
</div>
</section>

<section class="contacto" id="contacto">
<div class="contacto-deco" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
<div class="inner contacto-grid">
<div>
<div class="sec-eyebrow cont-eyebrow" data-i18n="cont.eyebrow">{E('comun.cont.eyebrow')}</div>
<h2 class="display" data-i18n="cont.h2">{E('comun.cont.h2')}</h2>
<p data-i18n="cont.p">{E('comun.cont.p')}</p>
<p class="contacto-directo" data-i18n-first="cont.dir">{E('comun.cont.dir')}<a href="mailto:cifra@cifragrowth.com">cifra@cifragrowth.com</a> <span class="par"><span class="sep" aria-hidden="true">·</span><a class="wa-link" href="#contacto" data-wa rel="noopener" target="_blank">WhatsApp</a></span> <span class="par"><span class="sep" aria-hidden="true">·</span><a href="https://instagram.com/cifra.growth" rel="noopener" target="_blank">@cifra.growth</a></span></p>
</div>
<div class="contacto-card">
<form id="contact-form">
<input name="access_key" type="hidden" value="e37f3d19-0ae0-4b16-9eec-3ea2982ef1eb"/>
<input name="subject" type="hidden" value="{p["asunto"]}"/>
<input name="Página" type="hidden" value="{p["servicio"]}"/>
<input autocomplete="off" name="botcheck" style="display:none" tabindex="-1" type="checkbox"/>
<div><label data-i18n="form.nombre" for="f-nombre">{E('comun.form.nombre')}</label><input data-i18n-ph="form.ph1" id="f-nombre" name="Nombre" placeholder="{E('comun.form.ph1')}" required="" type="text"/></div>
<div><label data-i18n="form.empresa" for="f-empresa">{E('comun.form.empresa')}</label><input data-i18n-ph="form.ph2" id="f-empresa" name="Empresa" placeholder="{E('comun.form.ph2')}" type="text"/></div>
<div><label data-i18n="form.email" for="f-email">{E('comun.form.email')}</label><input data-i18n-ph="form.ph3" id="f-email" name="Email" placeholder="{E('comun.form.ph3')}" required="" type="email"/></div>
<div><label data-i18n="form.desafio" for="f-desafio">{E('form.desafio')}</label><textarea data-i18n-ph="form.ph4" id="f-desafio" name="Principal desafío" placeholder="{E('form.ph4')}" rows="3"></textarea></div>
<button class="btn btn-primary" data-i18n="form.btn" style="border:none;cursor:pointer;justify-content:center" type="submit">{E('comun.form.btn')}</button>
<div class="form-note" id="form-status"></div>
</form>
</div>
</div>
</section>
</div>
<footer>
<div class="inner">
<div class="foot-grid">
<div>
<div class="wm" style="margin-bottom:10px">cifra<span class="dot">.</span></div>
<div class="foot-desc" data-i18n="foot.desc">{E('comun.foot.desc')}</div>
</div>
<div class="foot-links">
<a data-i18n="foot.inicio" href="/">{E('comun.foot.inicio')}</a>
<a data-i18n="foot.serv" href="/#servicios">{E('comun.foot.serv')}</a>
<a href="/{p["otra_slug"]}/">{p["otra_nombre"]}</a>
<a data-i18n="foot.cont" href="#contacto">{E('comun.foot.cont')}</a>
</div>
<div class="foot-links">
<a href="mailto:cifra@cifragrowth.com">cifra@cifragrowth.com</a>
<a class="wa-link" href="#contacto" data-wa rel="noopener" target="_blank">WhatsApp</a>
<a href="https://instagram.com/cifra.growth" rel="noopener" target="_blank">@cifra.growth</a>
<a data-i18n="foot.priv" href="/privacidad">{E('comun.foot.priv')}</a>
</div>
</div>
<div class="foot-bottom">
<span class="foot-copy">© {anio} Cifra Growth <span class="sep" aria-hidden="true">·</span> <span data-i18n="foot.rights">{E('comun.foot.rights')}</span></span>
</div>
</div>
</footer>
{BOTONES}
{SC_FORM}
{SC_WA}
{SC_MAIL}
{SC_WACLIC}
{SC_FONDO}
{SC_TILT}
{SC_CARTAS}
{SC_FILA}
{SC_SUBIR}
{SC_REVEAL}
</body>
</html>'''


PAGINAS = [
 {'pref': 'ga', 'slug': 'google-ads', 'logo': 'google-ads', 'marca': '#4285F4',
  'servicio': 'Google Ads', 'form_id': 'lp_google_ads',
  'asunto': 'Consulta de Google Ads desde cifragrowth.com',
  'otra_slug': 'meta-ads', 'otra_nombre': 'Meta Ads',
  'og_title': 'Cifra — Agencia de Google Ads'},
 {'pref': 'ma', 'slug': 'meta-ads', 'logo': 'meta-ads', 'marca': '#0866FF',
  'servicio': 'Meta Ads', 'form_id': 'lp_meta_ads',
  'asunto': 'Consulta de Meta Ads desde cifragrowth.com',
  'otra_slug': 'google-ads', 'otra_nombre': 'Google Ads',
  'og_title': 'Cifra — Agencia de Meta Ads'},
]

for p in PAGINAS:
    os.makedirs(p['slug'], exist_ok=True)
    out = p['slug'] + '/index.html'
    open(out, 'w', encoding='utf-8').write(pagina(p))
    print(out, os.path.getsize(out) // 1024, 'KB')
