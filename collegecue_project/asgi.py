"""
ASGI config for collegecue_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import job_portal.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collegecue_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            job_portal.routing.websocket_urlpatterns
        )
    ),
}) 

application = get_asgi_application()
