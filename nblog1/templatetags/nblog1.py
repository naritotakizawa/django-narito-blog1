from urllib import parse
from django import template
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe
from nblog1.forms import EmailForm
import markdown
from markdown.extensions import Extension

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """GETパラメータの一部を置き換える。"""
    url_dict = request.GET.copy()
    url_dict[field] = str(value)
    return url_dict.urlencode()


@register.filter
def markdown_to_html(text):
    """マークダウンをhtmlに変換する。"""
    html = markdown.markdown(text, extensions=settings.MARKDOWN_EXTENSIONS)
    return mark_safe(html)


class EscapeHtml(Extension):

    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')


@register.filter
def markdown_to_html_with_escape(text):
    """マークダウンをhtmlに変換する。

    生のHTMLやCSS、JavaScript等のコードをエスケープした上で、マークダウンをHTMLに変換します。
    公開しているコメント欄等には、こちらを使ってください。

    """
    extensions = settings.MARKDOWN_EXTENSIONS + [EscapeHtml()]
    html = markdown.markdown(text, extensions=extensions)
    return mark_safe(html)


@register.inclusion_tag('nblog1/includes/subscribe_section.html')
def render_subscribe_section():
    context = {
        'subscribe_email_form': EmailForm,
        'USE_LINE_BOT': settings.USE_LINE_BOT,
        'USE_WEB_PUSH': settings.USE_WEB_PUSH,
    }
    if settings.USE_WEB_PUSH:
        context['ONE_SIGNAL_APP_ID'] = settings.ONE_SIGNAL_APP_ID
    return context
