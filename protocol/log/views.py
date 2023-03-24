from rest_framework.views import APIView
from constants.error_code import ErrorCode
from protocol.log.service import RouterContrller
from protocol.utils.http_utils import response_data
from protocol.log.mongo import MongoDBClient

class CollectTopologyProgressData(APIView):
    def get(self, request, *args, **kwargs):
        topo_name = kwargs.get("topo")
        project_direct = request.GET.get("path")
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
            if project_direct is None:
                data = RouterContrller.get_info_now()
            else:
                data = RouterContrller.get_info_now(project_direct=project_direct)
            return response_data(data=data)
        return response_data(data="Please write the topolopy name, /api/netinfo/<topo_name>/")


class RefreshTopologyProgressData(APIView):  
    def get(self, request, *args, **kwargs):
        topo_name = kwargs.get("topo")
        project_direct = request.GET.get("path")
        if topo_name is None:
            return response_data(code=ErrorCode.E_PARAM_ERROR, message="Please write the topolopy name, /api/netinfo/refresh/<topo_name>/")
        if project_direct is None:
            data = RouterContrller.get_info_now()
        else:
            data = RouterContrller.get_info_now(project_direct=project_direct)
        if MongoDBClient.exists_by_name(topo_name):
            MongoDBClient.update_by_name(name=topo_name, data=data)
        else:
            MongoDBClient.insert(name=topo_name, data=data)
        return response_data(data="success")


class FPathInfoView(APIView):
    def get(self, request, *args, **kwargs):
        return response_data(data="")