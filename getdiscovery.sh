#!/usr/bin/sh
etcd='10.11.11.253'
for pid in $(pidof -x getdiscovery.sh); do
    if [ $pid != $$ ]; then
        echo "[$(date)] : discovery.sh : Process is already running with PID $pid"
        exit 1
    fi
done
cd /TopStor
rm -rf /root/discovery/*
mkdir /root/discovery

nmcli conn mod cmynode +ipv4.addresses $etcd/24
nmcli conn up cmynode
rm -rf /TopStordata/discovery.sh
cp /TopStor/discovery.sh /TopStordata/
sed -i 's/SLEEP/sleep 10/g' /TopStordata/discovery.sh
leaderip=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
echo starting etcd 
docker run  --rm --name discovery --hostname discovery -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $etcd:2379:2379 -v /TopStor/:/TopStor -v /root/discovery:/default.etcd -v /TopStordata/discovery.sh:/runme.sh --net bridge0 moataznegm/quickstor:etcd  &
docker exec intdns nslookup discovery | grep Address | grep -v 127 | awk '{print $2}'
newip=`docker exec intdns nslookup discovery | grep Address | grep -v 127 | awk '{print $2}'`
echo newip=$newip
docker rm -f discovery
rm -rf /TopStordata/discovery.sh
cp /TopStor/discovery.sh /TopStordata/
sed -i 's/SLEEP//g' /TopStordata/discovery.sh
sed -i "s/ETCDIP/$newip/g" /TopStordata/discovery.sh
docker run  -itd --rm --name discovery --hostname discovery -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $etcd:2379:2379 -v /TopStor/:/TopStor -v /root/discovery:/default.etcd -v /TopStordata/discovery.sh:/runme.sh --net bridge0 moataznegm/quickstor:etcd
counter=0
while true
do
	lines=`/TopStor/etcdget.py $etcd possible --prefix`
	counter=$((counter+1))
	echo $lines
	lines=`/TopStor/etcdget.py $etcd tostop`'s'
	/TopStor/syncpossibles.py $leaderip $etcd
	echo $lines | grep yes
	if [ $? -eq 0 ];
	then
		break
	fi
	if [ $counter -ge 120 ];
	then
		break
	fi
	sleep 5 

done
docker rm -f discovery
nmcli conn mod cmynode -ipv4.addresses $etcd/24
nmcli conn up cmynode
