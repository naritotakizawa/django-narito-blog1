from django.contrib.sitemaps import Sitemap
from django.shortcuts import resolve_url
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return Post.objects.filter(is_public=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return resolve_url('nblog1:post_detail', pk=obj.pk)


class BlogSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['nblog1:top']

    def location(self, obj):
        return resolve_url(obj)
