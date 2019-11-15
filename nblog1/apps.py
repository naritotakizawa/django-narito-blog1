from django.apps import AppConfig


class Nblog1Config(AppConfig):
    name = 'nblog1'

    def ready(self):
        # シグナルのロード
        # デコレーターで登録しているので、signals.pyを読み込む必要があるため
        from . import signals
