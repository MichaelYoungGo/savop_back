import pymongo
import time

client = pymongo.MongoClient("localhost", 27017)
db = client.savnet


class MongoDBClient():
    def get_all():
        return [ i for i in db.topo.find()]
    def find_one_by_name(name):
        return  [ i for i in db.topo.find({"topo_name": name})]
    def exists_by_name(name):
        count = db.topo.count_documents({"topo_name": name})
        if count != 0:
            return True
        return False
    def insert(name, data):
        db.topo.insert_one({"topo_name": name, "data": data, "createtime": time.strftime('%Y-%m-%d %H:%M:%S')})
    def update_by_name(name, data):
        db.topo.update_one({"topo_name": name},  {"$set":{"data": data, "updatetime": time.strftime('%Y-%m-%d %H:%M:%S')}})

    