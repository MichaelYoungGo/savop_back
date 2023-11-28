# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     views
   Description :  CRUD for topology data
   Author :       MichaelYoungGo
   date：          2023/6/25
-------------------------------------------------
   Change Activity:
                   2023/6/25:
-------------------------------------------------
"""
import json

import pymongo
import time
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from protocol.utils.http_utils import response_data
from constants.error_code import ErrorCode

client = pymongo.MongoClient("localhost", 27017)
db = client.savnet


class MongoDBClient:
    @staticmethod
    def get_all():
        data = []
        for i in db.static_topo.find():
            i.pop("_id")
            data.append(i.get("data"))
        return data

    @staticmethod
    def find_one_by_name(name):
        return [i for i in db.static_topo.find({"name": name})]

    @staticmethod
    def find_one_by_id(id_):
        return [i for i in db.static_topo.find({"id": id_})]

    @staticmethod
    def exists_by_name(name):
        count = db.static_topo.count_documents({"name": name})
        if count != 0:
            return True
        return False

    @staticmethod
    def exists_by_name_exclude_by_id(name, id_):
        count = db.static_topo.count_documents({"$and": [{"name": name}, {"id": { "$ne": id_}}]})
        if count != 0:
            return True
        return False

    @staticmethod
    def exists_by_id(id_):
        count = db.static_topo.count_documents({"id": id_})
        if count != 0:
            return True
        return False

    @staticmethod
    def insert(id_, name, data):
        db.static_topo.insert_one({"id": id_, "name": name, "data": data, "createtime": time.strftime('%Y-%m-%d %H:%M:%S')})

    @staticmethod
    def update_by_name(name, data):
        db.static_topo.update_one({"name": name},  {"$set":{"data": data, "updatetime": time.strftime('%Y-%m-%d %H:%M:%S')}})

    @staticmethod
    def delete_by_id(id_):
        db.static_topo.delete_one({"id": id_})


class TopologySet(ViewSet):
    @action(detail=False, methods=['get'], url_path="list", url_name="list_topo")
    def list_(self, request, *args, **kwargs):
        data = MongoDBClient.get_all()
        return response_data(data=data)

    @action(detail=False, methods=['get'], url_path="search", url_name="search_topo")
    def search(self, request, *args, **kwargs):
        params = request.query_params.get("id")
        if params is None:
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Request parameter can not be empty. Please checkout your request!")
        # params = int(params)
        if MongoDBClient.exists_by_id(id_=params) is False:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="the query topology don't existed")

        data = MongoDBClient.find_one_by_id(id_=params)[0]
        data.pop("_id")
        data.pop("id")
        data.pop("name")
        return response_data(data=data)

    @action(detail=False, methods=['post'], url_path="add", url_name="add_topo")
    def add(self, request, *args, **kwargs):
        topo_data = request.data
        if not bool(topo_data):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology data can not be empty. Please checkout your request!")
        topo_name = topo_data.get("name")
        topo_id = topo_data.get("id")
        if (bool(topo_name) is False) or (bool(topo_id) is False):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology name or id can not be empty. Please checkout your request!")
        if (bool(topo_name) is False) or (bool(topo_id) is False):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology name or id can not be empty. Please checkout your request!")
        if MongoDBClient.exists_by_name(name=topo_name):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology name have existed. Please checkout your request!")
        if MongoDBClient.exists_by_id(id_=topo_id):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology id have existed. Please checkout your request!")
        MongoDBClient.insert(id_=topo_id, name=topo_name, data=topo_data)
        return response_data(data="add successfully")

    @action(detail=False, methods=['post'], url_path="modify", url_name="modify_topo")
    def modify(self, request, *args, **kwargs):
        topo_data = request.data
        if not bool(topo_data):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology data can not be empty. Please checkout your request!")
        topo_name = topo_data.get("name")
        topo_id = topo_data.get("id")
        if (bool(topo_name) is False) or (bool(topo_id) is False):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology name or id can not be empty. Please checkout your request!")
        if (bool(topo_name) is False) or (bool(topo_id) is False):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology name or id can not be empty. Please checkout your request!")
        if MongoDBClient.exists_by_name_exclude_by_id(name=topo_name, id_=topo_id):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Topology name have existed. Please checkout your request!")
        MongoDBClient.delete_by_id(id_=topo_id)
        MongoDBClient.insert(id_=topo_id, name=topo_name, data=topo_data)
        return response_data(data="modify, successfully!")

    @action(detail=False, methods=['get'], url_path="delete", url_name="delete_topo")
    def delete(self, request, *args, **kwargs):
        params = request.query_params.get("id")
        if params is None:
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Request parameter can not be empty. Please checkout your request!")
        # params = int(params)
        if MongoDBClient.exists_by_id(id_=params) is False:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="the delete topology don't existed")
        MongoDBClient.delete_by_id(id_=params)
        return response_data(data="delete, successfully!")

    @action(detail=False, methods=['get'], url_path="config", url_name="delete_topo")
    def config(self, request, *args, **kwargs):
        params = request.query_params.get("id")
        if params is None:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="Request parameter can not be empty. Please checkout your request!")
        if MongoDBClient.exists_by_id(id_=params) is False:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="the config topology don't existed")
        # 将数据库中的数据转化为纯数据文件
        data = MongoDBClient.find_one_by_id(id_=params)[0]
        topo_name = data["name"]
        data = data["data"]["content"]
        config_file = {"devices": {}, "links": [], "enable_rpki": False, "prefix_method": "blackhole", "ip_version": 4}
        # 将纯数据文件转化为描述任意topo结构的json文件
        # 首先提取topo的各种构件信息
        as_info = {}
        prefix_info = {}
        router_info = {}
        for component in data["nodes"]:
            component_type = component["id"].split("_")[0]
            if component_type == "as":
                as_id = component["id"]
                label = component["label"]
                as_info[as_id] = label
            elif component_type == "pref":
                router_id = component["businessInfo"]["affiliationRouter"]
                prefix_IPs = component["businessInfo"]["prefixIP"]
                prefix_IP_list = prefix_IPs.split(",")
                prefix_info.update({router_id: prefix_IP_list})
            elif component_type == "rt":
                router_mongo_id = component["id"]
                router_id = component["businessInfo"]["routerId"]
                router_info.update({router_mongo_id: router_id})
        for component in data["nodes"]:
            component_type = component["id"].split("_")[0]
            if component_type == "rt":
                as_id = component["businessInfo"]["affiliationAS"]
                router_id = component["businessInfo"]["routerId"]
                router_mongo_id = component["id"]
                config_file["devices"].update({router_id: {"as": as_info[as_id], "prefixes": prefix_info[router_mongo_id]}})
        for component in data["edges"]:
            source_router_mongo_id = component["source"]
            target_router_mongo_id = component["target"]
            source_router_id = router_info[source_router_mongo_id]
            target_router_id = router_info[target_router_mongo_id]
            config_file["links"].append([source_router_id, target_router_id, "dsav"])
        # 打开文件以进行写入，如果文件不存在则创建
        with open(f'/root/sav_simulate/sav-start/base_configs/{topo_name}.json', 'w') as file:
            file.write(json.dumps(config_file, indent=2))
        return response_data(data=config_file)