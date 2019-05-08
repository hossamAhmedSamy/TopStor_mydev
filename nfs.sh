#!/bin/sh
enpdev='enp0s8'
pool=`echo $@ | awk '{print $1}'`
vol=`echo $@ | awk '{print $2}'`
ipaddr=`echo $@ | awk '{print $3}'`
ipsubnet=`echo $@ | awk '{print $4}'`
echo $@ > /root/nfsparam
/sbin/pcs resource delete --force ip-$vol  2>/dev/null
/sbin/pcs resource create ip-$vol ocf:heartbeat:IPaddr2 ip=$ipaddr nic=$enpdev cidr_netmask=$ipsubnet op monitor interval=5s on-fail=restart
/sbin/pcs resource group add ip-all ip-$vol
docker stop nfs-$vol
docker container rm nfs-$vol
docker run -d -v /$pool/$vol:/$pool/$vol -v /etc/exports.$vol:/etc/exports:ro --cap-add SYS_ADMIN -p $ipaddr:2049:2049  -p $ipaddr:2049:2049/udp  -p $ipaddr:32765:32765 -p $ipaddr:32765:32765/udp -p $ipaddr:111:111 -p $ipaddr:111:111/udp -p $ipaddr:32767:32767 -p $ipaddr:32767:32767/udp --name nfs-$vol 10.11.11.124:5000/nfs
