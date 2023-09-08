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

    def observe_experiment(self, command_scope_list, group, signal_):
        print(f"观察第{str(group)}组{signal_}%的实验室结果:")
        with open('/root/sav_simulate/sav-start/build/signal/signal.txt', 'r') as f:
            signal = json.load(f)
        source = signal["source"]
        all_result = []
        for as_number in command_scope_list:
            if (int(as_number) in [701, 3491, 6461, 6453, 1239, 5511, 6762, 2914, 3257, 7018, 174, 1299, 209, 3356]) and (source in ["EFP-uRPF-Algorithm-A_app", "EFP-uRPF-Algorithm-B_app"]):
                continue
            if int(as_number) in [9607, 33891, 16735, 209]:
                continue
            print(f"AS-{as_number}")
            with open(f"{self.RUN_LOG_PATH}/{as_number}/signal_execute_status.txt", "r") as f:
                signal_execute_status = json.load(f)
            print(signal_execute_status)
            result = {"command": signal_execute_status["command"],
                      "judge_stable_time": signal_execute_status["judge_stable_time"],
                      "sav_convergence_duration": signal_execute_status["convergence_duration"],
                      "fib_convergence_duration": signal_execute_status["fib_convergence_duration"],
                      "sav_rule_number": signal_execute_status["pre_sav_rule_number"]}
            print(result)
            all_result.append({f"AS-{as_number}": result})
            mkdir_command = f'mkdir -p {self.OUT_PATH}/{source}/{group}/{signal_}/{as_number}'
            result = subprocess.run(mkdir_command, shell=True, capture_output=True, encoding='utf-8')
            mv_command = f'cp {self.RUN_LOG_PATH}/{as_number}/signal_execute_status.txt {self.OUT_PATH}/{source}/{group}/{signal_}/{as_number}/'
            result = subprocess.run(mv_command, shell=True, capture_output=True, encoding='utf-8')
        return all_result

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
        all_result = self.observe_experiment(command_scope_list=command_scope_list, group=group, signal_=signal)
        sav_convergence_duration, fib_convergence_duration, sav_rule_number = 0, 0, 0
        for result in all_result:
            sav_rule_number += list(result.values())[0]["sav_rule_number"]
            if list(result.values())[0]["sav_convergence_duration"] > sav_convergence_duration:
                sav_convergence_duration = list(result.values())[0]["sav_convergence_duration"]
            if list(result.values())[0]["fib_convergence_duration"] > fib_convergence_duration:
                fib_convergence_duration = list(result.values())[0]["fib_convergence_duration"]
        print(f"sav_convergence_duration: {sav_convergence_duration}\n "
              f"fib_convergence_duration: {fib_convergence_duration}\n"
              f" sav_rule_number: {sav_rule_number}\n")


if __name__ == "__main__":
    collect_data = CollectData()
    # collect_data.parse_signal(signal="signal_10")
    # 监控实验实时情况的代码片段
    turn = True
    while turn:
        try:
            collect_data.run(group=1, signal="signal_90")
            turn = False
            break
        except Exception as e:
            print(e)
            time.sleep(2)
    # CollectData().replenish_signal_15_FIB_convergence_duration()
    # # 补充singal_15的FIB表收敛时间的代码片段


