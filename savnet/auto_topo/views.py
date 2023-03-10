from rest_framework.views import APIView
from savnet.utils.http_utils import response_data

class SavnetAutoBuildTopology(APIView):
     def get(self, request, *args, **kwargs):
           return response_data(data="auto_build")