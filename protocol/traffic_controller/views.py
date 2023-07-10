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

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from protocol.utils.http_utils import response_data
from protocol.utils.command import command_executor
from constants.error_code import ErrorCode


class TrafficControllerSet(ViewSet):
    @action(detail=False, methods=['get', 'post'], url_path="sender", url_name="traffic_sender")
    def sender(self, request, *args, **kwargs):
        parameters = request.data
        if len(parameters.keys()) < 5:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="lack parameter")
        send_pos, receive_pos, dst, src, trans_num = parameters.get("send_pos"), parameters.get("receive_pos"), \
            parameters.get("dst"), parameters.get("src"), parameters.get("trans_num", 10),
        if (send_pos is None) or (receive_pos is None) or (dst is None) or (src is None) or (not isinstance(trans_num, int)):
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="lack parameter")
        # checkout if the dst have exited
        dst_ip, dst_prefix = parameters.get("dst").split("/")[0], parameters.get("dst").split("/")[1]
        src_ip, src_prefix = parameters.get("src").split("/")[0], parameters.get("src").split("/")[1]
        receive_link_info_command = f"docker exec -i node_{receive_pos} ip -j a"
        link_info_result = command_executor(command=receive_link_info_command)
        if link_info_result.returncode != 0:
            return response_data(code=ErrorCode.E_SERVER, message="Docker command execution failed")
        link_info = json.loads(link_info_result.stdout)
        ipaddr_not_exited = True
        for info in link_info:
            for addr_info in info["addr_info"]:
                if addr_info["local"] == dst_ip:
                    ipaddr_not_exited = False
        if ipaddr_not_exited:
            eth = link_info[1]["ifname"]
            add_ipaddr_command = f"docker exec -i node_{receive_pos} ip addr add {dst_ip}/{dst_prefix} dev {eth}"
            add_ipaddr_result = command_executor(command=add_ipaddr_command)
            if add_ipaddr_result.returncode != 0:
                return response_data(ErrorCode.E_SERVER, message="Docker command execution failed")
        traffic_send_command = f"docker exec -i node_{send_pos} python3 /root/savop/extend_server/trafficTools/traffic_sender.py --dst \
                                {dst_ip} --src {src_ip} --trans_num {trans_num} "
        send_result = command_executor(command=traffic_send_command)
        if ipaddr_not_exited:
            del_ipaddr_command = f"docker exec -i node_{receive_pos} ip addr del {dst_ip}/{dst_prefix} dev {eth}"
            del_ipaddr_result = command_executor(command=del_ipaddr_command)
            if del_ipaddr_result.returncode != 0:
                return response_data(code=ErrorCode.E_SERVER, message="Docker command execution failed")
        if send_result.returncode != 0:
            return response_data(code=ErrorCode.E_SERVER, message="Docker command execution failed")
        send_data = eval(send_result.stdout)
        return response_data(data=send_data)

    @action(detail=False, methods=['get', 'post'], url_path="receiver", url_name="traffic_receiver")
    def receiver(self, request, *args, **kwargs):
        return response_data(data="hello world")
