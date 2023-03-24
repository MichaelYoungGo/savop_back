from rest_framework.views import APIView
from protocol.utils.http_utils import response_data

class AutoBuildTopology(APIView):
    def get(self, request, *args, **kwargs):
        topo_list = [{"No": 1, "router_name": "A", "as_no": 65501, "links": [{"B": "customer"}, {"C": "customer"}], "prefixs": ["192.168.0.1/24"]},
                     {"No": 2, "router_name": "B", "as_no": 65502, "links": [{"A": "provider"}, {"C": "peer"}, {"D": "customer"}], "prefixs": ["192.168.0.2/24"]},
                     {"No": 3, "router_name": "C", "as_no": 65503, "links": [{"A": "provider"}, {"B": "peer"}, {"E": "customer"}], "prefixs": ["192.168.0.3/24"]},
                     {"No": 4, "router_name": "D", "as_no": 65504, "links": [{"B": "provider"}, {"F": "customer"}], "prefixs": ["192.168.0.4/24"]},
                     {"No": 5, "router_name": "E", "as_no": 65505, "links": [{"C": "provider"}, {"F": "peer"}, {"G": "customer"}], "prefixs": ["192.168.0.5/24"]},
                     {"No": 6, "router_name": "F", "as_no": 65506, "links": [{"D": "provider"}, {"E": "peer"}, {"H": "customer"}], "prefixs": ["192.168.0.6/24"]},
                     {"No": 7, "router_name": "G", "as_no": 65507, "links": [{"E": "provider"}, {"H": "peer"}, {"I": "customer"}], "prefixs": ["192.168.0.7/24"]},
                     {"No": 8, "router_name": "H", "as_no": 65508, "links": [{"F": "provider"}, {"G": "peer"}, {"J": "customer"}], "prefixs": ["192.168.0.8/24"]},
                     {"No": 9, "router_name": "I", "as_no": 65509, "links": [{"G": "provider"}, {"K": "customer"}], "prefixs": ["192.168.0.9/24"]},
                     {"No": 10, "router_name": "J", "as_no": 65510, "links": [{"H": "provider"}, {"K": "customer"}], "prefixs": ["192.168.0.10/24"]},
                     {"No": 11, "router_name": "K", "as_no": 65511, "links": [{"I": "provider"}, {"J": "provider"}], "prefixs": ["192.168.0.11/24"]}]
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
            router_name = router["router_name"].lower()
            as_no = router["as_no"]
            content = f"router id {router_id}\n"
            content += "protocol device {\n\tscan time 60;\n};\n"
            content +=  "protocol kernel {\n\tscan time 60;\n\tipv4 {\n\t\texport all;\n\t\timport all;\n};\n\tlearn;\n\tpersist;\n};\n"
            content += f'protocol direct {{\n\tipv4;\n\tinterface "{router_name}_*";\n}};\n'
            content += "protocol static {\n\tipv4 {\n\t\texport all;\n\t\timport all;\n\t};"
            for prefix in router["prefixs"]:
                content += f"\n\troute {prefix} blackhole;"
            content += "\n};\n"
            content += f"template bgp sav_inter{{\n\tlocal as {as_no};\n\tlong lived graceful restart on;\n\tdebug all; \
                \n\tsavnet4{{\n\t\timport none;\n\t\texport none;\n\t}};\n\tipv4{{\n\t\texport all;\n\t\timport all;\n\t}}; \
                \n\tenable extended messages;\n}};\n"
            for interface_name, interface_value in router["net_interface"].items():
                router_name, role, IP_Addr = router_name.upper(), interface_value["role"], interface_value["IP_Addr"],
                peer_router_name = interface_name.split("_")[1].upper()
                peer_interface = interface_name.split("_")[1] + "_" + interface_name.split("_")[0]
                for peer_router in topo_list:
                    if peer_router["router_name"] != peer_router_name:
                        continue
                    peer_router_as_No = peer_router["No"]
                    peer_interface_IP_Addr = peer_router["net_interface"][peer_interface]["IP_Addr"]
                    break
                protocol_name = interface_name.split("_")[0] + interface_name.split("_")[1]
                content += f'protocol bgp savbgp_{protocol_name} from sav_inter{{ \
                    \n\tdescription "modified BGP between node {router_name} and {peer_router_name}"; \
                    \n\tlocal role {role}; \
                    \n\tsource address {IP_Addr}; \
                    \n\tneighbor {peer_interface_IP_Addr}  as {peer_router_as_No}; \
                    \n\tinterface "{interface_name}"; \
                    \n\tdirect;\n}};\n'
            with open(f"/root/test/configs/{index+1}.conf", "w") as f:
                f.write(content)
        # (1) bird.config
        json_content = '{ \
                \n\t"valid_prefixes": [], \
                \n\t"invalid_prefixes": [], \
                \n\t"required_clients": [ \
                \n\t\t"bird","strict-uRPF","loose-uRPF" \
                \n\t] \
            \n}\n'
        for index in range(0, len(topo_list)):
            with open(f"/root/test/configs/{index+1}.json", "w") as f:
                f.write(json_content)
        # docker-compose.yml
        yml_content = '"version: "2"\nservices:"\n'
        for index in range(0, len(topo_list)):
            with open(f"/root/test/docker-compose.yml", "w") as f:
                f.write(yml_content)
                
        return response_data(data="auto_build")