import math
import re
import secrets

from django.db import models
from django.urls import reverse
from django.utils import timezone


class ContactSubmission(models.Model):
    """A project-intake submission. Legacy rows (pre-v2) only have
    name/email/subject/message; every v2 field is optional at the DB level so
    those rows stay valid."""

    PROJECT_TYPES = [
        ('platform', 'A new platform or product'),
        ('automation', 'Automating a workflow'),
        ('infrastructure', 'Cloud, DevOps or infrastructure'),
        ('security', 'Security and hardening'),
        ('takeover', 'Taking over or fixing an existing system'),
        ('other', 'Something else'),
    ]
    BUDGETS = [
        ('', 'Not sure yet'),
        ('under-5k', 'Under $5k'),
        ('5k-15k', '$5k – $15k'),
        ('15k-50k', '$15k – $50k'),
        ('50k-plus', '$50k +'),
    ]
    TIMELINES = [
        ('', 'Flexible'),
        ('asap', 'As soon as possible'),
        ('1-3-months', 'Within 1–3 months'),
        ('3-months-plus', 'In 3+ months'),
    ]
    STATUSES = [('new', 'New'), ('replied', 'Replied'), ('closed', 'Closed')]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, blank=True)
    budget = models.CharField(max_length=20, choices=BUDGETS, blank=True)
    timeline = models.CharField(max_length=20, choices=TIMELINES, blank=True)
    is_urgent = models.BooleanField(default=False)
    subject = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    source = models.CharField(max_length=200, blank=True, help_text='Page the intake was started from.')
    status = models.CharField(max_length=10, choices=STATUSES, default='new')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.submitted_at:%Y-%m-%d %H:%M}"

    @property
    def summary_subject(self):
        if self.subject:
            return self.subject
        label = dict(self.PROJECT_TYPES).get(self.project_type)
        return f"{label} — {self.company or self.name}" if label else 'New project enquiry'


def _token():
    return secrets.token_urlsafe(24)


class Subscriber(models.Model):
    """Journal subscribers. Double opt-in: nobody is emailed until they
    confirm via the tokenised link."""

    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True, default=_token, editable=False)
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def is_active(self):
        return self.confirmed_at is not None and self.unsubscribed_at is None


class CaseStudy(models.Model):
    """Problem → system → architecture → implementation → outcome.

    `architecture` drives the interactive diagram: {"nodes": [{"id", "label",
    "layer", "detail"}], "edges": [["from", "to"], ...]}. `outcomes` is a
    list of {"value", "label"} — only facts that can be backed up."""

    STATUSES = [
        ('live', 'Live'),
        ('ongoing', 'Live · ongoing development'),
        ('in-development', 'In development'),
        ('completed', 'Completed'),
        ('support-ended', 'Support period ended'),
    ]

    slug = models.SlugField(unique=True)
    client = models.CharField(max_length=120)
    title = models.CharField(max_length=200, help_text='Headline, e.g. "Booking that runs itself".')
    sector = models.CharField(max_length=120)
    summary = models.TextField(help_text='One or two sentences for cards and meta description.')
    status = models.CharField(max_length=20, choices=STATUSES, default='completed')
    public_url = models.URLField(blank=True)
    layers = models.JSONField(default=list, blank=True)
    services = models.JSONField(default=list, blank=True, help_text='Service slugs from services_data.')
    stack = models.JSONField(default=list, blank=True)
    scope_note = models.CharField(max_length=300, blank=True,
                                  help_text='What HZORTECH did vs. what belongs to the client.')
    context = models.TextField(blank=True)
    problem = models.TextField(blank=True)
    system = models.TextField(blank=True)
    implementation = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    architecture = models.JSONField(default=dict, blank=True)
    outcomes = models.JSONField(default=list, blank=True)
    cover = models.CharField(max_length=200, blank=True, help_text='Static path of the cover image.')
    cover_alt = models.CharField(max_length=200, blank=True)
    cover_is_illustration = models.BooleanField(
        default=False, help_text='Tick when the cover is illustrative rather than the real product.')
    gallery = models.JSONField(default=list, blank=True,
                               help_text='[{"src", "alt", "caption", "device": "desktop|mobile"}]')
    legacy_anchor = models.CharField(max_length=40, blank=True,
                                     help_text='Old /projects/#anchor id kept working.')
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=100)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'client']
        verbose_name_plural = 'case studies'

    def __str__(self):
        return self.client

    def get_absolute_url(self):
        return reverse('case_study', kwargs={'slug': self.slug})

    @property
    def domain(self):
        return re.sub(r'^https?://(www\.)?', '', self.public_url).rstrip('/')


class Post(models.Model):
    TOPICS = [
        ('security', 'Security'),
        ('devops', 'DevOps'),
        ('cloud', 'Cloud'),
        ('automation', 'Automation'),
        ('engineering', 'Engineering'),
    ]

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    dek = models.CharField(max_length=300, help_text='Standfirst shown under the headline.')
    topic = models.CharField(max_length=20, choices=TOPICS)
    body = models.TextField(help_text='Markdown. Fenced code blocks are syntax-highlighted.')
    body_html = models.TextField(blank=True, editable=False)
    toc = models.JSONField(default=list, blank=True, editable=False)
    author_name = models.CharField(max_length=120, default='HZORTECH Engineering')
    reading_minutes = models.PositiveSmallIntegerField(default=1, editable=False)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        from .markdown_render import render_markdown
        self.body_html, self.toc = render_markdown(self.body)
        words = len(re.findall(r'\w+', self.body))
        self.reading_minutes = max(1, math.ceil(words / 230))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})


class GeneratedAsset(models.Model):
    """Ledger of Higgsfield generation requests. Generation is asynchronous:
    `manage.py higgsfield submit` stores the request id, and `sync` (polling)
    or the webhook updates status and downloads the result."""

    STATUSES = [
        ('queued', 'Queued'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('nsfw', 'Blocked by moderation'),
        ('canceled', 'Canceled'),
    ]

    slot = models.CharField(max_length=80, help_text='Where the asset is used, e.g. "home.forge".')
    model_slug = models.CharField(max_length=120)
    prompt = models.TextField()
    arguments = models.JSONField(default=dict)
    request_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='queued')
    result = models.JSONField(default=dict, blank=True)
    result_url = models.URLField(max_length=1000, blank=True)
    local_path = models.CharField(max_length=300, blank=True)
    error = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.slot} · {self.model_slug} · {self.status}'

    @property
    def is_done(self):
        return self.status in {'completed', 'failed', 'nsfw', 'canceled'}
