from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import CaseStudy, Post
from .services_data import SERVICE_ORDER


class StaticViewSitemap(Sitemap):
    protocol = "https"

    pages = [
        ("home",     1.0, "weekly"),
        ("services", 0.9, "monthly"),
        ("projects", 0.9, "monthly"),
        ("about",    0.8, "monthly"),
        ("contact",  0.8, "monthly"),
        ("blog",     0.7, "weekly"),
        ("privacy",  0.2, "yearly"),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


class ServiceDetailSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.85

    def items(self):
        return SERVICE_ORDER

    def location(self, slug):
        return reverse('service_detail', kwargs={'slug': slug})


class CaseStudySitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return CaseStudy.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
