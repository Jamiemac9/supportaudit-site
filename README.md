# seaaudit.com

Website for **SEA Audit**: independent resident support file audits for supported exempt accommodation (SEA) and transitional supported housing in England.

- `dist/` is the finished website. This is the folder Cloudflare serves.
- `src/` is the source: page content (`src/pages`), styles, scripts, fonts and images.
- `tools/build.py` turns `src/` into `dist/`: shared header and footer, structured data, minified and cache-busted assets, `sitemap.xml`, `robots.txt`, `llms.txt`, and Cloudflare `_headers` and `_redirects`.

## Deploy on Cloudflare Pages

### Option A: upload the folder (quickest)
1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Upload assets**.
2. Name the project `seaaudit`, upload the contents of `dist/` (or the zip), then **Deploy site**.
3. To update later: open the project → **Create deployment** → upload the new `dist/`.

### Option B: connect this GitHub repo (updates go live on every push)
1. **Workers & Pages** → **Create** → **Pages** → **Connect to Git** → choose this repository.
2. Production branch `main`. Framework preset **None**. Build command: *leave empty*. Build output directory: `dist`.
3. **Save and Deploy**.

### Custom domain
1. Add `seaaudit.com` to Cloudflare (**Add a domain**, Free plan) and change the nameservers at your registrar to the two Cloudflare gives you.
2. Pages project → **Custom domains** → add `seaaudit.com`, then add `www.seaaudit.com`.
3. **Rules** → **Redirect Rules** → create from the template **Redirect from WWW to root** so there is one canonical address.
4. **SSL/TLS** → Edge Certificates → turn on **Always Use HTTPS**.

## Search engines (Google, Bing and others)
- **Google Search Console**: add a *Domain* property for `seaaudit.com` (Cloudflare can add the DNS record for you), then submit `https://seaaudit.com/sitemap.xml`.
- **Bing Webmaster Tools**: sign in and choose **Import from Google Search Console**. This verifies the site and copies the sitemap. Bing also powers DuckDuckGo, Yahoo and Ecosia results and is used by several AI assistants.
- **IndexNow** (instant notification to Bing, Yandex, Seznam, Naver): Cloudflare → **Caching** → **Configuration** → turn on **Crawler Hints**. A key file is also included (`/e1aec5c07168f339e17a9e3a75882ea1.txt`) for manual submissions.
- **AI assistants**: `robots.txt` allows search and answer crawlers and `llms.txt` summarises the site. In Cloudflare → **Security** → **Bots**, check that *Block AI bots* is off if you want to be cited by ChatGPT, Claude, Perplexity and others.
- Optional verification tags: set `BING_VERIFY` or `GOOGLE_VERIFY` in `tools/build.py` and rebuild.

## Analytics (GA4, Consent Mode v2)
GA4 property `G-4KW5S92V6Z` is installed on every page with Google Consent Mode v2. A small notice asks visitors to accept analytics; Google's tag only loads after they accept, as UK PECR rules currently require. The choice can be changed from **Cookie settings** in the footer. Booking form submissions send a `generate_lead` event: mark it as a key event in GA4 (**Admin** → **Events**).

In GA4 → **Admin** → **Data streams**, set the stream URL to `https://seaaudit.com`.

## UK traffic and bot filtering
- Most unexplained "China" or "Singapore" traffic in GA4 since 2025 is a known bot pattern: zero engagement, sessions under 10 seconds, often landing on 404s. The consent notice already keeps most of it out, because bots don't accept cookies.
- To stop it at the edge: Cloudflare → **Security** → **Bots** → turn on **Bot Fight Mode**. Then **Security** → **WAF** → **Custom rules** → create a rule:
  - Expression: `(ip.src.country ne "GB" and not cf.client.bot)`
  - Action: **Managed Challenge**

  Real overseas visitors see a one-click check, verified search engine crawlers pass straight through, and scripted bots are stopped.
- For past data in GA4, build an **Exploration** with a segment that excludes Country = China and Singapore. Data that has already been processed can't be deleted.

## Booking form
Until a key is added, the form opens the visitor's email app with their details filled in. To receive requests by email automatically:
1. Get a free access key at [web3forms.com](https://web3forms.com) using `hello@seaaudit.com`.
2. Paste it into `WEB3FORMS_KEY` at the top of `src/assets/js/app.js`, rebuild, and redeploy.

## Editing
1. Edit a page in `src/pages/` (content only; the header, footer and metadata are added by the build).
2. Update `TODAY` in `tools/build.py` (it sets `lastmod` in the sitemap and `dateModified` in structured data).
3. `npm install` (first time only), then `python3 tools/build.py`.
4. Preview with `npm run serve` and open http://localhost:8080, then deploy `dist/`.

Placeholders to replace before launch: `[ICO number]` and `[Founder photo]` on the About page, plus the full privacy notice and terms.

## Moving from supportaudit.co.uk
Once seaaudit.com is live:
1. In this repository → **Settings** → **Pages**, unpublish the old site (the `docs/` folder is the old Support Audit site and can then be deleted).
2. At Namecheap, set `supportaudit.co.uk` to a permanent (301) **URL Redirect** to `https://seaaudit.com`, or move the domain to Cloudflare and add a Redirect Rule that keeps the path.

## Credits
Font: Schibsted Grotesk (SIL Open Font License), self-hosted. Smooth scrolling: Lenis (MIT).
