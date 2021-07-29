#!/bin/sh
cd /TopStor
export ETCDCTL_API=3
enpdev='enp0s8'
pool=`echo $@ | awk '{print $1}'`
vol=`echo $@ | awk '{print $2}'`
ipaddr=`echo $@ | awk '{print $3}'`
ipsubnet=`echo $@ | awk '{print $4}'`
portalport=`echo $@ | awk '{print $5}'`
targetiqn=`echo $@ | awk '{print $6}'`
chapuser=`echo $@ | awk '{print $7}'`
chappas=`echo $@ | awk '{print $8}'`
vtype='iscsi'
echo $@ > /root/iscsiparam
pcs resource | grep $ipaddr | grep -v iscsi
if [ $? -eq 0 ];
then
  /TopStor/logmsg.py ISCSIwa01 warning $userreq $ipaddr 
  exit
fi
rightip=`/pace/etcdget.py ipaddr/$ipaddr/$ipsubnet`
echo  rightip=$rightip
resname=`echo $rightip | awk -F'/' '{print $1}'`
resname=$vtype-$pool-$vol-$ipaddr
echo resname=$resname
/pace/etcdput.py ipaddr/$ipaddr/$ipsubnet $resname/$vol
/pace/broadcasttolocal.py ipaddr/$ipaddr/$ipsubnet $resname/$vol 
pcs resource | grep $ipaddr | grep iscsi
if [ $? -ne 0 ];
then
 echo creating the ip
 /sbin/pcs resource delete --force $resname  2>/dev/null
 /sbin/pcs resource create $resname ocf:heartbeat:IPaddr2 ip=$ipaddr nic=$enpdev cidr_netmask=$ipsubnet op monitor interval=5s on-fail=restart
 /sbin/pcs resource group add ip-all $resname 
fi
echo continue
cat /TopStordata/iscsi.${vol}>> /TopStordata/iscsi.$ipaddr
echo /pace/addzfsvolumeastarget.sh $pool ${vol} $ipaddr $portalport $targetiqn $chapuser $chappas
/pace/addzfsvolumeastarget.sh $pool ${vol} $ipaddr $portalport $targetiqn $chapuser $chappas
