from django.urls import path

from . import api, views

urlpatterns = [
    path('',                          views.home,              name='home'),
    path('about/',                    views.about,             name='about'),
    path('services/',                 views.services,          name='services'),
    path('services/<slug:slug>/',     views.service_detail,    name='service_detail'),
    path('projects/',                 views.projects,          name='projects'),
    path('projects/<slug:slug>/',     views.case_study,        name='case_study'),
    path('work/',                     views.work,              name='work'),
    path('contact/',                  views.contact,           name='contact'),
    path('contact/thanks/',           views.contact_thanks,    name='contact_thanks'),
    path('privacy/',                  views.privacy,           name='privacy'),
    path('blog/',                     views.blog,              name='blog'),
    path('blog/<slug:slug>/',         views.post_detail,       name='post_detail'),
    path('newsletter/',               views.newsletter_signup, name='newsletter_signup'),
    path('newsletter/confirm/<str:token>/',     views.newsletter_confirm,     name='newsletter_confirm'),
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),

    # JSON API
    path('api/v1/services/',              api.services_index,  name='api_services'),
    path('api/v1/projects/',              api.projects_index,  name='api_projects'),
    path('api/v1/projects/<slug:slug>/',  api.project_detail,  name='api_project_detail'),
    path('api/v1/posts/',                 api.posts_index,     name='api_posts'),
    path('api/v1/search-index/',          api.search_index,    name='api_search_index'),
    path('api/v1/intake/',                api.intake,          name='api_intake'),
    path('api/v1/subscribe/',             api.subscribe_api,   name='api_subscribe'),
    path('api/v1/hooks/higgsfield/<str:token>/', api.higgsfield_webhook, name='api_higgsfield_webhook'),
]
