from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from mainApp.consumers import ChatConsumer

websockets = URLRouter([
    path(
        "ws/notifications/",
        ChatConsumer,
        name="ws_notifications",
    ),
])


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": AuthMiddlewareStack(websockets),
})