# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     collect_expermental_data
   Description :
   Author :       MichaelYoung
   date：          2023/8/28
-------------------------------------------------
   Change Activity:
                   2023/8/28:
-------------------------------------------------
"""
import json
import subprocess
import time


class CollectData:
    SINGANL_PATH = "/root/sav_simulate/savop_back/data/NSDI/signal"
    RUN_LOG_PATH = "/root/sav_simulate/sav-start/build/logs"
    OUT_PATH = "/root/sav_simulate/savop_back/data/NSDI/result"

    def parse_signal(self, signal):
        with open(f"{self.SINGANL_PATH}/{signal}.txt", "r") as f:
            signal_json = json.load(f)
        command_scope_list = signal_json["command_scope"].split(",")
        return command_scope_list

    def observe_experiment(self, command_scope_list, group, signal):
        print(f"观察第{str(group)}组{signal}的实验室结果:")
        for as_number in command_scope_list:
            print(f"AS-{as_number}")
            # if as_number == "3356":
            #     continue
            with open(f"{self.RUN_LOG_PATH}/{as_number}/signal_execute_status.txt", "r") as f:
                signal_execute_status = json.load(f)
            print(signal_execute_status)
            result = {"command": signal_execute_status["command"],
                      "judge_stable_time": signal_execute_status["judge_stable_time"],
                      "convergence_duration": signal_execute_status["convergence_duration"]}
            print(result)
            mkdir_command = f'mkdir -p {self.OUT_PATH}/{str(group)}/{signal}/{as_number}'
            result = subprocess.run(mkdir_command, shell=True, capture_output=True, encoding='utf-8')
            mv_command = f'cp {self.RUN_LOG_PATH}/{as_number}/signal_execute_status.txt {self.OUT_PATH}/{group}/{signal}/{as_number}/'
            result = subprocess.run(mv_command, shell=True, capture_output=True, encoding='utf-8')
            print(result.returncode)

    def run(self, group, signal):
        command_scope_list = self.parse_signal(signal=signal)
        command_scope_list.reverse()
        self.observe_experiment(command_scope_list=command_scope_list, group=group, signal=signal)


if __name__ == "__main__":
    collect_data = CollectData()
    # collect_data.parse_signal(signal="signal_10")
    turn = True
    while turn:
        try:
            collect_data.run(group=1, signal="signal_15")
            turn = False
            break
        except Exception as e:
            print(e)
            time.sleep(2)

