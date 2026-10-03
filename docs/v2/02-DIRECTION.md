# HZORTECH v2 — Architecture & Creative Direction

## 1. Architecture decision

**Chosen: Django server-rendered pages + Vite/React/TypeScript "islands".**

| Option | Verdict |
|---|---|
| Next.js (headless Django) | Rejected. It needs a second Node runtime on a 1 GB t3.micro that already runs Postgres, Gunicorn and nginx. It would duplicate routing, SEO and form/CSRF handling, and every content page would depend on an API round trip. It adds complexity without a user-visible gain for a content-and-conversion site. |
| React SPA served by Django | Rejected. Content is invisible without JavaScript, SEO and time-to-first-content get worse, and it breaks the no-JS form fallback. |
| **Django templates + Vite islands** | **Chosen.** Django remains the system of record and renders every page (SEO, forms, CSRF, admin, zero-JS baseline). Vite builds one small core bundle (motion system, navigation, reveals) plus lazily loaded React islands for real interactivity (system map, project intake, command menu, service signatures, WebGL hero), code-split per island and mounted only when they approach the viewport. There is a single deploy unit, and no Node runs in production because the frontend is built in a Docker stage. |

```
browser ──► nginx ──► gunicorn/Django ──► PostgreSQL
                        │  renders HTML (all content, SEO, forms)
                        │  /api/v1/* JSON (intake, subscribe, search index, content)
                        └─ /static/dist/* ◄── Vite build (hashed, immutable)
                                   core.js  (Lenis + GSAP + reveals + nav, ~40 KB gz)
                                   islands/*.js  (lazy, per component)
```

- `frontend/`: Vite 6 + React 19 + TypeScript. `vite build` writes `frontend/dist` and a manifest, and Django serves it at `/static/dist/`. The `{% vite %}` template tag reads the manifest (CSS, entry, modulepreload); in development it points at the Vite dev server.
- **Islands protocol:** `<div data-island="system-map" data-props-id="…">` plus `{{ data|json_script }}`. The core runtime observes islands and calls `import()` on the chunk when the island is within about one viewport. Every island renders server-side fallback content first, so the page works without JS.
- **Content models:** `CaseStudy` and `Post` (Django models, admin-editable, seeded by data migrations), `Subscriber` (double opt-in), an extended `ContactSubmission` (intake fields), and `GeneratedAsset` (the Higgsfield request ledger). Services stay in `services_data.py`, restructured into a layer taxonomy.
- **Security:** a per-request CSP nonce. `script-src 'self' 'nonce-…'` with no `unsafe-inline` for scripts. Third-party origins shrink to Cloudflare Turnstile plus the consent-gated Meta Pixel. Fonts are self-hosted.
- **CI:** a new `test` job (ruff, Django tests, tsc, eslint, vitest, vite build) gates `deploy`. Images are tagged with the commit SHA in addition to `latest`.

## 2. Creative direction — "Forged Systems"

The brand already carries a strong idea: **hzor (հզոր) means *strong*.** The mark is a hand gripping a sword, with an Armenian eternity sign on the pommel. The designer's posts are black, crimson and condensed heavy type: *"Strength in code. Power in tech."*

v2 turns that into a system:

- **Engineering:** hairline blueprint grids, registration marks and coordinates (`40.1792° N 44.4991° E`), section indices (`§ 03`), and precise mono annotations used sparingly.
- **Cinema:** full-bleed black frames, letterboxed video, slow deliberate camera moves, one crimson light source per scene.
- **Systems:** every capability is shown as part of one architecture (Product → Platform → Automation → Infrastructure, with Security as a perimeter through all of them).
- **Motion:** motion *explains*. Particles become the mark, packets flow through the system map, and the forge sequence narrates the process. There is no motion for its own sake.
- **Precision:** a strict type scale, a 12-column grid, tabular numerals, and nothing decorative that doesn't carry information.

The central metaphor is **"Forged, not assembled."** It comes from HZORTECH's own copy ("infrastructure that was assembled, not engineered"): heat (assess) → shape (architect) → strike (build) → **quench (harden)** → temper (test) → the finished blade (hand over). *Hardening* is both a metallurgy and a security term.

### Tokens

| Token | Dark (canonical) | Light ("paper") |
|---|---|---|
| bg | `#0A0A0B` | `#F1EEE8` |
| surface | `#121214` | `#E8E4DC` |
| raised | `#1A1A1D` | `#FFFFFF` |
| line | `rgba(237,234,228,.12)` | `rgba(14,14,16,.14)` |
| text | `#EDEAE4` | `#0E0E10` |
| text-2 | `#B4AFA7` | `#45423D` |
| text-3 | `#8C877F` (≥4.6:1) | `#5E5A54` |
| hzor (brand fill) | `#BB1F25` | `#BB1F25` |
| hzor-text | `#F0444A` (5.3:1) | `#B01C22` (5.9:1) |
| signal/infra | `#7FA7C9` | `#2F5E86` |
| signal/automation | `#E0A34A` | `#8A5A12` |
| signal/platform | `#5FB39A` | `#1F6B55` |

Cinematic sections are always dark ("dark islands"), even in the light theme.

### Typography
- **Archivo** variable (wdth 62–125, wght 100–900), self-hosted. Display uses condensed extra-bold uppercase, echoing the brand posters. Kinetic type animates the `wdth` axis. UI and body use the normal width.
- **JetBrains Mono** variable for technical annotations only.
- **Source Serif 4** variable for Journal article bodies only.
- Fluid scale: 12 / 14 / 16 / 18 / 21 / 28 / 40 / 56 / 80 / 120 / 176 px, clamped between 360 and 1680 px viewports.

### Motion system
- **Lenis** smooth scroll (desktop pointer only; native on touch), driven by the GSAP ticker; `ScrollTrigger.update` runs on Lenis scroll.
- **GSAP** timelines and ScrollTrigger scrubs through `gsap.matchMedia()` with three contexts: `desktop`, `mobile`, and `reduce` (reduce means no scrubs, no pins, and final states rendered statically).
- **SplitText** for kinetic headings (line masks). Its accessibility mode keeps the text readable to screen readers.
- **Cross-document View Transitions** (`@view-transition { navigation: auto }`) for page transitions: a progressive enhancement with no JS router.
- A **performance governor** measures frame time for 2 s after any WebGL starts. If p75 exceeds 32 ms, it steps down (DPR → particle count → static poster). `saveData` and ≤ 4 GB device memory start in low mode.
- **Loading:** the LCP is always HTML text or a poster image. WebGL and image sequences load after `load` and idle time, and only near the viewport.

## 3. Information architecture

```
/                     Home — narrative (below)
/work/  → alias of /projects/ (301 to /projects/, keeping the existing URL canonical)
/projects/            Selected work index (8 case studies, filter by layer)
/projects/<slug>/     Case study: Context → Problem → System → Architecture → Implementation → Outcome
/services/            Capabilities: one system, 5 layers, 10 disciplines
/services/<slug>/     Discipline page with its own signature visualisation (10 variants)
/about/               The story: Hzor → the people → how we work → principles
/blog/                Journal index (featured, topics, list)
/blog/<slug>/         Article (Source Serif body, TOC, reading time, related)
/contact/             Project intake (4-step progressive form; single-page no-JS fallback)
/privacy/  /404
/newsletter/  /newsletter/confirm/<token>/
/api/v1/…             intake, subscribe, search-index, projects, posts, services, hooks/higgsfield
```

**Old anchors keep working.** `/services/#web-dev|crm|devops|api|security|migration` and `/projects/#proj-*` IDs are kept on the new pages. No existing URL is removed.

### Homepage narrative
1. **Opening:** the WebGL particle field condenses into the HT sword mark. H1: "We engineer the systems businesses run on." Primary CTA: "Start a project".
2. **Proposition:** a kinetic editorial statement: product + platform + automation + infrastructure, built as one system.
3. **System map (interactive):** a live architecture of a typical HZORTECH platform. Nodes are buttons. Traffic, deploy and incident scenarios show how the system behaves.
4. **Capabilities:** 5 layers × 10 disciplines, as an index with previews.
5. **Forged, not assembled:** a scroll-scrubbed Higgsfield film (image sequence) narrating the process in 5 beats.
6. **Selected work:** 4 featured case studies with real screenshots in a sticky stacked sequence.
7. **Your visit, measured:** a live engineering visualisation of this page's real Web Vitals, transfer size, request count and security headers, which is honest proof of craft.
8. **The people:** two founders and their paths.
9. **Standards:** what every engagement ships with (tests, IaC, runbooks, handover), the compliance frameworks worked within, and the toolchain.
10. **Journal:** the latest articles.
11. **Final CTA:** project-type chips that deep-link into the intake.

## 4. Higgsfield plan (small, purposeful)
| Asset | Model | Role |
|---|---|---|
| "Forge" film, 16:9, 1080p, about 10 s | Seedance 2.0 (text-to-video) | Home §5 scroll-scrubbed image sequence, and the About page backdrop |
| Up to 3 editorial stills for the case studies without public sites (HPC, SmartHome, Dr. Mary Lips) | Image model | Case-study covers where no real screenshot exists |

Everything else is real (client screenshots) or code-generated (diagrams, signatures, typographic Journal covers, OG images). Generation runs asynchronously (`manage.py higgsfield submit`, then `sync` by polling or webhook). Request IDs, prompts, arguments, status and result URLs are stored in the `GeneratedAsset` table and exported to `assets/higgsfield-ledger.json` for provenance.
