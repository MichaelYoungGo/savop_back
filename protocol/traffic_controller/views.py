# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     views
   Description :  traffic controller
   Author :       MichaelYoungGo
   date：          2023/7/6
-------------------------------------------------
   Change Activity:
                   2023/7/6:
-------------------------------------------------
"""
import json
import multiprocessing
import time
from collections import OrderedDict
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from protocol.utils.http_utils import response_data
from protocol.utils.command import command_executor
from constants.error_code import ErrorCode
from protocol.utils.decorator import api_check_mode_name, api_check_mode_status


def start_udp_server(receive_pos, dst_ip, trans_num, q):
    print("udp server start")
    traffic_receive_command = f"docker exec -i r{receive_pos} python3 /root/savop/sav-agent/tools/UDP_server.py  \
                           --dst {dst_ip} --trans_num {trans_num}"
    receive_result = command_executor(command=traffic_receive_command)
    if receive_result.returncode == 0:
        q.put(receive_result.stdout)
    else:
        q.put(receive_result.returncode)
    print("udp server end")


def start_udp_client(send_pos, dst_ip, src_ip, trans_num, iface):
    print("udp client start")
    traffic_send_command = f"docker exec -i r{send_pos} python3 /root/savop/sav-agent/tools/UDP_client.py  \
                           --dst {dst_ip} --src {src_ip} --trans_num {trans_num} --iface {iface}"
    send_result = command_executor(command=traffic_send_command)
    print("udp client end")


class TrafficControllerSet(ViewSet):
    @api_check_mode_name
    @api_check_mode_status
    @action(detail=False, methods=['get', 'post'], url_path="sender", url_name="traffic_sender")
    def sender(self, request, *args, **kwargs):
        parameters = request.data
        if len(parameters.keys()) < 6:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="lack parameter")
        send_pos, receive_pos, dst, src, trans_num, iface = parameters.get("send_pos"), parameters.get("receive_pos"), \
            parameters.get("dst"), parameters.get("src"), parameters.get("trans_num", 10), parameters.get("iface")
        if (send_pos is None) or (receive_pos is None) or (dst is None) or (src is None) or (
        not isinstance(trans_num, int)) or (iface is None):
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="lack parameter")
        # checkout if the dst have exited
        dst_ip, dst_prefix = parameters.get("dst").split("/")[0], parameters.get("dst").split("/")[1]
        src_ip = parameters.get("src").split("/")[0]
        # receive_link_info_command = f"docker exec -i node_{receive_pos} ip -j a"
        # link_info_result = command_executor(command=receive_link_info_command)
        # if link_info_result.returncode != 0:
        #     return response_data(code=ErrorCode.E_SERVER, message="Docker command execution failed")
        # link_info = json.loads(link_info_result.stdout)
        # ipaddr_not_exited = True
        # for info in link_info:
        #     #if info["ifname"] != iface:
        #     #    continue
        #     for addr_info in info["addr_info"]:
        #         if addr_info["local"] == dst_ip:
        #             ipaddr_not_exited = False
        # if ipaddr_not_exited:
        #     eth = link_info[1]["ifname"]
        #     add_ipaddr_command = f"docker exec -i node_{receive_pos} ip addr add {dst_ip}/{dst_prefix} dev {eth}"
        #     add_ipaddr_result = command_executor(command=add_ipaddr_command)
        #     if add_ipaddr_result.returncode != 0:
        #         return response_data(ErrorCode.E_SERVER, message=f"Docker command execution failed, {add_ipaddr_command}")

        # traffic_send_command = f"docker exec -i node_{send_pos} python3 /root/savop/extend_server/trafficTools/traffic_sender.py --dst \
        #                         {dst_ip} --src {src_ip} --trans_num {trans_num} --iface {iface}"
        # send_result = command_executor(command=traffic_send_command)

        # if ipaddr_not_exited:
        #     del_ipaddr_command = f"docker exec -i node_{receive_pos} ip addr del {dst_ip}/{dst_prefix} dev {eth}"
        #     del_ipaddr_result = command_executor(command=del_ipaddr_command)
        #     if del_ipaddr_result.returncode != 0:
        #         return response_data(code=ErrorCode.E_SERVER, message=f"Docker command execution failed, {del_ipaddr_command}")
        # if send_result.returncode != 0:
        #     return response_data(code=ErrorCode.E_SERVER, message=f"Docker command execution failed, {traffic_send_command}")
        # send_data = eval(send_result.stdout)
        # 获取全局IP地址视野
        router_info = command_executor(command="docker ps |grep savop |awk '{print $NF}'")
        router_name_list = [i for i in router_info.stdout.split("\n") if len(i) >= 2]
        router_map = {}
        for router_name in router_name_list:
            IP_info = command_executor(f"docker exec -i {router_name} ip -j address")
            IP_json = json.loads(IP_info.stdout)
            for i in IP_json:
                if "eth_" not in i["ifname"]:
                    continue
                for add_info in i["addr_info"]:
                    router_map.update({add_info["local"]: router_name})
        # 获取发包路径，无论在
        trace_route_info = command_executor(f"docker exec -i {iface.replace('eth_', 'r')} traceroute {dst_ip} |grep -v traceroute |awk '{{print $2}}'")
        normal_packet_path =[f"r{send_pos}", iface.replace('eth_', 'r')] + [router_map[i] for i in trace_route_info.stdout.split("\n") if len(i) >= 7]
        # 清空拦截日志
        clear_block_log = command_executor("echo \"\" > /var/log/syslog")
        q = multiprocessing.Queue()
        server = multiprocessing.Process(target=start_udp_server, args=(receive_pos, dst_ip, trans_num, q))
        client = multiprocessing.Process(target=start_udp_client, args=(send_pos, dst_ip, src_ip, trans_num, iface))
        server.start()
        time.sleep(0.5)
        client.start()
        client.join()
        server.join()
        server_result = q.get()
        if type(server_result) == int:
            return response_data(code=ErrorCode.E_SERVER, message="UDP server command execution failed")
        data = eval(server_result)
        data.update({"normal_path": normal_packet_path})
        intercept_router = ""
        if data["fail_count"] != 0:
            container_id = command_executor(command="grep \"IPTABLES\" /var/log/syslog|awk '{print $8}'|uniq").stdout.strip()
            intercept_router = command_executor(command=f"docker ps |grep {container_id}|awk '{{print $NF}}'").stdout.strip()
        normal_packet_path = list(OrderedDict.fromkeys(normal_packet_path).keys())
        data.update({"intercept_router": intercept_router})
        data.update({"normal_path": normal_packet_path})
        return response_data(data=data)

    @action(detail=False, methods=['get', 'post'], url_path="receiver", url_name="traffic_receiver")
    def receiver(self, request, *args, **kwargs):
        return response_data(data="hello world")
