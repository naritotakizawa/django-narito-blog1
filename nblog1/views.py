import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import (
    PostSearchForm, CommentCreateForm, ReplyCreateForm,
    EmailForm, FileUploadForm
)
from .models import Post, Comment, Reply, EmailPush, LinePush, Tag


class PublicPostIndexView(generic.ListView):
    """公開記事の一覧を表示する。"""
    paginate_by = 10
    model = Post

    def _get_queryset(self):
        queryset = super().get_queryset()
        self.form = form = PostSearchForm(self.request.GET or None)
        if form.is_valid():
            # 選択したタグが含まれた記事
            tags = form.cleaned_data.get('tags')
            if tags:
                for tag in tags:
                    queryset = queryset.filter(tags=tag)

            # タイトルか本文にキーワードが含まれたもの
            # キーワードが半角スペースで区切られていれば、その回数だけfilterする。つまりAND。
            key_word = form.cleaned_data.get('key_word')
            if key_word:
                for word in key_word.split():
                    queryset = queryset.filter(Q(title__icontains=word) | Q(text__icontains=word))

        queryset = queryset.order_by('-updated_at').prefetch_related('tags')
        return queryset

    def get_queryset(self):
        return self._get_queryset().filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        return context


class PrivatePostIndexView(LoginRequiredMixin, PublicPostIndexView):
    """非公開の記事一覧を表示する。"""

    def get_queryset(self):
        return self._get_queryset().filter(is_public=False)


class PostDetailView(generic.DetailView):
    """記事詳細ページを表示する。"""
    model = Post

    def get_queryset(self):
        return super().get_queryset().prefetch_related('tags', 'comment_set__reply_set')

    def get_object(self, queryset=None):
        """その記事が公開か、ユーザがログインしていれば表示する。"""
        post = super().get_object()
        if post.is_public or self.request.user.is_authenticated:
            return post
        else:
            raise Http404


class CommentCreate(generic.CreateView):
    """記事へのコメント作成ビュー。"""
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        post_pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_pk)
        comment = form.save(commit=False)
        comment.target = post
        comment.request = self.request
        comment.save()
        messages.info(self.request, 'コメントしました。')
        return redirect('nblog1:post_detail', pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context


class ReplyCreate(generic.CreateView):
    """コメントへの返信作成ビュー。"""
    model = Reply
    form_class = ReplyCreateForm
    template_name = 'nblog1/comment_form.html'

    def form_valid(self, form):
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        reply = form.save(commit=False)
        reply.target = comment
        reply.request = self.request
        reply.save()
        messages.info(self.request, '返信しました。')
        return redirect('nblog1:post_detail', pk=comment.target.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        context['post'] = comment.target
        return context


@require_POST
def subscribe_email(request):
    """ブログの購読ページ"""
    form = EmailForm(request.POST)
    # メール購読の処理
    if form.is_valid():
        push = form.save()
        context = {
            'token': dumps(push.pk),
        }
        subject = render_to_string('nblog1/mail/confirm_push_subject.txt', context, request)
        message = render_to_string('nblog1/mail/confirm_push_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [push.mail]
        bcc = [settings.DEFAULT_FROM_EMAIL]
        email = EmailMessage(subject, message, from_email, to, bcc)
        email.send()
        return JsonResponse({'message': 'Thanks!! メールに、登録用のURLを送付しました。'})

    return JsonResponse(form.errors.get_json_data(), status=400)


def subscribe_email_register(request, token):
    """メール購読の確認処理"""
    try:
        user_pk = loads(token, max_age=60*60*24)  # 1日以内

    # 期限切れ
    except SignatureExpired:
        return HttpResponseBadRequest()

    # tokenが間違っている
    except BadSignature:
        return HttpResponseBadRequest()

    # tokenは問題なし
    else:
        try:
            push = EmailPush.objects.get(pk=user_pk)
        except EmailPush.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            if not push.is_active:
                # まだ仮登録で、他に問題なければ本登録とする
                push.is_active = True
                push.save()
                return redirect('nblog1:subscribe_email_done')

    return HttpResponseBadRequest()


def subscribe_email_done(request):
    """メール購読完了"""
    return render(request, 'nblog1/subscribe_email_done.html')


@csrf_exempt
def line_callback(request):
    """ラインの友達追加時に呼び出され、ラインのIDを登録する。"""
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        events = request_json['events']
        line_user_id = events[0]['source']['userId']

        # チャネル設定のWeb hook接続確認時にはここ。このIDで見に来る。
        if line_user_id == 'Udeadbeefdeadbeefdeadbeefdeadbeef':
            pass

        # 友達追加時・ブロック解除時
        elif events[0]['type'] == 'follow':
            LinePush.objects.create(user_id=line_user_id)

        # アカウントがブロックされたとき
        elif events[0]['type'] == 'unfollow':
            LinePush.objects.filter(user_id=line_user_id).delete()

    return HttpResponse()


def image_upload(request):
    """ファイルのアップロード用ビュー"""
    form = FileUploadForm(files=request.FILES)
    if form.is_valid():
        path = form.save()
        url = '{0}://{1}{2}'.format(
            request.scheme,
            request.get_host(),
            path,
        )
        return JsonResponse({'url': url})
    return HttpResponseBadRequest()


def posts_suggest(request):
    """サジェスト候補の記事をJSONで返す。"""
    keyword = request.GET.get('keyword')
    if keyword:
        post_list = [{'pk': post.pk, 'name': str(post)} for post in Post.objects.filter(title__icontains=keyword)]
    else:
        post_list = []
    return JsonResponse({'object_list': post_list})
