#!/bin/bash
cd /pace
rm -rf /var/lib/etcd/*
rm -rf /pacedata/running*
iscsimapping='/pacedata/iscsimapping';
runningpools='/pacedata/pools/runningpools';
clusterip='10.11.11.230'
enpdev='enp0s8'
myhost=`hostname -s`
myip=`/sbin/pcs resource show CC | grep Attributes | awk '{print $2}' | awk -F'=' '{print $2}'`
 ccnic=`pcs resource show CC | grep nic\= | awk -F'nic=' '{print $2}' | awk '{print $1}'`
if [ ! -f /pacedata/clusterip ];
then
 echo $clusterip > /pacedata/clusterip
else
 clusterip=`cat /pacedata/clusterip` 
fi

result=`ETCDCTL_API=3 ./nodesearch.py $myip`
freshcluster=0
echo $result | grep nothing 
if [ $? -eq 0 ];
then
 freshcluster=1
 ./etccluster.py
 systemctl daemon-reload
 systemctl start etcd
 ETCDCTL_API=3 ./runningetcdnodes.py $myip
 ETCDCTL_API=3 ./etcdput.py leader$myhost $myip
 pcs resource create clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24
 ETCDCTL_API=3 ./etcdput.py clusterip $clusterip
else
 cat /pacedata/runningetcdnodes.txt | grep $myhost &>/dev/null
 if [ $? -ne 0 ];
 then
  /sbin/pcs resource delete --force clusterip && /sbin/ip addr del $clusterip/24 dev $enpdev
  ETCDCTL_API=3 ./etcdget.py clusterip  > /pacedata/clusterip
 fi
fi

myhost=`hostname -s`
hostnam=`cat /TopStordata/hostname`
poollist='/pacedata/pools/'${myhost}'poollist';
lastreboot=`uptime -s`
seclastreboot=`date --date="$lastreboot" +%s`
secrunning=`cat $runningpools | grep runningpools | awk '{print $2}'`
 ./addtargetdisks.sh
lsblk -Sn | grep LIO &>/dev/null
if [ $? -ne 0 ]; then
sleep 2
fi
if [ -z $secrunning ]; then
 echo hithere: $lastreboot : $seclastreboot
 secdiff=222;
else
 secdiff=$((seclastreboot-secrunning));
fi
if [ $secdiff -ne 0 ]; then
 echo runningpools $seclastreboot > $runningpools
 ./keysend.sh &>/dev/null
 pcs resource create IPinit ocf:heartbeat:IPaddr nic="$ccnic" ip="10.11.11.254" cidr_netmask=24
 rm -rf /TopStor/key/adminfixed.gpg && cp /TopStor/factory/factoryadmin /TopStor/key/adminfixed.gpg
 zpool export -a
 echo $freshcluster | grep 1
 if [ $? -eq 0 ];
 then 
  sh iscsirefresh.sh
  sh listingtargets.sh
 fi
 touch /var/www/html/des20/Data/Getstatspid
fi
 zpool export -a

