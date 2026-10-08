# Search and AI visibility spec

How supportaudit.co.uk is built to rank (SEO), be quoted as the answer (AEO), and be cited by AI assistants and Google AI Overviews (GEO / AIO).

## 1. Entity statement (use word for word everywhere)

> Support Audit is an independent audit service for supported exempt and transitional housing in England, auditing resident support files for Registered Providers and managing agents and rating each file Gold, Green, Amber or Red.

Use it on the site, in schema, on LinkedIn, Google Business Profile, Bing Places and every directory listing. Keep name, area served (England) and contact (hello@supportaudit.co.uk) identical everywhere.

## 2. Page map

| Page | URL | Title | Primary query | Schema |
|---|---|---|---|---|
| Home | `/` | Support Audit \| Supported Housing File Audits | supported housing audit | ProfessionalService, WebSite, FAQPage |
| Audits | `/audits/` | Supported Housing Audits: Mock Audit and Audit Rounds | mock audit supported housing | Service ×3, FAQPage, BreadcrumbList |
| Use cases | `/use-cases/` | When to Audit Supported Housing Files | managing agent audit supported housing | WebPage, BreadcrumbList |
| Resources | `/resources/` | Supported Housing Guides, Glossary and Key Dates | supported exempt accommodation | CollectionPage, DefinedTermSet, FAQPage |
| Licensing guide | `/resources/supported-housing-licensing/` | Supported Housing Licensing Explained (2026 Update) | supported housing licensing | Article, FAQPage, BreadcrumbList |
| Support file guide | `/resources/resident-support-file/` | What a Good Resident Support File Contains | resident support file checklist | Article, BreadcrumbList |
| About | `/about/` | About Support Audit \| Independent, Evidence-Led | brand | AboutPage, Person |
| Book a call | `/book-a-call/` | Book a Discovery Call \| Support Audit | brand | ContactPage, FAQPage |

All of this is already in each page's `<head>`.

## 3. Build rules (already applied)

- Question-style H2s followed by a direct 40–60 word answer.
- All content in the HTML on load; JavaScript only shows and hides.
- Visible published and reviewed dates and a named author on guides, matching Article schema.
- Primary sources (legislation.gov.uk, GOV.UK) linked and numbered.
- Comparisons as real HTML tables.
- `robots.txt` allows search and AI crawlers; `llms.txt` summarises the site; `sitemap.xml` has lastmod dates.
- FAQ markup no longer earns Google rich results for most sites (restricted since August 2023), but it still helps machines read the Q&A.

## 4. After launch

1. Add the site to **Google Search Console** and **Bing Webmaster Tools** (Bing feeds several AI assistants) and submit `sitemap.xml`.
2. Create a Google Business Profile as a service-area business and a Bing Places listing using the entity statement.
3. Review the licensing guide whenever government publishes draft regulations (expected late 2026) and update its dates.

## 5. Next ten guides

| Guide | Target question | Links to |
|---|---|---|
| Supported exempt accommodation explained | What is supported exempt accommodation? | Audits |
| Support plan goals that evidence real support | How do I write support plan goals? | Mock Audit |
| Session notes that pass an audit | How should support session notes be written? | Mock Audit |
| Risk assessments and risk management plans | When does a risk need a management plan? | Audit rounds |
| Registered Provider or managing agent: who is responsible? | Who is responsible for support in leased supported housing? | Audit rounds |
| Evidencing move-on in transitional housing | How do you evidence move-on? | Audits |
| A simple process for missed support sessions | What happens when a resident misses a session? | Monitoring |
| A 12-month plan to get licence-ready | How do I prepare for supported housing licensing? | Mock Audit |
| Local supported housing strategies explained | What does the 31 March 2027 deadline mean? | Licensing guide |
| What councils look for in exempt Housing Benefit claims | How do councils check exempt claims? | Mock Audit |
