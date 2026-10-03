"""/api/v1 — a small, explicit JSON boundary.

Read endpoints expose published content (services, case studies, posts, the
search index) for the frontend islands and any future headless client.
Write endpoints (intake, subscribe) are CSRF-protected, rate-limited and
share their domain logic with the HTML forms (business_page.intake). The
Higgsfield webhook is authenticated by a secret path token.
"""

import hmac
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import higgsfield
from .forms import ProjectIntakeForm, SubscribeForm
from .intake import client_ip, rate_limited, save_intake, subscribe, verify_turnstile
from .models import CaseStudy, GeneratedAsset, Post
from .services_data import LAYERS, SERVICE_ORDER, SERVICES

log = logging.getLogger(__name__)


def _body(request):
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body or b'{}')
        except ValueError:
            return None
        return data if isinstance(data, dict) else None
    return request.POST


def _errors(form):
    return {field: [str(e) for e in errs] for field, errs in form.errors.items()}


def _case_summary(c):
    return {
        'slug': c.slug, 'client': c.client, 'title': c.title, 'sector': c.sector,
        'summary': c.summary, 'status': c.status, 'status_label': c.get_status_display(),
        'layers': c.layers, 'services': c.services, 'public_url': c.public_url,
        'url': c.get_absolute_url(),
    }


@require_GET
@cache_page(60 * 5)
def services_index(request):
    return JsonResponse({'layers': [
        {**{k: v for k, v in layer.items() if k != 'legacy_anchor'},
         'services': [{'slug': s, 'name': SERVICES[s]['nav_label'], 'summary': SERVICES[s]['short'],
                       'url': f'/services/{s}/'} for s in layer['services']]}
        for layer in LAYERS
    ]})


@require_GET
def projects_index(request):
    return JsonResponse({'results': [_case_summary(c) for c in CaseStudy.objects.filter(is_published=True)]})


@require_GET
def project_detail(request, slug):
    c = CaseStudy.objects.filter(is_published=True, slug=slug).first()
    if not c:
        return JsonResponse({'error': 'not_found'}, status=404)
    return JsonResponse({
        **_case_summary(c), 'stack': c.stack, 'scope_note': c.scope_note,
        'context': c.context, 'problem': c.problem, 'system': c.system,
        'implementation': c.implementation, 'outcome': c.outcome,
        'architecture': c.architecture, 'outcomes': c.outcomes,
    })


@require_GET
def posts_index(request):
    return JsonResponse({'results': [
        {'slug': p.slug, 'title': p.title, 'dek': p.dek, 'topic': p.topic,
         'published_at': p.published_at.isoformat(), 'reading_minutes': p.reading_minutes,
         'url': p.get_absolute_url()}
        for p in Post.objects.filter(is_published=True)
    ]})


@require_GET
def search_index(request):
    """Everything the command menu can jump to."""
    items = [
        {'group': 'Pages', 'title': t, 'url': u, 'hint': h} for t, u, h in [
            ('Home', '/', ''), ('Work', '/projects/', 'Case studies'), ('Capabilities', '/services/', 'Five layers'),
            ('About', '/about/', 'The people'), ('Journal', '/blog/', 'Field notes'),
            ('Start a project', '/contact/', 'Reply within 48 h'), ('Privacy', '/privacy/', ''),
        ]
    ]
    items += [{'group': 'Capabilities', 'title': SERVICES[s]['nav_label'], 'url': f'/services/{s}/',
               'hint': SERVICES[s]['layer_name'], 'keywords': ' '.join(SERVICES[s]['stack'])} for s in SERVICE_ORDER]
    items += [{'group': 'Work', 'title': c.client, 'url': c.get_absolute_url(), 'hint': c.sector,
               'keywords': ' '.join(c.stack or [])} for c in CaseStudy.objects.filter(is_published=True)]
    items += [{'group': 'Journal', 'title': p.title, 'url': p.get_absolute_url(), 'hint': p.get_topic_display()}
              for p in Post.objects.filter(is_published=True)]
    items += [
        {'group': 'Contact', 'title': 'Email contact@hzortech.com', 'url': 'mailto:contact@hzortech.com', 'hint': ''},
        {'group': 'Contact', 'title': 'WhatsApp +374 77 075 919', 'url': 'https://wa.me/37477075919', 'hint': 'Opens WhatsApp'},
    ]
    resp = JsonResponse({'items': items})
    resp['Cache-Control'] = 'public, max-age=300'
    return resp


@require_POST
def intake(request):
    data = _body(request)
    if data is None:
        return JsonResponse({'ok': False, 'errors': {'__all__': ['Malformed request.']}}, status=400)
    form = ProjectIntakeForm(data)
    if form.is_spam:
        return JsonResponse({'ok': True, 'urgent': False}, status=201)
    if rate_limited(request, 'intake'):
        return JsonResponse({'ok': False, 'errors': {'__all__': [
            'Too many submissions from your connection. Please wait a few minutes, or email contact@hzortech.com.']}}, status=429)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': _errors(form)}, status=400)
    if not verify_turnstile(data.get('cf-turnstile-response', ''), client_ip(request)):
        return JsonResponse({'ok': False, 'errors': {'__all__': [
            'The spam check didn’t pass. Please try again, or email contact@hzortech.com.']}}, status=400)
    sub, emailed = save_intake(form, request)
    return JsonResponse({'ok': True, 'id': sub.pk, 'urgent': sub.is_urgent, 'emailed': emailed}, status=201)


@require_POST
def subscribe_api(request):
    data = _body(request)
    if data is None:
        return JsonResponse({'ok': False, 'errors': {'email': ['Malformed request.']}}, status=400)
    form = SubscribeForm(data)
    if data.get('website'):
        return JsonResponse({'ok': True, 'state': 'pending'})
    if rate_limited(request, 'subscribe'):
        return JsonResponse({'ok': False, 'errors': {'email': ['Too many attempts — try again shortly.']}}, status=429)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': _errors(form)}, status=400)
    _, state = subscribe(form.cleaned_data['email'], request)
    return JsonResponse({'ok': True, 'state': state})


@csrf_exempt
@require_POST
def higgsfield_webhook(request, token):
    expected = settings.HIGGSFIELD_WEBHOOK_TOKEN
    if not expected or not hmac.compare_digest(token, expected):
        return JsonResponse({'error': 'forbidden'}, status=403)
    try:
        payload = json.loads(request.body or b'{}')
    except ValueError:
        return JsonResponse({'error': 'bad_json'}, status=400)
    rid = payload.get('request_id')
    asset = GeneratedAsset.objects.filter(request_id=rid).first() if rid else None
    if not asset:
        return JsonResponse({'error': 'unknown_request'}, status=404)
    higgsfield.apply_status(asset, payload)
    log.info('Higgsfield webhook: %s → %s', rid, asset.status)
    return JsonResponse({'ok': True, 'status': asset.status})
