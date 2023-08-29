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
import subprocess
from datetime import datetime
import sqlite3


class Monitor:
    DATA_PATH = "/root/savop"

    def _command_executor(self, command):
        result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        # result = subprocess.run("ls /root/", shell=True, capture_output=True, encoding='utf-8')
        return result.returncode

    def _get_current_datatime_str(self):
        current_datetime = datetime.now()
        return current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def _get_sav_rule_number(self):
        conn = sqlite3.connect('/root/savop/sav-agent/data/sib.sqlite')
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM STB"
        cursor.execute(query)
        results = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return results

    def check_signal_file(self, path):
        # 根据signal.txt, signal_excute_status.txt, sav_agent_config判断下一步路由器的执行动作
        # 执行动作有：start, restart, stop, keep
        try:
            with open(f'{self.DATA_PATH}/signal/signal.txt', 'r') as f:
                signal = json.load(f)
        except Exception as e:
            signal = {}
        time.sleep(0.5)
        try:
            with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', 'r') as f_s:
                signal_excute_status = json.load(f_s)
        except Exception as e:
            print(e)
            print(f"signal_execute_status cannot open!!{path}/logs/signal_execute_status.txt")
            signal_excute_status = {}
        try:
            with open(f'/root/savop/SavAgent_config.json', 'r') as f:
                sav_agent_config = json.load(f)
        except Exception as e:
            sav_agent_config = {}
        if not signal:
            return "null"
        command = signal["command"]
        command_timestamp = signal["command_timestamp"]
        command_scope = [int(value) for value in signal["command_scope"].split(",")]
        local_as = sav_agent_config["local_as"]
        pre_command = signal_excute_status.get("command", "")
        if command == "stop":
            if command not in pre_command:
                action = "stop"
            elif (command in pre_command) and (command_timestamp in pre_command):
                action = "keep"
            elif (command in pre_command) and (command_timestamp not in pre_command):
                action = "stop"
            else:
                raise "未知的路由状态"
        elif command == "start":
            if (command in pre_command) and (command_timestamp in pre_command) and (local_as in command_scope):
                action = "keep"
            elif (command_timestamp not in pre_command) and (local_as in command_scope):
                print(f"80_{int(time.time())}_start_reason_{command_timestamp}_precommand_{pre_command}")
                print(signal_excute_status)
                action = "start"
                signal_excute_status = {}
            elif (command not in pre_command) and (local_as in command_scope):
                print(f"84_{int(time.time())}_start_reason_{command}")
                action = "start"
                signal_excute_status = {}
            elif (command_timestamp not in pre_command) and (local_as not in command_scope):
                action = "stop"
            elif (command_timestamp in pre_command) and (local_as not in command_scope):
                action = "keep"
            else:
                raise "未知的路由转态"
        else:
            raise "非法的控制命令"
        # 判断该节点是监控结点还是非监控结点
        if local_as in command_scope:
            signal_excute_status.update({"monitor_node": True})
        else:
            signal_excute_status.update({"monitor_node": False})
        with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', "w") as json_file:
            json.dump(signal_excute_status, json_file)
        return action

    def modify_sav_config_file(self):
        # 预留函数，防止将来测试不同的机制的sav协议，此时修改配置文件
        pass

    def monitor_sav_convergence(self):
        # 功能：监控sav-agent与bird的状态，并计算sav_rule的收敛时间
        # 根据monitor_node字段判断是否为监控结点，非监控结点不需要打开监控功能
        # 根据字段action, execute_result来判断sav协议机制已经开始
        # 根据pre_sav_rule_number, current_sav_rule_number, statble_number来判断sav是否收敛
        # 根据stable_number==0和stable_time确定已经收敛无效继续监控
        with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', 'r') as f:
            signal_excute_status = json.load(f)
        if signal_excute_status["monitor_node"] is False:
            return
        if "stable_number" in list(signal_excute_status.keys()) and ("judge_stable_time" in list(signal_excute_status.keys())):
            # sav已经稳定，不需要继续监控
            if signal_excute_status["stable_number"] == 0:
                return
        if (signal_excute_status["action"] == "start") and (signal_excute_status["execute_result"] == "ok"):
            # 对sav_rule进行监控，根据pre_sav_rule_number和current_sav_rule_number一致，则statble_number减1；为0时，稳定，记录时间
            # 出现十次sav_rule条数稳定，则判定sav机制已经收敛
            if signal_excute_status.get("stable_number", 11) == 11:
                signal_excute_status.update({"pre_sav_rule_number": self._get_sav_rule_number()})
                signal_excute_status.update({"monitor_cycle_start_time": int(time.time())})
                signal_excute_status["stable_number"] = signal_excute_status["stable_number"] - 1
            else:
                current_sav_rule_number = self._get_sav_rule_number()
                if current_sav_rule_number == signal_excute_status["pre_sav_rule_number"]:
                    if current_sav_rule_number != 0:
                        signal_excute_status["stable_number"] = signal_excute_status["stable_number"] - 1
                    if signal_excute_status["stable_number"] == 0:
                        signal_excute_status["judge_stable_time"] = self._get_current_datatime_str()
                        signal_excute_status["convergence_duration"] = signal_excute_status["monitor_cycle_start_time"] - signal_excute_status["sav_start"]
                else:
                    signal_excute_status.update({"stable_number": 10})
                    signal_excute_status.update({"pre_sav_rule_number": current_sav_rule_number})
                    signal_excute_status.update({"monitor_cycle_start_time": int(time.time())})
            with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', "w") as json_file:
                json.dump(signal_excute_status, json_file)

    def stop_server(self, action):
        print("停止路由器")
        with open(f'{self.DATA_PATH}/signal/signal.txt', 'r') as f:
            signal = json.load(f)
        signal_excute_status = {}
        signal_excute_status.update({"command": f'{signal["command"]}_{signal["command_timestamp"]}',
                                     "execute_start_time": f"{self._get_current_datatime_str()}",
                                     "action": action})
        result = self._command_executor("bash /root/savop/router_kill_and_start.sh stop")
        if result == 0:
            signal_excute_status.update({"execute_end_time": f"{self._get_current_datatime_str()}",
                                         "execute_result": "ok"})
        else:
            signal_excute_status.update({"execute_end_time": f"{self._get_current_datatime_str()}",
                                         "execute_result": "fail"})
        with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', "w") as json_file:
            json.dump(signal_excute_status, json_file)

    def start_server(self, action):
        print("启动路由器")
        with open(f'{self.DATA_PATH}/signal/signal.txt', 'r') as f:
            signal = json.load(f)
        with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', 'r') as f:
            signal_excute_status = json.load(f)
        signal_excute_status.update({"command": f'{signal["command"]}_{signal["command_timestamp"]}',
                                     "execute_start_time": f"{self._get_current_datatime_str()}",
                                     "action": action})
        result = self._command_executor("bash /root/savop/router_kill_and_start.sh start")
        if result == 0:
            signal_excute_status.update({"execute_end_time": f"{self._get_current_datatime_str()}",
                                         "execute_result": "ok", "sav_start": int(time.time()),
                                         "stable_number": 11
                                         })
        else:
            signal_excute_status.update({"execute_end_time": f"{self._get_current_datatime_str()}",
                                         "execute_result": "fail"})
        with open(f'{self.DATA_PATH}/logs/signal_execute_status.txt', "w") as json_file:
            json.dump(signal_excute_status, json_file)

    def run(self):
        # 循环，监控配置文件与sav数据库的转态
        while True:
            time.sleep(1)
            action = self.check_signal_file(self.DATA_PATH)
            # 循环，监控配置文件与sav数据库的转态
            if action == "start":
                self.start_server(action=action)
            elif action == "stop":
                self.stop_server(action=action)
            elif action == "keep":
                self.monitor_sav_convergence()
            elif action == "null":
                print("没有控制信号")
                pass
            else:
                raise


if __name__ == "__main__":
    sav_monitor = Monitor()
    sav_monitor.run()
