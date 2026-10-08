from django.conf import settings

from .services_data import LAYERS, SERVICES

NAV = [
    ('work', 'Work', 'projects'),
    ('capabilities', 'Capabilities', 'services'),
    ('about', 'About', 'about'),
    ('journal', 'Journal', 'blog'),
]

COMPANY = {
    'name': 'HZORTECH',
    'whatsapp': 'https://wa.me/37477075919',
    'city': 'Yerevan, Armenia',
    'coords': '40.1792° N · 44.4991° E',
    'hours': 'Mon–Fri · 09:00–18:00 (GMT+4)',
    'founded': 2022,
    'instagram': 'https://www.instagram.com/hzortech',
    'linkedin': 'https://linkedin.com/company/hzortech',
}


def site(request):
    return {
        'csp_nonce': getattr(request, 'csp_nonce', ''),
        'site_url': settings.SITE_URL.rstrip('/'),
        'company': COMPANY,
        'nav_items': NAV,
        'footer_layers': [
            {**layer, 'items': [SERVICES[s] for s in layer['services']]} for layer in LAYERS
        ],
        'meta_pixel_id': settings.META_PIXEL_ID,
    }


def _org_graph():
    url = settings.SITE_URL.rstrip('/')
    return {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': ['Organization', 'ProfessionalService'],
                '@id': f'{url}/#organization',
                'name': 'HZORTECH',
                'url': f'{url}/',
                'logo': {'@type': 'ImageObject', 'url': f'{url}/static/business_page/img/logo-tile-512.png',
                         'width': 512, 'height': 512},
                'image': f'{url}/static/business_page/img/og-image.png',
                'description': ('Engineering company in Yerevan, Armenia building digital platforms — the product, '
                                'backend, automation, cloud infrastructure and security behind it.'),
                'foundingDate': str(COMPANY['founded']),
                'address': {'@type': 'PostalAddress', 'addressLocality': 'Yerevan', 'addressCountry': 'AM'},
                'geo': {'@type': 'GeoCoordinates', 'latitude': 40.179186, 'longitude': 44.499103},
                'areaServed': ['Armenia', 'European Union', 'United States', 'United Kingdom', 'Worldwide'],
                'knowsLanguage': ['en', 'hy', 'ru'],
                'contactPoint': {'@type': 'ContactPoint', 'url': f'{url}/contact/',
                                 'contactType': 'sales', 'availableLanguage': ['English', 'Armenian', 'Russian']},
                'openingHoursSpecification': {'@type': 'OpeningHoursSpecification',
                                              'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                                              'opens': '09:00', 'closes': '18:00'},
                'sameAs': [COMPANY['instagram'], COMPANY['linkedin'], COMPANY['whatsapp']],
            },
            {
                '@type': 'WebSite', '@id': f'{url}/#website', 'url': f'{url}/', 'name': 'HZORTECH',
                'publisher': {'@id': f'{url}/#organization'}, 'inLanguage': 'en',
            },
        ],
    }


_ORG = None


def seo(request):
    global _ORG
    if _ORG is None:
        _ORG = _org_graph()
    return {'org_graph': _ORG}
