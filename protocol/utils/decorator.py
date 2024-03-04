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
from functools import wraps
from constants.error_code import ErrorCode
from protocol.utils.http_utils import response_data
from constants.common_variable import SAV_ROOT_DIR


def api_check_mode_name(func):
    """
    作用：用户调用接口时，检查用户使用的模型是否和底层运行的模型匹配
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("触发装饰器，检查模型的一致性！")
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