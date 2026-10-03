# HZORTECH v2 — Phase 1: Repository Inventory & Design Audit

Audited: 2026-09-30, branch `master` @ `5065fca` (live site matched the repo at audit time).

---

## 1. Repository inventory

| Area | Finding |
|---|---|
| **Frontend architecture** | Server-rendered Django templates. No build step. Bootstrap 5.3.3 + Bootstrap Icons from jsDelivr CDN on every page. GSAP 3.12.5 + ScrollTrigger (CDN, home only). Three.js 0.169 via import map (home only). Leaflet 1.9.4 from unpkg + CARTO tiles (contact only). ~1,370-line `base.html` holding all CSS, all global JS and a ~700-line inline EN/HY/RU dictionary. `static/business_page/js/i18n.js` (402 lines) is **not referenced anywhere**, so it is dead code. |
| **Django architecture** | Django 6.0, one project (`hzortech`), one app (`business_page`). Function views. `SecurityHeadersMiddleware` sets CSP (`script-src 'unsafe-inline'`), HSTS and so on. WhiteNoise `CompressedManifestStaticFilesStorage`. |
| **Templates** | `base`, `home` (1,301 lines), `about`, `services` (695), `service_detail` (shared by 10 slugs), `projects`, `contact`, `blog`, `privacy`, `404`. Heavy inline `style=""`. |
| **Content sources** | `services_data.py` is a plain dict of 10 service landing pages. Projects, blog, about and home copy are all hard-coded in templates. |
| **APIs** | None. No JSON endpoints. |
| **Forms** | `ContactForm` (name, email, subject optional, message). The newsletter form is raw POST with no Django form, and nothing is persisted. |
| **Database** | One model: `ContactSubmission`. PostgreSQL in production (`POSTGRES_HOST` present), SQLite fallback locally. |
| **Routing** | `/`, `/about/`, `/services/`, `/services/<slug>/` (10), `/projects/`, `/contact/`, `/privacy/`, `/blog/`, `/newsletter/` (POST), `/admin/`, `/sitemap.xml`, `/robots.txt`, `/security.txt`. |
| **Auth** | Django admin only. No public auth. |
| **Deployment** | GitHub Actions `deploy.yml`: every push to `master` builds `ghcr.io/thesharaavakian/hzortech:latest` and deploys over SSH to EC2 (t3.micro) running `docker compose` (postgres 15 + django/gunicorn + nginx:80). Cloudflare Flexible SSL in front. Terraform provisions EC2. There is **no test or lint stage**. `k8s/`, `nginx.conf`, `nginx_bootstrap.conf` and `run_gunicorn.sh` are dead. |
| **Env vars** | `DJANGO_SECRET_KEY` (required), `DEBUG`, `POSTGRES_*`, `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `CONTACT_EMAIL`, `TURNSTILE_SITE_KEY/SECRET_KEY`. Locally, `.env.local` (gitignored) holds `HF_KEY` for Higgsfield. |
| **Python packages** | Django 6, gunicorn, whitenoise, psycopg2-binary, requests. The Higgsfield SDK (`higgsfield-client 0.2.0`) is intentionally kept out of the production image. |
| **Static/media** | 12 MB: 26 AI-generated JPG stills (1376×768, navy/blue "glowing icon" style), 8 MP4 loops, favicon set, designer logo mark. There is no `MEDIA_ROOT`. `graphics-new/` (untracked) holds the designer's master logo (3544×4843 PNG), favicon master and social posts. |
| **Tests** | `tests.py` is empty, so coverage is zero. |

### Tools, MCP servers and skills: availability, test and relevance

| Tool | Status (tested) | Relevant? | Planned use |
|---|---|---|---|
| Higgsfield REST API via `higgsfield-client` + `HF_KEY` | ✅ Auth verified. A valid key returns 404 on a fake request id and a bad key returns 401. `GET /models` lists 82 models. | Yes | Server-side, asynchronous generation of a small set of hero/scroll assets |
| Higgsfield MCP server | ❌ Needs OAuth, which a non-interactive session can't complete | Superseded by the REST API | — |
| Higgsfield CLI | Installed, but the previous session found it trial-blocked | No | — |
| Playwright MCP | ✅ Captured desktop and mobile screenshots of 5 live client sites | Yes | Case-study imagery, full QA (routes, forms, keyboard, reduced motion, viewports, console) |
| Built-in browser pane | ✅ Loaded hzortech.com | Yes | Visual spot checks |
| Claude-in-Chrome | Available (deferred) | No (Playwright covers it) | — |
| Figma, Notion, Linear and other design-plugin MCPs | ❌ Need auth | No | — |
| Skills: `awwwards-animations`, `gsap-scrolltrigger`, `threejs-webgl`, `higgsfield-generate`, `design:accessibility-review`, `design:ux-copy`, `design:design-critique` | Available | Yes | Motion architecture (Lenis↔ScrollTrigger integration, cleanup), WebGL scene, model/prompt selection, WCAG pass, microcopy, self-critique |
| 3D-engine skills (Babylon, PlayCanvas, A-Frame, Spline, Rive, Lottie, Blender, Substance, PixiJS) | Available | **No.** One restrained Three.js scene is enough, and more engines would only add bytes | Not used |
| `higgsfield-websites` | Available | **No.** It deploys to Cloudflare Workers/TanStack, which conflicts with the "Django stays" requirement | Not used |

Local toolchain: Node 22, npm 9, Python 3.14, Docker, Pillow. **No ffmpeg** (the `imageio-ffmpeg` wheel will be used). **The disk is 97% full (about 4.9 GB free)**, so dependencies stay lean.

---

## 2. Design audit

### 2.1 Contradictions and broken UX (highest priority)

| # | Issue | Where |
|---|---|---|
| C1 | **The homepage statistics contradict each other and every other page.** "50+ Projects Delivered" vs "20+ businesses" (hero, same page) vs "Six live engagements" (projects page). "99.9% Success Rate" is undefined, and "1M+ Lines of Code" is a vanity metric. | `home.html` counter strip |
| C2 | **Four competing service taxonomies**: 4 layers (home), 6 sections (services index), 10 landing pages (service_detail), and 6 "core fields" (about). The footer links to 6 anchors, and the services index duplicates the detail pages with different copy, which causes SEO cannibalisation. | home, services, about, footer |
| C3 | The **WhatsApp link uses the wrong country code**, `wa.me/34777075919` (Spain), where it should be +374 77 075 919 (Armenia). It appears twice. | base.html |
| C4 | The **Meta Pixel fires before any consent**, yet the cookie banner says "essential cookies only. No tracking." and the privacy policy says "We do not use cookies for tracking purposes." This is a legal and trust contradiction. | base.html, privacy.html |
| C5 | **Contact form required/optional confusion.** A fake terminal line says "all fields except subject are required", while labels carry no required markers. Placeholders act as labels, and the labels aren't bound to inputs (no `for`/`id`). "Include URGENT in subject for same-day triage" depends on the one optional field and contradicts the 48-hour promise. `novalidate` is set, errors are shown in colour only and are never announced. | contact.html, forms.py |
| C6 | **Cloud coverage contradicts itself.** The services FAQ claims "Azure, GCP, VMware", while the cloud page says "We specialise in AWS." The listed AWS regions also differ between pages. | services.html vs services_data |
| C7 | **Migration downtime contradicts itself.** "Downtime: 0 minutes (guarantee)" vs "minimal downtime" vs "zero downtime". SOC 2 is listed on one page but not the other. Uptime claims vary (99.9% SLA, 99.99% target). | services.html, services_data |
| C8 | **Unattributed outcome claims** are presented as results: "−78% detection time", "15×/day (from 2×/week)", "−60% compute cost", "~80% alert noise reduction", "2,000-endpoint reference". None is tied to a named, verifiable engagement. | services, services_data |
| C9 | **The blog has no articles.** Every "Request Full Guide" button goes to the contact page, while the schema declares a `Blog`. | blog.html |
| C10 | "**Careers: ELITE ONLY**" lists 4 "[OPEN]" roles in a fake terminal for a two-person company that elsewhere says "the core stays the two of us". | home.html vs about.html |
| C11 | The **"Proof of craft" deploy snippet** shows `./scripts/deploy.sh --strategy=blue-green` and claims a "pinned SHA" while showing a tag. The company's own pipeline deploys `:latest` with no blue/green. security.txt says "We practise what we sell." | home.html, deploy.yml |
| C12 | **Newsletter**: it promises a "Monthly Security Health Check", but signups aren't stored anywhere (`fail_silently`, no model). | views.newsletter_signup |
| C13 | **Schema errors.** `SearchAction` points at a search the site doesn't have. The Armenian mobile number is marked `contactOption: TollFree`. The `hreflang` block is broken (the `hy` alternate sits inside a malformed comment), and every alternate points to the same English URL. | base.html |
| C14 | `service_detail.html` puts a `<style>` element inside base's `<style>`, which is invalid CSS nesting and truncates the stylesheet early. | service_detail.html |
| C15 | The security.txt contact (`shara@`) differs from the sitewide contact (`contact@`). | security.txt |

### 2.2 Typography
- A single family (Inter Tight) is used for everything, and there are about ten micro-mono labels per viewport (`.hz-label` at 0.62–0.7rem, uppercase, spaced). Monospace captions compete with the body text and no hierarchy survives.
- Every H1 and H2 is uppercase at weight 900. Service H1s such as "AUTOMATED. SCALABLE. ZERO DOWNTIME." say nothing about the page topic, which hurts both SEO and clarity.
- Body copy sits at 0.8–0.88rem in many cards, below comfortable reading size, and muted grey on off-white lowers readability further.

### 2.3 Layout, spacing, hierarchy
- The whole site is card grids inside a Bootstrap `.container`, separated by `<hr>`. Every section carries the same weight, so there is no rhythm or pacing.
- Heavy inline styles (hundreds of `style=""` attributes) mean there is no real component system.
- Heading levels skip (h2 → h5 in the layer cards).

### 2.4 Navigation and information architecture
- The primary CTA reads "Initialize", jargon that says nothing about what happens next. The floating "Send Brief" button, the floating WhatsApp button, the nav CTA and the in-page CTAs all compete.
- "SYSTEMS ONLINE" with a pulsing dot, and "CTRL+K", are decorative chrome that suggest a product dashboard, not a services company.
- The command palette has no focus trap and no labelled title. It searches only 5 links.
- Projects are not individually linkable (only `#anchors`), so there is no deep case-study URL to share.

### 2.5 Content density and copy
- The mission statement is abstract ("engineering sovereignty", "fusion of Armenian engineering precision with the frontier…").
- Service pages are ten copies of one template: problem, solution, stack chips, deliverables, 5 steps, FAQ, with identical structure and visuals.
- The About page reads like a résumé (bullet cards of prior employers) with no narrative. It never explains the name: *hzor* (հզոր) means "strong".

### 2.6 Imagery and colour
- The 26 AI stills share a navy/blue "glowing icon" look (shields, houses, clouds, DNA helix). They are **literal, generic and off-brand**: the designer's identity is black and crimson (`#BB1F25`) with a sword monogram and Armenian ornament, but the imagery is navy blue.
- Real proof isn't used. Four of the five client sites are live and screenshot-able (captured during this audit), but the site shows abstract renders of "a car made of circuits".
- **The GSG Computers live site (gsgcomp.am) is currently rendering broken, with no CSS and 170 console errors.** Flag this to the client.

### 2.7 Repeated terminal/code visual language
There are about 10 fake terminals: the hero code background, the contact "initiate --consultation", the careers "scan --talent", three blog cards, three proof-of-craft tabs, and the migration deep-dive. Together they read as costume rather than competence, and several contain claims the company's own infrastructure doesn't meet (C11).

### 2.8 Interaction and animation
- The hero pins for 320% of the viewport. That is a long scroll-jack before any proof, and the memory notes the history of jank fixes it needed.
- Pulsing badges, a ticker with no pause control (a WCAG 2.2.2 failure for keyboard and touch users), magnetic buttons, tilt cards, reveal-on-scroll everywhere, and ring glows. Motion is everywhere, so none of it is meaningful.
- The `.reveal` class hides content (`opacity:0`) until JavaScript runs, and a 2.5 s watchdog was needed.

### 2.9 Accessibility
Unbound form labels; errors announced by colour only; no skip link; the command palette lacks a focus trap; icon-only social links rely on inline `onmouseover`; the language switcher uses `onclick` attributes on buttons with no state (`aria-pressed`); decorative text uses low-contrast `--dim` grey (#909399 on #F7F7F5 ≈ 2.9:1, a fail); the auto-scrolling ticker; reduced-motion handling is partial.

### 2.10 Responsive
The layout is desktop-first and simply stacks on mobile. The mobile hero is a full 100dvh pinned sequence with WebGL. The gallery is desktop-only horizontal. Floating CTA and WhatsApp buttons overlap content at 390px.

### 2.11 Performance
Render-blocking Bootstrap CSS (about 230 KB with icons) on every page. Four videos plus Three.js with bloom plus GSAP on the home page. Font CSS loads from Google (third-party). The inline 700-line i18n dictionary ships on every page. The Leaflet map pulls from two third-party origins.

### 2.12 Conversion
There is one intake path, a 4-field form, with no project-type qualification, no budget or timeline signal, and no visible "what happens next". CTAs are labelled with jargon ("Initialize collaboration").

### 2.13 SEO
- Meta keywords (ignored by search engines) and titles stuffed with "in Armenia | HZORTECH Yerevan".
- The services index duplicates the ten landing pages.
- There are no article URLs and no project URLs.
- The hreflang implementation is broken (C13), and the client-side JS translation means Armenian and Russian content is invisible to crawlers.
- The sitemap has no `lastmod`.

### 2.14 Trust and credibility
Unverifiable statistics (C1, C8); "elite" self-description; an empty blog; fake open roles; monogram-only founders; claims contradicted by the company's own pipeline. Real, strong assets go unused: named live clients, a national research HPC engagement, founders with banking, security and HPC backgrounds, and a genuinely good designer mark.

### 2.15 Case-study presentation
Projects are six equal cards with a spec table. There is no problem → system → architecture → outcome story, no deep links, and no real screenshots. Two strong named clients (GSG Computers, Arev Motors) appear only on the homepage and are missing from the projects page.

---

## 3. What v2 preserves (facts)
Company facts (Yerevan; founded 2022; two founders with the stated backgrounds; contact@hzortech.com; +374 77 075 919; Mon–Fri 09:00–18:00 GMT+4; EN/HY/RU communication). All 10 service slugs and their technical substance (stacks, deliverables, processes, FAQs). All 8 named clients and their stated scopes, stacks and outcomes. Engagement models. Compliance frameworks *aligned to* (not certified). Turnstile, the ContactSubmission model, admin, the email flow, the Meta Pixel (now consent-gated), and the deployment topology.

## 4. What v2 removes or reframes, pending a source
C1 stats → replaced with verifiable facts. C8 outcome percentages → removed from headline positions and listed in the final report so they can be restored with attribution. C10 open roles → replaced with an honest "we work with trusted specialists" note. C11 snippets → replaced with real configuration from this repository.
