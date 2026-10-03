"""Server-side Higgsfield integration.

The key (`HF_KEY=<id>:<secret>`) is read from the environment only — never
from settings that reach templates, never sent to the browser. Generation is
asynchronous by design:

    submit()  → POST /{model}           → store request_id (GeneratedAsset)
    sync()    → GET  /requests/{id}/status (poll)  ─┐
    webhook   → POST /api/v1/hooks/higgsfield/<token>/ ─┴→ apply_status()
    download  → result media saved under HIGGSFIELD_OUTPUT_DIR

Plain `requests` is used (already a production dependency) so the webhook
path works in the production image without the optional SDK.
"""

import json
import logging
import mimetypes
import os
from pathlib import Path

import requests
from django.conf import settings
from django.utils import timezone

from .models import GeneratedAsset

log = logging.getLogger(__name__)

API_BASE = 'https://api.higgsfield.ai'
TERMINAL = {'completed', 'failed', 'nsfw', 'canceled'}


class HiggsfieldError(RuntimeError):
    pass


def _key():
    key = os.environ.get('HF_KEY')
    if not key and os.environ.get('HF_API_KEY') and os.environ.get('HF_API_SECRET'):
        key = f"{os.environ['HF_API_KEY']}:{os.environ['HF_API_SECRET']}"
    if not key:
        raise HiggsfieldError('HF_KEY is not set (expected HF_KEY=<key-id>:<key-secret> in the environment).')
    return key


def _session():
    s = requests.Session()
    s.headers.update({
        'Authorization': f'Key {_key()}',
        'Content-Type': 'application/json',
        'User-Agent': 'hzortech-site/2.0',
    })
    return s


def _raise_for(resp):
    if resp.status_code >= 400:
        try:
            detail = resp.json().get('detail')
        except ValueError:
            detail = resp.text[:300]
        raise HiggsfieldError(f'Higgsfield API {resp.status_code}: {detail}')


def submit(slot, model_slug, arguments, *, webhook_url=None, notes=''):
    """Queue a generation and record it. Returns the GeneratedAsset."""
    if 'prompt' not in arguments:
        raise HiggsfieldError('arguments must include a prompt')
    url = f'{API_BASE}/{model_slug}'
    params = {'hf_webhook': webhook_url} if webhook_url else None
    resp = _session().post(url, params=params, data=json.dumps(arguments), timeout=60)
    _raise_for(resp)
    data = resp.json()
    return GeneratedAsset.objects.create(
        slot=slot,
        model_slug=model_slug,
        prompt=arguments['prompt'],
        arguments=arguments,
        request_id=data['request_id'],
        status=data.get('status', 'queued'),
        result=data,
        notes=notes,
    )


def find_media_url(payload):
    """Result payloads differ per model family (video / videos / images)."""
    for key in ('video', 'image', 'audio'):
        val = payload.get(key)
        if isinstance(val, dict) and val.get('url'):
            return val['url']
        if isinstance(val, str) and val.startswith('http'):
            return val
    for key in ('videos', 'images'):
        val = payload.get(key)
        if isinstance(val, list) and val:
            first = val[0]
            if isinstance(first, dict) and first.get('url'):
                return first['url']
            if isinstance(first, str):
                return first
    return ''


def apply_status(asset, payload):
    """Update a ledger row from a status payload (poll or webhook)."""
    status = payload.get('status') or asset.status
    asset.status = status
    asset.result = payload
    if status == 'completed':
        asset.result_url = find_media_url(payload) or asset.result_url
        asset.completed_at = asset.completed_at or timezone.now()
    elif status in {'failed', 'nsfw'}:
        asset.error = str(payload.get('error') or payload.get('detail') or status)
    asset.save()
    return asset


def poll(asset):
    resp = _session().get(f'{API_BASE}/requests/{asset.request_id}/status', timeout=60)
    _raise_for(resp)
    return apply_status(asset, resp.json())


def output_dir():
    return Path(getattr(settings, 'HIGGSFIELD_OUTPUT_DIR', settings.BASE_DIR / 'assets' / 'generated'))


def download(asset, *, force=False):
    """Save the result media locally; returns the path (or '' if not ready)."""
    if asset.status != 'completed' or not asset.result_url:
        return ''
    if asset.local_path and Path(asset.local_path).exists() and not force:
        return asset.local_path
    with requests.get(asset.result_url, stream=True, timeout=300) as resp:
        _raise_for(resp)
        ctype = resp.headers.get('content-type', '').split(';')[0]
        ext = mimetypes.guess_extension(ctype) or Path(asset.result_url.split('?')[0]).suffix or '.bin'
        target_dir = output_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{asset.slot.replace('.', '-')}-{asset.request_id[:8]}{ext}"
        with open(target, 'wb') as fh:
            for chunk in resp.iter_content(1 << 16):
                fh.write(chunk)
    asset.local_path = str(target)
    asset.save(update_fields=['local_path', 'updated_at'])
    return asset.local_path


def export_ledger(path=None):
    """Write the provenance ledger (committed with the processed assets)."""
    path = Path(path or settings.BASE_DIR / 'assets' / 'higgsfield-ledger.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            'slot': a.slot,
            'model': a.model_slug,
            'request_id': a.request_id,
            'status': a.status,
            'prompt': a.prompt,
            'arguments': a.arguments,
            'result_url': a.result_url,
            'local_file': os.path.relpath(a.local_path, settings.BASE_DIR) if a.local_path else '',
            'notes': a.notes,
            'created_at': a.created_at.isoformat(),
            'completed_at': a.completed_at.isoformat() if a.completed_at else None,
        }
        for a in GeneratedAsset.objects.order_by('created_at')
    ]
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
    return path
