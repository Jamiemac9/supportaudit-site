#!/usr/bin/env python3
"""Build seaaudit.com into ./dist.

    python3 tools/build.py            # needs Node with esbuild + html-minifier-terser (npm i)

Pages live in src/pages/*.html (main content only). This script wraps each in the shared
head, navigation and footer, expands [[macros]], writes structured data, hashes and minifies
assets, and generates sitemap.xml, robots.txt, llms.txt and the Cloudflare _headers/_redirects.
"""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
NODE_BIN = os.environ.get('NODE_BIN', os.path.join(ROOT, 'node_modules', '.bin'))

# ---------------------------------------------------------------- settings
DOMAIN = 'https://seaaudit.com'
BRAND = 'SEA Audit'
EMAIL = 'hello@seaaudit.com'
TODAY = '2026-10-12'
PUBLISHED = '2026-10-08'
GA_ID = 'G-4KW5S92V6Z'
BING_VERIFY = ''      # optional: content of the msvalidate.01 meta tag from Bing Webmaster Tools
GOOGLE_VERIFY = ''    # optional: content of the google-site-verification meta tag
INDEXNOW_KEY = open(os.path.join(ROOT, 'tools', 'indexnow.key')).read().strip()

NAV = [('Audits', '/audits/'), ('Use cases', '/use-cases/'), ('Resources', '/resources/'), ('About', '/about/')]

PAGES = {
    'index': dict(url='/', nav=None, type='WebPage',
        title='SEA Audit | Supported Exempt Accommodation Audits',
        desc='Independent audits of resident support files for supported exempt accommodation in England. Evidence-led reports, rated Gold to Red, ready for licensing.'),
    'audits': dict(url='/audits/', nav='/audits/', type='WebPage', crumbs=[('Audits', '/audits/')],
        title='Supported Housing Audits: Mock Audit & Rounds | SEA Audit',
        desc='Mock Audits, six-monthly audit rounds and monitoring for Registered Providers and managing agents in England. Desktop audits, fixed fees, clear actions.'),
    'use-cases': dict(url='/use-cases/', nav='/use-cases/', type='WebPage', crumbs=[('Use cases', '/use-cases/')],
        title='When to Audit Supported Housing Files | SEA Audit',
        desc='Nine situations where Registered Providers and managing agents use an independent supported housing audit, from licensing to onboarding a new agent.'),
    'resources': dict(url='/resources/', nav='/resources/', type='CollectionPage', crumbs=[('Resources', '/resources/')],
        title='Supported Housing Guides, Glossary & Key Dates | SEA Audit',
        desc='Plain-English guides, quick answers, key dates and a 22-term glossary for supported exempt accommodation in England, with primary sources.'),
    'guide-licensing': dict(url='/resources/supported-housing-licensing/', nav='/resources/', type='Article',
        crumbs=[('Resources', '/resources/'), ('Supported housing licensing', '/resources/supported-housing-licensing/')],
        headline='Supported housing licensing explained',
        title='Supported Housing Licensing Explained (2026 Update)',
        desc='What the Supported Housing (Regulatory Oversight) Act 2023 means for England: the National Supported Housing Standards, who needs a licence and when.'),
    'guide-support-file': dict(url='/resources/resident-support-file/', nav='/resources/', type='Article',
        crumbs=[('Resources', '/resources/'), ('Resident support file', '/resources/resident-support-file/')],
        headline='What a good resident support file contains',
        title='What a Good Resident Support File Contains | SEA Audit',
        desc='The ten core documents in a supported housing resident support file, what auditors look for, the most common gaps and a free self-check.'),
    'about': dict(url='/about/', nav='/about/', type='AboutPage', crumbs=[('About', '/about/')],
        title='About SEA Audit | Independent Supported Housing Audits',
        desc='Who is behind SEA Audit, how every audit is carried out and graded by an auditor, and how we protect resident data under UK GDPR.'),
    'book-a-call': dict(url='/book-a-call/', nav=None, type='ContactPage', crumbs=[('Book a call', '/book-a-call/')],
        title='Book a Discovery Call | SEA Audit',
        desc='Book a free 20-minute call about your resident support files and get a fixed-price proposal for the right supported housing audit.'),
}

STEPS = [
    ('01', 'Scope', 'A short call to agree which files are in scope, which standards apply and your timescale. We confirm a fixed fee before anything starts.'),
    ('02', 'Secure transfer', 'You share the resident files for the review period through a secure transfer. Only the files in scope are requested, and everything is handled as special category data.'),
    ('03', 'Review', 'Every file is checked against the same structured checklist: signatures, dates, reviews, risk plans and support hours, line by line. The auditor then reads each file as a whole, makes every judgement and sets every grade.'),
    ('04', 'Report', 'Each resident gets a rating with a reason, evidence for every finding, the strengths we found and practical next steps. Managing agents also get an overall feedback report.'),
    ('05', 'Improve', 'We debrief with your team and check progress 4 to 8 weeks later. A re-audit then confirms actions are closed, or monitoring keeps standards steady between rounds.'),
]

# ---------------------------------------------------------------- icons & macros
def svg(path, size=18, sw=2.4):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>')

TICK = '<path d="M5 12.5l4.5 4.5L19 7.5"></path>'
ICONS = {
    'tick': svg(TICK), 'tick16': svg(TICK, 16, 2.6),
    'bang': svg('<path d="M12 7v6"></path><path d="M12 17h.01"></path>', 22, 2.6),
    'bang16': svg('<path d="M12 7v6"></path><path d="M12 17h.01"></path>', 16, 2.6),
    'cross': svg('<path d="M7 7l10 10M17 7L7 17"></path>', 22, 2.6),
    'star': svg('<path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4 6.7 19.4l1.2-6L3.4 9.3l6-.7z"></path>', 22, 2.2),
    'arrow': '<svg class="arr" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>',
    'arrow16': '<svg class="arr" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>',
    'pm': '<span class="pm" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"></path></svg></span>',
}
SARR = '<svg class="sarr" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>'


def btn(kind, href, label, arrow=False):
    mag = ' data-magnetic' if kind == 'acc' else ''
    return (f'<a class="btn btn-{kind}" href="{href}"{mag}><span class="rl"><span class="rl-in"><span>{label}</span>'
            f'<span aria-hidden="true">{label}</span></span></span>{ICONS["arrow"] if arrow else ""}</a>')


def steps_html():
    b = []
    p = []
    for i, (n, t, d) in enumerate(STEPS):
        on = i == 0
        b.append(f'<button class="st{" on" if on else ""}" type="button" aria-pressed="{"true" if on else "false"}" data-step="{i}"><span class="sn">{n}</span><span data-step-title>{t}</span>{SARR}</button>')
        p.append(f'<div class="pane{" on" if on else ""}" data-step-pane="{i}" style="display: flex; flex-direction: column; gap: 16px"><span class="pn" aria-hidden="true">{n}</span><h3 class="h3" style="font-size: clamp(1.75rem,1.4rem + 1vw,2.25rem)">{t}</h3><p class="lead">{d}</p></div>')
    return '\n'.join(b), '\n'.join(p)


def expand(body):
    sb, sp = steps_html()
    body = body.replace('[[steps]]', sb).replace('[[step-panes]]', sp)
    body = body.replace('[[form-short]]', open(os.path.join(SRC, 'partials', 'form-short.html')).read())
    body = re.sub(r'\[\[btn (\w+)\|([^|\]]+)\|([^|\]]+)(\|arrow)?\]\]', lambda m: btn(m.group(1), m.group(2), m.group(3), bool(m.group(4))), body)
    body = re.sub(r'\[\[(\w+)\]\]', lambda m: ICONS[m.group(1)], body)
    left = re.findall(r'\[\[[^\]]*\]\]', body)
    if left:
        sys.exit(f'Unknown macros: {left}')
    return body


# ---------------------------------------------------------------- layout
def mark():
    return '<span class="mk" aria-hidden="true"><i></i><i></i><i></i><i></i></span>'


def nav_html(cur):
    links = ''.join(f'<a href="{u}"{" aria-current=\"page\"" if u == cur else ""}>{n}</a>' for n, u in NAV)
    mlinks = ''.join(f'<a href="{u}">{n}{ICONS["arrow"]}</a>' for n, u in [('Home', '/')] + NAV + [('Book a call', '/book-a-call/')])
    return f'''<header class="nav"><div class="wrap nav-in">
<a class="logo" href="/">{mark()}<b>SEA</b> <span class="w">Audit</span><span class="sr-only"> home</span></a>
<nav class="nav-links" aria-label="Main">{links}</nav>
<div class="nav-r">{btn("acc", "/book-a-call/", "Book a call")}<button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="Open menu"><span></span></button></div>
</div></header>
<div class="menu" id="menu" hidden><nav aria-label="Mobile">{mlinks}</nav>
<div class="menu-foot">{btn("acc", "/book-a-call/", "Book a discovery call", True)}<a href="mailto:{EMAIL}">{EMAIL}</a></div></div>'''


FOOTER = f'''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><a class="logo" href="/">{mark()}<b>SEA</b> <span class="w">Audit</span></a><p>Independent resident support file audits for supported exempt accommodation and transitional supported housing in England.</p></div>
<div><h2 class="h4">Audits</h2><ul><li><a href="/audits/">Mock Audit</a></li><li><a href="/audits/">Audit rounds</a></li><li><a href="/audits/">Monitoring</a></li><li><a href="/use-cases/">Use cases</a></li></ul></div>
<div><h2 class="h4">Resources</h2><ul><li><a href="/resources/supported-housing-licensing/">Licensing guide</a></li><li><a href="/resources/resident-support-file/">Support file guide</a></li><li><a href="/resources/#glossary">Glossary</a></li><li><a href="/resources/#sources">Sources</a></li></ul></div>
<div><h2 class="h4">Company</h2><ul><li><a href="/about/">About and approach</a></li><li><a href="/book-a-call/">Book a call</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
</div>
<div class="big" aria-hidden="true"><b>SEA</b> Audit</div>
<div class="foot-base"><span>© 2026 {BRAND}. Supported exempt accommodation audits, England. Content reviewed {TODAY[8:].lstrip("0")} October 2026.</span><span><a href="/about/#privacy">Privacy</a> · <a href="/about/#privacy">Terms</a> · <button type="button" data-cookie-settings>Cookie settings</button></span></div>
</div></footer>'''

INTRO = f'<div class="intro" aria-hidden="true"><div class="ib">{mark()}<span class="iw"><span>SEA <em>Audit</em></span></span></div></div>'

INLINE_MOTION = """(function(d,w){var h=d.documentElement,rm=w.matchMedia&&w.matchMedia('(prefers-reduced-motion: reduce)').matches;h.classList.add(rm?'no-motion':'motion');var seen='1';try{seen=sessionStorage.getItem('sea-seen');sessionStorage.setItem('sea-seen','1')}catch(e){}var intro=!rm&&!seen&&!location.hash&&w.innerWidth>=900;var go=function(){h.classList.add('go')};if(intro){h.classList.add('is-intro');setTimeout(function(){var i=d.querySelector('.intro');if(i)i.classList.add('out');go()},1050);setTimeout(function(){h.classList.remove('is-intro')},1950)}else{setTimeout(go,40)}setTimeout(function(){if(!(w.SEA&&w.SEA.ready)){h.classList.remove('motion');h.classList.add('no-motion','go')}},4000)})(document,window);"""

INLINE_GA = f"""window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('consent','default',{{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied'}});window.SEA_loadGA=function(){{if(window.SEA_ga)return;window.SEA_ga=1;gtag('consent','update',{{analytics_storage:'granted'}});var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id={GA_ID}';document.head.appendChild(s);gtag('js',new Date());gtag('config','{GA_ID}');}};try{{if(localStorage.getItem('sea-consent')==='granted')window.SEA_loadGA();}}catch(e){{}}"""


# ---------------------------------------------------------------- structured data
ORG = {
    '@type': 'ProfessionalService', '@id': DOMAIN + '/#org', 'name': BRAND, 'alternateName': 'SEAAudit.com',
    'url': DOMAIN + '/', 'email': EMAIL, 'logo': DOMAIN + '/assets/img/icon-512.png', 'image': DOMAIN + '/assets/img/og.jpg',
    'description': 'SEA Audit is an independent audit service for supported exempt accommodation and transitional supported housing in England, auditing resident support files for Registered Providers and managing agents and rating each file Gold, Green, Amber or Red.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Solihull', 'addressRegion': 'West Midlands', 'addressCountry': 'GB'},
    'areaServed': {'@type': 'Country', 'name': 'United Kingdom', 'containsPlace': {'@type': 'AdministrativeArea', 'name': 'England'}},
    'founder': {'@id': DOMAIN + '/about/#jamie'},
    'knowsAbout': ['Supported exempt accommodation', 'National Supported Housing Standards', 'Supported housing licensing',
                   'Resident support file audits', 'Transitional supported housing', 'Registered Providers', 'Managing agents'],
    'serviceType': 'Supported housing resident support file audit',
}
PERSON = {'@type': 'Person', '@id': DOMAIN + '/about/#jamie', 'name': 'Jamie McCollin', 'jobTitle': 'Founder',
          'worksFor': {'@id': DOMAIN + '/#org'}, 'url': DOMAIN + '/about/',
          'knowsAbout': ['Supported housing', 'Housing compliance', 'Property management']}


def strip(s):
    s = re.sub(r'<sup>.*?</sup>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def schema(key, cfg, body):
    url = DOMAIN + cfg['url']
    page_type = 'WebPage' if cfg['type'] == 'Article' else cfg['type']
    graph = [ORG, {'@type': 'WebSite', '@id': DOMAIN + '/#website', 'url': DOMAIN + '/', 'name': BRAND,
                   'publisher': {'@id': DOMAIN + '/#org'}, 'inLanguage': 'en-GB'}]
    page = {'@type': page_type, '@id': url + '#page', 'url': url, 'name': cfg['title'], 'description': cfg['desc'],
            'inLanguage': 'en-GB', 'isPartOf': {'@id': DOMAIN + '/#website'}, 'about': {'@id': DOMAIN + '/#org'},
            'dateModified': TODAY}
    graph.append(page)
    if cfg.get('crumbs'):
        items = [('Home', '/')] + cfg['crumbs']
        graph.append({'@type': 'BreadcrumbList', '@id': url + '#crumbs', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': DOMAIN + u} for i, (n, u) in enumerate(items)]})
        page['breadcrumb'] = {'@id': url + '#crumbs'}
    graph.append(PERSON)
    if cfg['type'] == 'Article':
        cites = sorted(set(re.findall(r'href="(https://(?:www\.)?(?:legislation\.gov\.uk|gov\.uk|homeless\.org\.uk)[^"]*)"', body)))
        graph.append({'@type': 'Article', '@id': url + '#article', 'headline': cfg['headline'], 'description': cfg['desc'],
                      'mainEntityOfPage': {'@id': url + '#page'}, 'datePublished': PUBLISHED, 'dateModified': TODAY,
                      'inLanguage': 'en-GB', 'image': DOMAIN + '/assets/img/og.jpg', 'author': {'@id': DOMAIN + '/about/#jamie'},
                      'publisher': {'@id': DOMAIN + '/#org'}, 'spatialCoverage': {'@type': 'Country', 'name': 'England'},
                      'citation': cites})
    if key == 'audits':
        for name, aud, d in (
            ('Mock Audit', 'Managing agents and support providers in supported housing',
             'A fixed-fee desktop review of a sample of resident support files, rated Gold, Green, Amber or Red, with an action plan and debrief.'),
            ('Audit Rounds', 'Registered Providers working with managing agents',
             'Every resident file for a managing agent audited on a regular cycle, usually every six months, with per-resident reports and overall agent feedback.'),
            ('Monitoring', 'Registered Providers, managing agents and support providers',
             'Monthly sampling of resident files between audits, with early warning on reviews, support hours and missed sessions.')):
            graph.append({'@type': 'Service', 'name': name, 'serviceType': 'Supported housing resident support file audit',
                          'provider': {'@id': DOMAIN + '/#org'}, 'areaServed': {'@type': 'Country', 'name': 'United Kingdom'},
                          'audience': {'@type': 'BusinessAudience', 'audienceType': aud}, 'description': d, 'url': url})
    if key == 'resources':
        terms = re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', body, re.S)
        graph.append({'@type': 'DefinedTermSet', '@id': url + '#glossary', 'name': 'Supported housing glossary',
                      'hasDefinedTerm': [{'@type': 'DefinedTerm', 'name': strip(t), 'description': strip(d)} for t, d in terms]})
    if key != 'about':
        qa = re.findall(r'<summary>(.*?)<span class="pm".*?<div class="fa">(.*?)</div></details>', body, re.S)
        if qa:
            graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
                {'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qa]})
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':'))


# ---------------------------------------------------------------- assets
def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f'{cmd[0]} failed:\n{r.stderr}')
    return r.stdout


def hashed(rel, data):
    h = hashlib.sha256(data).hexdigest()[:10]
    base, ext = os.path.splitext(rel)
    out = f'{base}.{h}{ext}'
    path = os.path.join(DIST, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(data)
    return '/' + out


def build_assets():
    esb = os.path.join(NODE_BIN, 'esbuild')
    css = run([esb, os.path.join(SRC, 'assets/css/site.css'), '--minify']).encode()
    app_src = open(os.path.join(SRC, 'assets/js/app.js')).read()
    app_min = run([esb, '--minify', '--loader=js', '--target=es2017'], input=app_src)
    lenis = open(os.path.join(SRC, 'assets/vendor/lenis.min.js')).read()
    js = ('/*! lenis | MIT | darkroom.engineering */\n' + lenis.split('\n//# sourceMappingURL')[0] + '\n' + app_min).encode()
    field = run([esb, '--minify', '--loader=js', '--target=es2017'], input=open(os.path.join(SRC, 'assets/js/field.js')).read()).encode()
    out = {'css': hashed('assets/css/site.css', css), 'js': hashed('assets/js/app.js', js), 'field': hashed('assets/js/field.js', field)}
    for d in ('fonts', 'img'):
        shutil.copytree(os.path.join(SRC, 'assets', d), os.path.join(DIST, 'assets', d))
    shutil.copy(os.path.join(SRC, 'assets/vendor/lenis-LICENSE.txt'), os.path.join(DIST, 'assets/js/lenis-LICENSE.txt'))
    return out


# ---------------------------------------------------------------- pages
def head(key, cfg, assets, body):
    url = DOMAIN + cfg['url']
    t, d = html.escape(cfg['title']), html.escape(cfg['desc'])
    art = ''
    if cfg['type'] == 'Article':
        art = (f'<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{TODAY}">'
               '<meta name="author" content="Jamie McCollin">')
    verify = ''
    if BING_VERIFY:
        verify += f'<meta name="msvalidate.01" content="{BING_VERIFY}">'
    if GOOGLE_VERIFY:
        verify += f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">'
    return f'''<!doctype html>
<html lang="en-GB" data-field="{assets['field']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en-GB" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta property="og:type" content="{'article' if cfg['type'] == 'Article' else 'website'}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/assets/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="SEA Audit: resident support files that stand up to scrutiny">
<meta name="twitter:card" content="summary_large_image">
{art}{verify}<meta name="theme-color" content="#050E19">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/schibsted-grotesk-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/schibsted-grotesk-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{assets['css']}">
<script>{INLINE_MOTION}</script>
<!-- Google tag (gtag.js) with Consent Mode v2: loads only after the visitor accepts analytics -->
<script>{INLINE_GA}</script>
<script type="application/ld+json">{schema(key, cfg, body)}</script>
<script src="{assets['js']}" defer></script>
</head>'''


def page(key, cfg, assets):
    body = expand(open(os.path.join(SRC, 'pages', key + '.html')).read())
    read = '<div class="read-prog" aria-hidden="true"><i></i></div>' if cfg['type'] == 'Article' else ''
    doc = (head(key, cfg, assets, body) + f'\n<body data-page="{key}">\n<a class="skip" href="#main">Skip to content</a>\n{INTRO}\n'
           '<div class="field-fallback" aria-hidden="true"></div><div class="grain" aria-hidden="true"></div>\n<div class="prog" aria-hidden="true"></div>'
           f'{read}\n{nav_html(cfg["nav"])}\n<div class="sa"><main id="main">\n{body}\n</main></div>\n{FOOTER}\n</body>\n</html>\n')
    return doc


NOT_FOUND = '''<section class="hero-s" style="min-height:80vh;display:flex;align-items:center"><div class="wrap stackv gap24">
<span class="eb">Error 404</span><h1 class="d">This page isn&#39;t <span class="glow">in the file.</span></h1>
<p class="lead">The page you were looking for has moved or doesn&#39;t exist. Try one of these instead.</p>
<div class="row">[[btn acc|/|Back to the home page|arrow]][[btn ghost|/resources/|Browse resources]][[btn ghost|/book-a-call/|Book a call]]</div>
</div></section>'''


def minify(path):
    hm = os.path.join(NODE_BIN, 'html-minifier-terser')
    run([hm, '--collapse-whitespace', '--conservative-collapse', '--remove-comments', '--minify-js', 'true',
         '--remove-redundant-attributes', '--decode-entities', '-o', path, path])


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    assets = build_assets()
    for key, cfg in PAGES.items():
        out = os.path.join(DIST, cfg['url'].strip('/'), 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w').write(page(key, cfg, assets))
        minify(out)
        print('page', cfg['url'])
    # 404
    nf_cfg = dict(url='/404', nav=None, type='WebPage', title='Page not found | SEA Audit', desc='This page could not be found.')
    nf = page_from_body('404', nf_cfg, assets, expand(NOT_FOUND))
    open(os.path.join(DIST, '404.html'), 'w').write(nf.replace('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">', '<meta name="robots" content="noindex">'))
    minify(os.path.join(DIST, '404.html'))
    # static
    for f in os.listdir(os.path.join(SRC, 'static')):
        shutil.copy(os.path.join(SRC, 'static', f), os.path.join(DIST, f))
    write_meta()
    print('built ->', DIST)


def page_from_body(key, cfg, assets, body):
    doc = (head(key, cfg, assets, body).replace(f'<link rel="canonical" href="{DOMAIN}/404">', '')
           .replace(f'<link rel="alternate" hreflang="en-GB" href="{DOMAIN}/404">', '').replace(f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}/404">', '')
           + f'\n<body data-page="404">\n<div class="field-fallback" aria-hidden="true"></div><div class="grain" aria-hidden="true"></div>\n{nav_html(None)}\n<div class="sa"><main id="main">{body}</main></div>\n{FOOTER}\n</body></html>')
    doc = re.sub(r'<script type="application/ld\+json">.*?</script>', '', doc, flags=re.S)
    return doc


def write_meta():
    urls = '\n'.join(f'  <url><loc>{DOMAIN}{c["url"]}</loc><lastmod>{TODAY}</lastmod>'
                     f'<xhtml:link rel="alternate" hreflang="en-GB" href="{DOMAIN}{c["url"]}"/></url>' for c in PAGES.values())
    open(os.path.join(DIST, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}\n</urlset>\n')
    open(os.path.join(DIST, 'robots.txt'), 'w').write(f'''# seaaudit.com
User-agent: *
Allow: /
Disallow: /404

# AI search and answer assistants (lets them cite the site)
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Bingbot
Allow: /

# Model training crawlers. Change Allow to Disallow to opt out.
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
''')
    open(os.path.join(DIST, f'{INDEXNOW_KEY}.txt'), 'w').write(INDEXNOW_KEY)
    open(os.path.join(DIST, 'llms.txt'), 'w').write(f'''# SEA Audit

> SEA Audit is an independent audit service for supported exempt accommodation (SEA) and transitional supported housing in England. It audits resident support files for Registered Providers and managing agents and rates each file Gold, Green, Amber or Red, with the reason for every rating.

Audits are desktop reviews of resident records, carried out remotely or at the provider's office. Every finding names the document, the date and what good looks like. An experienced auditor makes every judgement and sets every grade. Based in Solihull, West Midlands; serving England.

## Services
- [Audits]({DOMAIN}/audits/): Mock Audit, audit rounds and monitoring compared, the full checklist, the rating key and how audits map to the National Supported Housing Standards
- [Use cases]({DOMAIN}/use-cases/): nine situations where providers use an independent audit

## Guides
- [Supported housing licensing explained]({DOMAIN}/resources/supported-housing-licensing/): the Supported Housing (Regulatory Oversight) Act 2023, the National Supported Housing Standards, who needs a licence and when
- [What a good resident support file contains]({DOMAIN}/resources/resident-support-file/): the ten core documents, common gaps and a self-check
- [Resources]({DOMAIN}/resources/): quick answers, key dates, a 22-term glossary and primary sources

## About and contact
- [About and approach]({DOMAIN}/about/): founder, method and data protection
- [Book a discovery call]({DOMAIN}/book-a-call/)
- Email: {EMAIL}
''')
    open(os.path.join(DIST, '_headers'), 'w').write('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/assets/css/*
  Cache-Control: public, max-age=31536000, immutable
/assets/js/*
  Cache-Control: public, max-age=31536000, immutable
/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *
/assets/img/*
  Cache-Control: public, max-age=604800
/sitemap.xml
  Content-Type: application/xml; charset=utf-8
/llms.txt
  Content-Type: text/plain; charset=utf-8
''')
    open(os.path.join(DIST, '_redirects'), 'w').write('''/index.html / 301
/home / 301
/contact /book-a-call/ 301
/book /book-a-call/ 301
/licensing /resources/supported-housing-licensing/ 301
/support-file /resources/resident-support-file/ 301
/glossary /resources/#glossary 301
''')
    open(os.path.join(DIST, 'site.webmanifest'), 'w').write(json.dumps({
        'name': BRAND, 'short_name': BRAND, 'start_url': '/', 'display': 'browser', 'background_color': '#050E19',
        'theme_color': '#050E19', 'icons': [{'src': '/assets/img/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                                            {'src': '/assets/img/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}, indent=1))


if __name__ == '__main__':
    main()
