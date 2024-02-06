# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     asgi
   Description :
   Author :       MichaelYoung
   date：          2024/1/19
-------------------------------------------------
   Change Activity:
                   2024/1/19:
-------------------------------------------------
"""
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from protocol.master_controller.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'protocol.settings.protocol')



django_asgi_app  = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
    # Just HTTP for now. (We can add other protocols later.)
})