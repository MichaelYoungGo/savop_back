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

start = 0


class BirdConfigGenerator:
    def config_generator(self, topo_list):
        print("创建bird的配置文件")
        for index in range(0, len(topo_list)):
            router = topo_list[index]
            router_id = router["router_id"]
            router_name = router["router_name"].lower()
            as_no = router["as_no"]
            content = f"router id {router_id}\n"
            content += "roa4 table master4{\n\tsorted 1;\n};\n"
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
            content += 'protocol direct {{\n\tipv4;\n\tinterface "eth_*";\n}};\n'
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
                       f"\n\t\t}};\n}};\n"
            content += "template bgp sav_inter from basic{" \
                       "\n\trpdp4{" \
                       "\n\timport none" \
                       "\n\texport none;" \
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
            with open(f"/root/test/configs/{as_no}.conf", "w") as f:
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
            links = []
            for interface_name, interface_value in node["net_interface"].items():
                local_interface_role = interface_value["role"]
                for peer_router in topo_list:
                    peer_router_name = interface_name.replace("eth", "node")
                    if peer_router["router_name"] != peer_router_name:
                        continue
                    peer_router_as_no = peer_router["as_no"]
                    peer_interface_name = router_name.replace("node", "eth")
                    peer_interface_IP_Addr = peer_router["net_interface"][peer_interface_name]["IP_Addr"]
                    peer_router_id = peer_router["router_id"]
                    peer_role = peer_router["net_interface"][peer_interface_name]["role"]
                    break
                links.append({"remote_addr": f"{peer_interface_IP_Addr}:5000", "remote_as": peer_router_as_no,
                              "remote_id": "peer_router_id", "local_role": local_interface_role,
                              "interface_name": interface_name})
            links_str = str(links)
            json_content = f'{{' \
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
                           '\n\t"grpc_server_addr": "0.0.0.0:5000",' \
                           f'\n\t"grpc_id": "{grpc_id}",' \
                           f'\n\t"local_as":{local_as},' \
                           '\n\t"grpc_config": {' \
                           '\n\t\t"server_addr": "0.0.0.0:5000",' \
                           f'\n\t\t"id": "{id_}",' \
                           f'\n\t\t"local_as": {local_as},' \
                           f'\n\t\t"enabled": false,' \
                           f'\n\t\t"links": {links_str}' \
                           '\n\t},' \
                           '\n\t"location": "edge"' \
                           '\n}\n'
            with open(f"/root/test/configs/{local_as}.json", "w") as f:
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
        with open(f"/root/test/topo.sh", "w") as f:
            f.write(host_run_content)


class DockerComposeGenerator:
    def config_generator(self, topo_list):
        print("创建DockerCompose的配置文件")
        yml_content = 'version: "2"\nservices:\n'
        for index in range(0, len(topo_list)):
            pos = index + 1
            router_name = topo_list[index]["router_name"]
            as_no = topo_list[index]["as_no"]
            content = f"  {router_name}: \
                    \n  # {router_name} \
                    \n    image: savop_bird_base \
                    \n    container_name: {router_name} \
                    \n    cap_add: \
                    \n      - NET_ADMIN \
                    \n    volumes: \
                    \n      - ./configs/{as_no}.conf:/usr/local/etc/bird.conf \
                    \n      - ./configs/{as_no}.json:/root/savnet_bird/SavAgent_config.json \
                    \n      - ./logs/{as_no}/:/root/savnet_bird/logs/ \
                    \n      - ./logs/{as_no}/data:/root/savop/sav-agent/data/ \
                    \n    network_mode: none \
                    \n    command: \
                    \n        bash container_run.sh\n"
            yml_content = yml_content + content
        with open(f"/root/test/docker-compose.yml", "w") as f:
            f.write(yml_content)


class ConfigGenerator:
    mode_data = {}
    business_relationship_data = {}
    topo_list = []
    sav_agent_config_generator = SavAgentConfigGenerator()
    bird_config_generator = BirdConfigGenerator()
    topo_config_generator = TopoConfigGenerator()
    docker_compose_generator = DockerComposeGenerator()

    def __init__(self, mode_file_path, business_relation_file_path):
        self.mode_data = self.mode_data_analysis(path=mode_file_path)
        self.business_relationship_data = self.business_relation_data_analysis(path=business_relation_file_path)
        self.topo_list = self._convert_data_format()

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
            else:
                # raise "商业关系在真实的环境中不存在"
                # global start
                # start = start + 1
                neighbor_length = len(neighbor_list)
                neighbor_neighbor_length = len(self.mode_data[neighbor]["neighbors"])
                if neighbor_length > neighbor_neighbor_length:
                    links.append({f"node_{neighbor}": "customer"})
                elif neighbor_length < neighbor_neighbor_length:
                    links.append({f"node_{neighbor}": "provider"})
                elif int(neighbor) > int(as_num):
                    links.append({f"node_{neighbor}": "provider"})
                elif int(neighbor) < int(as_num):
                    links.append({f"node_{neighbor}": "customer"})
                else:
                    raise
                # print(start)
        return links

    def run(self):
        # self.bird_config_generator.config_generator(topo_list=self.topo_list)
        # self.sav_agent_config_generator.config_generator(topo_list=self.topo_list)
        self.topo_config_generator.config_generator(topo_list=self.topo_list)
        # self.docker_compose_generator.config_generator(topo_list=self.topo_list)



if __name__ == "__main__":
    mode_file = "/root/sav_simulate/savop_back/data/NSDI/small_as_topo_all_prefixes.json"
    business_relation_file = "/root/sav_simulate/savop_back/data/NSDI/20230801.as-rel.txt"
    config_generator = ConfigGenerator(mode_file, business_relation_file)
    config_generator.run()
    print("over!!!!!!!!!!!!!")
