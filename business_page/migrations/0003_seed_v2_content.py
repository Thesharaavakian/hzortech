from django.db import migrations

CASES = [
    dict(
        slug='labittech', client='LabITTech', title='From spreadsheets to a real enrolment platform',
        sector='Education / IT training', status='live', public_url='https://www.techlabit.com/',
        layers=['product', 'platform', 'infrastructure'], services=['software-development', 'devops'],
        stack=['Python', 'Django', 'PostgreSQL', 'Docker', 'nginx', 'GitHub Actions'],
        scope_note='Full-stack build, cloud deployment and the CI/CD pipeline — not a template or a theme.',
        context='LabITTech runs IT training courses and lab services and needed a public platform students and staff could both rely on — course listings, enrolment, student tracking and lab-environment provisioning in one system.',
        problem='The course catalogue, enrolments and lab bookings lived in spreadsheets and email threads. Nothing was connected: a change to a course schedule had to be copied by hand into three places, and there was no record of who was actually enrolled in what.',
        system='A Django application with a single source of truth for courses, cohorts and enrolments. Staff manage the catalogue and track students from one admin surface; the public site reads from the same data, so there is never a second copy to keep in sync.',
        implementation='Built the data model around courses → cohorts → enrolments, with Django admin as the staff interface (no separate back-office to build and maintain). Deployed behind nginx with Gunicorn, containerised with Docker, and shipped a GitHub Actions pipeline that builds, tests and deploys on every push to the main branch.',
        outcome='LabITTech runs its course catalogue and enrolment process on the platform today, deploying changes through the pipeline rather than by hand.',
        outcomes=[{'value': 'Live', 'label': 'Public platform, in production'}, {'value': 'CI/CD', 'label': 'Every deploy goes through the pipeline, not manual steps'}],
        cover='business_page/img/cases/labittech-cover.jpg', cover_alt='TechLabIT homepage, “The new standard for your IT needs”',
        gallery=[{'src': 'business_page/img/cases/labittech-browser.jpg', 'alt': 'TechLabIT homepage in a browser frame', 'device': 'desktop', 'caption': 'Homepage'},
                 {'src': 'business_page/img/cases/labittech-mobile.jpg', 'alt': 'TechLabIT homepage on a phone', 'device': 'mobile', 'caption': 'Mobile'}],
        legacy_anchor='proj-labittech', featured=True, order=10,
        architecture={'nodes': [
            {'id': 'web', 'label': 'Public site', 'layer': 'product', 'x': 150, 'y': 100, 'detail': 'Course catalogue and enrolment, Django templates.'},
            {'id': 'admin', 'label': 'Staff admin', 'layer': 'product', 'x': 850, 'y': 100, 'detail': 'Django admin — course, cohort and enrolment management.'},
            {'id': 'app', 'label': 'Django app', 'layer': 'platform', 'x': 500, 'y': 250, 'detail': 'One codebase, one data model, Gunicorn workers.'},
            {'id': 'db', 'label': 'PostgreSQL', 'layer': 'platform', 'x': 500, 'y': 400, 'detail': 'System of record for courses, cohorts and enrolments.'},
            {'id': 'nginx', 'label': 'nginx', 'layer': 'infrastructure', 'x': 500, 'y': 480, 'detail': 'Reverse proxy and static files.'},
            {'id': 'ci', 'label': 'GitHub Actions', 'layer': 'infrastructure', 'x': 150, 'y': 480, 'detail': 'Build, test, deploy on every push.'},
        ], 'edges': [['web', 'app'], ['admin', 'app'], ['app', 'db'], ['nginx', 'app'], ['ci', 'nginx']]},
    ),
    dict(
        slug='darksight', client='DarkSight', title='Hosting and shipping a security product, securely',
        sector='Cybersecurity', status='completed', public_url='https://darksight.com/',
        layers=['product', 'infrastructure'], services=['software-development', 'devops'],
        stack=['Docker', 'nginx', 'AWS', 'GitHub Actions'],
        scope_note='Corporate site and infrastructure for a third-party certified security provider — the security product itself is DarkSight’s own.',
        context='DarkSight is an independent, certified security and solutions provider. Their public site had to be fast, credible to a security-literate audience, and deployed through the same disciplined pipeline they’d expect of a client.',
        problem='A security vendor’s own web presence is held to a higher bar — any sloppiness in headers, hosting or deployment practice undercuts the product being sold.',
        system='A containerised site behind nginx on AWS, deployed through GitHub Actions with no manual steps on the server — the same deployment discipline we hold our own site to.',
        implementation='Dockerised the application, configured nginx for TLS and security headers, and built a CI/CD pipeline that builds and ships on every merge. Infrastructure is documented, not assembled by hand.',
        outcome='DarkSight runs on a production-ready, fully hosted platform with a repeatable deployment process.',
        outcomes=[{'value': 'Live', 'label': 'Production site and infrastructure'}, {'value': 'CI/CD', 'label': 'No manual deploy steps'}],
        cover='business_page/img/cases/darksight-cover.jpg', cover_alt='DarkSight homepage, vulnerability management dashboard',
        gallery=[{'src': 'business_page/img/cases/darksight-browser.jpg', 'alt': 'DarkSight homepage in a browser frame', 'device': 'desktop', 'caption': 'Homepage'},
                 {'src': 'business_page/img/cases/darksight-mobile.jpg', 'alt': 'DarkSight homepage on a phone', 'device': 'mobile', 'caption': 'Mobile'}],
        legacy_anchor='proj-darksight', featured=True, order=20,
        architecture={'nodes': [
            {'id': 'cdn', 'label': 'TLS / edge', 'layer': 'security', 'x': 500, 'y': 90, 'detail': 'TLS termination and edge protection.'},
            {'id': 'nginx', 'label': 'nginx', 'layer': 'infrastructure', 'x': 500, 'y': 230, 'detail': 'Reverse proxy, security headers.'},
            {'id': 'app', 'label': 'Containerised app', 'layer': 'product', 'x': 500, 'y': 370, 'detail': 'Docker container, built from source.'},
            {'id': 'ci', 'label': 'GitHub Actions', 'layer': 'infrastructure', 'x': 850, 'y': 230, 'detail': 'Build and deploy on every merge.'},
            {'id': 'aws', 'label': 'AWS', 'layer': 'infrastructure', 'x': 150, 'y': 370, 'detail': 'Hosting and compute.'},
        ], 'edges': [['cdn', 'nginx'], ['nginx', 'app'], ['ci', 'nginx'], ['app', 'aws']]},
    ),
    dict(
        slug='rbtex', client='RBTEX', title='Zero unplanned downtime on a live crypto exchange',
        sector='FinTech / Blockchain', status='support-ended', public_url='https://rbtex.com/',
        layers=['infrastructure'], services=['devops', 'cloud'],
        stack=['Docker', 'Kubernetes', 'Terraform', 'GitHub Actions'],
        scope_note='DevOps, CI/CD and infrastructure engineering — the trading platform itself is RBTEX’s own.',
        context='RBTEX runs a live cryptocurrency trading and payment-gateway platform, where downtime and bad deploys have an immediate financial cost.',
        problem='A trading platform cannot absorb unplanned downtime, and deploys that go wrong need to be caught and reversed before customers notice.',
        system='Container orchestration on Kubernetes with infrastructure defined in Terraform, and a CI/CD pipeline covering build, test and controlled rollout.',
        implementation='Provisioned and managed the Kubernetes infrastructure as code, built the GitHub Actions pipeline for build/test/deploy, and provided ongoing technical support for the live platform through the engagement.',
        outcome='Zero unplanned downtime over the support period, with infrastructure fully defined in code. The engagement’s support period has since concluded.',
        outcomes=[{'value': '0', 'label': 'Unplanned outages during the support period'}, {'value': '100% IaC', 'label': 'Infrastructure defined in Terraform'}],
        cover='business_page/img/cases/rbtex-cover.jpg', cover_alt='RBTex homepage, “Crypto Trading Made Easy”',
        gallery=[{'src': 'business_page/img/cases/rbtex-browser.jpg', 'alt': 'RBTex homepage in a browser frame', 'device': 'desktop', 'caption': 'Homepage'},
                 {'src': 'business_page/img/cases/rbtex-mobile.jpg', 'alt': 'RBTex homepage on a phone', 'device': 'mobile', 'caption': 'Mobile'}],
        legacy_anchor='proj-rbtex', featured=False, order=60,
        architecture={'nodes': [
            {'id': 'ci', 'label': 'GitHub Actions', 'layer': 'infrastructure', 'x': 150, 'y': 120, 'detail': 'Build, test, controlled rollout.'},
            {'id': 'k8s', 'label': 'Kubernetes', 'layer': 'infrastructure', 'x': 500, 'y': 250, 'detail': 'Container orchestration for the trading platform.'},
            {'id': 'tf', 'label': 'Terraform', 'layer': 'infrastructure', 'x': 850, 'y': 120, 'detail': 'Infrastructure as code — networks, nodes, access.'},
            {'id': 'app', 'label': 'Trading platform', 'layer': 'product', 'x': 500, 'y': 420, 'detail': 'RBTEX’s own application, containerised and orchestrated.'},
        ], 'edges': [['ci', 'k8s'], ['tf', 'k8s'], ['k8s', 'app']]},
    ),
    dict(
        slug='arev-motors', client='Arev Motors', title='A dealership platform for imported EVs',
        sector='Automotive / EV retail', status='ongoing', public_url='https://arevmotors.am/',
        layers=['product', 'platform'], services=['software-development'],
        stack=['HTML', 'CSS', 'JavaScript'],
        scope_note='Marketing site and vehicle inventory for an EV importer and dealership.',
        context='Arev Motors imports electric vehicles manufactured in China and needed a dealership site built around inventory, parts and service — not a generic brochure template.',
        problem='EV buyers need to browse real, current inventory, compare specs, and reach the dealership directly — a static brochure site couldn’t carry that.',
        system='A deliberately dependency-free front end — plain HTML, CSS and JavaScript, no framework or build step — covering inventory, parts, tuning, services and a contact flow.',
        implementation='Built eight pages (home, inventory, parts, tuning, services, about, contact, 404) sharing one stylesheet and one script, with a filterable, searchable parts catalogue and a vehicle comparison view. No framework was introduced because none of the page’s interactivity needed one — a deliberate choice, revisited only if the platform grows a real need for state management.',
        outcome='Arev Motors runs its public inventory and dealership site on the platform today, with ongoing development as the vehicle range grows.',
        outcomes=[{'value': 'Live', 'label': 'Public dealership site, in production'}, {'value': 'Zero deps', 'label': 'No framework, no build step — by design'}],
        cover='business_page/img/cases/arevmotors-cover.jpg', cover_alt='Arev Motors homepage, “Electric vehicles, imported properly”',
        gallery=[{'src': 'business_page/img/cases/arevmotors-browser.jpg', 'alt': 'Arev Motors homepage in a browser frame', 'device': 'desktop', 'caption': 'Homepage'},
                 {'src': 'business_page/img/cases/arevmotors-mobile.jpg', 'alt': 'Arev Motors homepage on a phone', 'device': 'mobile', 'caption': 'Mobile'}],
        legacy_anchor='proj-arevmotors', featured=True, order=30,
        architecture={'nodes': [
            {'id': 'web', 'label': 'Dealership site', 'layer': 'product', 'x': 300, 'y': 150, 'detail': 'Home, inventory, parts, tuning, services, contact.'},
            {'id': 'js', 'label': 'Vanilla JS', 'layer': 'platform', 'x': 700, 'y': 150, 'detail': 'Filtering, search, comparison — no framework.'},
            {'id': 'form', 'label': 'Contact flow', 'layer': 'platform', 'x': 500, 'y': 350, 'detail': 'Inquiry form wired to the dealership’s inbox.'},
        ], 'edges': [['web', 'js'], ['web', 'form']]},
    ),
    dict(
        slug='gsg-computers', client='GSG Computers', title='An electronics retailer’s storefront, from scratch',
        sector='Retail / Electronics', status='ongoing', public_url='https://gsgcomp.am/',
        layers=['product'], services=['software-development'],
        stack=['E-commerce platform', 'Armenian localisation'],
        scope_note='Storefront build and product catalogue for a computer and electronics retailer in Gavar, Armenia.',
        context='GSG Computers sells computers, laptops, surveillance equipment and repairs in Gavar, Armenia, and needed an online storefront in Armenian to match the physical shop.',
        problem='The business had no online presence — customers could only browse and buy in person, with no way to check stock or prices remotely.',
        system='A localised product catalogue and storefront covering categories from laptops to surveillance equipment, in Armenian.',
        implementation='Built the storefront, category structure and product listings, matching the shop’s real inventory and pricing in Armenian Dram.',
        outcome='GSG Computers runs its online storefront alongside the physical shop, with the catalogue actively maintained.',
        outcomes=[{'value': 'Live', 'label': 'Public storefront, in production'}],
        cover='business_page/img/cases/gsg-cover.jpg', cover_alt='GSG Computers homepage, Armenian electronics storefront',
        gallery=[{'src': 'business_page/img/cases/gsg-mobile.jpg', 'alt': 'GSG Computers homepage on a phone', 'device': 'mobile', 'caption': 'Mobile'}],
        legacy_anchor='proj-gsg', featured=False, order=40,
        architecture={},
    ),
    dict(
        slug='dr-mary-lips', client='Dr. Mary Lips', title='Taking booking off the phone entirely',
        sector='Healthcare / Aesthetics', status='ongoing', public_url='',
        layers=['product', 'automation'], services=['software-development', 'crm-automation'],
        stack=['Django', 'PostgreSQL', 'Calendar API', 'SMTP'],
        scope_note='Website, booking automation and client-journey workflows for an aesthetic-medicine practice.',
        context='Dr. Mary Lips runs an aesthetic medicine practice where every appointment used to be booked by phone, by hand, during clinic hours.',
        problem='Phone-only booking meant missed calls became missed appointments, staff time went to scheduling instead of patients, and there was no automated follow-up after a visit.',
        system='A Django website with an integrated booking engine: patients self-book against real availability, staff get automatic notifications, and follow-ups go out without anyone remembering to send them.',
        implementation='Built the booking data model around practitioners, services and availability, integrated a calendar API for scheduling, and wired SMTP notifications for both staff (new booking) and patients (confirmation, reminder, follow-up).',
        outcome='Manual booking overhead is at zero — every appointment is self-served online, with automated staff notifications and patient follow-ups.',
        outcomes=[{'value': '100%', 'label': 'Bookings self-served online, zero manual scheduling'}],
        cover='business_page/img/proj-drmarylips.jpg', cover_alt='Abstract illustration representing healthcare automation', cover_is_illustration=True,
        legacy_anchor='proj-drmarylips', featured=False, order=50,
        architecture={},
    ),
    dict(
        slug='smarthome-armenia', client='SmartHome Armenia', title='One platform for every connected home',
        sector='IoT / Smart home', status='ongoing', public_url='',
        layers=['automation', 'infrastructure'], services=['smart-home-automation', 'devops'],
        stack=['Python', 'Django', 'WebSockets', 'Docker'],
        scope_note='Platform development, IoT integration and DevOps for a smart-home automation company.',
        context='SmartHome Armenia installs and manages connected-home systems for customers across the Armenian market and needed one platform to run the whole business on — not a device app per installer.',
        problem='Smart-home installers typically end up juggling each manufacturer’s own app. Customers want one dashboard; the business wanted one system to manage installs, customers and devices.',
        system='A device-integration layer feeding a real-time control dashboard, with a customer portal and installer management on the same platform.',
        implementation='Built the device integration layer, a WebSocket-driven real-time dashboard for live telemetry, and the customer and installer management tooling, containerised for deployment.',
        outcome='SmartHome Armenia runs its live platform with an active customer base, with ongoing development as the device catalogue grows.',
        outcomes=[{'value': 'Live', 'label': 'Platform in production, active customer base'}],
        cover='business_page/img/proj-smarthome.jpg', cover_alt='Abstract illustration representing a connected smart home', cover_is_illustration=True,
        legacy_anchor='proj-smarthome', featured=False, order=70,
        architecture={},
    ),
    dict(
        slug='ra-scientific-hpc', client='RA Scientific Research HPC', title='Scheduling 1,000+ simulations a month',
        sector='Government / Scientific research', status='ongoing', public_url='',
        layers=['infrastructure'], services=['hpc-linux', 'python'],
        stack=['Python', 'AWS Batch', 'Slurm', 'Terraform', 'PostgreSQL'],
        scope_note='HPC workflow and scheduling system for a national research computing engagement.',
        context='A Republic of Armenia research engagement needed computational orchestration for quantum-simulation and other compute-heavy scientific workloads, spanning on-premise clusters and cloud burst capacity.',
        problem='Researchers were spending time on job scheduling and infrastructure instead of running experiments, with no automated path from on-premise compute to cloud burst when local capacity ran out.',
        system='A Python-based workflow manager that dispatches jobs to on-premise clusters or AWS Batch depending on load, with infrastructure defined in Terraform.',
        implementation='Built the job dispatch and scheduling framework in Python, integrated AWS Batch for cloud burst capacity, and defined the supporting infrastructure as Terraform code.',
        outcome='The system automates over 1,000 simulation jobs a month, with researchers submitting work instead of managing where it runs.',
        outcomes=[{'value': '1,000+', 'label': 'Simulation jobs automated per month'}],
        cover='business_page/img/proj-hpc.jpg', cover_alt='Abstract illustration representing high-performance computing', cover_is_illustration=True,
        legacy_anchor='proj-hpc', featured=False, order=80,
        architecture={},
    ),
]

POSTS = [
    dict(
        slug='wazuh-tuning-rules-that-cut-alert-noise', title='Wazuh in production: the tuning rules that cut alert noise',
        dek='Out of the box, Wazuh generates thousands of alerts a day and most of them are noise. These are the rule overrides we apply on every deployment.',
        topic='security', featured=True, published_at='2026-05-11 09:00:00+04:00',
        body='''A default Wazuh install is honest about everything it sees, which is the problem. A single
quiet Linux box can generate thousands of low-value alerts a day — cron jobs authenticating
through PAM, routine package updates, log rotation — and if your team's first instinct is to
mute the whole category, you lose the signal along with the noise.

The fix isn't "alert on less." It's "alert on the right things, at the right level," which
means writing local rule overrides instead of touching the shipped ruleset.

## Start from `local_rules.xml`, never the defaults

Every override lives in `/var/ossec/etc/rules/local_rules.xml`, never in the vendor rule files.
Vendor updates will silently overwrite anything you change there, and you'll relearn this lesson
at the worst possible time.

```xml
<!-- Silence cron's routine PAM session open/close — level 0 means
     "log it, don't alert on it." We still want it in the index for
     forensics, just not in anyone's inbox. -->
<rule id="100001" level="0">
  <if_sid>5501</if_sid>
  <match>CRON</match>
  <description>Ignore routine cron PAM session events</description>
</rule>
```

## Rule one: silence routine service accounts, not whole rule groups

It's tempting to disable an entire `if_sid` group once you've seen enough false positives from
it. Don't — that group might be the one thing standing between you and a real credential-stuffing
attempt next month. Scope the override to the specific noisy actor (`CRON`, your backup agent, your
monitoring user) and leave the group's real alerting intact for everyone else.

## Rule two: raise brute-force thresholds to match your actual traffic

The default SSH brute-force rule fires after a handful of failures in a short window, which is
sized for a quiet box, not a bastion host that legitimately eats failed logins from misconfigured
CI runners. Tune the `frequency` and `timeframe` to what *your* environment considers abnormal:

```xml
<rule id="100100" level="12" frequency="8" timeframe="60">
  <if_matched_sid>5710</if_matched_sid>
  <description>SSH brute force — 8 failed attempts in 60s</description>
  <group>authentication_failures,pci_dss_10.2.4</group>
</rule>
```

## Rule three: separate "interesting" from "actionable"

Not every alert needs a human. We route `level >= 10` to PagerDuty, `level 7-9` to a Slack
channel someone actually reads, and `level < 7` to the index only. This single change — not a
new tool, not more agents — is what turned a channel nobody opened into one the on-call engineer
actually trusts.

## Rule four: integrate active response, but scope it tightly

Auto-blocking an IP after a correlated brute-force rule is powerful and also a great way to lock
out your own office if the thresholds are wrong. Test active response rules against a *staging*
rule set with a short block duration before trusting them in production with a long one.

## Rule five: review the top-20 noisiest rule IDs monthly

`ossec-logtest` and a simple count over the alerts index tell you exactly which rule IDs are
dominating your volume. Fifteen minutes a month spent tuning the top offenders does more for
signal quality than any dashboard redesign.

None of this is exotic. It's the unglamorous, repeatable process that turns a SIEM from a
compliance checkbox into something your team actually watches.
''',
    ),
    dict(
        slug='zero-downtime-aws-migration-checklist', title='The pre-cutover checklist we run on every AWS migration',
        dek='Fourteen checks covering DNS TTLs, health validation, rollback triggers and the thirty days after cutover — the difference between a migration and an incident.',
        topic='cloud', featured=False, published_at='2026-05-04 09:00:00+04:00',
        body='''Most migration failures aren't caused by the migration itself — they're caused by skipping a
step that felt optional under time pressure. This is the checklist we run before every cutover,
written down specifically so nothing gets skipped under pressure.

## Phase 1 — a day before cutover

1. **Lower DNS TTL to 60 seconds**, at least 24 hours ahead of the cutover window, so the eventual
   switch propagates in under a minute instead of whatever the previous TTL happened to be.
2. **Confirm the shadow environment is receiving a live data copy** — not a snapshot taken days ago.
3. **Run the full application test suite against the shadow environment**, not just a smoke test.
4. **Verify every environment variable and secret exists in the new environment** — a missing
   `EMAIL_HOST_PASSWORD` is a silent failure, not a loud one.
5. **Confirm monitoring and alerting are live on the new environment** before you need them.

## Phase 2 — cutover

6. **Freeze writes to the old database**, or set up logical replication so nothing written during
   the cutover window is lost.
7. **Run the final data sync and verify row counts and checksums** against the source — not just
   "the migration script exited 0."

```bash
# Row counts should match exactly; checksums catch silent truncation
# or encoding issues that row counts alone would miss.
psql -h old-db -c "SELECT count(*), md5(array_agg(id)::text) FROM orders;"
psql -h new-db -c "SELECT count(*), md5(array_agg(id)::text) FROM orders;"
```

8. **Switch DNS**, and watch propagation actively rather than assuming the low TTL did its job.
9. **Health-check the new environment under real traffic**, not just synthetic requests.

```bash
for i in $(seq 1 12); do
  curl -sf -o /dev/null -w "%{http_code} %{time_total}s\n" https://app.example.com/healthz
  sleep 5
done
```

10. **Confirm the rollback path still works** — DNS back to the old TTL, old environment still
    warm and able to accept traffic — *before* you need it, not after.

## Phase 3 — the thirty days after

11. **Keep the old environment running and in sync for at least seven days**, longer for anything
    regulated. The urge to tear it down immediately after a clean cutover is exactly the moment
    you shouldn't.
12. **Monitor error rates and latency against the pre-migration baseline**, not just "no errors."
    A system that's technically up but 3x slower is still an incident.
13. **Re-run the data integrity check a week later** against both environments if they're still
    in sync, to catch any drift the initial check missed.
14. **Write the post-migration report while it's fresh** — what worked, what nearly didn't, what
    the next migration should do differently.

The checklist isn't exciting. That's the point — a migration that follows a boring, written
process is one where nothing is riding on anyone's memory at 2am.
''',
    ),
    dict(
        slug='github-actions-hardening-checklist', title='GitHub Actions hardening: four controls most teams skip',
        dek='Secret scanning, OIDC instead of long-lived keys, pinned action versions and scoped permissions — the controls that actually prevent a supply-chain compromise.',
        topic='devops', featured=False, published_at='2026-04-28 09:00:00+04:00',
        body='''A CI/CD pipeline has write access to your production environment, which makes it one of the
highest-value targets in your entire stack — and also one of the most commonly under-secured,
because "it's just the deploy script" feels lower-stakes than it is.

## Control one: scope workflow permissions explicitly

The default `GITHUB_TOKEN` permission model is broader than almost any workflow needs. State
exactly what each job requires, and nothing else:

```yaml
permissions:
  contents: read
  packages: write
  id-token: write   # only if you're using OIDC — see below
```

A workflow that only builds and pushes an image has no business holding `issues: write` or
`pull-requests: write`, even if that's the default.

## Control two: OIDC instead of long-lived cloud keys

Long-lived AWS or GCP keys stored as repository secrets are a standing liability — they don't
expire, they're reused across every run, and a leaked key is a leaked key until someone notices
and rotates it. OpenID Connect federation issues a short-lived token per workflow run instead:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
    aws-region: eu-north-1
    # no access-key-id, no secret-access-key — nothing to leak
```

If your pipeline still has an `AWS_SECRET_ACCESS_KEY` in repository secrets, that's the single
highest-leverage fix available before anything else on this list.

## Control three: pin third-party actions to a commit SHA

`uses: actions/checkout@v4` resolves to whatever `v4` points to *today* — a compromised or
force-pushed tag changes what your pipeline runs without your workflow file changing at all.
Pin to the commit SHA, with the version as a comment for readability:

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.1
```

This matters more for third-party actions than for GitHub's own, and most for any action with
write access to secrets or the ability to run arbitrary code.

## Control four: enable secret scanning and dependency review, and act on both

GitHub's own secret scanning and push protection catch committed credentials before they merge;
Dependabot and dependency review catch known-vulnerable packages before they ship. Both are free
on public repositories and cheap on private ones. The control only works if someone is assigned
to triage what it flags — scanning that nobody reads is theatre, not security.

None of these four controls require buying a new tool. They require treating the pipeline with
the same scrutiny as the production system it deploys to — because that's what it is.
''',
    ),
]


def seed(apps, schema_editor):
    # Historical models from apps.get_model() are frozen to their fields —
    # they do NOT carry Post.save()'s markdown-rendering override, so this
    # migration computes body_html/toc/reading_minutes itself rather than
    # relying on a save() that migrations never actually call.
    import math
    import re

    from business_page.markdown_render import render_markdown

    CaseStudy = apps.get_model('business_page', 'CaseStudy')
    Post = apps.get_model('business_page', 'Post')
    for data in CASES:
        CaseStudy.objects.update_or_create(slug=data['slug'], defaults=data)
    for data in POSTS:
        body = data.pop('body')
        body_html, toc = render_markdown(body)
        reading_minutes = max(1, math.ceil(len(re.findall(r'\w+', body)) / 230))
        Post.objects.update_or_create(slug=data['slug'], defaults={
            **data, 'body': body, 'body_html': body_html, 'toc': toc, 'reading_minutes': reading_minutes,
        })


def unseed(apps, schema_editor):
    CaseStudy = apps.get_model('business_page', 'CaseStudy')
    Post = apps.get_model('business_page', 'Post')
    CaseStudy.objects.filter(slug__in=[c['slug'] for c in CASES]).delete()
    Post.objects.filter(slug__in=[p['slug'] for p in POSTS]).delete()


class Migration(migrations.Migration):

    dependencies = [('business_page', '0002_v2_content_models')]

    operations = [migrations.RunPython(seed, unseed)]
