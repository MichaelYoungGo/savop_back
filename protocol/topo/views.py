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
        params = int(params)
        if MongoDBClient.exists_by_id(id_=params) is False:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="the query topology don't existed")

        data = MongoDBClient.find_one_by_id(id_=params)[0]
        data.pop("_id")
        return response_data(data=data)

    @action(detail=False, methods=['get'], url_path="add", url_name="add_topo")
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

    @action(detail=False, methods=['get'], url_path="modify", url_name="modify_topo")
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
        if MongoDBClient.exists_by_name(name=topo_name):
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
        params = int(params)
        if MongoDBClient.exists_by_id(id_=params) is False:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="the delete topology don't existed")
        MongoDBClient.delete_by_id(id_=params)
        return response_data(data="delete, successfully!")




