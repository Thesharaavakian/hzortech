"""Editorial content that isn't worth a database table: company story,
standards, engagement models, the system-map definition. Kept as plain data
so templates stay declarative and islands receive it via json_script."""

FOUNDERS = [
    {
        'key': 'shara', 'initials': 'SA', 'name': 'Shara Avakian', 'role': 'Principal Engineer & Founder',
        'summary': 'Cloud, security and banking-systems engineer. Builds the platforms and the infrastructure under them.',
        'path': [
            ('Golden SB-Tech', 'Technical support for live banking payment-workflow systems — production triage, incident escalation, process automation.'),
            ('Senex Security', 'Security and QA specialist — vulnerability management and endpoint-hardening programmes for Ford Saudi Arabia and Bank of Dubai.'),
            ('IIAP — National research institute', 'Junior cloud engineer — Python compute services, SaaS platform integration and HPC scheduling for quantum-simulation workloads.'),
        ],
        'education': 'Degree in Computer Science; completing a Master’s in Computer Systems.',
        'skills': ['Python', 'Django', 'DevOps', 'Kubernetes', 'Terraform', 'Wazuh', 'Blue team', 'CI/CD'],
    },
    {
        'key': 'marat', 'initials': 'MS', 'name': 'Marat Sargsyan', 'role': 'Engineering Partner',
        'summary': 'Systems and technical-operations engineer. Keeps what we ship running and supported.',
        'path': [
            ('IQS — Integrated Quantum Solutions, Yerevan', 'Systems and technical support.'),
            ('Gavar State University', 'Background in computer engineering.'),
        ],
        'education': '',
        'skills': ['Systems support', 'Technical operations'],
    },
]

PRINCIPLES = [
    ('Automation first', 'Every engagement is reviewed for manual work that can be eliminated. Efficient systems, not larger teams.'),
    ('Security by default', 'Access control, logging and hardening are built in from day one — not retrofitted before go-live.'),
    ('Direct communication', 'You talk to the engineers who build your system. No account managers, no filtered status reports.'),
    ('Full handover', 'Every engagement ships runbooks and knowledge transfer. Your team can run what we build.'),
]

STANDARDS = [
    ('A written spec before code', 'Scope, data model, acceptance criteria and what is out of scope — agreed before a line is written.'),
    ('Infrastructure as code', 'Environments defined in Terraform and version control. Nothing hand-configured that could be lost.'),
    ('Tests and CI from day one', 'Automated tests and a pipeline that runs them on every change, not a QA phase at the end.'),
    ('Security by default', 'Least-privilege access, hardened hosts, logging and monitoring designed in — not added before launch.'),
    ('Monitoring and runbooks', 'Alerts that fire before your customers notice, and written procedures for when they do.'),
    ('You own it', 'Source, infrastructure, credentials and documentation are yours. We hand over, and stay if you want us to.'),
]

FRAMEWORKS = ['ISO 27001', 'PCI DSS', 'GDPR', 'CBA regulations', 'CIS Benchmarks']

ENGAGEMENTS = [
    {
        'name': 'Project', 'label': 'Fixed scope',
        'desc': 'A defined deliverable, timeline and price — for a specific problem to solve.',
        'points': ['Written spec with acceptance criteria', 'Documentation + 30-day support', 'One-off price agreed upfront'],
    },
    {
        'name': 'Retainer', 'label': 'Monthly',
        'desc': 'Ongoing engineering capacity each month — for teams that need continuous improvement.',
        'points': ['Monthly review and recommendations', 'Defined response times', 'Scope adjustable each quarter'],
    },
    {
        'name': 'Dedicated', 'label': 'Enterprise',
        'desc': 'Dedicated engineering time with defined response for regulated or high-uptime environments.',
        'points': ['Priority access to the full team', 'Compliance documentation support', 'Quarterly roadmap planning'],
    },
]

PROCESS = [
    ('Assess', 'Heat', 'We start with the raw problem — what exists, what hurts, what it costs. Measured, not assumed.'),
    ('Architect', 'Shape', 'The system is designed before it is built: data, services, infrastructure and failure modes.'),
    ('Build', 'Strike', 'Working software in iterations, with CI from day one. You see progress, not just the end.'),
    ('Harden', 'Quench', 'Security, monitoring and recovery are set into the system — the way steel is hardened.'),
    ('Hand over', 'Temper', 'Documented, tested, running in production. Yours to operate — or ours to keep supporting.'),
]

GENERAL_FAQ = [
    ('Can you build our product and host it too?',
     'Yes — that is the point of working with one team across every layer. We design, build and deploy, configure the domain and TLS, and hand over a system that runs without you managing servers.'),
    ('Which cloud do you work with?',
     'AWS is our primary platform, mostly in EU regions. We also work with bare-metal and VPS Linux servers and hybrid setups where some workloads stay on-premise.'),
    ('Do you take over existing systems?',
     'Yes. We audit what exists, document it, and then modernise, extend or stabilise it in priority order — Django, Flask, Node.js and legacy PHP codebases included.'),
    ('How quickly do you reply?',
     'Within 48 hours on working days, with questions or a direct assessment. Production emergencies marked urgent are triaged the same business day.'),
    ('Which languages do you work in?',
     'English, Armenian and Russian. Technical documentation is delivered in English by default.'),
]

# ── The interactive system map on the homepage ────────────────────────────
# Coordinates are in a 1000×620 viewBox. `layer` keys match services_data.LAYERS.
SYSTEM_MAP = {
    'nodes': [
        {'id': 'users', 'label': 'Customers', 'kind': 'actor', 'layer': 'product', 'x': 70, 'y': 90,
         'detail': 'The people your platform exists for — on the web, on a phone, or at a device in their home.',
         'service': None},
        {'id': 'edge', 'label': 'Edge & WAF', 'kind': 'guard', 'layer': 'security', 'x': 250, 'y': 90,
         'detail': 'TLS, caching, rate limiting and a web application firewall in front of everything. Hostile traffic stops here.',
         'service': 'security'},
        {'id': 'web', 'label': 'Web app', 'kind': 'node', 'layer': 'product', 'x': 450, 'y': 90,
         'detail': 'The product your customers use — fast, accessible, built to a written spec rather than a template.',
         'service': 'software-development'},
        {'id': 'admin', 'label': 'Admin & dashboards', 'kind': 'node', 'layer': 'product', 'x': 690, 'y': 90,
         'detail': 'The tools your own team uses: back-office, reporting and operations dashboards.',
         'service': 'software-development'},
        {'id': 'api', 'label': 'API', 'kind': 'node', 'layer': 'platform', 'x': 450, 'y': 220,
         'detail': 'A documented REST API (OpenAPI) that every client and integration talks to — one contract, versioned.',
         'service': 'api-integration'},
        {'id': 'core', 'label': 'Services', 'kind': 'node', 'layer': 'platform', 'x': 690, 'y': 220,
         'detail': 'Business logic in Python and Django: typed, tested and structured so it can grow without rewrites.',
         'service': 'python'},
        {'id': 'data', 'label': 'PostgreSQL · Redis', 'kind': 'store', 'layer': 'platform', 'x': 900, 'y': 220,
         'detail': 'The system of record, with backups, point-in-time recovery and a cache in front of the hot paths.',
         'service': 'python'},
        {'id': 'devices', 'label': 'Devices', 'kind': 'node', 'layer': 'automation', 'x': 70, 'y': 350,
         'detail': 'Sensors, controllers and gateways reporting over MQTT or WebSockets — local-first, so automations keep working offline.',
         'service': 'smart-home-automation'},
        {'id': 'workers', 'label': 'Workers & queues', 'kind': 'node', 'layer': 'automation', 'x': 450, 'y': 350,
         'detail': 'Background jobs and scheduled tasks: follow-ups, reports, syncs. Retries with back-off; nothing silently lost.',
         'service': 'crm-automation'},
        {'id': 'crm', 'label': 'CRM & workflows', 'kind': 'node', 'layer': 'automation', 'x': 690, 'y': 350,
         'detail': 'Sales pipelines and business workflows that run on triggers, not on someone remembering.',
         'service': 'crm-automation'},
        {'id': 'third', 'label': 'Third-party APIs', 'kind': 'ext', 'layer': 'platform', 'x': 900, 'y': 350,
         'detail': 'Payments, email, messaging, calendars — integrated behind retries, dead-letter queues and alerts.',
         'service': 'api-integration'},
        {'id': 'ci', 'label': 'CI/CD', 'kind': 'node', 'layer': 'infrastructure', 'x': 250, 'y': 480,
         'detail': 'Every change is built, tested, scanned and deployed by a pipeline — with automatic rollback on failed health checks.',
         'service': 'devops'},
        {'id': 'cloud', 'label': 'Cloud (AWS)', 'kind': 'node', 'layer': 'infrastructure', 'x': 450, 'y': 480,
         'detail': 'Infrastructure defined in Terraform: networks, compute, databases and backups — reproducible and reviewed.',
         'service': 'cloud'},
        {'id': 'monitor', 'label': 'Monitoring', 'kind': 'node', 'layer': 'infrastructure', 'x': 690, 'y': 480,
         'detail': 'Metrics, logs and alerts that fire before customers notice, with runbooks for what to do next.',
         'service': 'devops'},
        {'id': 'siem', 'label': 'SIEM', 'kind': 'guard', 'layer': 'security', 'x': 900, 'y': 480,
         'detail': 'Wazuh or Elastic SIEM correlating events across every layer — detection, alerting and response.',
         'service': 'security'},
    ],
    'edges': [
        ['users', 'edge'], ['edge', 'web'], ['web', 'api'], ['admin', 'api'], ['api', 'core'], ['core', 'data'],
        ['core', 'workers'], ['workers', 'crm'], ['workers', 'third'], ['devices', 'api'],
        ['ci', 'cloud'], ['cloud', 'monitor'], ['monitor', 'siem'], ['cloud', 'api'], ['edge', 'siem'],
    ],
    'scenarios': {
        'traffic': {
            'label': 'Normal traffic',
            'summary': 'A customer request travels through the edge to the web app and API, reads and writes data, and queues follow-up work.',
            'paths': [['users', 'edge', 'web', 'api', 'core', 'data'], ['core', 'workers', 'crm'], ['workers', 'third'], ['devices', 'api', 'core']],
            'log': [
                'GET /account 200 · 38 ms',
                'POST /api/v1/bookings 201 · 64 ms',
                'job crm.follow_up queued → sent',
                'webhook payments.succeeded 200',
                'mqtt home/42/thermostat → rule matched',
            ],
        },
        'deploy': {
            'label': 'Deploy',
            'summary': 'A commit goes through CI, a new release rolls out to the cloud, health checks pass, and the previous version stays ready for rollback.',
            'paths': [['ci', 'cloud', 'api'], ['cloud', 'monitor']],
            'log': [
                'ci: build #412 — tests 318/318 passed',
                'ci: image scanned — 0 critical',
                'deploy: release 2.4.1 → 1 of 2 hosts',
                'health: /healthz 200 ×3 — promoting',
                'rollback: 2.4.0 kept warm for 24 h',
            ],
        },
        'incident': {
            'label': 'Incident',
            'summary': 'Hostile traffic hits the edge; the SIEM correlates repeated failures, raises an alert, and the source is blocked before it reaches the app.',
            'paths': [['users', 'edge'], ['edge', 'siem'], ['monitor', 'siem']],
            'hostile': ['users', 'edge'],
            'log': [
                'edge: 8 failed logins from 203.0.113.7 in 60 s',
                'siem: rule 100100 (brute force) fired · level 12',
                'alert → on-call engineer notified',
                'edge: 203.0.113.7 blocked — 0 requests reached the app',
                'incident report drafted for the post-mortem',
            ],
        },
    },
}
