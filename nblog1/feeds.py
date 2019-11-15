from django.contrib.syndication.views import Feed
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from .models import Post


class RssLatestPostsFeed(Feed):
    """最新記事のフィード。"""
    link = reverse_lazy('nblog1:top')

    def items(self):
        """記事一覧を返す。"""
        return Post.objects.filter(
            is_public=True
        ).order_by('-created_at').prefetch_related('tags')[:15]

    def item_title(self, item):
        """記事のタイトルを返す。"""
        return item.title

    def item_description(self, item):
        """記事の説明を返す。"""
        return item.description

    def item_link(self, item):
        """記事へのリンクを返す。"""
        return resolve_url('nblog1:post_detail', pk=item.pk)

    def item_pubdate(self, item):
        return item.created_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]


class AtomLatestPostsFeed(RssLatestPostsFeed):
    feed_type = Atom1Feed
