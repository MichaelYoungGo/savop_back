# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     command
   Description :   command tools
   Author :        MichealYoungGo
   date：          2023/7/4
-------------------------------------------------
   Change Activity:
                   2023/7/4:
-------------------------------------------------
"""
import subprocess


def command_executor(command):
    return subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')

def command_executor_with_popen(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                            universal_newlines=True)