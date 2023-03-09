#!/usr/bin/bash
# set -ex
rm -f  "./bird" "./birdc" "./birdcl"

make
if [ -f "./bird" ] && [ -f "./birdc" ] && [ -f "./birdcl" ];then
echo "adding edge the three files, bird birdc birdcl, are all ready"
else
echo "adding edge lack file bird birdc birdcl"
exit -1
fi
docker-compose down
docker rmi -f savnet_bird_base
docker build . -t savnet_bird_base
node_array=("1" "2" "3" "4" "5" "6" )
docker container rm $(docker container ls -aq)
# remove all stopped containers
docker rmi $(docker images --filter "dangling=true" -q --no-trunc)
# remove all images taged as <none>
for node_num in ${node_array[*]}
do
    rm -rf ./logs/$node_num/*
done
docker-compose up -d --force-recreate  --remove-orphans


# remove folders created last time
rm -r /var/run/netns
mkdir /var/run/netns

# node_array must be countinus mubers
pid_array=()

for node_num in ${node_array[*]}
do
    temp=$(sudo docker inspect -f '{{.State.Pid}}' node_$node_num)
    ln -s /proc/$temp/ns/net /var/run/netns/$temp
    pid_array+=($temp)
done

funCreateV(){
    # para 1: local node in letter, must be lowercase;a
    # para 2: peer node in letter, must be lowercase;b
    # para 3: local node in number,1
    # para 4: peer node in number,2
    # para 5: the IP addr of the local node interface 
    # para 6: the IP addr of the peer node interface    
    PID_L=${pid_array[$3-1]}
    PID_P=${pid_array[$4-1]}
    NET_L="$1_$2"
    NET_P="$2_$1"
    # echo $PID_L $PID_P $NET_L $NET_P ${5} ${6}
    ip link add ${NET_L} type veth peer name ${NET_P}
    ip link set ${NET_L}  netns ${PID_L}
    ip link set ${NET_P}  netns ${PID_P}
    ip netns exec ${PID_L} ip addr add ${5} dev ${NET_L}
    ip netns exec ${PID_L} ip link set ${NET_L} up
    ip netns exec ${PID_P} ip addr add ${6} dev ${NET_P}
    ip netns exec ${PID_P} ip link set ${NET_P} up
}

# A-B
echo "adding edge A-B"
funCreateV 'a' 'b' 1 2 '10.0.1.1/24' '10.0.1.2/24'

# A-F
echo "adding edge A-F"
funCreateV 'a' 'f' 1 6 '10.0.2.1/24' '10.0.2.2/24'

# B-C
# echo "adding edge B-C"
# funCreateV 'b' 'c' 2 3 '10.0.3.1/24' '10.0.3.2/24'

# B-D
echo "adding edge B-D"
funCreateV 'b' 'd' 2 4 '10.0.4.1/24' '10.0.4.2/24'

# C-E
echo "adding edge B-E"
funCreateV 'b' 'e' 3 5 '10.0.5.1/24' '10.0.5.2/24'

# C-F
echo "adding edge B-F"
funCreateV 'b' 'f' 3 6 '10.0.6.1/24' '10.0.6.2/24'

# D-E
echo "adding edge D-E"
funCreateV 'd' 'e' 4 5 '10.0.7.1/24' '10.0.7.2/24'


#sleep 1
echo '========================node A log========================'
docker logs node_1
echo '========================node B log========================'
docker logs node_2
echo '========================node C log========================'
docker logs node_3
echo '========================node D log========================'
docker logs node_4
echo '========================node E log========================'
docker logs node_5
echo '========================node F log========================'
docker logs node_6
# wait for the containers to perform, you can change the value based 
# on your hardware and configurations
sleep 10
echo '========================node A route========================'
docker exec -it node_1 route -n -F
echo '========================node B route========================'
docker exec -it node_2 route -n -F
echo '========================node C route========================'
docker exec -it node_3 route -n -F
echo '========================node D route========================'
docker exec -it node_4 route -n -F
echo '========================node E route========================'
docker exec -it node_5 route -n -F
echo '========================node F route========================'
docker exec -it node_6 route -n -F

# docker-compose down