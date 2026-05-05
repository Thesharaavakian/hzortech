from django.contrib import admin
from django.urls import path, include
from business_page import urls

handler404 = 'business_page.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(urls)),
]
