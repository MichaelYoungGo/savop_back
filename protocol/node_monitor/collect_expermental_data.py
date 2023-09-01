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
import os
import subprocess
import time
import datetime


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
        all_result = []
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
            all_result.append({f"AS-{as_number}": result["convergence_duration"]})
            mkdir_command = f'mkdir -p {self.OUT_PATH}/{str(group)}/{signal}/{as_number}'
            result = subprocess.run(mkdir_command, shell=True, capture_output=True, encoding='utf-8')
            mv_command = f'cp {self.RUN_LOG_PATH}/{as_number}/signal_execute_status.txt {self.OUT_PATH}/{group}/{signal}/{as_number}/'
            result = subprocess.run(mv_command, shell=True, capture_output=True, encoding='utf-8')
            print(result.returncode)
        print(all_result)

    def replenish_signal_15_FIB_convergence_duration(self):
        directory = "/root/sav_simulate/savop_back/data/NSDI/result/1/signal_15"
        as_list = []
        with os.scandir(directory) as entries:
            for entry in entries:
                as_list.append(entry.name)
        for as_num in as_list:
            with open(f"{directory}/{as_num}/signal_execute_status.txt") as f:
                signal_execute_status = json.load(f)
            sav_start_time = signal_execute_status["sav_start"]
            server_log_path = f"/root/sav_simulate/sav-start/build/logs/{as_num}/server.log"
            grep_command = subprocess.run(f'grep "FIB STABILIZED" {server_log_path} |awk -F "  " \'{{ print $1 }}\' | head -n 1', shell=True, capture_output=True, encoding='utf-8')
            if grep_command.returncode != 0:
                raise
            fib_convergence_time = grep_command.stdout.replace("\n", "")[1:-1]
            fib_convergence_timestamp = int(time.mktime(time.strptime(fib_convergence_time, "%Y-%m-%d %H:%M:%S,%f")))
            fib_convergence_duration = fib_convergence_timestamp - sav_start_time + 8 * 60 * 60
            signal_execute_status.update({"fib_convergence_duration": fib_convergence_duration})
            print(signal_execute_status)
            with open(f"{directory}/{as_num}/signal_execute_status.txt", "w") as json_file:
                json.dump(signal_execute_status, json_file)
        print("over!!!")

    def run(self, group, signal):
        command_scope_list = self.parse_signal(signal=signal)
        command_scope_list.reverse()
        self.observe_experiment(command_scope_list=command_scope_list, group=group, signal=signal)


if __name__ == "__main__":
    collect_data = CollectData()
    # collect_data.parse_signal(signal="signal_10")
    # 监控实验实时情况的代码片段
    turn = True
    while turn:
        try:
            collect_data.run(group=1, signal="signal_100")
            turn = False
            break
        except Exception as e:
            print(e)
            time.sleep(2)
    # CollectData().replenish_signal_15_FIB_convergence_duration()
    # # 补充singal_15的FIB表收敛时间的代码片段


