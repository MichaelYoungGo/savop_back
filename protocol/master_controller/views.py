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
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from protocol.utils.http_utils import response_data
from protocol.utils.command import command_executor
from constants.error_code import ErrorCode

class HostControllerSet(ViewSet):
    @action(detail=False, methods=['get'], url_path="test", url_name="test")
    def start(self, request, *args, **kwargs):
        return response_data(data="test success")