from rest_framework.views import APIView
from savnet.utils.http_utils import response_data

class SavnetAutoBuildTopology(APIView):
    def get(self, request, *args, **kwargs):
        topo_list = [{"No": 1, "router_name": "A", "as_no": 65501, "links": [{"B": "customer"}, {"C": "customer"}], "prefixs": ["192.168.0.1"]},
                     {"No": 2, "router_name": "B", "as_no": 65502, "links": [{"A": "provider"}, {"C": "peer"}, {"D": "customer"}], "prefixs": ["192.168.0.2"]},
                     {"No": 3, "router_name": "C", "as_no": 65503, "links": [{"A": "provider"}, {"B": "peer"}, {"E": "customer"}], "prefixs": ["192.168.0.3"]},
                     {"No": 4, "router_name": "D", "as_no": 65504, "links": [{"B": "provider"}, {"F": "customer"}], "prefixs": ["192.168.0.4"]},
                     {"No": 5, "router_name": "E", "as_no": 65505, "links": [{"C": "provider"}, {"G": "customer"}], "prefixs": ["192.168.0.5"]},
                     {"No": 6, "router_name": "F", "as_no": 65506, "links": [{"D": "provider"}, {"H": "customer"}], "prefixs": ["192.168.0.6"]},
                     {"No": 7, "router_name": "G", "as_no": 65507, "links": [{"E": "provider"}, {"H": "peer"}, {"I": "customer"}], "prefixs": ["192.168.0.7"]},
                     {"No": 8, "router_name": "H", "as_no": 65508, "links": [{"F": "provider"}, {"G": "peer"}, {"J": "customer"}], "prefixs": ["192.168.0.8"]},
                     {"No": 9, "router_name": "I", "as_no": 65509, "links": [{"G": "provider"}, {"K": "customer"}], "prefixs": ["192.168.0.9"]},
                     {"No": 10, "router_name": "J", "as_no": 65510, "links": [{"H": "provider"}, {"K": "customer"}], "prefixs": ["192.168.0.10"]},
                     {"No": 11, "router_name": "K", "as_no": 65511, "links": [{"I": "provider"}, {"J": "provider"}], "prefixs": ["192.168.0.11"]}]
        
        # 产生bird的配置文件
        # (1) bird.config

        return response_data(data="auto_build")