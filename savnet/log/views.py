from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response

from constants.error_code import ErrorCode
from savnet.log import service
from savnet.utils.http_utils import response_data


class FPathInfoView(APIView):
    def get(self, request, *args, **kwargs):
        resp_data = service.test()
        return response_data(data=resp_data)
