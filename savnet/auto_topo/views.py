from rest_framework.views import APIView
from savnet.utils.http_utils import response_data

class SavnetAutoBuildTopology(APIView):
    def get(self, request, *args, **kwargs):
        topo_list = [{"No": 1, "router_name": "A", "as_no": 65501, "links": [{"B": "customer"}, {"C": "customer"}], "prefixs": ["192.168.0.1"]},
                     {"No": 2, "router_name": "B", "as_no": 65502, "links": [{"A": "provider"}, {"C": "peer"}, {"D": "customer"}], "prefixs": ["192.168.0.2"]},
                     {"No": 3, "router_name": "C", "as_no": 65503, "links": [{"A": "provider"}, {"B": "peer"}, {"E": "customer"}], "prefixs": ["192.168.0.3"]},
                     {"No": 4, "router_name": "D", "as_no": 65504, "links": [{"B": "provider"}, {"F": "customer"}], "prefixs": ["192.168.0.4"]},
                     {"No": 5, "router_name": "E", "as_no": 65505, "links": [{"C": "provider"}, {"F": "peer"}, {"G": "customer"}], "prefixs": ["192.168.0.5"]},
                     {"No": 6, "router_name": "F", "as_no": 65506, "links": [{"D": "provider"}, {"E": "peer"}, {"H": "customer"}], "prefixs": ["192.168.0.6"]},
                     {"No": 7, "router_name": "G", "as_no": 65507, "links": [{"E": "provider"}, {"H": "peer"}, {"I": "customer"}], "prefixs": ["192.168.0.7"]},
                     {"No": 8, "router_name": "H", "as_no": 65508, "links": [{"F": "provider"}, {"G": "peer"}, {"J": "customer"}], "prefixs": ["192.168.0.8"]},
                     {"No": 9, "router_name": "I", "as_no": 65509, "links": [{"G": "provider"}, {"K": "customer"}], "prefixs": ["192.168.0.9"]},
                     {"No": 10, "router_name": "J", "as_no": 65510, "links": [{"H": "provider"}, {"K": "customer"}], "prefixs": ["192.168.0.10"]},
                     {"No": 11, "router_name": "K", "as_no": 65511, "links": [{"I": "provider"}, {"J": "provider"}], "prefixs": ["192.168.0.11"]}]
        # 产生网口、IP、router_id
        # 网口
        for node in topo_list:
            router_name, links = node["router_name"], node["links"]
            net_interface = {}
            for link in links:
                net_interface_name = router_name.lower() + "_" + list(link.keys())[0].lower()
                net_interface.update({net_interface_name: {"role": list(link.values())[0], "IP_Addr": None}})
                node.update({"net_interface": net_interface})
        # IP
        net_seg = 1
        for node in topo_list:
            net_interface = node["net_interface"]
            for net_interface_name, net_interface_info in net_interface.items():
                IP_Addr = net_interface_info.get("IP_Addr")
                if IP_Addr is None:
                    net_interface_info["IP_Addr"] = "10.0." + str(net_seg) + ".1"
                    for peer_node in topo_list:
                        net_interface_str = net_interface_name.split("_")
                        if peer_node["router_name"] != net_interface_str[1].upper():
                            continue
                        peer_net_interface = net_interface_str[1].lower() + "_" + net_interface_str[0].lower()
                        if peer_node["net_interface"][peer_net_interface]["IP_Addr"] is not None:
                            break
                        else:
                            peer_node["net_interface"][peer_net_interface]["IP_Addr"] = "10.0." + str(net_seg) + ".2"
                            break
                    net_seg += 1
        # Router_id
        for node in topo_list:
            router_id = "10.255.255.255"
            for value in list(node["net_interface"].values()):
                if value["IP_Addr"] < router_id:
                    router_id = value["IP_Addr"]
            node["router_id"] = router_id
            router_id = "10.255.255.255"
        # 产生bird的配置文件
        # (1) bird.config
        for index in range(0, len(topo_list)):
            router = topo_list[index]
            router_id = router["router_id"]
            content = f"router id {router_id}\n"
            content +=  "protocol device {\n\tscan time 60;\n};"
            content +=  "protocol kernel {\n\tscan time 60;\n\t\tipv4 {\n\t\t\texport all;\n\t\timport all;\n};\n\t\tlearn;\n\t\t\tpersist;\n};"
        return response_data(data="auto_build")