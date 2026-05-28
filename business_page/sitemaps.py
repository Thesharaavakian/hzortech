from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    protocol = "https"
    i18n = False

    pages = [
        ("home",     1.0, "weekly"),
        ("services", 0.9, "monthly"),
        ("projects", 0.9, "monthly"),
        ("about",    0.8, "monthly"),
        ("contact",  0.7, "monthly"),
        ("blog",     0.6, "weekly"),
        ("privacy",  0.3, "yearly"),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]
