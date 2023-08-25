# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     monitor
   Description :  sav服务监控与控制程序， 主要用于监控网络收敛状态，控制协议重新启动（nsdi论文需要使用该功能）
   Author :       MichaelYoung
   date：          2023/8/22
-------------------------------------------------
   Change Activity:
                   2023/8/22:
-------------------------------------------------
"""
import time
import json


class Monitor:
    DATA_PATH = ""
    def check_signal_file(self):
        with open('file.json', 'r') as json_file:
            data = json.load(json_file)

    def modify_sav_config_file(self):
        pass

    def calculte_sav_convergence_time(self):
        pass

    def kill_server(self):
        pass

    def start_server(self):
        pass

    def run(self):
        # 循环，监控配置文件与sav数据库的转态
        while True:
            time.sleep(1)
            # 循环，监控配置文件与sav数据库的转态
            pass


if __name__ == "__main__":
    pass