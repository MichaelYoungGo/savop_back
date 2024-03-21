# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     views.py
   Description :
   Author :       MichaelYoung
   date：          2024/1/19
-------------------------------------------------
   Change Activity:
                   2024/1/19:
-------------------------------------------------
"""
import json
import subprocess
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from protocol.utils.http_utils import response_data
from protocol.utils.command import command_executor
from constants.error_code import ErrorCode
from constants.common_variable import SAV_ROOT_DIR
from protocol.utils.decorator import api_check_mode_name, api_check_mode_status

class HostControllerSet(ViewSet):
    @action(detail=False, methods=['get'], url_path="config", url_name="config")
    def config(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = ""
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --topo_json {topo_name} --config refresh"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for content in command_result.stdout.split("\n"):
            if "run over" in content:
                break
            data += content
        return response_data(data=data)

    @action(detail=False, methods=['get'], url_path="distribute", url_name="distribute")
    def distribute(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = ""
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --topo_json {topo_name} --distribute all"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for content in command_result.stdout.split("\n"):
            if "run over" in content:
                break
            data += content
        return response_data(data=data)

    @action(detail=False, methods=['get'], url_path="run", url_name="run")
    def run(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = ""
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --topo_json {topo_name} --action start"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for content in command_result.stdout.split("\n"):
            if "run over" in content:
                break
            data += content
        return response_data(data=data)


    @api_check_mode_name
    @api_check_mode_status
    @action(detail=False, methods=['get'], url_path="metric", url_name="metric")
    def metric(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = {}
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --metric {topo_name}"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for metric in command_result.stdout.split("\n"):
            if "the protocol performance metric" in metric:
                continue
            if "run over" in metric:
                break
            data.update(json.loads(metric))
        return response_data(data=data)

    @api_check_mode_name
    @api_check_mode_status
    @action(detail=False, methods=['get'], url_path="sav_table", url_name="sav_table")
    def sav_table(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = {}
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --table {topo_name}"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for sav_table in command_result.stdout.split("\n"):
            if "the protocol table" in sav_table:
                continue
            if "run over" in sav_table:
                break
            data.update(json.loads(sav_table))
        return response_data(data=data)

    @api_check_mode_name
    @api_check_mode_status
    @action(detail=False, methods=['get'], url_path="performance", url_name="performance")
    def performance(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = {}
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --performance all"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for performance in command_result.stdout.split("\n"):
            if "the protocol table" in performance:
                continue
            if "run over" in performance:
                break
            data.update(json.loads(performance))
        return response_data(data=data)

    @api_check_mode_name
    @api_check_mode_status
    @action(detail=False, methods=['get'], url_path="step", url_name="step")
    def step(self, request, *args, **kwargs):
        topo_name = request.query_params.get("topo")
        data = []
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --step {topo_name}"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for step in command_result.stdout.split("\n"):
            if "the protocol process of sending packets" in step:
                continue
            if "run over" in step:
                break
            data.append(json.loads(step))
        return response_data(data=data)

    @api_check_mode_name
    @api_check_mode_status
    @action(detail=False, methods=['get', 'post'], url_path="enable", url_name="enable")
    def enable(self, request, *args, **kwargs):
        protocol_name = request.query_params.get("protocol_name")
        router_scope = request.data["router_scope"]
        data = []
        router = router_scope[0]
        for index in range(1, len(router_scope)):
            router += "," + router_scope[index]
        command = f"python3 {SAV_ROOT_DIR}/savop/sav_control_master.py --enable {protocol_name} --router {router}"
        command_result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        for result in command_result.stdout.split("\n"):
            if "the enable sav_table's rules situation" in result:
                continue
            if "run over" in result:
                break
            data.append(json.loads(result))
        return response_data(data=data)
