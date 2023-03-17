from rest_framework.views import APIView
from constants.error_code import ErrorCode
from savnet.log.service import SavnetContrller
from savnet.utils.http_utils import response_data
from savnet.log.mongo import MongoDBClient



class CollectSavnetTopologyProgressData(APIView):
    def get(self, request, *args, **kwargs):
        topo_name = kwargs.get("topo")
        if topo_name is not None and topo_name != "now":
            with open("/root/savnet_back/data/topology.txt",'r', encoding='utf-8')as f:
                lines = f.readlines()
                for l in lines:
                    if l.split("\t")[0] == topo_name:
                        topo_data = eval(l.split("\t")[1])
            return response_data(data=topo_data)
        if topo_name == "now":
            routers_info = SavnetContrller.get_routers_info()
            links_info = SavnetContrller.get_links_info()
            prefixs_info = SavnetContrller.get_prefixs_info()
            msg_info = SavnetContrller.get_msg_data()
            data = {}
            data.update(routers_info)
            data.update(links_info)
            data.update(prefixs_info)
            data.update(msg_info)
            return response_data(data=data)
        return response_data(data="Please write the topolopy name, /api/netinfo/<topo_name>/")


class RefreshSavnetTopologyProgressData(APIView):  
    def get(self, request, *args, **kwargs):
        topo_name = kwargs.get("topo")
        if topo_name is None:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="Please write the topolopy name, /api/netinfo/refresh/<topo_name>/")
        data = SavnetContrller.get_info_now()
        if MongoDBClient.exists_by_name(topo_name):
            MongoDBClient.update_by_name(name=topo_name, data=data)
        else:
            MongoDBClient.insert(name=topo_name, data=data)
        return response_data(data="success")


class FPathInfoView(APIView):
    def get(self, request, *args, **kwargs):
        with open("/root/savnet_back/data/topology.txt",'r', encoding='utf-8')as f:
                lines = f.readlines()
                for l in lines:
                    topo_data = eval(l.split("\t")[1])
        route_A = [
        {"Destination": "192.168.1.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "Metric": 32, "Ref": 0, "Use": 0, "Iface":  "*"},  
        {"Destination": "192.168.2.0", "Gateway": "10.0.1.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "a_b"},  
        {"Destination": "192.168.3.0", "Gateway": "10.0.1.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "a_b"},
        {"Destination": "192.168.4.0", "Gateway": "10.0.1.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "a_b"},
        {"Destination": "192.168.5.0", "Gateway": "10.0.1.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "a_b"},
        {"Destination": "192.168.6.0", "Gateway": "10.0.2.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "a_f"},
        {"Destination": "192.168.7.0", "Gateway": "10.0.2.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "a_f"}]
        route_B = [
        {"Destination": "192.168.1.0", "Gateway": "10.0.1.1", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use":0, "Iface": "b_a"},
        {"Destination": "192.168.2.0", "Gateway": "10.0.4.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "b_d"},
        {"Destination": "192.168.3.0", "Gateway": "10.0.4.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "b_d"},
        {"Destination": "192.168.4.0", "Gateway": "10.0.4.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "b_d"},
        {"Destination": "192.168.5.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "*"}]
        route_C = [
        {"Destination": "192.168.5.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "Metric": 32, "Ref": 0, "Use":0, "Iface": "*"}]
        route_D = [
        {"Destination": "192.168.1.0", "Gateway": "10.0.4.1", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "d_b"},
        {"Destination": "192.168.2.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "*"},
        {"Destination": "192.168.3.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "*"},
        {"Destination": "192.168.4.0", "Gateway": "10.0.7.2", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use": 0, "Iface": "d_e"},
        {"Destination": "192.168.5.0", "Gateway": "10.0.4.1", "Genmask": "255.255.255.0", "Flags": "UG", "Metric": 32, "Ref": 0, "Use":  0, "Iface": "d_b"}]
        route_E = [
        {"Destination": "192.168.1.0", "Gateway": "10.0.7.1", "Genmask": "255.255.255.0", "Flags": "UG", "MSS": 0, "Window": 0, "irtt": 0, "Iface": "e_d"},
        {"Destination": "192.168.2.0", "Gateway": "10.0.7.1", "Genmask": "255.255.255.0", "Flags": "UG", "MSS": 0, "Window": 0, "irtt": 0, "Iface": "e_d"},
        {"Destination": "192.168.3.0", "Gateway": "10.0.7.1", "Genmask": "255.255.255.0", "Flags": "UG", "MSS": 0, "Window": 0, "irtt": 0, "Iface": "e_d"},
        {"Destination": "192.168.4.0", "Gateway": "0.0.0.0",  "Genmask": "255.255.255.0", "Flags": "U", "MSS": 0, "Window": 0, "irtt": 0, "Iface": "*"},
        {"Destination": "192.168.5.0", "Gateway": "10.0.7.1", "Genmask": "255.255.255.0", "Flags": "UG", "MSS": 0, "Window": 0, "irtt": 0, "Iface": "e_d"}]
        route_F = [
        {"Destination": "192.168.1.0", "Gateway": "10.0.2.1", "Genmask": "255.255.255.0", "Flags": "UG", "MSS": 0, "Window":0, "irtt": 0, "Iface": "f_a"},
        {"Destination": "192.168.6.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "MSS": 0, "Window":0, "irtt": 0, "Iface": "*"},
        {"Destination": "192.168.7.0", "Gateway": "0.0.0.0", "Genmask": "255.255.255.0", "Flags": "U", "MSS": 0, "Window":0, "irtt": 0, "Iface": "*"}]
        route_tables = []
        route_tables.append(route_A)
        route_tables.append(route_B)
        route_tables.append(route_C)
        route_tables.append(route_D)
        route_tables.append(route_E)
        route_tables.append(route_F)
        for index in range(0, 6):
            topo_data["routers_info"][index]["router_table"] = route_tables[index]

        sav_A = [
            {"id":1,"prefix":"192.168.6.0/24","neighbor_as":65505,"interface":"a_f","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":2,"prefix":"192.168.7.0/24","neighbor_as":65505,"interface":"a_f","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":3,"prefix":"192.168.5.0/24","neighbor_as":65504,"interface":"a_b","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":4,"prefix":"192.168.2.0/24","neighbor_as":65504,"interface":"a_b","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":5,"prefix":"192.168.3.0/24","neighbor_as":65504,"interface":"a_b","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":6,"prefix":"192.168.4.0/24","neighbor_as":65504,"interface":"a_b","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"}]
        sav_B = [
            {"id":1,"prefix":"192.168.2.0/24","neighbor_as":65502,"interface":"b_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":2,"prefix":"192.168.3.0/24","neighbor_as":65502,"interface":"b_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":3,"prefix":"192.168.4.0/24","neighbor_as":65502,"interface":"b_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":4,"prefix":"192.168.1.0/24","neighbor_as":65501,"interface":"b_a","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"}]
        sav_C = []
        sav_D = [
            {"id":1,"prefix":"192.168.5.0/24","neighbor_as":65504,"interface":"d_b","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":2,"prefix":"192.168.4.0/24","neighbor_as":65503,"interface":"d_e","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":3,"prefix":"192.168.1.0/24","neighbor_as":65504,"interface":"d_b","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"}]
        sav_E = [
            {"id":1,"prefix":"192.168.2.0/24","neighbor_as":65502,"interface":"e_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":2,"prefix":"192.168.3.0/24","neighbor_as":65502,"interface":"e_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":3,"prefix":"192.168.5.0/24","neighbor_as":65502,"interface":"e_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"},
            {"id":4,"prefix":"192.168.1.0/24","neighbor_as":65502,"interface":"e_d","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"}]
        sav_F = [{"id":1,"prefix":"192.168.1.0/24","neighbor_as":65501,"interface":"f_a","source":None,"direction":None,"createtime":"2023-03-14 07:19:31","updatetime":"2023-03-14 07:19:31"}]
        sav_tables = []
        sav_tables.append(sav_A)
        sav_tables.append(sav_B)
        sav_tables.append(sav_C)
        sav_tables.append(sav_D)
        sav_tables.append(sav_E)
        sav_tables.append(sav_F)
        for index in range(0, 6):
            topo_data["routers_info"][index]["sav_table"] = sav_tables[index]
        with open("/root/savnet_back/data/topology_new.txt",'w', encoding='utf-8')as f:
            f.write("classic_1\t" + str(topo_data))
        return response_data(data=topo_data)
