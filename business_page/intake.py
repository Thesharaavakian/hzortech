"""Domain logic shared by the HTML views and the JSON API, so both paths
behave identically (validation, spam checks, persistence, email)."""

import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import ContactSubmission, Subscriber

log = logging.getLogger(__name__)

RATE_LIMIT = 5          # submissions …
RATE_WINDOW = 60 * 10   # … per 10 minutes per IP


def client_ip(request):
    return (request.META.get('HTTP_CF_CONNECTING_IP')
            or request.META.get('HTTP_X_REAL_IP')
            or request.META.get('REMOTE_ADDR', ''))


def rate_limited(request, bucket):
    key = f'rl:{bucket}:{client_ip(request)}'
    count = cache.get(key, 0)
    if count >= RATE_LIMIT:
        return True
    cache.set(key, count + 1, RATE_WINDOW)
    return False


def verify_turnstile(token, ip):
    """Cloudflare Turnstile server-side check. Skipped when no secret is
    configured (local/dev); fails open if Cloudflare is unreachable so an
    outage on their side never loses a real enquiry (the honeypot and rate
    limit still apply)."""
    secret = settings.TURNSTILE_SECRET_KEY
    if not secret:
        return True
    try:
        resp = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={'secret': secret, 'response': token, 'remoteip': ip},
            timeout=5,
        )
        return bool(resp.json().get('success', False))
    except Exception:  # noqa: BLE001 — network/JSON errors: fail open, logged
        log.warning('Turnstile verification unreachable; failing open')
        return True


def save_intake(form, request):
    """Persist a validated ProjectIntakeForm and send notifications.
    Returns (submission, emailed: bool)."""
    d = form.cleaned_data
    sub = ContactSubmission.objects.create(
        name=d['name'], email=d['email'], company=d.get('company', ''),
        project_type=d.get('project_type', ''), budget=d.get('budget', ''),
        timeline=d.get('timeline', ''), is_urgent=d.get('is_urgent', False),
        message=d['message'], source=(request.POST.get('source') or request.path)[:200],
    )
    labels = dict(ContactSubmission.PROJECT_TYPES)
    lines = [
        f"From: {sub.name} <{sub.email}>" + (f" — {sub.company}" if sub.company else ''),
        f"Type: {labels.get(sub.project_type, 'Not specified')}",
        f"Budget: {dict(ContactSubmission.BUDGETS).get(sub.budget) or 'Not specified'}",
        f"Timeline: {dict(ContactSubmission.TIMELINES).get(sub.timeline) or 'Not specified'}",
        f"Urgent: {'YES' if sub.is_urgent else 'no'}",
        f"Started on: {sub.source}",
        '', sub.message, '',
        f"Admin: {settings.SITE_URL.rstrip('/')}{reverse('admin:business_page_contactsubmission_change', args=[sub.pk])}",
    ]
    prefix = '[HZORTECH][URGENT]' if sub.is_urgent else '[HZORTECH]'
    emailed = True
    try:
        send_mail(f'{prefix} {sub.summary_subject}', '\n'.join(lines),
                  settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_EMAIL], fail_silently=False)
    except Exception:  # noqa: BLE001 — the submission is saved; ops sees it in admin
        emailed = False
        log.exception('Intake notification email failed (submission %s saved)', sub.pk)
    reply = (
        f"Hello {sub.name},\n\n"
        "Thanks for telling us about your project — it has reached HZORTECH and will be read by one of "
        "our engineers, not a sales team.\n\n"
        + ("You marked this as urgent, so we will triage it today (Mon–Fri, 09:00–18:00 Yerevan time, GMT+4).\n\n"
           if sub.is_urgent else
           "We reply within 48 hours on working days, with questions or a direct assessment.\n\n")
        + "— The HZORTECH team\nhzortech.com"
    )
    try:
        send_mail('HZORTECH — we received your project brief', reply,
                  settings.DEFAULT_FROM_EMAIL, [sub.email], fail_silently=True)
    except Exception:  # noqa: BLE001
        pass
    return sub, emailed


def subscribe(email, request):
    """Double opt-in. Returns (subscriber, state) where state is one of
    'pending' (confirmation sent), 'already' (already active)."""
    email = email.strip().lower()
    sub, created = Subscriber.objects.get_or_create(email=email, defaults={'source': request.path[:200]})
    if sub.is_active:
        return sub, 'already'
    if sub.unsubscribed_at:
        sub.unsubscribed_at = None
        sub.confirmed_at = None
        sub.save(update_fields=['unsubscribed_at', 'confirmed_at'])
    confirm = f"{settings.SITE_URL.rstrip('/')}{reverse('newsletter_confirm', args=[sub.token])}"
    try:
        send_mail(
            'Confirm your HZORTECH Journal subscription',
            "Hello,\n\nPlease confirm you want to receive new HZORTECH Journal articles by email "
            f"(roughly monthly, nothing else):\n\n{confirm}\n\n"
            "If you didn't ask for this, ignore this email — you won't hear from us again.\n\n— HZORTECH",
            settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False,
        )
    except Exception:  # noqa: BLE001
        log.exception('Subscription confirmation email failed for subscriber %s', sub.pk)
    return sub, 'pending'


def confirm_subscription(token):
    sub = Subscriber.objects.filter(token=token).first()
    if sub and not sub.confirmed_at:
        sub.confirmed_at = timezone.now()
        sub.unsubscribed_at = None
        sub.save(update_fields=['confirmed_at', 'unsubscribed_at'])
    return sub


def unsubscribe(token):
    sub = Subscriber.objects.filter(token=token).first()
    if sub and not sub.unsubscribed_at:
        sub.unsubscribed_at = timezone.now()
        sub.save(update_fields=['unsubscribed_at'])
    return sub
