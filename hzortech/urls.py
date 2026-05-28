from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from business_page.sitemaps import StaticViewSitemap
from business_page import urls
import os

handler404 = 'business_page.views.custom_404'

sitemaps = {'static': StaticViewSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', serve, {
        'path': 'robots.txt',
        'document_root': os.path.join(settings.BASE_DIR, 'business_page', 'static'),
    }),
    path('security.txt', serve, {
        'path': 'security.txt',
        'document_root': os.path.join(settings.BASE_DIR, 'business_page', 'static'),
    }),
    path('', include(urls)),
]
