# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     views
   Description :  control the router node in the savop simulation
   Author :       MichaelYoungGo
   date：          2023/7/4
-------------------------------------------------
   Change Activity:
                   2023/7/4:
-------------------------------------------------
"""

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from protocol.utils.http_utils import response_data
from protocol.utils.command import command_executor
from constants.error_code import ErrorCode


class NodeControllerSet(ViewSet):
    @action(detail=False, methods=['get'], url_path="refresh_protocol", url_name="refresh_protocol")
    def refresh_protocol(self, request, *args, **kwargs):
        protocol_name = request.query_params.get("protocol_name")
        if protocol_name is None:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="The protocol name cannot be empty")
        protocol_dict = {"strict-uRPF": "strict_urpf_app", "rpdp": "rpdp_app", "loose-uRPF": "loose_urpf_app",
                         "EFP-uRPF-A": "EFP-uRPF-Algorithm-A_app", "EFP-uRPF-B": "EFP-uRPF-Algorithm-B_app",
                         "FP-uRPF": "fpurpf_app"}
        if protocol_name not in protocol_dict.keys():
            return response_data(code=ErrorCode.E_PARAM_ERROR, message='he protocol name does not exist. Please choose one of the following: strict-uRPF,\
                                       rpdp_app, loose-uRPF, EFP-uRPF-A, EFP-uRPF-B, FP-uRPF')
        protocol_name = protocol_dict[protocol_name]
        node_command = "docker ps | grep savop_bird_base | awk '{print $11}'"
        node_command_result = command_executor(command=node_command)
        returncode, stdout, stderr = node_command_result.returncode, node_command_result.stdout, node_command_result.stderr
        if returncode != 0:
            return response_data(ErrorCode.E_SERVER, message="Docker command execution failed")
        node_list = stdout.split("\n")[:-1]
        node_list.sort()
        for node_name in node_list:
            refresh_command = f"docker exec -it {node_name} curl http://localhost:8888/refresh_proto/{protocol_name}/"
            refresh_result = command_executor(command=refresh_command)
            if refresh_result.returncode != 0:
                return response_data(ErrorCode.E_SERVER, message="Docker command execution failed")
        return response_data(data="refresh success")

