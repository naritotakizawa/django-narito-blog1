from django.urls import path
from . import views, feeds

app_name = 'nblog1'

urlpatterns = [
    path('', views.PublicPostIndexView.as_view(), name='top'),
    path('private/', views.PrivatePostIndexView.as_view(), name='private_post_list'),
    path('detail/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('comment/create/<int:pk>/', views.CommentCreate.as_view(), name='comment_create'),
    path('reply/create/<int:pk>/', views.ReplyCreate.as_view(), name='reply_create'),

    path('subscribe/email/', views.subscribe_email, name='subscribe_email'),
    path('subscribe/email/register/<str:token>/', views.subscribe_email_register, name='subscribe_email_register'),
    path('subscribe/email/done/', views.subscribe_email_done, name='subscribe_email_done'),
    path('subscribe/email/release/done/', views.subscribe_email_release_done, name='subscribe_email_release_done'),
    path('subscribe/email/release/<str:token>/', views.subscribe_email_release, name='subscribe_email_release'),

    path('posts/suggest/', views.posts_suggest, name='posts_suggest'),
    path('image/upload/', views.image_upload, name='image_upload'),

    path('rss/', feeds.RssLatestPostsFeed(), name='rss'),
    path('atom/', feeds.AtomLatestPostsFeed(), name='atom'),
]
