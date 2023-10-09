# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     caculate_comunication_overhead
   Description :
   Author :       MichaelYoung
   date：          2023/9/21
-------------------------------------------------
   Change Activity:
                   2023/9/21:
-------------------------------------------------
"""
import json


class CalculateCommunicateOverhead:
    def read_file(self, file_path, file_name):
        data = {"detail": {}}
        with open(f"{file_path}/{file_name}", "r") as file:
            detail_content = ""
            for line in file.readlines():
                if ("active_app" in line) and ("percentage" in line) and ("percentage" in line):
                    if len(detail_content) > 100:
                        detail_json = json.loads(detail_content)
                        data["detail"].update({f"{percentage}%": detail_json})
                        detail_content = ""
                    line = line.replace("\n", "")
                    active_app = line.split(",")[0].split(":")[1].strip()
                    percentage = line.split(",")[1].split(":")[1].strip()
                    base_size = line.split(",")[2].split(":")[1].strip()
                    data.update({"active_app": active_app, "base_size": base_size})
                else:
                    detail_content += line
            if len(detail_content) > 100:
                detail_json = json.loads(detail_content)
                data["detail"].update({f"{percentage}%": detail_json})
                detail_content = ""
        return data

    def get_communicate_overhead(self, data, count_key):
        overhead = {}
        for key, value in data["detail"].items():
            recv_size, send_size = 0, 0
            for metric in list(value["agent_metrics"].values()):
                recv_size += metric["rpdp_app"][count_key]["recv"]["size"] * 8
                send_size += metric["rpdp_app"][count_key]["send"]["size"] * 8
            overhead.update({key: {"recv_size": recv_size, "send_size": send_size}})
        return overhead



    def run(self):
        file_path = "/root/sav_simulate/savop_back/data/NSDI/analyze"
        file_name = "exp_result_rpdp_dsav_stable_time.txt"
        if "dsav" in file_name:
            count_key = "modified_bgp"
        if "grpc" in file_name:
            count_key = "grpc"
        data = self.read_file(file_path=file_path, file_name=file_name)
        over_head = self.get_communicate_overhead(data=data, count_key=count_key)
        print(f"{file_name}:")
        for key, value in over_head.items():
            print(key, f"recv_size: {value['recv_size']}", f"send_size: {value['send_size']}")


        file_name = "exp_result_rpdp_grpc_stable_time_not_finish.txt"
        if "dsav" in file_name:
            count_key = "modified_bgp"
        if "grpc" in file_name:
            count_key = "grpc"
        data = self.read_file(file_path=file_path, file_name=file_name)
        over_head = self.get_communicate_overhead(data=data, count_key=count_key)
        print(f"{file_name}:")
        for key, value in over_head.items():
            print(key, f"recv_size: {value['recv_size']}", f"send_size: {value['send_size']}")


if __name__ == '__main__':
    calculator = CalculateCommunicateOverhead()
    calculator.run()