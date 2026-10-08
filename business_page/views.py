import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import content
from .forms import ProjectIntakeForm, SubscribeForm
from .intake import (
    client_ip,
    confirm_subscription,
    rate_limited,
    save_intake,
    subscribe,
    unsubscribe,
    verify_turnstile,
)
from .models import CaseStudy, ContactSubmission, Post
from .services_data import LAYER_BY_KEY, LAYERS, SERVICE_ORDER, SERVICES

FORGE_SEQ = 'business_page/seq/forge-d90931a5'


def _layers_with_services():
    return [{**layer, 'items': [SERVICES[s] for s in layer['services']]} for layer in LAYERS]


def _published_cases():
    return CaseStudy.objects.filter(is_published=True)


def _published_posts():
    return Post.objects.filter(is_published=True)


@lru_cache(maxsize=1)
def _forge_manifest():
    path = Path(__file__).resolve().parent / 'static' / FORGE_SEQ / 'manifest.json'
    return json.loads(path.read_text())


def _forge_props():
    m = _forge_manifest()
    # Frame files are addressed by index from JS, so the base must be the
    # un-hashed directory (the directory name itself is the version).
    return {
        'base': f"/{settings.STATIC_URL.strip('/')}/{FORGE_SEQ}/",
        'desktop': m['desktop'],
        'mobile': m['mobile'],
        'chapters': len(content.PROCESS),
    }


def home(request):
    cases = list(_published_cases())
    featured = [c for c in cases if c.featured][:4]
    return render(request, 'business_page/home.html', {
        'layers': _layers_with_services(),
        'featured_cases': featured,
        'case_count': len(cases),
        'latest_posts': _published_posts()[:3],
        'team_backgrounds': content.TEAM_BACKGROUNDS,
        'standards': content.STANDARDS,
        'frameworks': content.FRAMEWORKS,
        'process': content.PROCESS,
        'forge_seq': FORGE_SEQ,
        'forge_props': _forge_props(),
        'hero_props': {'mark': f"/{settings.STATIC_URL.strip('/')}/business_page/brand/mark.svg"},
        'system_map': content.SYSTEM_MAP,
        'system_map_props': {
            **content.SYSTEM_MAP,
            'layers': [{'key': layer['key'], 'name': layer['name']} for layer in LAYERS],
            'services': {slug: {'name': SERVICES[slug]['nav_label'], 'url': f'/services/{slug}/'} for slug in SERVICE_ORDER},
        },
    })


def about(request):
    return render(request, 'business_page/about.html', {
        'team_backgrounds': content.TEAM_BACKGROUNDS,
        'principles': content.PRINCIPLES,
        'layers': _layers_with_services(),
        'forge_seq': FORGE_SEQ,
        'case_count': _published_cases().count(),
    })


def services(request):
    layers = _layers_with_services()
    return render(request, 'business_page/services.html', {
        'layers': layers,
        'all_services': [s for layer in layers for s in layer['items']],
        'engagements': content.ENGAGEMENTS,
        'process': content.PROCESS,
        'faqs': content.GENERAL_FAQ,
        'frameworks': content.FRAMEWORKS,
    })


def service_detail(request, slug):
    svc = SERVICES.get(slug)
    if svc is None:
        raise Http404
    layer = LAYER_BY_KEY[svc['layer']]
    related_services = [SERVICES[s] for s in svc.get('related', []) if s in SERVICES]
    cases = [c for c in _published_cases() if slug in (c.services or [])]
    return render(request, 'business_page/service_detail.html', {
        'svc': svc,
        'layer': layer,
        'related_services': related_services,
        'related_cases': cases[:3],
        'signature_props': {'variant': svc['signature'], 'name': svc['nav_label'], 'layer': svc['layer']},
    })


def projects(request):
    layer = request.GET.get('layer', '')
    cases = list(_published_cases())
    shown = [c for c in cases if layer in (c.layers or [])] if layer in LAYER_BY_KEY else cases
    return render(request, 'business_page/projects.html', {
        'cases': shown,
        'all_count': len(cases),
        'layers': LAYERS,
        'active_layer': layer if layer in LAYER_BY_KEY else '',
    })


def work(request):
    return redirect('projects', permanent=True)


def case_study(request, slug):
    case = get_object_or_404(_published_cases(), slug=slug)
    ordered = list(_published_cases())
    idx = next(i for i, c in enumerate(ordered) if c.pk == case.pk)
    next_case = ordered[(idx + 1) % len(ordered)] if len(ordered) > 1 else None
    return render(request, 'business_page/case_study.html', {
        'case': case,
        'case_layers': [LAYER_BY_KEY[k] for k in case.layers if k in LAYER_BY_KEY],
        'case_services': [SERVICES[s] for s in case.services if s in SERVICES],
        'next_case': next_case,
        'architecture_props': {
            **(case.architecture or {}),
            'layers': [{'key': layer['key'], 'name': layer['name']} for layer in LAYERS],
            'title': f'{case.client} — system architecture',
        },
    })


def contact(request):
    initial_type = request.GET.get('type', '')
    if initial_type not in dict(ContactSubmission.PROJECT_TYPES):
        initial_type = ''
    if request.method == 'POST':
        form = ProjectIntakeForm(request.POST)
        if form.is_spam:
            messages.success(request, 'sent')
            return redirect('contact')
        if rate_limited(request, 'intake'):
            messages.error(request, 'Too many submissions from your connection in a short time. Please wait a few minutes and try again.')
        elif form.is_valid():
            if not verify_turnstile(request.POST.get('cf-turnstile-response', ''), client_ip(request)):
                messages.error(request, 'The spam check didn’t pass. Please try again in a moment.')
            else:
                sub, _ = save_intake(form, request)
                request.session['intake_urgent'] = sub.is_urgent
                return redirect('contact_thanks')
    else:
        form = ProjectIntakeForm(initial={'project_type': initial_type})
    return render(request, 'business_page/contact.html', {
        'form': form,
        'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
        'intake_props': {
            'initialType': initial_type,
            'turnstileSiteKey': settings.TURNSTILE_SITE_KEY,
            'endpoint': '/api/v1/intake/',
            'choices': {
                'project_type': ContactSubmission.PROJECT_TYPES,
                'budget': ContactSubmission.BUDGETS,
                'timeline': ContactSubmission.TIMELINES,
            },
        },
    })


def contact_thanks(request):
    urgent = request.session.pop('intake_urgent', False)
    return render(request, 'business_page/contact_thanks.html', {'urgent': urgent})


def blog(request):
    topic = request.GET.get('topic', '')
    topics = dict(Post.TOPICS)
    posts = list(_published_posts())
    shown = [p for p in posts if p.topic == topic] if topic in topics else posts
    featured = next((p for p in shown if p.featured), shown[0] if shown else None)
    return render(request, 'business_page/blog.html', {
        'featured': featured,
        'posts': [p for p in shown if p != featured],
        'topics': Post.TOPICS,
        'topic_counts': {k: sum(1 for p in posts if p.topic == k) for k in topics},
        'active_topic': topic if topic in topics else '',
        'post_count': len(posts),
        'subscribe_form': SubscribeForm(),
    })


def post_detail(request, slug):
    post = get_object_or_404(_published_posts(), slug=slug)
    others = list(_published_posts().exclude(pk=post.pk))
    related = [p for p in others if p.topic == post.topic][:2] or others[:2]
    topic_service = {
        'security': 'security', 'devops': 'devops', 'cloud': 'cloud',
        'automation': 'crm-automation', 'engineering': 'software-development',
    }.get(post.topic)
    return render(request, 'business_page/post_detail.html', {
        'post': post,
        'related': related,
        'topic_service': SERVICES.get(topic_service),
        'subscribe_form': SubscribeForm(),
    })


def privacy(request):
    return render(request, 'business_page/privacy.html')


@require_POST
def newsletter_signup(request):
    form = SubscribeForm(request.POST)
    back = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/blog/'
    if not back.startswith('/'):
        back = '/blog/'
    if form.data.get('website'):
        messages.success(request, 'Check your inbox to confirm your subscription.')
    elif rate_limited(request, 'subscribe'):
        messages.error(request, 'Too many attempts. Please try again in a few minutes.')
    elif form.is_valid():
        _, state = subscribe(form.cleaned_data['email'], request)
        messages.success(request, 'You’re already subscribed — thank you.' if state == 'already'
                         else 'Almost done — check your inbox and confirm your subscription.')
    else:
        messages.error(request, form.errors['email'][0])
    return redirect(back)


def newsletter_confirm(request, token):
    sub = confirm_subscription(token)
    if not sub:
        raise Http404
    return render(request, 'business_page/newsletter_state.html', {'state': 'confirmed', 'sub': sub})


def newsletter_unsubscribe(request, token):
    sub = unsubscribe(token)
    if not sub:
        raise Http404
    return render(request, 'business_page/newsletter_state.html', {'state': 'unsubscribed', 'sub': sub})


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
