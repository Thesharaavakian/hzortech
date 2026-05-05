from django.urls import path
from . import views

urlpatterns = [
    path('',          views.home,     name='home'),
    path('about/',    views.about,    name='about'),
    path('services/', views.services, name='services'),
    path('projects/', views.projects, name='projects'),
    path('contact/',  views.contact,  name='contact'),
    path('privacy/',  views.privacy,  name='privacy'),
]
