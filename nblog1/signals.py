from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from .models import Comment, Reply


@receiver(post_save, sender=Comment)
def send_mail_to_author(sender, instance, created, **kwargs):
    """コメントがあったことを管理者に伝える"""
    if created:
        # views.py側で、requestオブジェクトをインスタンスに格納しています。
        request = instance.request

        # コメントの投稿者を識別するため、投稿者のセッションにコメントのpkを入れておく
        request.session[str(instance.pk)] = True

        context = {
            'post': instance.target,
        }
        subject = render_to_string('nblog1/mail/comment_notify_subject.txt', context, request)
        message = render_to_string('nblog1/mail/comment_notify_message.txt', context, request)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.DEFAULT_FROM_EMAIL]
        send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Reply)
def send_mail_to_comment_user(sender, instance, created, **kwargs):
    """コメントに返信があったことを、管理者とコメント者に伝える"""
    if created:
        # views.py側で、requestオブジェクトをインスタンスに格納しています。
        request = instance.request

        comment = instance.target
        post = comment.target
        context = {
            'post': post,
        }
        subject = render_to_string('nblog1/mail/reply_notify_subject.txt', context, request)
        message = render_to_string('nblog1/mail/reply_notify_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = []
        bcc = [settings.DEFAULT_FROM_EMAIL]
        # コメントした人がメールアドレスを入力しており
        # コメントした人と返信した人が違う場合は、コメントした人に返信あるよとメール
        if comment.email and not request.session.get(str(comment.pk)):
            recipient_list.append(comment.email)
        email = EmailMessage(subject, message, from_email, recipient_list, bcc)
        email.send()
