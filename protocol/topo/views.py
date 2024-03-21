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
import copy
import pymongo
import time
import ipaddress
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
    def find_one_by_name_and_id(name, id_):
        return [i for i in db.static_topo.find({"$and":[{"id": id_}, {"name": name}]})]

    @staticmethod
    def exists_by_name(name):
        count = db.static_topo.count_documents({"name": name})
        if count != 0:
            return True
        return False

    @staticmethod
    def exists_by_name_exclude_by_id(name, id_):
        count = db.static_topo.count_documents({"$and": [{"name": name}, {"id": {"$ne": id_}}]})
        if count != 0:
            return True
        return False

    @staticmethod
    def exists_by_name_and_id(name, id_):
        count = db.static_topo.count_documents({"$and": [{"name": name}, {"id": id_}]})
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
        reverse = request.query_params.get("reverse", "false")
        if reverse == "true":
            data = MongoDBClient.get_all()
            data.reverse()
        else:
            data = MongoDBClient.get_all()
        return response_data(data=data)

    @action(detail=False, methods=['get'], url_path="search", url_name="search_topo")
    def search(self, request, *args, **kwargs):
        params = request.query_params.get("id")
        name = request.query_params.get("name")
        if (params is None) and (name is None):
            return response_data(code=ErrorCode.E_PARAM_ERROR,
                                 message="Request parameter can not be empty. Please checkout your request!")
        # params = int(params)
        elif (name is None) and (params is not None):
            if MongoDBClient.exists_by_id(id_=params) is False:
                return response_data(code=ErrorCode.E_PARAM_ERROR, message="the query topology don't existed")
            else:
                data = MongoDBClient.find_one_by_id(id_=params)[0]
        elif (params is None) and (name is not None):
            if MongoDBClient.exists_by_name(name=name) is False:
                return response_data(code=ErrorCode.E_PARAM_ERROR, message="the query topology don't existed")
            else:
                data = MongoDBClient.find_one_by_name(name=name)[0]
        else:
            if MongoDBClient.exists_by_name_and_id(name=name, id_=params) is False:
                return response_data(code=ErrorCode.E_PARAM_ERROR, message="the query topology don't existed")
            else:
                data = MongoDBClient.find_one_by_name_and_id(name=name, id_=params)[0]
        data.pop("_id")
        data.pop("id")
        data.pop("name")
        config_flag = request.query_params.get("config_flag")
        if config_flag == "true":
            with open(f'/root/sav_simulate/savop/base_configs/{data["data"]["name"]}.json', 'r') as file:
                config_content = json.load(file)
            data["data"].update({"init_json": config_content})
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

    @action(detail=False, methods=['get', 'post'], url_path="config", url_name="delete_topo")
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
        config_file = {"devices": {}, "links": [], "as_relations": {"provider-customer": []}, "enable_rpki": False,
                       "prefix_method": "independent_interface", "auto_ip_version": 4, "enable_rpki": False,
                       "sav_app_map": [{
                        "devices": [],
                        "sav_apps": [],
                        "active_app": None,
                        "ignore_irrelevant_nets": True,
                        "fib_threshold": 5,
                        "original_bird": False,
                        "enable_rpki": False,
                        "ignore_private": True
                        }], "rpdp_full_link": False, "rpdp_full_link_type": "rpdp-http"}
        # 将纯数据文件转化为描述任意topo结构的json文件
        # 首先提取topo的各种构件信息
        as_info = {}
        prefix_info = {}
        router_info = {}
        for autoSyst in data["autoSysts"]:
            as_id = autoSyst["id"]
            label = autoSyst["label"]
            as_info[as_id] = label

        for prefix in data["prefixs"]:
            router_id = prefix["businessInfo"]["affiliationRouter"]
            prefix_IPs = prefix["businessInfo"]["prefixIP"]
            if len(prefix_info.get(router_id, {})) == 0:
                prefix_info.update({router_id: prefix_IPs})
            else:
                prefix_info[router_id].extend(prefix_IPs)
        for route in data["routes"]:
            router_mongo_id = route["id"]
            as_id = route["businessInfo"]["affiliationAS"]
            router_info.update({router_mongo_id: as_id})

        for index in range(0, len(data["routes"])):
            router_id = data["routes"][index]["id"]
            as_id = data["routes"][index]["businessInfo"]["affiliationAS"]
            device_id = data["routes"][index]["label"].replace("r", "")
            prefixes = config_file["devices"].get(device_id, {}).get("prefixes", {})
            for p in prefix_info[router_id]:
                ip_network = ipaddress.ip_network(p["IPaddress"], strict=False)
                prefixes.update({ip_network.compressed: {"id": p["id"], "miig_tag": p["miig_tag"], "miig_type": p["miig_type"]}})
            config_file["devices"].update({device_id: {"as": int(as_info[as_id]), "prefixes": prefixes, "id": router_id}})
            #更新sav_app_map
            sav_app_map = copy.deepcopy(data["routes"][index]["businessInfo"])
            sav_app_map.update({"devices": [device_id]})
            sav_app_map.update({"active_app": sav_app_map["active_sav_app"]})
            del sav_app_map["affiliationAS"]
            del sav_app_map["active_sav_app"]
            config_file["sav_app_map"].append(sav_app_map)
        for component in data["edges"]:
            source_router_id = component["source"]
            target_router_id = component["target"]
            for index in range(0, len(data["routes"])):
                if data["routes"][index]["id"] == source_router_id:
                    source_router_index = data["routes"][index]["label"].replace("r", "")
                    break
            for index in range(0, len(data["routes"])):
                if data["routes"][index]["id"] == target_router_id:
                    target_router_index = data["routes"][index]["label"].replace("r", "")
                    break
            config_file["links"].append([str(source_router_index), str(target_router_index), "bgp"])
            if len(component["businessInfo"]) == 0:
                continue
            elif component["businessInfo"]["businessRelation"] == "CtoP":
                as_relateion = [as_info[router_info[target_router_id]], as_info[router_info[source_router_id]]]
            elif component["businessInfo"]["businessRelation"] == "PtoC":
                as_relateion = [as_info[router_info[source_router_id]], as_info[router_info[target_router_id]]]
            else:
                continue
            config_file["as_relations"]["provider-customer"].append(as_relateion)
        config_file["as_relations"]["provider-customer"] = [list(t) for t in {tuple(element) for element in config_file["as_relations"]["provider-customer"]}]
        # 更新topo属性
        config_file.update(data["properties"])

        # 临时代码
        config_file["links"].extend([["1", "4", "rpdp-http"], ["1", "5", "rpdp-http"],
                                    ["3", "4", "rpdp-http"], ["4", "5", "rpdp-http"]])
        # 打开文件以进行写入，如果文件不存在则创建
        with open(f'/root/sav_simulate/savop/base_configs/{topo_name}.json', 'w') as file:
            file.write(json.dumps(config_file, indent=2))
        return response_data(data=config_file)