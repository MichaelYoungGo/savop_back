# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ConfigGenerator
   Description :
   Author :       MichaelYoung
   date：          2023/8/16
-------------------------------------------------
   Change Activity:
                   2023/8/16:
-------------------------------------------------
"""
import json
import copy
import queue
import time
from datetime import datetime
import subprocess

start = 0

DEPLOY_DIR = "/root/sav_simulate/sav-start"


class BirdConfigGenerator:
    def config_generator(self, topo_list):
        print("创建bird的配置文件")
        for index in range(0, len(topo_list)):
            router = topo_list[index]
            router_id = router["router_id"]
            router_name = router["router_name"].lower()
            as_no = router["as_no"]
            content = f"router id {router_id};\n"
            content += "ipv4 table master4{\n\tsorted 1;\n};\n"
            content += "roa4 table r4{\n\tsorted 1;\n};\n"
            content += "protocol device {\n\tscan time 60;\n\tinterface \"eth_*\";\n};\n"
            content += "protocol kernel {" \
                       "\n\tscan time 60;" \
                       "\n\tipv4 {" \
                       "\n\t\texport all;" \
                       "\n\t\timport all;" \
                       "\n\t};" \
                       "\n\tlearn;" \
                       "\n\tpersist;" \
                       "\n};\n"
            content += 'protocol direct {\n\tipv4;\n\tinterface "eth_*";\n};\n'
            content += "protocol static {\n\tipv4 {\n\t\texport all;\n\t\timport all;\n\t};"
            for prefix in router["prefixs"]:
                if "0.0.0.0" in prefix:
                    continue
                content += f"\n\troute {prefix} blackhole;"
            content += "\n};\n"
            content += f"template bgp basic{{\n\tlocal as {as_no};\n\tlong lived graceful restart on;\n\tdebug all;" \
                       f"\n\tenable extended messages;" \
                       f"\n\tipv4{{" \
                       f"\n\t\texport all;" \
                       f"\n\t\timport all;" \
                       f"\n\t\timport table on;" \
                       f"\n\t}};\n}};\n"
            content += "template bgp sav_inter from basic{" \
                       "\n\trpdp4{" \
                       "\n\t\timport none;" \
                       "\n\t\texport none;" \
                       "\n\t};\n};\n"
            for interface_name, interface_value in router["net_interface"].items():
                router_name, role, IP_Addr = router_name, interface_value["role"], interface_value["IP_Addr"],
                peer_router_name = interface_name.replace("eth", "node")
                peer_interface = "eth_" + as_no
                for peer_router in topo_list:
                    if peer_router["router_name"] != peer_router_name:
                        continue
                    peer_router_as_No = peer_router["as_no"]
                    peer_interface_IP_Addr = peer_router["net_interface"][peer_interface]["IP_Addr"]
                    break
                protocol_name = str(as_no) + "_" + peer_router_name.split("_")[1]
                content += f'protocol bgp savbgp_{protocol_name} from sav_inter{{ \
                    \n\tdescription "modified BGP between node {router_name} and {peer_router_name}"; \
                    \n\tlocal role {role}; \
                    \n\tsource address {IP_Addr}; \
                    \n\tneighbor {peer_interface_IP_Addr}  as {peer_router_as_No}; \
                    \n\tinterface "{interface_name}"; \
                    \n\tdirect;\n}};\n'
            with open(f"{DEPLOY_DIR}/configs/conf_nsdi/{as_no}.conf", "w") as f:
                f.write(content)

    def config_limit_prefix_length_generator(self, topo_list):
        print("创建bird的配置文件")
        for index in range(0, len(topo_list)):
            prefix_length = 100
            router = topo_list[index]
            router_id = router["router_id"]
            router_name = router["router_name"].lower()
            as_no = router["as_no"]
            content = f"router id {router_id};\n"
            content += "ipv4 table master4{\n\tsorted 1;\n};\n"
            content += "roa4 table r4{\n\tsorted 1;\n};\n"
            content += "protocol device {\n\tscan time 60;\n\tinterface \"eth_*\";\n};\n"
            content += "protocol kernel {" \
                       "\n\tscan time 60;" \
                       "\n\tipv4 {" \
                       "\n\t\texport all;" \
                       "\n\t\timport all;" \
                       "\n\t};" \
                       "\n\tlearn;" \
                       "\n\tpersist;" \
                       "\n};\n"
            content += 'protocol direct {\n\tipv4;\n\tinterface "eth_*";\n};\n'
            content += "protocol static {\n\tipv4 {\n\t\texport all;\n\t\timport all;\n\t};"
            for prefix in router["prefixs"]:
                if "0.0.0.0" in prefix:
                    continue
                prefix_length -= 1
                content += f"\n\troute {prefix} blackhole;"
                if prefix_length == 0:
                    break
            content += "\n};\n"
            content += f"template bgp basic{{\n\tlocal as {as_no};\n\tlong lived graceful restart on;\n\tdebug all;" \
                       f"\n\tenable extended messages;" \
                       f"\n\tipv4{{" \
                       f"\n\t\texport all;" \
                       f"\n\t\timport all;" \
                       f"\n\t\timport table on;" \
                       f"\n\t}};\n}};\n"
            content += "template bgp sav_inter from basic{" \
                       "\n\trpdp4{" \
                       "\n\t\timport none;" \
                       "\n\t\texport none;" \
                       "\n\t};\n};\n"
            proto_count = 0
            for interface_name, interface_value in router["net_interface"].items():
                router_name, role, IP_Addr = router_name, interface_value["role"], interface_value["IP_Addr"],
                peer_router_name = interface_name.replace("eth", "node")
                peer_interface = "eth_" + as_no
                for peer_router in topo_list:
                    if peer_router["router_name"] != peer_router_name:
                        continue
                    peer_router_as_No = peer_router["as_no"]
                    peer_interface_IP_Addr = peer_router["net_interface"][peer_interface]["IP_Addr"]
                    protocol_name = str(as_no) + "_" + peer_router_name.split("_")[1]
                    # delay参数，网络端口延迟启动
                    content += f'protocol bgp savbgp_{protocol_name} from sav_inter{{ \
                        \n\tdescription "modified BGP between node {router_name} and {peer_router_name}"; \
                        \n\tlocal role {role}; \
                        \n\tsource address {IP_Addr}; \
                        \n\tneighbor {peer_interface_IP_Addr}  as {peer_router_as_No}; \
                        \n\tinterface "{interface_name}"; \
                        \n\tconnect delay time {proto_count}; \
                        \n\tdirect;\n}};\n'
                proto_count += 1
            with open(f"{DEPLOY_DIR}/configs/conf_nsdi/{as_no}.conf", "w") as f:
                f.write(content)


class SavAgentConfigGenerator:
    def config_generator(self, topo_list):
        print("创建SavAgent的配置文件")
        for index in range(0, len(topo_list)):
            node = topo_list[index]
            router_name = node["router_name"]
            grpc_id = node["router_id"]
            local_as = node["as_no"]
            id_ = node["router_id"]
            # 使用quic之后将配置文件格式进行了调整，调整了SavAgent.json的格式
            # links = []
            # for interface_name, interface_value in node["net_interface"].items():
            #     local_interface_role = interface_value["role"]
            #     for peer_router in topo_list:
            #         peer_router_name = interface_name.replace("eth", "node")
            #         if peer_router["router_name"] != peer_router_name:
            #             continue
            #         peer_router_as_no = peer_router["as_no"]
            #         peer_interface_name = router_name.replace("node", "eth")
            #         peer_interface_IP_Addr = peer_router["net_interface"][peer_interface_name]["IP_Addr"]
            #         peer_router_id = peer_router["router_id"]
            #         peer_role = peer_router["net_interface"][peer_interface_name]["role"]
            #         links.append({"remote_addr": f"{peer_interface_IP_Addr}:5000", "remote_as": peer_router_as_no,
            #                       "remote_id": peer_router_id, "local_role": local_interface_role,
            #                       "interface_name": interface_name})
            #         break
            # links_str = json.dumps(links)
            # json_content = f'{{' \
            #                '\n\t"apps": [' \
            #                '\n\t\t"strict-uRPF",' \
            #                '\n\t\t"rpdp_app",' \
            #                '\n\t\t"loose-uRPF",' \
            #                '\n\t\t"EFP-uRPF-A",' \
            #                '\n\t\t"EFP-uRPF-B",' \
            #                '\n\t\t"FP-uRPF"' \
            #                '\n\t],' \
            #                '\n\t"enabled_sav_app": "rpdp_app",' \
            #                '\n\t"fib_stable_threshold": 5,' \
            #                '\n\t"ca_host": "10.10.0.2",' \
            #                '\n\t"ca_port": 3000,' \
            #                '\n\t"grpc_server_addr": "0.0.0.0:5000",' \
            #                f'\n\t"grpc_id": "{grpc_id}",' \
            #                f'\n\t"local_as":{local_as},' \
            #                '\n\t"grpc_config": {' \
            #                '\n\t\t"server_addr": "0.0.0.0:5000",' \
            #                f'\n\t\t"id": "{id_}",' \
            #                f'\n\t\t"local_as": {local_as},' \
            #                f'\n\t\t"enabled": false,' \
            #                f'\n\t\t"links": {links_str}' \
            #                '\n\t},' \
            #                '\n\t"location": "edge"' \
            #                '\n}\n'
            # 新的SavAgent.json格式
            link_map = {}
            for interface_name, interface_value in node["net_interface"].items():
                for peer_router in topo_list:
                    peer_router_name = interface_name.replace("eth", "node")
                    if peer_router["router_name"] != peer_router_name:
                        continue
                    peer_router_as_no = peer_router["as_no"]
                    peer_interface_name = router_name.replace("node", "eth")
                    peer_interface_IP_Addr = peer_router["net_interface"][peer_interface_name]["IP_Addr"]
                    peer_router_id = peer_router["router_id"]
                    link_map.update({f"savbgp_{local_as}_{peer_router_as_no}": {
                        "link_type": "grpc",
                        "link_data": {
                                         "remote_addr": f"{peer_interface_IP_Addr}:5000",
                                         "remote_addr": peer_router_id}}})
                    break
            link_map_str = json.dumps(link_map)
            # 不做quic实验时，不需要使用link_map信息
            link_map_str = {}
            json_content = '{' \
                           '\n\t"apps": [' \
                           '\n\t\t"strict-uRPF",' \
                           '\n\t\t"rpdp_app",' \
                           '\n\t\t"loose-uRPF",' \
                           '\n\t\t"EFP-uRPF-A",' \
                           '\n\t\t"EFP-uRPF-B",' \
                           '\n\t\t"FP-uRPF"' \
                           '\n\t],' \
                           '\n\t"enabled_sav_app": "rpdp_app",' \
                           '\n\t"fib_stable_threshold": 5,' \
                           '\n\t"ca_host": "10.10.0.2",' \
                           '\n\t"ca_port": 3000,' \
                           '\n\t"grpc_config": {' \
                           '\n\t\t"server_addr": "0.0.0.0:5000",' \
                           '\n\t\t"server_enabled": false' \
                           '\n\t},' \
                           f'\n\t"link_map": {link_map_str},' \
                           '\n\t"quic_config": {"server_enabled": true},' \
                           f'\n\t"local_as":{local_as},' \
                           f'\n\t"rpdp_id": "{id_}",' \
                           '\n\t"location": "edge_full"' \
                           '\n}\n'
            with open(f"{DEPLOY_DIR}/configs/conf_nsdi/{local_as}.json", "w") as f:
                f.write(json_content)


class TopoConfigGenerator:
    def config_generator(self, topo_list):
        print("创建网络拓扑的配置文件")
        host_run_content = '#!/usr/bin/bash' \
                           '\n# remove folders created last time' \
                           '\nrm -r /var/run/netns' \
                           '\nmkdir /var/run/netns' \
                           '\n' \
                           '\nnode_array=('
        as_no_list = []
        for pos in range(1, len(topo_list) + 1):
            as_no = topo_list[pos-1]["as_no"]
            as_no_list.append(as_no)
            host_run_content += f'"{as_no}" '
        host_run_content += ")"
        host_run_content += '\n# node_array must be countinus mubers'
        host_run_content += '\npid_array=()'
        host_run_content += '\nfor node_num in ${node_array[*]}\
                \ndo\
                \n    temp=$(sudo docker inspect -f \'{{.State.Pid}}\' node_$node_num)\
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
                \n    PID_L=${pid_array[$3]}\
                \n    PID_P=${pid_array[$4]}\
                \n    NET_L=$1\
                \n    NET_P=$2\
                \n    ip link add ${NET_L} type veth peer name ${NET_P}\
                \n    ip link set ${NET_L}  netns ${PID_L}\
                \n    ip link set ${NET_P}  netns ${PID_P}\
                \n    ip netns exec ${PID_L} ip addr add ${5} dev ${NET_L}\
                \n    ip netns exec ${PID_L} ip link set ${NET_L} up\
                \n    ip netns exec ${PID_P} ip addr add ${6} dev ${NET_P}\
                \n    ip netns exec ${PID_P} ip link set ${NET_P} up\
                \n}' \
        # 添加网口与IP
        ##########################################################################################
        topo_list_copy = copy.deepcopy(topo_list)
        for node in topo_list_copy:
            local_router_as_no = node["as_no"]
            local_router_name = node["router_name"]
            net_interface_name_list = list(node["net_interface"].keys())
            while len(net_interface_name_list) != 0:
                local_interface_name = net_interface_name_list.pop(0)
                local_interface_IP_Addr = node["net_interface"][local_interface_name]["IP_Addr"]
                del node["net_interface"][local_interface_name]
                peer_interface_name = local_router_name.replace("node", "eth")
                peer_router_name = local_interface_name.replace("eth", "node")
                peer_router_as_No = peer_router_name.split("_")[1]
                if peer_router_as_No not in as_no_list:
                    continue
                for peer_router in topo_list_copy:
                    if peer_router["router_name"] != peer_router_name:
                        continue
                    peer_router_as_No = peer_router["as_no"]
                    peer_interface_IP_Addr = peer_router["net_interface"][peer_interface_name]["IP_Addr"]
                    del peer_router["net_interface"][peer_interface_name]
                    break
                local_pos = as_no_list.index(local_router_as_no)
                peer_pos = as_no_list.index(peer_router_as_No)
                host_run_content += f"\n# {local_router_name}-{peer_router_as_No}\
                        \necho \"adding edge {local_router_name}-{peer_router_as_No}\"\
                        \nsleep 0.5\
                        \nfunCreateV '{local_interface_name}' '{peer_interface_name}' '{local_pos}' '{peer_pos}' '{local_interface_IP_Addr}/24' '{peer_interface_IP_Addr}/24'"
        ###########################################################################################
        host_run_content += "\nsleep 15"
        host_run_content += "\nFOLDER=$(cd \"$(dirname \"$0\")\";pwd)"
        host_run_content += '\nfor node_num in ${node_array[*]}' \
                            '\ndo' \
                            '\n\techo "======================== node_$node_num log========================"' \
                            '\n\tdocker logs node_${node_num}' \
                            '\n\techo "======================== node_$node_num FIB========================"' \
                            '\n\tdocker exec -it node_${node_num} route -n -F' \
                            '\n\tdocker exec -it node_${node_num} route -n -F >${FOLDER}/logs/${node_num}/router_table.txt 2>&1' \
                            '\n\tdocker exec -it node_${node_num} curl -s http://localhost:8888/sib_table/ >${FOLDER}/logs/${node_num}/sav_table.txt 2>&1' \
                            '\ndone\n'
        with open(f"{DEPLOY_DIR}/topology/topo_nsdi.sh", "w") as f:
            f.write(host_run_content)


class CaConfigGenerator:
    def config_generator(self, topo_list):
        print("创建产生CA配置的脚本")
        bash_content = '#!/usr/bin/bash' \
                       '\nset -e' \
                       '\n# CA' \
                       '\nCA_FOLDER=./ca' \
                       '\nCA_KEY=$CA_FOLDER/key.pem' \
                       '\nCA_CER=$CA_FOLDER/cert.pem' \
                       '\nfunCGenPrivateKeyAndSign(){' \
                       '\n\tCA_KEY=$2/key.pem' \
                       '\n\tCA_CER=$2/cert.pem' \
                       '\n\tCNF=$1/../../req.conf' \
                       '\n\tKEY=$1/key.pem' \
                       '\n\tCSR=$1/cert.csr' \
                       '\n\tCER=$1/cert.pem' \
                       '\n\tEXT=$1/sign.ext' \
                       '\n\trm -f $CSR' \
                       '\n\trm -f $CER' \
                       '\n\trm -f $KEY' \
                       '\n\topenssl genpkey -algorithm RSA -outform PEM -out $KEY' \
                       '\n\topenssl req -new -key $KEY -out $CSR -config $CNF' \
                       '\n\topenssl x509 -req -in  $CSR -CA $CA_CER -CAkey $CA_KEY -CAcreateserial -out $CER -days 365 -extfile $EXT' \
                       '\n}\n'
        for index in range(0, len(topo_list)):
            router_name = topo_list[index]["router_name"]
            as_no = topo_list[index]["as_no"]
            content = f'echo "start refresh container {router_name} ca"\n'
            content += f"funCGenPrivateKeyAndSign ./node_nsdi/node_{as_no} ./ca\n"
            bash_content = bash_content + content
        with open(f"{DEPLOY_DIR}/certification_authority/refresh_key_nsdi.sh", "w") as f:
            f.write(bash_content)
        # 生成每个结点的证书
        for index in range(0, len(topo_list)):
            router_name = topo_list[index]["router_name"]
            create_node_dir_command = f"mkdir -p {DEPLOY_DIR}/certification_authority/node_nsdi/{router_name}"
            result = subprocess.run(create_node_dir_command, shell=True, capture_output=True, encoding='utf-8')
            sign_content = 'authorityKeyIdentifier=keyid,issuer' \
                           '\nbasicConstraints=CA:FALSE' \
                           '\nkeyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment' \
                           f'\nsubjectAltName = DNS:{router_name}, DNS:localhost'
            with open(f"{DEPLOY_DIR}/certification_authority/node_nsdi/{router_name}/sign.ext", "w") as f:
                f.write(sign_content)


class DockerComposeGenerator:
    def config_generator(self, topo_list, container_run_command="bash container_run.sh"):
        print("创建DockerCompose的配置文件")
        yml_content = 'version: "2"\nservices:\n'
        for index in range(0, len(topo_list)):
            router_name = topo_list[index]["router_name"]
            as_no = topo_list[index]["as_no"]
            content = f"  {router_name}: \
                    \n    image: savop_bird_base \
                    \n    init: true \
                    \n    container_name: {router_name} \
                    \n    cap_add: \
                    \n      - NET_ADMIN \
                    \n    volumes: \
                    \n      - ./configs/{as_no}.conf:/usr/local/etc/bird.conf \
                    \n      - ./configs/{as_no}.json:/root/savop/SavAgent_config.json \
                    \n      - ./logs/{as_no}/:/root/savop/logs/ \
                    \n      - ./logs/{as_no}/data:/root/savop/sav-agent/data/ \
                    \n      - ./signal:/root/savop/signal \
                    \n      - /etc/localtime:/etc/localtime \
                    \n      - ./nodes/{router_name}/cert.pem:/root/savop/cert.pem \
                    \n      - ./nodes/{router_name}/key.pem:/root/savop/key.pem \
                    \n      - ./ca/cert.pem:/root/savop/ca_cert.pem \
                    \n    network_mode: none \
                    \n    command: \
                    \n        {container_run_command} \
                    \n    privileged: true\n"
            yml_content = yml_content + content
        with open(f"{DEPLOY_DIR}/docker_compose/docker_compose_nsdi.yml", "w") as f:
            f.write(yml_content)


class ConfigGenerator:
    mode_data = {}
    business_relationship_data = {}
    topo_list = []
    topo_list_bfs = []
    sav_agent_config_generator = SavAgentConfigGenerator()
    bird_config_generator = BirdConfigGenerator()
    topo_config_generator = TopoConfigGenerator()
    docker_compose_generator = DockerComposeGenerator()
    ca_config_generator = CaConfigGenerator()

    def __init__(self, mode_file_path, business_relation_file_path):
        self.mode_data = self.mode_data_analysis(path=mode_file_path)
        self.business_relationship_data = self.business_relation_data_analysis(path=business_relation_file_path)
        self.topo_list = self._convert_data_format()
        self.topo_list_bfs = self._BFS(topo_list=self.topo_list)
        print("\n")

    def mode_data_analysis(self, path):
        print(f"分析{path}, 获取模型数据")
        with open(path, "r") as file:
            data = json.load(file)
        print("检查网络结点的直连关系，必须确保两两配对")
        for as_num in data.keys():
            neighbors_list = data[as_num]["neighbors"]
            for neighbor_num in neighbors_list:
                if as_num not in data[neighbor_num]["neighbors"]:
                    data[neighbor_num]["neighbors"].append(as_num)
        return data

    def business_relation_data_analysis(self, path):
        print(f"解析{path}，商业关系数据")
        business_relation_data = {}
        with open(path, "r") as file:
            for line in file:
                content_list = line.replace("\n", '').split("|")
                if len(content_list) != 3:
                    raise
                key, value = content_list[0] + "-" + content_list[1], int(content_list[2])
                if key in business_relation_data.keys():
                    raise
                business_relation_data.update({key: value})
        return business_relation_data

    def _convert_data_format(self):
        print("转换数据格式，补充所有关键字段")
        index = 1
        topo_list = []
        # 确定商业关系
        for as_num, as_content in self.mode_data.items():
            node = {"No": index, "router_name": f"node_{as_num}", "as_no": as_num, "prefixs": as_content["prefix"]}
            links = self._get_business_role(as_num, as_content["neighbors"])
            node["links"] = links
            if len(links) == 0:
                # 一个结点所有的商业关系都无法确定，则舍弃这个结点
                continue
            topo_list.append(node)
            index += 1
        # 产生网口、IP、router_id
        # 网口
        for node in topo_list:
            router_name, links = node["router_name"], node["links"]
            net_interface = {}
            for link in links:
                net_interface_name = list(link.keys())[0].replace("node", "eth")
                net_interface.update({net_interface_name: {"role": list(link.values())[0], "IP_Addr": None}})
            node.update({"net_interface": net_interface})
        # IP
        net_seg = "0.0"
        for node in topo_list:
            net_interface = node["net_interface"]
            for net_interface_name, net_interface_info in net_interface.items():
                IP_Addr = net_interface_info.get("IP_Addr")
                if IP_Addr is None:
                    net_interface_info["IP_Addr"] = "10." + str(net_seg) + ".1"
                    for peer_node in topo_list:
                        peer_node_name = net_interface_name.replace("eth", "node")
                        # net_interface_str = net_interface_name.split("_")
                        if peer_node["router_name"] != peer_node_name:
                            continue
                        peer_net_interface = node["router_name"].replace("node", "eth")
                        if peer_node["net_interface"][peer_net_interface]["IP_Addr"] is not None:
                            break
                        else:
                            peer_node["net_interface"][peer_net_interface]["IP_Addr"] = "10." + str(net_seg) + ".2"
                            break
                    net_seg = self.net_seg_self_add(net_seg=net_seg)
        # Router_id
        for node in topo_list:
            router_id = "10.255.255.255"
            for value in list(node["net_interface"].values()):
                if value["IP_Addr"] < router_id:
                    router_id = value["IP_Addr"]
            node["router_id"] = router_id
            router_id = "10.255.255.255"
        return topo_list

    def net_seg_self_add(self, net_seg):
        net_seg_list = net_seg.split(".")
        a, b = net_seg_list[0], net_seg_list[1]
        if int(b) < 255:
            b = str(int(b) + 1)
        else:
            a = str(int(a) + 1)
            b = "0"
        if int(a) >= 255:
            raise
        return f"{a}.{b}"

    def _get_business_role(self, as_num, neighbor_list):
        links = []
        for neighbor in neighbor_list:
            key_1, key_2 = as_num + "-" + neighbor, neighbor + "-" + as_num
            if key_1 in self.business_relationship_data:
                role = self.business_relationship_data[key_1]
                if role == -1:
                    links.append({f"node_{neighbor}": "customer"})
                elif role == 0:
                    links.append({f"node_{neighbor}": "peer"})
                else:
                    raise
            elif key_2 in self.business_relationship_data:
                role = self.business_relationship_data[key_2]
                if role == -1:
                    links.append({f"node_{neighbor}": "provider"})
                elif role == 0:
                    links.append({f"node_{neighbor}": "peer"})
                else:
                    raise
            # 调整实验策略，不再使用真实环境中不存在的商业关系
            # else:
            #     # raise "商业关系在真实的环境中不存在"
            #     # global start
            #     # start = start + 1
            #     neighbor_length = len(neighbor_list)
            #     neighbor_neighbor_length = len(self.mode_data[neighbor]["neighbors"])
            #     if neighbor_length > neighbor_neighbor_length:
            #         links.append({f"node_{neighbor}": "customer"})
            #     elif neighbor_length < neighbor_neighbor_length:
            #         links.append({f"node_{neighbor}": "provider"})
            #     elif int(neighbor) > int(as_num):
            #         links.append({f"node_{neighbor}": "provider"})
            #     elif int(neighbor) < int(as_num):
            #         links.append({f"node_{neighbor}": "customer"})
            #     else:
            #         raise
        return links

    def run_all_nodes(self):
        self.bird_config_generator.config_generator(topo_list=self.topo_list)
        self.sav_agent_config_generator.config_generator(topo_list=self.topo_list)
        self.topo_config_generator.config_generator(topo_list=self.topo_list)
        self.docker_compose_generator.bash_generator(topo_list=self.topo_list)

    def run_50_nodes(self):
        self.bird_config_generator.config_limit_prefix_length_generator(topo_list=self.topo_list_bfs[0:50])
        self.sav_agent_config_generator.config_generator(topo_list=self.topo_list_bfs[0:50])
        self.topo_config_generator.config_generator(topo_list=self.topo_list_bfs[0:50])
        self.docker_compose_generator.config_generator(topo_list=self.topo_list_bfs[0:50], container_run_command="python3 /root/savop/sav-agent/monitor.py")
        #self.docker_compose_generator.config_generator(topo_list=self.topo_list_bfs[0:50])
        self.ca_config_generator.config_generator(topo_list=self.topo_list_bfs[0:50])

    def run_3_nodes(self):
        global DEPLOY_DIR
        DEPLOY_DIR = "/root/nsdi_3_nodes_config_file"
        self.bird_config_generator.config_limit_prefix_length_generator(topo_list=self.topo_list_bfs[0:3])
        self.sav_agent_config_generator.config_generator(topo_list=self.topo_list_bfs[0:3])
        self.topo_config_generator.config_generator(topo_list=self.topo_list_bfs[0:3])
        self.docker_compose_generator.bash_generator(topo_list=self.topo_list_bfs[0:3])

    def _BFS(self, topo_list, start=0):
        # 无向图、广度优先算法
        topo_list_origin = copy.deepcopy(topo_list)
        visited = []
        q = queue.Queue()
        topo_list_bfs = []
        q.put(topo_list_origin[start])
        visited.append(topo_list_origin[start])
        while not q.empty():
            node = q.get()
            topo_list_bfs.append(node)
            for link in node.get("links"):
                router_name = list(link.keys())[0].replace("eth", "node")
                for i in topo_list_origin:
                    if i["router_name"] == router_name:
                        neighbor = i
                        break
                if neighbor not in visited:
                    visited.append(neighbor)
                    q.put(neighbor)
        return topo_list_bfs

    def caculate_lan_as(self, length, rate, source):
        # 计算rate比例的局域网
        lan_length = int(length * rate / 100)
        command_scope = ""
        for index in range(0, lan_length):
            if index < lan_length - 1:
                command_scope = command_scope + str(self.topo_list_bfs[index]["as_no"]) + ","
            else:
                command_scope = command_scope + str(self.topo_list_bfs[index]["as_no"])
        print(int(time.time()))
        command_timestamp = str(int(time.time())) + f"{rate:03d}"
        command_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signal_dict = {"command": "start", "command_scope": command_scope, "command_timestamp": command_timestamp,
                       "command_date": command_date, "source": source}
        return signal_dict

    def generetor_signal(self, length, source, off=False):
        # 产生控制不同局域网的信号文件
        for rate in range(5, 101, 5):
            time.sleep(2)
            signal = self.caculate_lan_as(length=length, rate=rate, source=source)
            print(f'signal_{str(rate)}.txt')
            print(signal)
            if off:
                with open(f'/root/sav_simulate/savop_back/data/NSDI/signal/signal_{str(rate)}.txt', "w") as json_file:
                    json.dump(signal, json_file)
            # 更全的信号文件，包含局域网的有效边数，边的集合，但是这些内容对控制程序运行没有作用，因此存到signal_{rate}_full.txt文件中
            print("补充有效的BGP边")
            as_number_list = signal["command_scope"].split(",")
            bgp_link = {}
            bgp_link_number = 0
            for index in range(0, len(as_number_list)):
                if self.topo_list_bfs[index]["as_no"] != as_number_list[index]:
                    raise
                effect_link = []
                all_link_list = self.topo_list_bfs[index]["links"]
                for link in all_link_list:
                    router_name = list(link.keys())[0]
                    role = list(link.values())[0]
                    neighbor_as_number = router_name.split("_")[1]
                    if neighbor_as_number not in as_number_list:
                        continue
                    effect_link.append({router_name: role})
                    bgp_link_number += 1
                bgp_link.update({f"node_{as_number_list[index]}": effect_link})
            signal.update({"bgp_link_number": bgp_link_number, "bgp_link": bgp_link})
            with open(f'/root/sav_simulate/savop_back/data/NSDI/signal/signal_{str(rate)}_full.txt', "w") as json_file:
                json.dump(signal, json_file)


if __name__ == "__main__":
    mode_file = "/root/sav_simulate/savop_back/data/NSDI/small_as_topo_all_prefixes.json"
    business_relation_file = "/root/sav_simulate/savop_back/data/NSDI/20230801.as-rel.txt"
    config_generator = ConfigGenerator(mode_file, business_relation_file)
    # config_generator.run_3_nodes()
    config_generator.run_50_nodes()
    # 计算局域网的拓扑结点：
    # for rate in range(5, 101, 5):
    #     time.sleep(2)
    #     signal = config_generator.caculate_lan_as(rate=rate)
    #     print(f'signal_{str(rate)}.txt')
    #     print(signal)
    #     with open(f'/root/sav_simulate/savop_back/data/NSDI/signal/signal_{str(rate)}.txt', "w") as json_file:
    #         json.dump(signal, json_file)
    # print("over!!!!!!!!!!!!!")
    # config_generator.generetor_signal(length=50, source="EFP-uRPF-Algorithm-A_app", off=True)

