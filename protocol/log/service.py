import os
import subprocess
import json
import ast
import copy
from django.forms import model_to_dict
from constants.error_code import ErrorCode
from protocol.log.models import FPath
from netaddr import IPAddress

DEFAULT_PROJECT_DIR = "/root/savop/"
NAME_MAPPING = { 1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H", 9: "I", 10: "J", 11: "K"}

def test():
    asn_path = FPath.objects.values('fp_id', 'dst_prefix', 'asn_path')
    resp_data = {
        'ASN_Path': asn_path,
    }
    return resp_data


class RouterContrller:
    def get_routers_info(project_direct=DEFAULT_PROJECT_DIR):
        path=project_direct + "configs"
        file_name_list = os.listdir(path)
        file_num = len(file_name_list)
        routers_info = []
        as_info_list = []
        routers_tables = []
        for i in range(1, int(file_num/2)+1):
            info = { "route_id": str(i), "route_name": NAME_MAPPING.get(i)}
            as_info = {"route_id": str(i), "route_name": NAME_MAPPING.get(i)}
            file_conf_name, file_json_name = str(i) + ".conf", str(i) + ".json"
            with open(os.path.join(path, file_conf_name), mode="r") as f:
                lines = f.readlines()
                for li in lines:
                    if "router id" not in li:
                        continue
                    router_NO = li.split(" ")[-1].split(";")[0]
            info.update({"router_NO": router_NO})
            # router_table
            router_table = []
            command = "cat {}logs/{}/router_table.txt".format(project_direct,str(i))
            command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
            return_code, std_out = command_result.returncode, command_result.stdout
            try:
                router_table_list = std_out.split("\n")[1:-1]
                clum_name_list = [ i for i in router_table_list[0].split(" ") if i !=""]
                clum_list_length = len(clum_name_list)
                for router_info in router_table_list[1:]:
                    clum = {}
                    clum_content = [ i for i in router_info.split(" ") if i !="" ]
                    for index in range(0, clum_list_length):
                        clum.update({clum_name_list[index]: clum_content[index]})
                    router_table.append(clum)
            except:
                pass
            info.update({"router_table": router_table})
            #sav_table
            sav_table = []
            with open(os.path.join(project_direct+"logs/"+str(i), "sav_table.txt"), mode="r") as f:
                lines = f.readlines()
                content = ""
                for l in lines:
                    content = content + l
                try:
                    sav_table = json.loads(content)
                except:
                    pass
            info.update({"sav_table": sav_table})
            # PREFIX-AS_PATH
            prefix_as_path = []
            command = 'grep "UPDATED LOCAL PREFIX-AS_PATH TABLE" {}logs/{}/server.log | head -n 1'.format(project_direct,str(i))
            command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
            return_code, std_out = command_result.returncode, command_result.stdout
            start = std_out.find("{")
            print(command)
            prefix_as_path_table = eval(std_out[start:].replace("IPNetwork(", "").replace(")", ""))
            for prefix, value in prefix_as_path_table.items():
                value.update({"prefix": prefix})
                prefix_as_path.append(value)
            info.update({"prefix_as_path_table": prefix_as_path})

            with open(os.path.join(path, file_conf_name), mode="r") as f:
                lines = f.readlines()
                for li in lines:
                    if "local as" not in li:
                        continue
                    AS_number = li.split(" ")[-1].split(";")[0]
            as_info.update({"AS_number": AS_number})
            # the files of *.json have no useful information temporarity, maybe have after
            with open(os.path.join(path, file_json_name), mode="r") as f:
                lines = f.readlines()
            routers_info.append(info)
            as_info_list.append(as_info)
        return {"routers_info": routers_info, "as_info": as_info_list}
    
    def get_links_info(project_direct=DEFAULT_PROJECT_DIR):
        file = project_direct + "host_run.sh"
        command = "cat {0}|grep funCreateV|grep -v '()'|grep -v '#'".format(file)
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        return_code, std_out = command_result.returncode, command_result.stdout
        link_funcs = std_out.split("\n")[:-1]
        links_info = []
        for link in link_funcs:
            info = {}
            link_info_list = link.split(" ")[1:]
            src_router = link_info_list[0][1:-1]
            dst_router = link_info_list[1][1:-1]
            src_router = NAME_MAPPING.get(ord(src_router) - ord("a") + 1)
            dst_router = NAME_MAPPING.get(ord(dst_router)- ord("a") + 1)
            src_router_inf = link_info_list[0][1:-1] + "_" + link_info_list[1][1:-1]
            dst_router_inf = link_info_list[1][1:-1] + "_" + link_info_list[0][1:-1]
            src_router_link_ip =  link_info_list[4][1:-1]
            dst_router_link_ip =  link_info_list[5][1:-1]
            info.update({"src_router": src_router, "dst_router": dst_router, "src_router_inf": src_router_inf, "dst_router_inf": dst_router_inf, 
                         "src_router_link_ip": src_router_link_ip, "dst_router_link_ip": dst_router_link_ip})
            links_info.append(info)
        return {"links_info": links_info}
    
    def get_prefixs_info(project_direct=DEFAULT_PROJECT_DIR):
        path = project_direct + "configs"
        file_name_list = os.listdir(path)
        file_num = len(file_name_list)
        prefixs_info = []
        for i in range(1, int(file_num/2)+1):
            info = { "route_id": str(i), "route_name": NAME_MAPPING.get(i)}
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

    def get_msg_data(project_direct=DEFAULT_PROJECT_DIR, file_name = "server.log"):
        path = project_direct + "logs"
        global msg_step
        msg_step = []
        #Depth First Search, DFS
        RouterContrller.depth_first_search(path=path, file_name=file_name, entry="a", depth="0")
        # for step in msg_step:
        #     RouterContrller.remove_redundant_variables(step)
        sorted(msg_step, key=lambda x: RouterContrller.sort_msg(x["msg_name"]))
        return {"msg_step": msg_step}

    def sort_msg(msg_name):
        return msg_name

    def depth_first_search(path, file_name, entry, depth, msg_rx=None):
        if depth == "0":
            msg_list = RouterContrller.get_orgin_send_msg(path, entry)
            length, start = len(msg_list), 0
            while start != length:
                msg = msg_list[start]
                eth_out = msg["link"][-1]
                depth = RouterContrller.depth_auto_increm(depth)
                RouterContrller.depth_first_search(path=path, file_name=file_name, entry=eth_out, depth = depth, msg_rx=msg)
                start = start + 1
        else:
            path_ = os.path.join(path, str(ord(entry)-ord("a") + 1))
            sav_scope_list = msg_rx.get("sav_scope")
            sav_scope_str = str(sav_scope_list)
            sav_scope_str= sav_scope_str.replace("[", '\\\[').replace("]", "\\\]")
            previous_protocol_name = msg_rx.get("protocol_name")
            protocol_name = "savbgp_" + previous_protocol_name[-1] + previous_protocol_name[-2]
            as_path_str = str(msg_rx.get("sav_path"))
            as_path_str = as_path_str.replace("[", '\\\[').replace("]", "\\\]")
            # command = "grep INFO {}/server.log|grep -v -E 'SAV GRAPH LINK ADDED|SAV GRAPH|UPDATED LOCAL'|grep -A 2 -E \"GOT MSG ON.*'protocol_name': '{}'.*'sav_origin': '{}'\"|grep -A 2  \"'sav_scope': {}\"".format(path_, protocol_name,msg_rx.get("sav_origin"), sav_scope_str)
            command = "grep INFO {}/server.log|grep -v -E 'SAV GRAPH LINK ADDED|SAV GRAPH|UPDATED LOCAL'|grep -A 6 -E \"GOT MSG ON.*'protocol_name': '{}'.*as_path': {}.*'sav_origin': '{}'\"|grep -A 6  \"'sav_scope': {}\"".format(path_, protocol_name,as_path_str, msg_rx.get("sav_origin"), sav_scope_str)
            command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
            return_code, std_out, std_err = command_result.returncode, command_result.stdout, command_result.stderr
            msg_list = std_out.split("\n")[:-1]
            msg_list = [msg for msg in msg_list if len(msg) > 10]
            length, index = len(msg_list), 0
            sned_msg_index = 0
            get_msg_add_on = True
            while index < length:
                msg_str = msg_list[index]
                if "GOT MSG ON" in msg_str:
                    start = msg_str.find("{")
                    end = msg_str.find("}")
                    msg = eval(msg_str[start: end + 1])
                    if get_msg_add_on:
                        msg_rx.update({"msg_name": "msg_" + depth, "src_prefix": msg.get("sav_nlri"), "income_interface": msg.get("interface_name")})
                        msg_step.append(msg_rx)
                        get_msg_add_on = False
                    else:
                        break
                # if "SAV RULE EXISTS" in msg_str:
                #     start = msg_str.find("{")
                #     end = msg_str.find("}")
                #     msg =  eval(msg_str[start: end + 1])
                #     msg_rx.update({"msg_name": "msg_" + depth, "src_prefix": msg.get("prefix"), "income_interface": msg.get("interface")})
                #     msg_step.append(msg_rx)
                if "TERMINATING" in msg_str:
                    send_off = False
                if "SENT MSG ON LINK" in msg_str:
                    sned_msg_index = sned_msg_index + 1
                    start = msg_str.find("{")
                    end = msg_str.find("}")
                    msg = eval(msg_str[start: end + 1])
                    eth_out = msg.get("protocol_name")[-1] 
                    RouterContrller.depth_first_search(path=path, file_name=file_name, entry=eth_out,depth = depth+f".{sned_msg_index}", msg_rx=msg)
                index = index + 1
            if sned_msg_index != 0:
                depth = RouterContrller.depth_auto_increm(depth)

    def depth_auto_increm(depth_str):
        depth_list = depth_str.split(".")
        if len(depth_list) == 1:
            return str(int(depth_list[-1]) + 1)
        else:
            depth_list[-1] = str(int(depth_list[-1]) + 1)
            result = depth_list[0]
            for index in range(1, len(depth_list)):
                result = result + "." + depth_list[index]
            return result
    
    def get_orgin_send_msg(path, entry):
        msg_list = []
        command =  "grep INFO {}/server.log|grep 'send_msg\]'|grep \"'msg_type': 'origin'\"".format(os.path.join(path, str(ord(entry)-ord("a") + 1)))
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
    
    def get_info_now(project_direct=DEFAULT_PROJECT_DIR):
        routers_info = RouterContrller.get_routers_info(project_direct)
        links_info = RouterContrller.get_links_info(project_direct)
        prefixs_info = RouterContrller.get_prefixs_info(project_direct)
        msg_info = RouterContrller.get_msg_data(project_direct)
        data = {}
        data.update(routers_info)
        data.update(links_info)
        data.update(prefixs_info)
        data.update(msg_info)
        return data