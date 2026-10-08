#!/usr/bin/env python3
"""Convert the Support Audit design canvas pages (.dc.html) into a plain static site in /docs.

Usage: python3 tools/build.py <folder containing the .dc.html files>
"""
import html
import json
import os
import re
import sys

SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
DOMAIN = "https://supportaudit.co.uk"
TODAY = "2026-10-08"

LINKS = {
    "Main": "/",
    "Audits": "/audits/",
    "UseCases": "/use-cases/",
    "Resources": "/resources/",
    "GuideLicensing": "/resources/supported-housing-licensing/",
    "GuideSupportFile": "/resources/resident-support-file/",
    "About": "/about/",
    "Book": "/book-a-call/",
}

PAGES = {
    "Main": dict(
        title="Support Audit | Supported Housing File Audits",
        desc="Independent audits of resident support files for supported exempt and transitional housing in England. Evidence-led, rated Gold to Red.",
        type="WebPage", crumbs=None),
    "Audits": dict(
        title="Supported Housing Audits: Mock Audit and Audit Rounds",
        desc="Mock Audits, six-monthly audit rounds and monitoring for Registered Providers and managing agents. Fixed fees, rated reports, clear actions.",
        type="WebPage", crumbs=[("Audits", "/audits/")]),
    "UseCases": dict(
        title="When to Audit Supported Housing Files | Support Audit",
        desc="Nine situations where Registered Providers and managing agents use an independent audit, from licensing to onboarding a new agent.",
        type="WebPage", crumbs=[("Use cases", "/use-cases/")]),
    "Resources": dict(
        title="Supported Housing Guides, Glossary and Key Dates",
        desc="Plain-English guides, quick answers, key dates and a 22-term glossary for supported exempt accommodation, with primary sources.",
        type="CollectionPage", crumbs=[("Resources", "/resources/")]),
    "GuideLicensing": dict(
        title="Supported Housing Licensing Explained (2026 Update)",
        desc="What the 2023 Act means: the National Supported Housing Standards, who needs a licence, the Housing Benefit link and when licensing starts.",
        type="Article", headline="Supported housing licensing explained",
        crumbs=[("Resources", "/resources/"), ("Supported housing licensing", "/resources/supported-housing-licensing/")]),
    "GuideSupportFile": dict(
        title="What a Good Resident Support File Contains",
        desc="The ten core documents in a supported housing support file, what auditors look for, common gaps and a free self-check.",
        type="Article", headline="What a good resident support file contains",
        crumbs=[("Resources", "/resources/"), ("Resident support file", "/resources/resident-support-file/")]),
    "About": dict(
        title="About Support Audit | Independent, Evidence-Led",
        desc="Who is behind Support Audit, how software and auditors share the work, and how we protect resident data.",
        type="AboutPage", crumbs=[("About", "/about/")]),
    "Book": dict(
        title="Book a Discovery Call | Support Audit",
        desc="Book a free 20-minute call to talk through your resident files and get a fixed-price proposal for the right audit.",
        type="ContactPage", crumbs=[("Book a call", "/book-a-call/")]),
}

STEPS = [
    ("01", "Scope", "A short call to agree which files are in scope, which standards apply and your timescale. We confirm a fixed fee before anything starts."),
    ("02", "Secure transfer", "You share the resident files for the review period through a secure transfer. Only the files in scope are requested, and everything is handled as special category data."),
    ("03", "Review", "Our software checks every file against the audit checklist, flagging missing signatures, late reviews, unplanned risks and support hours. An experienced auditor then reviews every judgement and sets every grade."),
    ("04", "Report", "Each resident gets a rating with a reason, evidence for every finding, the strengths we found and practical next steps. Managing agents also get an overall feedback report."),
    ("05", "Improve", "We debrief with your team and check progress 4 to 8 weeks later. Then a re-audit confirms actions are closed, or monitoring keeps standards steady between rounds."),
]

CHECKS = [
    "Referral form complete, signed and dated",
    "Admission form signed on the move-in day",
    "Licence in the right name, with the right address and rent",
    "Needs assessment completed within four weeks of move-in",
    "Every support goal follows from an assessed need",
    "Goals are specific to this resident, not copied",
    "Every risk is scored, and the scores match the file",
    "A current plan for every risk above your threshold",
    "Support recorded every week of the review period",
    "Each session note names a goal and the progress made",
    "Missed sessions recorded and followed up",
    "Reviews on time, signed by the resident and staff",
]

ARROW = '<svg class="sarr" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>'

ORG = {
    "@type": "ProfessionalService",
    "@id": DOMAIN + "/#org",
    "name": "Support Audit",
    "url": DOMAIN + "/",
    "email": "hello@supportaudit.co.uk",
    "logo": DOMAIN + "/assets/logo.png",
    "image": DOMAIN + "/assets/og.png",
    "description": "Independent audit service for supported exempt and transitional housing in England, auditing resident support files for Registered Providers and managing agents and rating each file Gold, Green, Amber or Red.",
    "areaServed": {"@type": "Country", "name": "England"},
    "founder": {"@type": "Person", "@id": DOMAIN + "/about/#jamie", "name": "Jamie McCollin"},
    "knowsAbout": [
        "Supported exempt accommodation",
        "National Supported Housing Standards",
        "Supported housing licensing",
        "Resident support file audits",
        "Transitional supported housing",
    ],
}

PERSON = {
    "@type": "Person",
    "@id": DOMAIN + "/about/#jamie",
    "name": "Jamie McCollin",
    "jobTitle": "Founder",
    "worksFor": {"@id": DOMAIN + "/#org"},
    "url": DOMAIN + "/about/",
    "knowsAbout": ["Supported housing", "Housing compliance", "Property management"],
}


def strip(s):
    s = re.sub(r"<sup>.*?</sup>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def faqs(body):
    out = []
    for q, a in re.findall(r'<summary>(.*?)<span class="pm".*?<div class="fa">(.*?)</div></details>', body, re.S):
        out.append({"@type": "Question", "name": strip(q),
                    "acceptedAnswer": {"@type": "Answer", "text": strip(a)}})
    return out


def steps_html():
    btns, panes = [], []
    for i, (n, t, b) in enumerate(STEPS):
        on = i == 0
        btns.append(f'<button class="st{" on" if on else ""}" type="button" aria-pressed="{"true" if on else "false"}" data-step="{i}"><span class="sn">{n}</span><span data-step-title>{t}</span>{ARROW}</button>')
        panes.append(f'<div class="pane{" on" if on else ""}" data-step-pane="{i}" style="display: flex; flex-direction: column; gap: 16px">\n<span class="pn" aria-hidden="true">{n}</span>\n<h3 class="h3" style="font-size: clamp(1.75rem,1.4rem + 1vw,2.25rem)">{t}</h3>\n<p class="lead">{b}</p>\n</div>')
    return "\n".join(btns), "\n".join(panes)


def checks_html():
    return "\n".join(
        f'<label class="ck"><input type="checkbox" data-ck><span>{html.escape(l)}</span></label>' for l in CHECKS)


SC_IF = {
    "notSent": '<div data-form-body>',
    "sent": '<div data-form-done hidden>',
    "hasErr": '<div data-errbox hidden style="grid-column: 1/-1">',
    "show.rp": '<div data-aud="rp">',
    "show.ma": '<div data-aud="ma">',
    "show.both": '<div data-aud="both">',
}


def sc_if(m):
    key = m.group(1)
    if key.startswith("err."):
        return f'<div data-err="{key[4:]}" hidden>'
    return SC_IF[key]


def transform(name, src):
    body = src.split("<x-dc>", 1)[1].split("</x-dc>", 1)[0]
    helmet = re.search(r"<helmet>(.*?)</helmet>", body, re.S)
    css = "\n".join(re.findall(r"<style>(.*?)</style>", helmet.group(1), re.S)).strip()
    body = body.replace(helmet.group(0), "")

    # shared nav
    body = body.replace('aria-expanded="{{menuOpen}}" onClick="{{toggleMenu}}"',
                        'aria-expanded="false" aria-controls="drawer" data-menu-toggle')
    body = body.replace('<nav class="drawer {{drawerCls}}" aria-label="Mobile">',
                        '<nav class="drawer" id="drawer" aria-label="Mobile" data-drawer>')
    body = body.replace("<main>", '<main id="main">')

    # forms
    body = body.replace('<form onSubmit="{{submit}}"',
                        '<form data-booking-form novalidate')
    body = re.sub(r'(<form data-booking-form novalidate[^>]*>)',
                  r'\1\n<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">', body)
    body = body.replace("{{sentName}}", "<span data-sent-name>there</span>")
    body = body.replace('onClick="{{again}}"', "data-again")

    # home: audience tabs + steps
    body = body.replace('class="{{rpCls}}" type="button" aria-pressed="{{rpOn}}" onClick="{{setRp}}"',
                        'class="on" type="button" aria-pressed="true" data-tab="rp"')
    body = body.replace('class="{{maCls}}" type="button" aria-pressed="{{maOn}}" onClick="{{setMa}}"',
                        'type="button" aria-pressed="false" data-tab="ma"')
    body = body.replace('class="pane {{rpCls}}"', 'class="pane on" data-pane="rp"')
    body = body.replace('class="pane {{maCls}}"', 'class="pane" data-pane="ma"')
    b, p = steps_html()
    body = re.sub(r'<sc-for list="\{\{steps\}\}" as="item" hint-placeholder-count="5">.*?</sc-for>', lambda m: b, body, flags=re.S)
    body = re.sub(r'<sc-for list="\{\{steps\}\}" as="item" hint-placeholder-count="1">.*?</sc-for>', lambda m: p, body, flags=re.S)
    body = body.replace('style="width: {{barW}}"', 'style="width: 20%" data-step-bar')
    body = body.replace('<span>{{nextLabel}}</span><span aria-hidden="true">{{nextLabel}}</span>',
                        '<span data-next-label>Next: Secure transfer</span><span aria-hidden="true" data-next-label>Next: Secure transfer</span>')
    body = body.replace('onClick="{{stepNext}}"', "data-step-next")

    # use cases filter
    for key, f, on in (("All", "all", True), ("Rp", "rp", False), ("Ma", "ma", False)):
        body = body.replace(f'class="{{{{f{key}}}}}" type="button" aria-pressed="{{{{p{key}}}}}" onClick="{{{{show{key}}}}}"',
                            ('class="on" ' if on else "") + f'type="button" aria-pressed="{"true" if on else "false"}" data-filter="{f}"')
    body = body.replace('style="margin: -24px 0 28px">{{countLabel}}', 'style="margin: -24px 0 28px" data-count>Showing 9 of 9 use cases')

    # support file self-check
    body = body.replace("{{done}} / {{total}}", f"<span data-ck-done>0</span> / {len(CHECKS)}")
    body = body.replace('<span class="ck-msg">{{msg}}</span>', '<span class="ck-msg" data-ck-msg>Tick each item that is true for the file in front of you.</span>')
    body = body.replace('style="width: {{pct}}"', 'style="width: 0%" data-ck-bar')
    body = body.replace('onClick="{{reset}}"', "data-ck-reset")
    body = re.sub(r'<sc-for list="\{\{items\}\}".*?</sc-for>', lambda m: checks_html(), body, flags=re.S)

    # conditionals
    body = re.sub(r'<sc-if value="\{\{\s*([\w.]+)\s*\}\}"[^>]*>', sc_if, body)
    body = body.replace("</sc-if>", "</div>")

    # links
    body = re.sub(r'href="(\w+)\.dc\.html"', lambda m: f'href="{LINKS[m.group(1)]}"', body)

    leftovers = re.findall(r"\{\{.*?\}\}|<sc-|onClick=|onChange=|onSubmit=|\.dc\.html", body)
    if leftovers:
        raise SystemExit(f"{name}: unconverted template syntax: {set(leftovers)}")
    return body.strip(), css


def schema(name, cfg, body):
    url = DOMAIN + LINKS[name]
    graph = [ORG]
    page = {"@type": cfg["type"] if cfg["type"] != "Article" else "WebPage", "@id": url + "#page", "url": url,
            "name": cfg["title"], "description": cfg["desc"], "inLanguage": "en-GB",
            "isPartOf": {"@id": DOMAIN + "/#website"}, "dateModified": TODAY}
    graph.append(page)
    if name == "Main":
        graph.append({"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/",
                      "name": "Support Audit", "publisher": {"@id": DOMAIN + "/#org"}, "inLanguage": "en-GB"})
    if cfg["crumbs"]:
        items = [("Home", "/")] + cfg["crumbs"]
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(items)]})
        page["breadcrumb"] = {"@id": url + "#crumbs"}
        graph[-1]["@id"] = url + "#crumbs"
    if name in ("About",) or cfg["type"] == "Article":
        graph.append(PERSON)
    if cfg["type"] == "Article":
        cites = sorted(set(re.findall(r'href="(https://(?:www\.)?(?:legislation|gov)\.uk[^"]*|https://homeless\.org\.uk[^"]*)"', body)))
        graph.append({"@type": "Article", "@id": url + "#article", "headline": cfg["headline"],
                      "description": cfg["desc"], "mainEntityOfPage": {"@id": url + "#page"},
                      "datePublished": TODAY, "dateModified": TODAY, "inLanguage": "en-GB",
                      "image": DOMAIN + "/assets/og.png",
                      "author": {"@id": DOMAIN + "/about/#jamie"}, "publisher": {"@id": DOMAIN + "/#org"},
                      "citation": cites})
    if name == "Audits":
        for sname, aud, d in (
            ("Mock Audit", "Managing agents and support providers in supported housing",
             "A fixed-fee review of a sample of resident support files, rated Gold, Green, Amber or Red, with an action plan and debrief."),
            ("Audit Rounds", "Registered Providers working with managing agents",
             "Every resident file for a managing agent audited on a regular cycle, usually every six months, with per-resident reports and overall agent feedback."),
            ("Monitoring", "Registered Providers, managing agents and support providers",
             "Monthly sampling of resident files between audits, with early warning on reviews, support hours and missed sessions."),
        ):
            graph.append({"@type": "Service", "name": sname, "serviceType": "Supported housing resident support file audit",
                          "provider": {"@id": DOMAIN + "/#org"}, "areaServed": "England",
                          "audience": {"@type": "BusinessAudience", "audienceType": aud}, "description": d,
                          "url": url})
    if name == "Resources":
        terms = re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", body, re.S)
        graph.append({"@type": "DefinedTermSet", "@id": url + "#glossary", "name": "Supported housing glossary",
                      "hasDefinedTerm": [{"@type": "DefinedTerm", "name": strip(t), "description": strip(d)} for t, d in terms]})
    q = faqs(body) if name != "About" else []
    if q:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": q})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


HEAD = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Support Audit">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{domain}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{extra}<meta name="theme-color" content="#0A1A2F">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/logo.png">
<link rel="preload" href="/assets/fonts/schibsted-grotesk-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/schibsted-grotesk-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<style>
{css}
</style>
<script type="application/ld+json">
{ld}
</script>
<script src="/assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def main():
    for name, cfg in PAGES.items():
        src = open(os.path.join(SRC, name + ".dc.html"), encoding="utf-8").read()
        body, css = transform(name, src)
        url = DOMAIN + LINKS[name]
        extra = ""
        if cfg["type"] == "Article":
            extra = (f'<meta property="article:published_time" content="{TODAY}">\n'
                     f'<meta property="article:modified_time" content="{TODAY}">\n'
                     '<meta name="author" content="Jamie McCollin">\n')
        page = HEAD.format(title=html.escape(cfg["title"]), desc=html.escape(cfg["desc"]), url=url,
                           ogtype="article" if cfg["type"] == "Article" else "website", domain=DOMAIN,
                           extra=extra, css=css, ld=schema(name, cfg, body)) + body + "\n</body>\n</html>\n"
        path = os.path.join(OUT, LINKS[name].strip("/"), "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(page)
        print("wrote", os.path.relpath(path, ROOT))

    urls = "\n".join(
        f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in LINKS.values())
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    print("wrote docs/sitemap.xml")


if __name__ == "__main__":
    main()
