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
 systemctl stop nfs ;
 systemctl stop smb 
 zpool export $pool
 zpool import $pool 
 systemctl start nfs 
 systemctl start smb
else
 echo pool $pool is working normally >>/root/fixpool
 /pace/etcddel.py fixpool/$pool
fi
