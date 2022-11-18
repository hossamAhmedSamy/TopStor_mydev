#!/bin/sh
export ETCDCTL_API=3
pool=`echo $@ | awk '{print $1}'`
echo pool=$pool >/root/fixpool
count=0
while [ $count -lt 4 ];
do
 events=`/sbin/zpool events $pool | grep config_sync | tail -n 1 | awk -F':' '{print $2}'`
 nowis=`date | awk -F':' '{print $2}'`
 echo events=$events , nowis=$nowis , count=$count >>/root/fixpool
 if [ $nowis -lt $events ];
 then
  nowis=$((nowis+60))
 fi
 res=$((nowis-events))
 echo res=$res >> /root/fixpool 
 if [ $res -lt 3 ]; 
 then
  echo sleeping >> /root/fixpool
  sleep 65 
  count=$((count+1))
 else
  count=200
 fi
done
if [ $count -lt 12 ];
then
 echo we have to export >>/root/fixpool
# systemctl stop nfs ;
 pooldockers=`docker ps | grep $pool | awk '{print $NF}'`
 
# systemctl stop smb 
 for x in ${pooldockers[@]}; do
  docker stop $x
 done
 zpool export $pool
 zpool import $pool 
 for x in ${pooldockers[@]}; do
  docker start $x
 done
# systemctl start nfs 
# systemctl start smb
else
 echo pool $pool is working normally >>/root/fixpool
 /pace/etcddellocal.py fixpool/$pool
fi
