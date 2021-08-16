"""
ASGI config for new_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.ws_gateway import routing

protocol_router = {
        # Explicitly set 'http' key using Django's ASGI application.
        "http"     : django_asgi_app,  # django 3.1 使用 异步视图,如果代码是使用同步的,要设置, 性能太差
        "websocket": AuthMiddlewareStack(
                URLRouter(
                        routing.websocket_urlpatterns
                )
        ),
}

if django.__version__ > '3.1':
    protocol_router.pop('http', None)

application = ProtocolTypeRouter(protocol_router)
