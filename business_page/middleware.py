class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://unpkg.com "
            "https://challenges.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "frame-src https://challenges.cloudflare.com; "
            "connect-src 'self'; "
            "base-uri 'self';"
        )
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        return response
