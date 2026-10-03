"""Template tags for the v2 frontend.

{% vite_entry 'src/main.ts' %}
    Production: reads frontend/dist/.vite/manifest.json and emits the entry's
    CSS <link>s, <link rel=modulepreload> for its static imports, optional
    font preloads, and the module <script>. Files are referenced by their
    Vite-hashed names under /static/dist/ (never through Django's manifest
    storage — chunks import each other by relative path, so the URLs must be
    the originals). Development (DEBUG + VITE_DEV_SERVER): points at the Vite
    dev server, including the React refresh preamble.
"""

import json
from functools import lru_cache

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()


@lru_cache(maxsize=1)
def _manifest_cached(mtime):  # mtime keys the cache so rebuilds are picked up
    path = settings.VITE_DIST_DIR / '.vite' / 'manifest.json'
    return json.loads(path.read_text())


def _manifest():
    path = settings.VITE_DIST_DIR / '.vite' / 'manifest.json'
    if not path.exists():
        raise template.TemplateSyntaxError(
            'Vite manifest not found — run `npm run build` in frontend/ (or set VITE_DEV_SERVER with DEBUG=True).')
    return _manifest_cached(path.stat().st_mtime)


def _dist_url(file):
    return f"{settings.STATIC_URL if settings.STATIC_URL.startswith('/') else '/' + settings.STATIC_URL}dist/{file}"


def _collect(manifest, key, seen, css, preloads):
    if key in seen:
        return
    seen.add(key)
    chunk = manifest[key]
    for c in chunk.get('css', []):
        if c not in css:
            css.append(c)
    for imp in chunk.get('imports', []):
        preloads.append(manifest[imp]['file'])
        _collect(manifest, imp, seen, css, preloads)


@register.simple_tag(takes_context=True)
def vite_entry(context, entry, preload_fonts='', with_css=True):
    nonce = context.get('csp_nonce', '')
    dev = settings.VITE_DEV_SERVER
    if dev:
        dev = dev.rstrip('/')
        parts = []
        if entry.endswith('main.ts'):
            parts.append(format_html(
                '<script type="module" nonce="{}">import RefreshRuntime from "{}/@react-refresh";'
                'RefreshRuntime.injectIntoGlobalHook(window);window.$RefreshReg$=()=>{{}};'
                'window.$RefreshSig$=()=>(type)=>type;window.__vite_plugin_react_preamble_installed__=true;</script>',
                nonce, dev))
            parts.append(format_html('<script type="module" src="{}/@vite/client"></script>', dev))
        parts.append(format_html('<script type="module" src="{}/{}"></script>', dev, entry))
        return mark_safe('\n'.join(parts))

    manifest = _manifest()
    if entry not in manifest:
        raise template.TemplateSyntaxError(f'{entry!r} is not a Vite entry (known: {", ".join(manifest)})')
    css, preloads = [], []
    _collect(manifest, entry, set(), css, preloads)
    tags = []
    if preload_fonts:
        wanted = [w.strip() for w in preload_fonts.split(',') if w.strip()]
        for asset in manifest[entry].get('assets', []) + [a for c in manifest.values() for a in c.get('assets', [])]:
            if asset.endswith('.woff2') and any(w in asset for w in wanted):
                tag = format_html('<link rel="preload" href="{}" as="font" type="font/woff2" crossorigin>',
                                  _dist_url(asset))
                if tag not in tags:
                    tags.append(tag)
    if with_css:
        tags += [format_html('<link rel="stylesheet" href="{}">', _dist_url(c)) for c in css]
    tags += [format_html('<link rel="modulepreload" href="{}">', _dist_url(p)) for p in dict.fromkeys(preloads)]
    tags.append(format_html('<script type="module" src="{}"></script>', _dist_url(manifest[entry]['file'])))
    return mark_safe('\n'.join(tags))


@register.simple_tag
def vite_asset(path):
    """URL of a non-entry file processed by Vite (e.g. src/assets/x.png)."""
    if settings.VITE_DEV_SERVER:
        return f"{settings.VITE_DEV_SERVER.rstrip('/')}/{path}"
    return _dist_url(_manifest()[path]['file'])


@register.filter
def jsonld(value):
    """Serialise a dict as JSON-LD safe for embedding in <script>."""
    text = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    return mark_safe(text.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))


@register.simple_tag
def abs_static(path):
    return f"{settings.SITE_URL.rstrip('/')}{static(path)}"


@register.filter
def pad2(value):
    try:
        return f'{int(value):02d}'
    except (TypeError, ValueError):
        return value


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.simple_tag
def attrs(**kwargs):
    return mark_safe(' '.join(f'{k.replace("_", "-")}="{escape(v)}"' for k, v in kwargs.items() if v not in (None, '')))
