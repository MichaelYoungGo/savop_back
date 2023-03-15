from rest_framework.views import APIView
from savnet.utils.http_utils import response_data

class SavnetAutoBuildTopology(APIView):
    def get(self, request, *args, **kwargs):
        topo_list = [{"No": 1, "router_name": "A", "links": [{"B": "customer"}, {"C": "customer"}]},
                     {"No": 2, "router_name": "B", "links": [{"A": "provider"}, {"C": "peer"}, {"D": "customer"}]},
                     {"No": 3, "router_name": "C", "links": [{"A": "provider"}, {"B": "peer"}, {"E": "customer"}]},
                     {"No": 4, "router_name": "D", "links": [{"B": "provider"}, {"F": "customer"}]},
                     {"No": 5, "router_name": "E", "links": [{"C": "provider"}, {"G": "customer"}]},
                     {"No": 6, "router_name": "F", "links": [{"D": "provider"}, {"H": "customer"}]},
                     {"No": 7, "router_name": "G", "links": [{"E": "provider"}, {"H": "peer"}, {"I": "customer"}]},
                     {"No": 8, "router_name": "H", "links": [{"F": "provider"}, {"G": "peer"}, {"J": "customer"}]},
                     {"No": 9, "router_name": "I", "links": [{"G": "provider"}, {"K": "customer"}]},
                     {"No": 10, "router_name": "J", "links": [{"H": "provider"}, {"K": "customer"}]},
                     {"No": 11, "router_name": "K", "links": [{"I": "provider"}, {"J": "provider"}]}]
        return response_data(data="auto_build")