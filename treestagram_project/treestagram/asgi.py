import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treestagram.settings")

# This must come before any Django/channels imports
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# Only import channels/routing AFTER Django is initialized
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})