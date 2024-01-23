# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     consumers
   Description :
   Author :       MichaelYoung
   date：          2024/1/19
-------------------------------------------------
   Change Activity:
                   2024/1/19:
-------------------------------------------------
"""
import json
import time

from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        for i in range(0, 10):
            time.sleep(1)
            self.send(text_data=json.dumps({"message": i}))

class StartConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive_json(self, content, **kwargs):
        for i in range(0,10):
            self.send_json({"hello":"world"})
