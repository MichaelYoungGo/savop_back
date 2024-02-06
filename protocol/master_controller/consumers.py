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
import os
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from constants.error_code import ErrorCode
from protocol.utils.command import command_executor_with_popen
from constants.common_variable import SAV_ROOT_DIR



class SavControlMaster:
    def config(self):
        return {"action": "执行配置类命令"}

    def operate(self):
        return {"action": "执行操作命令"}

    def monitor(self):
        return {"action": "执行监控类命令"}

    def experiment(self, mode_name):
        cmd = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py -e {mode_name}"
        process = command_executor_with_popen(command=cmd)
        return process
        return {"action": f"Run {mode_name} with One Click"}


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

class ControlConsumer(JsonWebsocketConsumer):
    sav_control_master = SavControlMaster()
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive_json(self, content, **kwargs):
        if content.get("action", None) is None:
            self.send_json({"code": ErrorCode.E_PARAM_ERROR, "message":"action parameter lack"})
            self.close(code=ErrorCode.E_PARAM_ERROR)
        if content.get("mode_name", None) is None:
            self.send_json({"code": ErrorCode.E_PARAM_ERROR, "message":"testing_v4_inter parameter lack"})
            self.close(code=ErrorCode.E_PARAM_ERROR)
        action, mode_name = content.get("action"), content.get("mode_name")
        if action not in  ["config", "operate", "monitor", "experiment"]:
            self.send_json({"code": ErrorCode.E_PARAM_ERROR, "message":"action parameter must be one of  config, operate, monitor and experiment"})
            self.close(code=ErrorCode.E_PARAM_ERROR)
        match action:
            case "config":
                pass
            case "operate":
                pass
            case "monitor":
                pass
            case "experiment":
                process =  self.sav_control_master.experiment(mode_name=mode_name)
                for line in process.stdout:
                    self.send_json({"info": line})
                process.wait()
        self.close()