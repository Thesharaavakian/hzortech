from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .services_data import SERVICES, SERVICE_ORDER


class StaticViewSitemap(Sitemap):
    protocol = "https"

    pages = [
        ("home",     "/",          1.0, "weekly"),
        ("services", "/services/", 0.9, "monthly"),
        ("projects", "/projects/", 0.9, "monthly"),
        ("about",    "/about/",    0.8, "monthly"),
        ("contact",  "/contact/",  0.7, "monthly"),
        ("blog",     "/blog/",     0.6, "weekly"),
        ("privacy",  "/privacy/",  0.3, "yearly"),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[2]

    def changefreq(self, item):
        return item[3]


class ServiceDetailSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.85

    def items(self):
        return SERVICE_ORDER

    def location(self, slug):
        return reverse('service_detail', kwargs={'slug': slug})
