# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     decorator
   Description :
   Author :       MichaelYoung
   date：          2024/3/4
-------------------------------------------------
   Change Activity:
                   2024/3/4:
-------------------------------------------------
"""
import json
import subprocess
from functools import wraps
from constants.error_code import ErrorCode
from protocol.utils.http_utils import response_data
from constants.common_variable import SAV_ROOT_DIR
from protocol.utils.command import command_executor


def api_check_mode_name(func):
    """
    作用：用户调用接口时，检查用户使用的模型是否和底层运行的模型匹配
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        topo_name = args[1].query_params.get("topo", False)
        if topo_name is False:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="missing value for the 'topo' parameter")
        # 获取正在运行的模型名称
        with open(f"{SAV_ROOT_DIR}/savop_run/active_signal.json", 'r', encoding='utf-8') as f:
            active_signal_content = json.load(f)
        running_mode_name = active_signal_content.get("mode_name")
        if running_mode_name == topo_name:
            return func(*args, **kwargs)
        else:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="the requested model is not running")
    return wrapper

def api_check_mode_status(func):
    """
    作用：用户调用接口时，检查用户使用的模型是否和底层运行的模型匹配
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        topo_name = args[1].query_params.get("topo", False)
        # 获取模型运行的init_json文件
        with open(f"{SAV_ROOT_DIR}/savop/base_configs/{topo_name}.json", 'r', encoding='utf-8') as f:
            init_json_content = json.load(f)
        device_num = len(init_json_content.get("devices"))
        command_result = subprocess.run("docker ps |grep savop|wc -l", shell=True, capture_output=True, encoding='utf-8')
        if int(command_result.stdout.strip("\n")) == 0:
            return response_data(code=ErrorCode.E_SERVER, message=f"The {topo_name} model is not running")
        if int(command_result.stdout.strip("\n")) != device_num:
            return response_data(code=ErrorCode.E_SERVER, message=f"The {topo_name} model is running abnormally")

        router_info = command_executor(command="docker ps |grep savop |awk '{print $NF}'")
        router_name_list = [i for i in router_info.stdout.split("\n") if len(i) >= 2]
        for router_name in router_name_list:
            run_status = command_executor(f"docker exec -i {router_name} bash -c \"ps -ef|grep -E 'python3|bird'|grep -v grep|wc -l\"")
            if int(run_status.stdout.strip("\n")) != 5:
                return response_data(code=ErrorCode.E_SERVER, message=f"The {topo_name} model is running abnormally")
        return func(*args, **kwargs)
    return wrapper