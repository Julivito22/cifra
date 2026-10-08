# cifragrowth.com

Sitio de **Cifra — Growth marketing**. Es un sitio estático: HTML, CSS y JavaScript en un solo archivo por página, sin build ni dependencias. Se publica en **Cloudflare (Workers & Pages)** subiendo la carpeta completa.

## Qué hay acá

| Archivo / carpeta | Qué es |
|---|---|
| `index.html` | El sitio principal. Todo en un archivo: estilos, scripts, diccionario de los 5 idiomas. |
| `google-ads/index.html` | Landing del servicio de Google Ads (`cifragrowth.com/google-ads/`). |
| `meta-ads/index.html` | Landing del servicio de Meta Ads (`cifragrowth.com/meta-ads/`). |
| `privacidad.html` | Política de privacidad (solo en español por ahora). |
| `logos/` | Logos oficiales de cada plataforma, con su variante `-oscuro` para el modo oscuro. Ver `logos/LEEME.txt`. |
| `og-cifra.jpg` | Imagen que se ve al compartir el link (WhatsApp, LinkedIn, etc.). |
| `video-cifra.mp4` + `video-cifra-poster.jpg` | Video de marca del home. |
| `icon-32.png`, `icon-192.png`, `apple-touch-icon.png` | Íconos. |
| `robots.txt`, `sitemap.xml` | Para buscadores. |
| `google3c8ca1bfece49a12.html` | Archivo de verificación de Google Search Console. **No borrar**, se pierde la verificación. |
| `_fuente/` | Herramientas de mantenimiento. No se publica (ver abajo). |

## Cómo se publica

1. Cloudflare → **Workers & Pages → cifra-landing → New deployment**.
2. Subir la **carpeta entera**, no archivos sueltos.
3. El archivo de la raíz tiene que llamarse exactamente `index.html`. Si se sube como `index_2.html` (Chrome numera las descargas repetidas), el sitio devuelve 404.
4. Después de subir, recargar con `Cmd + Shift + R`.

## Idiomas

Cinco: español (por defecto), inglés, portugués de Brasil, italiano y francés. El cambio es del lado del cliente, sin recargar, y la elección queda guardada en el navegador.

`?lang=xx` en la URL manda sobre lo guardado. Esa es la URL que va como **URL final** en los anuncios por idioma:

- `https://cifragrowth.com/google-ads/?lang=en`
- `https://cifragrowth.com/meta-ads/?lang=pt`

## Las landings se generan, no se editan a mano

`google-ads/index.html` y `meta-ads/index.html` **salen de un script**. Si se editan a mano, el próximo build pisa los cambios.

```
cd _fuente
python3 lp_es.py        # exporta los textos en español a i18n/es.json
python3 build_lp.py     # genera las dos landings (necesita index.html en la carpeta de arriba)
```

- `_fuente/lp_es.py` — los textos en español. **Es la fuente**: acá se cambia el copy.
- `_fuente/i18n/*.json` — los cinco idiomas. Todos tienen que tener exactamente las mismas claves.
- `_fuente/build_lp.py` — toma el CSS, los scripts y el motor de idiomas de `index.html` y arma las dos páginas. Por eso las landings siempre quedan iguales al diseño del sitio: si cambia el home, se vuelve a correr y listo.

Prefijos de las claves: `comun.*` va en las dos páginas, `ga.*` es Google Ads, `ma.*` es Meta Ads.

## Pruebas

En `_fuente/` hay tres suites con Playwright (`lp.py`, `lpidi.py`, `links.py`): desborde horizontal en todos los anchos, modo claro y oscuro, los cinco idiomas, el formulario disparando la conversión, el carrusel, el menú desplegable. Necesitan un servidor local sobre una copia de la carpeta:

```
python3 -m http.server 8899 --bind 127.0.0.1
```

## Medición

- Google Ads: `AW-18430783545`
- GA4: `G-KL5ER8QJXX`
- GTM: `GTM-MCB5B5JF` (instalado pero vacío — si algún día se le cargan etiquetas, hay que borrar las de `gtag` del HTML o las conversiones se cuentan dos veces)
- Formulario: Web3Forms. Cada landing manda su propio `form_id` (`lp_google_ads`, `lp_meta_ads`), así en GA4 se ve qué página convierte mejor.

## Dos cosas para no romper

- **El número de WhatsApp no está escrito en el HTML**: se arma con JavaScript recién cuando alguien toca el link, para que los rastreadores de números no lo levanten. Está guardado en base64.
- **`data-i18n` reemplaza el contenido del elemento.** Nunca ponerlo en un elemento que tenga hijos que haya que conservar (ya se perdieron un punto rojo y una flechita por eso). La clave va en un `<span>` adentro.
