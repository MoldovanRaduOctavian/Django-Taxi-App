from channels.routing import ProtocolTypeRouter, URLRouter
from . import consumers
from django.urls import re_path, path

websocket_urlpatterns = [
    re_path(r"myApp/appRider/$", consumers.ChatConsumer.as_asgi()),
]

