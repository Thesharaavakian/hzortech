"""Asynchronous Higgsfield asset generation.

    manage.py higgsfield submit --slot home.forge \
        --model bytedance/seedance-2.0/text-to-video \
        --prompt-file assets/prompts/forge.txt \
        --arg duration=12 --arg resolution=1080p --arg aspect_ratio=16:9
    manage.py higgsfield sync [--wait] [--download]
    manage.py higgsfield list
    manage.py higgsfield export          # writes assets/higgsfield-ledger.json
    manage.py higgsfield record --slot x --model y --request-id z --status canceled --prompt ...

`submit` returns immediately after the request is queued; nothing blocks on
generation. If HF_KEY is not already in the environment, `.env.local` in the
project root is read (development convenience — production uses real env).
"""

import os
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from business_page import higgsfield as hf
from business_page.models import GeneratedAsset


def _load_env_local():
    path = Path(settings.BASE_DIR) / '.env.local'
    if os.environ.get('HF_KEY') or not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _coerce(value):
    if value.lower() in {'true', 'false'}:
        return value.lower() == 'true'
    try:
        return int(value)
    except ValueError:
        return value


class Command(BaseCommand):
    help = 'Submit, poll and download Higgsfield generations (asynchronous, server-side).'

    def add_arguments(self, parser):
        sub = parser.add_subparsers(dest='action', required=True)

        s = sub.add_parser('submit')
        s.add_argument('--slot', required=True)
        s.add_argument('--model', required=True)
        g = s.add_mutually_exclusive_group(required=True)
        g.add_argument('--prompt')
        g.add_argument('--prompt-file')
        s.add_argument('--arg', action='append', default=[], help='key=value (repeatable)')
        s.add_argument('--notes', default='')
        s.add_argument('--webhook', action='store_true',
                       help='Ask Higgsfield to POST status to /api/v1/hooks/higgsfield/<token>/ (needs SITE_URL + HIGGSFIELD_WEBHOOK_TOKEN).')

        y = sub.add_parser('sync')
        y.add_argument('--wait', action='store_true', help='Keep polling until every open request is terminal.')
        y.add_argument('--interval', type=int, default=15)
        y.add_argument('--download', action='store_true')

        sub.add_parser('list')
        sub.add_parser('export')

        r = sub.add_parser('record', help='Record a request made outside this command (e.g. a probe).')
        r.add_argument('--slot', required=True)
        r.add_argument('--model', required=True)
        r.add_argument('--request-id', required=True)
        r.add_argument('--status', default='queued')
        r.add_argument('--prompt', default='')
        r.add_argument('--notes', default='')

    def handle(self, *args, **opts):
        _load_env_local()
        try:
            getattr(self, f"do_{opts['action']}")(opts)
        except hf.HiggsfieldError as exc:
            raise CommandError(str(exc)) from exc

    def do_submit(self, o):
        prompt = o['prompt'] or Path(o['prompt_file']).read_text().strip()
        arguments = {'prompt': prompt}
        for pair in o['arg']:
            if '=' not in pair:
                raise CommandError(f'--arg must be key=value, got {pair!r}')
            k, v = pair.split('=', 1)
            arguments[k] = _coerce(v)
        webhook = None
        if o['webhook']:
            base, token = getattr(settings, 'SITE_URL', ''), getattr(settings, 'HIGGSFIELD_WEBHOOK_TOKEN', '')
            if not (base and token):
                raise CommandError('--webhook needs SITE_URL and HIGGSFIELD_WEBHOOK_TOKEN settings.')
            webhook = f'{base.rstrip("/")}/api/v1/hooks/higgsfield/{token}/'
        asset = hf.submit(o['slot'], o['model'], arguments, webhook_url=webhook, notes=o['notes'])
        self.stdout.write(self.style.SUCCESS(f'queued {asset.slot}: {asset.request_id}'))
        hf.export_ledger()

    def do_sync(self, o):
        while True:
            open_assets = [a for a in GeneratedAsset.objects.all() if not a.is_done]
            for a in open_assets:
                hf.poll(a)
                self.stdout.write(f'{a.slot:<24} {a.request_id}  {a.status}')
            if o['download']:
                for a in GeneratedAsset.objects.filter(status='completed'):
                    path = hf.download(a)
                    if path:
                        self.stdout.write(self.style.SUCCESS(f'{a.slot:<24} → {path}'))
            hf.export_ledger()
            if not o['wait'] or not any(not a.is_done for a in GeneratedAsset.objects.all()):
                break
            time.sleep(o['interval'])

    def do_list(self, o):
        for a in GeneratedAsset.objects.order_by('created_at'):
            self.stdout.write(f'{a.created_at:%Y-%m-%d %H:%M}  {a.slot:<24} {a.status:<11} {a.model_slug}  {a.request_id}')

    def do_export(self, o):
        self.stdout.write(str(hf.export_ledger()))

    def do_record(self, o):
        asset, _ = GeneratedAsset.objects.update_or_create(
            request_id=o['request_id'],
            defaults={'slot': o['slot'], 'model_slug': o['model'], 'status': o['status'],
                      'prompt': o['prompt'], 'notes': o['notes']},
        )
        self.stdout.write(f'recorded {asset}')
        hf.export_ledger()
