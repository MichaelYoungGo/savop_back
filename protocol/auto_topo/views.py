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
        # (2) docker-compose.yml
        yml_content = 'version: "2"\nservices:\n'
        for index in range(0, len(topo_list)):
            pos = index + 1
            router_name = topo_list[index]["router_name"]
            content = f"  node_{pos}: \
            \n  # {router_name} \
            \n    image: savop_bird_base \
            \n    container_name: node_{pos} \
            \n    cap_add: \
            \n      - NET_ADMIN \
            \n    volumes: \
            \n      - ./configs/{pos}.conf:/usr/local/etc/bird.conf \
            \n      - ./configs/{pos}.json:/root/savnet_bird/SavAgent_config.json \
            \n      - ./logs/{pos}/:/root/savnet_bird/logs/ \
            \n    network_mode: none \
            \n    command: \
            \n        bash container_run.sh\n"
            yml_content = yml_content + content
        with open(f"/root/test/docker-compose.yml", "w") as f:
            f.write(yml_content)
        #(3) host_run.sh
        host_run_content = '#!/usr/bin/bash\
        \n# set -ex\
        \n# rm -f  "./bird" "./birdc" "./birdcl"\
        \n\
        \n# make\
        \nif [ -f "./bird" ] && [ -f "./birdc" ] && [ -f "./birdcl" ];then\
        \n  echo "adding edge the three files, bird birdc birdcl, are all ready"\
        \nelse \
        \n  echo "adding edge lack file bird birdc birdcl"\
        \nexit -1\
        \nfi\
        \ndocker-compose down\
        \ndocker build . -t savop_bird_base\
        \nnode_array=('
        for pos in range(1, len(topo_list) + 1):
            host_run_content += f'"{pos}" '
        host_run_content += ")"
        host_run_content += '\
        \ndocker container rm $(docker container ls -aq)\
        \n# remove all stopped containers\
        \ndocker rmi $(docker images --filter "dangling=true" -q --no-trunc)\
        \n# remove all images taged as <none>\
        \nfor node_num in ${node_array[*]}\
        \ndo\
        \n    rm -rf ./logs/$node_num/*\
        \ndone\
        \ndocker-compose up -d --force-recreate  --remove-orphans\
        \n\n\
        \n# remove folders created last time\
        \nrm -r /var/run/netns\
        \nmkdir /var/run/netns\
        \n\
        \n# node_array must be countinus mubers\
        \npid_array=()\
        \nfor node_num in ${node_array[*]}\
        \ndo\
        \n    temp=$(sudo docker inspect -f \'\{\{.State.Pid\}\}\' node_$node_num)\
        \n    ln -s /proc/$temp/ns/net /var/run/netns/$temp\
        \n    pid_array+=($temp)\
        \ndone\
        \n\
        \nfunCreateV(){\
        \n    # para 1: local node in letter, must be lowercase;a\
        \n    # para 2: peer node in letter, must be lowercase;b\
        \n    # para 3: local node in number,;1\
        \n    # para 4: peer node in number,2\
        \n    # para 5: the IP addr of the local node interface\
        \n    # para 6: the IP addr of the peer node interface\
        \n    PID_L=${pid_array[$3-1]}\
        \n    PID_P=${pid_array[$4-1]}\
        \n    NET_L=$1\
        \n    NET_P=$2\
        \n    ip link add ${NET_L} type veth peer name ${NET_P}\
        \n    ip link set ${NET_L}  netns ${PID_L}\
        \n    ip link set ${NET_P}  netns ${PID_P}\
        \n    ip netns exec ${PID_L} ip addr add ${5} dev ${NET_L}\
        \n    ip netns exec ${PID_L} ip link set ${NET_L} up\
        \n    ip netns exec ${PID_P} ip addr add ${6} dev ${NET_P}\
        \n    ip netns exec ${PID_P} ip link set ${NET_P} up\
        \n}\
        '

        net_interface_name_list = []
        net_interface_dict = {} 
        for router in topo_list:
            net_interface_name_list += router["net_interface"].keys()
            net_interface_dict.update(router["net_interface"])
        while len(net_interface_name_list) != 0:
            local_interface = net_interface_name_list.pop(0)
            peer_interface = local_interface.split("_")[1] + "_" + local_interface.split("_")[0] 
            index = net_interface_name_list.index(peer_interface)
            net_interface_name_list.pop(index)
            locol_router_name, peer_router_name  = local_interface.split("_")[0].upper(), peer_interface.split("_")[0].upper()
            for index in range(0, len(topo_list)):
                if topo_list[index]["router_name"] == locol_router_name:
                    local_pos = index + 1
                if topo_list[index]["router_name"] == peer_router_name:
                    peer_pos = index + 1
            local_interface_IP_Addr, peer_interface_IP_Addr = net_interface_dict[local_interface]["IP_Addr"], net_interface_dict[peer_interface]["IP_Addr"]
            host_run_content += f"\
            \n#1 {locol_router_name}-{peer_router_name}\
            \necho \"adding edge {locol_router_name}-{peer_router_name}\"\
            \nfunCreateV {local_interface} {peer_interface} {local_pos} {peer_pos} {local_interface_IP_Addr} {peer_interface_IP_Addr}"

        host_run_content += "\nsleep 1"
        for index in range(0, len(topo_list)):
             router_name = topo_list[index]["router_name"]
             pos = index + 1
             host_run_content += f"\necho '========================node {router_name} log========================'\
                \n docker logs node_{pos}"
        host_run_content += "\n# wait for the containers to perform, you can change the value based \
        \n # on your hardware and configurations"
        host_run_content += "\nsleep 30"
        for index in range(0, len(topo_list)):
             router_name = topo_list[index]["router_name"]
             pos = index + 1
             host_run_content += f"\necho '========================node {router_name} route========================'\
                \ndocker exec -it node_{pos} route -n -F"
        
        host_run_content += "\ndocker exec -it node_1 birdc show route all"
        host_run_content += "\nsleep 1"
        host_run_content += "\nFOLDER=$(cd \"$(dirname \"$0\")\";pwd)"
        host_run_content += "\nfor node_num in $\{node_array[*]\}\
            \ndo\
            \n    docker exec -it node_${node_num} route -n -F >${FOLDER}/logs/${node_num}/router_table.txt 2>&1\
            \n    docker exec -it node_${node_num} curl -s http://localhost:8888/sib_table/ >${FOLDER}/logs/${node_num}/sav_table.txt 2>&1\
            \ndone\
            "
        host_run_content += "\ndocker-compose down"
        with open(f"/root/test/host_run.sh", "w") as f:
            f.write(host_run_content)
        return response_data(data="auto_build")