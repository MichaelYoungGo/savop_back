from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response

from constants.error_code import ErrorCode
from savnet.log.service import test, SavnetContrller
from savnet.utils.http_utils import response_data


class CollectSavnetTopologyProgressData(APIView):
    def get(self, request, *args, **kwargs):
        # SavnetContrller.get_log_data(path="/root/test/logs")
        routers_info = SavnetContrller.get_routers_info()
        links_info = SavnetContrller.get_links_info()
        prefixs_info = SavnetContrller.get_prefixs_info()
        data = {}
        data.update(routers_info)
        data.update(links_info)
        data.update(prefixs_info)
        return response_data(data=data)


class FPathInfoView(APIView):
    def get(self, request, *args, **kwargs):
        resp_data = test()
        return response_data(data=resp_data)
