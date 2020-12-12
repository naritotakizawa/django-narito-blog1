# django-narito-blog1
ブログ

## 動作環境
Django2.2以上

## 使い方
インストールする。

```python
pip install https://github.com/naritotakizawa/django-narito-blog1/archive/master.tar.gz
```

`settings.py`に追加する。

```python
INSTALLED_APPS = [
    'nblog1.apps.Nblog1Config',  # これ
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # これ
    'django.contrib.sitemaps',  # これ
    'django.contrib.humanize',  # これ
]
```

```python
# アップロードファイルの設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# サイトマップフレームワークで使う変数です。
SITE_ID = 1

# マークダウンの拡張
MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.toc',
]

# メールをコンソールに表示する。
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

USE_LINE_BOT = False

USE_WEB_PUSH = False

LOGIN_URL = 'admin:index'
```

`urls.py`に追加する。

```python
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nblog1.urls')),
]


# 開発環境でのメディアファイルの配信設定
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
```


マイグレートやスーパーユーザーを作成する。

```
python manage.py migrate
python manage.py createsuperuser
```

`nblog1/base_site.html`を上書きすることで、ブログ内のタイトル等の情報を上書きできます。例えば、次のように上書きします。

```html
{% extends 'nblog1/base.html' %}

{% block meta_title %}Narito Blog{% endblock %}
{% block meta_description %}Python/Djangoを中心に、プログラミングのメモや備忘録、チュートリアルを書いています。{% endblock %}
{% block meta_keywords %}Python,Django,プログラミング,ブログ{% endblock %}

{% block copyright %}© 2019 Narito Takizawa.{% endblock %}
{% block link %}
    <li><a href="https://twitter.com/toritoritorina/" target="_blank">Twitter</a></li>
    <li><a href="https://github.com/naritotakizawa/" target="_blank">Github</a></li>
    <li><a href="https://narito.ninja/diaries/" target="_blank">日記</a></li>
    <li><a href="https://narito.ninja/" target="_blank">ポートフォリオ</a></li>
    <li>
        <a href="http://www.amazon.co.jp/registry/wishlist/2ZCE9KHVM7FRA/ref=cm_sw_r_tw_ws_f.aTzbDCX47K6" target="_blank">欲しいもの</a>
    </li>
    <li><a href="mailto:toritoritorina@gmail.com" target="_blank">メール</a></li>
    <li><a href="https://github.com/naritotakizawa/django-narito-blog1/" target="_blank">ソースコード</a></li>
{% endblock %}

{% block extrahead %}
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-72333380-3"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
    
        function gtag() {
            dataLayer.push(arguments);
        }
    
        gtag('js', new Date());
    
        gtag('config', 'UA-72333380-3');
    </script>

    <!-- Google Ads -->
    <script data-ad-client="ca-pub-5235456993770661" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
{% endblock %}
```

## メール通知機能

購読やブログのコメントお知らせの際、メールの送信処理が使われます。デフォルトでは、メールはコンソールに表示されるだけです。実際にメールを送信するには、設定をする必要があります。

Gmailならば、例えば次のような設定をsettings.pyに記述してください。
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # console.EmailBackendを取り消す。
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_mail@gmail.com'  # あなたのアカウント
EMAIL_HOST_PASSWORD = 'your_app_pasword'  # 2段階認証のアプリパスワードが確実
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'your_mail@gmail.com'  # あなたのメールアドレス(Gmailなら、EMAIL_HOST_USERと同じになる)
```

## LINE通知機能
**HTTPS**のウェブサイトでないと、この機能は利用できません。

LINE BOT用のライブラリをインストールします。
```
pip install line-bot-sdk
```

LINE通知を行う場合は、ラインBOTのアカウントを作成する必要があります。ディベロッパーサイトで、登録をしてください。

また、urls.pyにてコールバック用ビュー(nblog1.views.line_callback)も読み込ませる必要があります。そのビューのURLを、linebotアカウントのコールバックURLに指定してください。
```python
path('dwnnwjknwk/line/callback/', views.line_callback, name='line_callback'),
```

そして、`settings.py`に次のように設定して終わりです。
```python
USE_LINE_BOT = True
LINE_BOT_API_KEY = 'キー'
```

## ブラウザ通知機能
**HTTPS**のウェブサイトでないと、この機能は利用できません。

必要なライブラリをインストールします。
```
pip install requests
```

ブラウザ通知はOneSignalを利用しています。サイトで登録をしてください。

また、OneSignalで作成されるmanifest.jsonやjsファイルを、Webサーバーのドキュメントルート直下に配置してください。ブログアプリケーションでは、それらを`<link rel="manifest" href="/manifest.json"/>`といった感じで読み込みます。

Nginxを利用している場合、例えば次のように設定します。
```
server {
...
...
    location /manifest.json {
        alias /usr/share/nginx/html/manifest.json;
    }
    location /OneSignalSDKWorker.js {
        alias /usr/share/nginx/html/OneSignalSDKWorker.js;
    }
    location /OneSignalSDKUpdaterWorker.js {
        alias /usr/share/nginx/html/OneSignalSDKUpdaterWorker.js;
    }

...
...

}
```

最後に、settings.pyにて次のように書きます。
```python
USER_WEB_PUSH = True
ONE_SIGNAL_REST_KEY = 'Basic キー'
ONE_SIGNAL_APP_ID = 'キー'
```
