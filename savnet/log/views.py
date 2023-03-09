from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response

from constants.error_code import ErrorCode
from savnet.log.service import SavnetContrller
from savnet.utils.http_utils import response_data


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


class FPathInfoView(APIView):
    def get(self, request, *args, **kwargs):
        resp_data = test()
        return response_data(data=resp_data)
