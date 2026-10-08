# supportaudit.co.uk

Static website for **Support Audit**: independent resident support file audits for supported exempt and transitional housing in England.

Plain HTML, CSS and JavaScript. No build step is needed to publish. The live site is everything in [`/docs`](docs), served by GitHub Pages.

## Structure

```
docs/                                   ← the website (GitHub Pages publishes this folder)
  index.html                            Home
  audits/                               Audits: Mock Audit, Audit Rounds, Monitoring
  use-cases/                            Nine use cases, filterable
  resources/                            Quick answers, key dates, glossary, sources
  resources/supported-housing-licensing/   Guide: licensing explained
  resources/resident-support-file/      Guide: what a good support file contains
  about/                                About, method, data protection
  book-a-call/                          Booking form
  404.html, robots.txt, sitemap.xml, llms.txt, CNAME
  assets/site.css, assets/site.js, assets/fonts/, og.png, favicon.svg
tools/build.py                          Converts the Claude design canvas export into /docs
SEARCH-SPEC.md                          SEO, answer engine and AI search spec
```

## Go live on GitHub Pages with a Namecheap domain

1. **Turn on Pages.** Repo → Settings → Pages → Source: *Deploy from a branch* → Branch `main`, folder `/docs` → Save.
2. **Add the domain in GitHub.** Same page → Custom domain: `supportaudit.co.uk` → Save.
3. **Point Namecheap at GitHub.** Namecheap → Domain List → Manage → *Advanced DNS*. Delete the default parking records (`CNAME www → parkingpage.namecheap.com` and `URL Redirect @`), then add:

   | Type | Host | Value |
   |---|---|---|
   | A Record | `@` | `185.199.108.153` |
   | A Record | `@` | `185.199.109.153` |
   | A Record | `@` | `185.199.110.153` |
   | A Record | `@` | `185.199.111.153` |
   | CNAME Record | `www` | `jamiemac9.github.io.` |

   Leave any MX/TXT records for email alone.
4. **Wait for DNS** (usually 10 to 60 minutes, up to 24 hours), then tick **Enforce HTTPS** in Settings → Pages.
5. **Verify the domain** (recommended, stops domain takeover): GitHub profile → Settings → Pages → Add a domain → add the TXT record it gives you in Namecheap.

## Booking form

Until a key is added, the form opens the visitor's email app with their details. To receive submissions by email instead:

1. Get a free access key at [web3forms.com](https://web3forms.com) using hello@supportaudit.co.uk.
2. Paste it into `WEB3FORMS_KEY` at the top of `docs/assets/site.js`, then commit and push.

## Editing

Edit the HTML in `docs/` directly and push. Pages republishes within a minute or two. When you change a page, update its `dateModified` in the page's JSON-LD and `<lastmod>` in `docs/sitemap.xml`.

Before launch, replace the placeholders: `[ICO number]`, `[Founder photo]`, `[Full privacy notice to be added.]`, `[Full terms to be added.]`.

Font: Schibsted Grotesk, self-hosted under the SIL Open Font License (`docs/assets/fonts/OFL-LICENSE.txt`).
