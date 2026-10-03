import os

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.static import serve

from business_page import urls
from business_page.sitemaps import CaseStudySitemap, PostSitemap, ServiceDetailSitemap, StaticViewSitemap

handler404 = 'business_page.views.custom_404'
handler500 = 'business_page.views.custom_500'

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceDetailSitemap,
    'work': CaseStudySitemap,
    'journal': PostSitemap,
}

_static_root = os.path.join(settings.BASE_DIR, 'business_page', 'static')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', serve, {'path': 'robots.txt', 'document_root': _static_root}),
    path('security.txt', serve, {'path': 'security.txt', 'document_root': _static_root}),
    path('.well-known/security.txt', serve, {'path': 'security.txt', 'document_root': _static_root}),
    path('', include(urls)),
]
