from django.contrib import admin
from .forms import AdminPostCreateForm
from .models import Post, Comment, Reply, Tag, EmailPush, LinePush


class ReplyInline(admin.StackedInline):
    model = Reply
    extra = 5


class CommentAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]


def notify(modeladmin, request, queryset):
    """通知を送信アクション"""
    for post in queryset:
        post.line_push(request)
        post.browser_push()
        post.email_push(request)


class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text')
    list_display = ['title', 'is_public', 'updated_at', 'created_at', 'title_len']
    list_filter = ['is_public', 'tags']
    form = AdminPostCreateForm
    actions = [notify]
    ordering = ('-updated_at',)

    def title_len(self, obj):
        return len(obj.title)

    title_len.short_description = 'タイトルの文字数'


notify.short_description = '通知を送信'
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply)
admin.site.register(Tag)
admin.site.register(EmailPush)
admin.site.register(LinePush)
