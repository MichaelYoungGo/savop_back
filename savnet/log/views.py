from rest_framework.views import APIView
from constants.error_code import ErrorCode
from savnet.log.service import SavnetContrller
from savnet.utils.http_utils import response_data
from savnet.log.mongo import MongoDBClient

class CollectSavnetTopologyProgressData(APIView):
    def get(self, request, *args, **kwargs):
        topo_name = kwargs.get("topo")
        if topo_name is not None and topo_name != "now":
            if MongoDBClient.exists_by_name(topo_name):
                data = MongoDBClient.find_one_by_name(name=topo_name)
                topo_data = data[0].get("data")
                # delete 10* router rule
                for router in topo_data["routers_info"]:
                    signal = True
                    while signal:
                        if len(router["router_table"]) == 0:
                            signal = False
                        if router["router_table"][0]["Destination"][0:4] == "10.0":
                           router["router_table"].pop(0) 
                        else:
                            signal = False
                return response_data(data=topo_data)
            else:
                return response_data(data="Please the topolopy doesn't exit!!")
        if topo_name == "now":
            data = SavnetContrller.get_info_now()
            #data = SavnetContrller.get_info_now(project_direct="/root/yhb_savnet_bird/")
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
        return response_data(data="")
