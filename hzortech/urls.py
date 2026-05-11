from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from business_page import urls
import os

handler404 = 'business_page.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('security.txt', serve, {
        'path': 'security.txt',
        'document_root': os.path.join(settings.BASE_DIR, 'business_page', 'static'),
    }),
    path('', include(urls)),
]
