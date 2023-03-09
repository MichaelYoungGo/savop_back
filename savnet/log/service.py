import os
import subprocess
import json
import ast
import copy
from django.forms import model_to_dict
from constants.error_code import ErrorCode
from savnet.log.models import FPath
from netaddr import IPAddress

NAME_MAPPING = { 1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H", 9: "I"}

def test():
    asn_path = FPath.objects.values('fp_id', 'dst_prefix', 'asn_path')
    resp_data = {
        'ASN_Path': asn_path,
    }
    return resp_data

class SavnetContrller:
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
    
    def get_links_info(file="/root/savnet_bird/host_run.sh"):
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
                info_ = copy.deepcopy(info)
                info_.update({"prefix_name": pre})
                prefixs_info.append(info_)
            # the files of *.json have no useful information temporarity, maybe have after
            with open(os.path.join(path, file_json_name), mode="r") as f:
                lines = f.readlines()
        return {"prefixs_info": prefixs_info}


    def get_msg_data(path="/root/savnet_bird/logs", file_name = "server.log"):
        global msg_step
        msg_step = []
        #Depth First Search, DFS
        SavnetContrller.depth_first_search(path=path, file_name=file_name, entry="a", depth="0")
        # for step in msg_step:
        #     SavnetContrller.remove_redundant_variables(step)
        return {"msg_step": msg_step}


    def depth_first_search(path, file_name, entry, depth, msg_rx=None):
        if depth == "0":
            msg_list = SavnetContrller.get_orgin_send_msg(path, entry)
            length, start = len(msg_list), 0
            while start != length:
                msg = msg_list[start]
                eth_out = msg["link"][-1]
                depth = SavnetContrller.depth_auto_increm(depth)
                SavnetContrller.depth_first_search(path=path, file_name=file_name, entry=eth_out, depth = depth, msg_rx=msg)
                start = start + 1
        else:
            path_ = os.path.join(path, str(ord(entry)-ord("a") + 1))
            sav_scope_list = msg_rx.get("sav_scope")[0]
            sav_scope_str = "'"+sav_scope_list[0]+"'"
            if len(sav_scope_list) > 1:
                 for index in range(1, len(sav_scope_list)):
                     sav_scope_str =  sav_scope_str + ", '" + sav_scope_list[index] + "'"
            command = "grep INFO {}/server.log |grep -v -E 'SAV GRAPH LINK ADDED|SAV GRAPH|UPDATED LOCAL'|grep -A 2 -E \"GOT MSG ON.*'sav_origin': '{}'\"|grep -A 2  \"'sav_scope': \\\[\\\[{}\\\]\\\]\"".format(path_, msg_rx.get("sav_origin"), sav_scope_str)
            command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
            return_code, std_out, std_err = command_result.returncode, command_result.stdout, command_result.stderr
            msg_list = std_out.split("\n")[:-1]
            msg_list = [msg for msg in msg_list if len(msg) > 10]
            length, index = len(msg_list), 0
            while index < length:
                msg_str = msg_list[index]
                # if "GOT MSG ON" in msg_str:
                #     sav_scope = msg_rx.get("sav_scope")[0][0]
                #     start = msg_str.find("{")
                #     end = msg_str.find("}")
                #     msg = eval(msg_str[start: end + 1])
                if "SAV RULE ADDED" in msg_str:
                    start = msg_str.find("{")
                    end = msg_str.find("}")
                    msg = eval(msg_str[start: end + 1])
                    msg_rx.update({"msg_name": "msg_" + depth, "src_prefix": msg.get("prefix"), "income_interface": msg.get("interface")})
                    msg_step.append(msg_rx)
                if "SAV RULE EXISTS" in msg_str:
                    start = msg_str.find("{")
                    end = msg_str.find("}")
                    msg =  eval(msg_str[start: end + 1])
                    msg_rx.update({"msg_name": "msg_" + depth, "src_prefix": msg.get("prefix"), "income_interface": msg.get("interface")})
                    msg_step.append(msg_rx)
                if "TERMINATING" in msg_str:
                    send_off = False
                if "SENT MSG ON LINK" in msg_str:
                    start = msg_str.find("{")
                    end = msg_str.find("}")
                    msg = eval(msg_str[start: end + 1])
                    eth_out = msg.get("protocol_name")[-1] 
                    SavnetContrller.depth_first_search(path=path, file_name=file_name, entry=eth_out,depth = depth+".1", msg_rx=msg)
                    depth = SavnetContrller.depth_auto_increm(depth)
                    send_off = False
                index = index + 1

    def depth_auto_increm(depth_str):
        depth_list = depth_str.split(".")
        if len(depth_list) == 1:
            return str(int(depth_list[-1]) + 1)
        else:
            print(depth_str)
            depth_list[-1] = str(int(depth_list[-1]) + 1)
            result = depth_list[0]
            for index in range(1, len(depth_list)):
                result = result + "." + depth_list[index]
            return result
    
    def get_orgin_send_msg(path, entry):
        msg_list = []
        command =  "grep INFO {}/server.log|grep '\[send_msg\]'|grep \"'msg_type': 'origin'\"".format(os.path.join(path, str(ord(entry)-ord("a") + 1)))
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        return_code, std_out = command_result.returncode, command_result.stdout
        send_msg_list = std_out.split("\n")[:-1]
        for msg_str in send_msg_list:
        # get next router
            start = msg_str.find("SENT MSG ON LINK")
            link = msg_str[start+18: start+27]
            # get msg
            start = msg_str.find("{")
            end = msg_str.find("}")
            test = msg_str[start: end + 1]
            msg = eval(msg_str[start: end + 1])
            msg.update({"link": link})
            msg_list.append(msg)
        return msg_list
    
    def remove_redundant_variables(msg_rx):
        msg_rx.pop("as4_session")
        msg_rx.pop("is_interior")
        msg_rx.pop("link")
        msg_rx.pop("protocol_name")
        return msg_rx