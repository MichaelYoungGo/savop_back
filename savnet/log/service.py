import os
import subprocess
from django.forms import model_to_dict
from constants.error_code import ErrorCode
from savnet.log.models import FPath

NAME_MAPPING = { 1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H", 9: "I"}

def test():
    asn_path = FPath.objects.values('fp_id', 'dst_prefix', 'asn_path')
    resp_data = {
        'ASN_Path': asn_path,
    }
    return resp_data

class SavnetContrller:
    def start(self):
        pass
    def refresh(slef):
        pass
    @staticmethod
    def get_log_data(path="/root/savnet_bird/logs", file_name = "server.log"):
        subdirs = [os.path.join(path, o) for o in os.listdir(path) if os.path.isdir(os.path.join(path,o))]
        info = []
        for subdir_i in subdirs:
            with open(os.path.join(subdir_i, file_name), mode="r") as f:
                lines = f.readlines()
                for line in lines:
                    if "[INFO]" not in line:
                        continue
                    info.append(line)
                    print(line)
        return "aaa"
    
    def get_routers_info(path="/root/savnet_bird/configs"):
        file_name_list = os.listdir(path)
        file_num = len(file_name_list)
        routers_info = []
        for i in range(1, int(file_num/2)+1):
            info = { "route_id": i, "route_name": NAME_MAPPING.get(i)}
            file_conf_name, file_json_name = str(i) + ".conf", str(i) + ".json"
            with open(os.path.join(path, file_conf_name), mode="r") as f:
                lines = f.readlines()
                for li in lines:
                    if "router id" not in li:
                        continue
                    router_NO = li.split(" ")[-1].split(";")[0]
            info.update({"router_NO": router_NO})
            # the files of *.json have no useful information temporarity, maybe have after
            with open(os.path.join(path, file_json_name), mode="r") as f:
                lines = f.readlines()
            routers_info.append(info)
        return {"routers_info": routers_info}
    
    def get_links_info(file="/root/savnet_bird/run.sh"):
        command = "cat {0}|grep funCreateV|grep -v '()'".format(file)
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        return_code, std_out = command_result.returncode, command_result.stdout
        link_funcs = std_out.split("\n")[:-1]
        links_info = []
        for link in link_funcs:
            info = {}
            link_info_list = link.split(" ")[1:]
            src_router = link_info_list[0][1:-1]
            dst_router = link_info_list[1][1:-1]
            src_router_inf = link_info_list[0][1:-1] + "_" + link_info_list[1][1:-1]
            dst_router_inf = link_info_list[1][1:-1] + "_" + link_info_list[0][1:-1]
            info.update({"src_router": src_router, "dst_router": dst_router, "src_router_inf": src_router_inf, "dst_router_inf": dst_router_inf})
            links_info.append(info)
        return {"links_info": links_info}
    
    def get_prefixs_info(path="/root/savnet_bird/configs"):
        file_name_list = os.listdir(path)
        file_num = len(file_name_list)
        prefixs_info = []
        for i in range(1, int(file_num/2)+1):
            info = { "route_id": i, "route_name": NAME_MAPPING.get(i)}
            file_conf_name, file_json_name = str(i) + ".conf", str(i) + ".json"
            # *.conf
            command = "cat %s |grep blackhole| awk '{ print $2 }'" % (os.path.join(path, file_conf_name))
            command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
            return_code, std_out = command_result.returncode, command_result.stdout
            prefix_info_list = std_out.split("\n")[:-1]
            for pre in prefix_info_list:
                info.update({"prefix_name": pre})
                prefixs_info.append(info)
            # the files of *.json have no useful information temporarity, maybe have after
            with open(os.path.join(path, file_json_name), mode="r") as f:
                lines = f.readlines()
        return {"prefixs_info": prefixs_info}



