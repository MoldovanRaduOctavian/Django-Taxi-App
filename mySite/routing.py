"""
ASGI config for mySite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

import myApp.routing

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(myApp.routing.websocket_urlpatterns))
        ),
})