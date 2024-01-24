# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     routing
   Description :
   Author :       MichaelYoung
   date：          2024/1/19
-------------------------------------------------
   Change Activity:
                   2024/1/19:
-------------------------------------------------
"""
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/control/$", consumers.ControlConsumer.as_asgi())
]