import secrets

from django.conf import settings


class SecurityHeadersMiddleware:
    """Per-request CSP nonce + hardened security headers.

    Scripts: only same-origin files and nonce'd inline scripts may run — no
    'unsafe-inline'. Third parties are limited to Cloudflare Turnstile (contact
    form) and the Meta Pixel, which is injected only after analytics consent.
    Styles keep 'unsafe-inline' because server-rendered style attributes carry
    per-item CSS custom properties (e.g. --hue); that is not a script vector.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)
        response = self.get_response(request)
        if response.get('Content-Security-Policy') is None:
            response['Content-Security-Policy'] = self.policy(request)
        # Sent unconditionally, not gated on request.is_secure() (Django's
        # own SECURE_HSTS_SECONDS mechanism is, and that gate evaluated
        # false in the real Cloudflare → nginx → Django chain in production
        # — see the SECURE_SSL_REDIRECT comment in settings.py). A header
        # here can't loop the way a redirect could, so this is the safe
        # way to keep sending it while that's unresolved.
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=(), usb=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        return response

    @staticmethod
    def policy(request):
        nonce = request.csp_nonce
        dev = settings.VITE_DEV_SERVER
        dev_src = f' {dev} {dev.replace("http", "ws")}' if dev else ''
        return '; '.join([
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}' https://challenges.cloudflare.com https://connect.facebook.net{dev_src}",
            f"style-src 'self' 'unsafe-inline'{dev_src}",
            "font-src 'self'",
            "img-src 'self' data: blob: https://www.facebook.com",
            "media-src 'self' blob:",
            "frame-src https://challenges.cloudflare.com",
            f"connect-src 'self' https://connect.facebook.net https://www.facebook.com{dev_src}",
            "worker-src 'self' blob:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ])
