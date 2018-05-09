#!/bin/bash
cd /pace
ps -ef | grep zfsping.sh | grep -v tty | grep -v grep
if [ $? -eq 0 ];
then
 exit
fi
echo start >> /root/tmp2
touch /pacedata/startzfs
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
 len=`wc -c /pacedata/clusterip | awk '{print $1}'`
 if [ $len -ge 6 ];
 then
  clusterip=`cat /pacedata/clusterip` 
 else
  echo $clusterip > /pacedata/clusterip
 fi
fi
systemctl status etcd &>/dev/null
if [ $? -ne 0 ];
then
  /sbin/pcs resource delete --force clusterip 2>/dev/null
fi
if [ ! -f /pacedata/nodesearch.txt ];
then
 result=`ETCDCTL_API=3 ./nodesearch.py $myip 2>/dev/null`
 echo $result > /pacedata/nodesearch.txt
else
 result=`cat /pacedata/nodesearch.txt`
fi 
freshcluster=0
echo $result | grep nothing 
if [ $? -eq 0 ];
then
 rm -rf /pacedata/running*
 freshcluster=1
 echo here=$clusterip
 ETCDCTL_API=3 ./etccluster.py 'new'
 chmod +r /etc/etcd/etcd.conf.yml
 systemctl daemon-reload
 systemctl start etcd
 ETCDCTL_API=3 ./runningetcdnodes.py $myip
 ETCDCTL_API=3 ./etcddel.py run disk  
 ETCDCTL_API=3 ./etcddel.py known --prefix 
 rm -rf /var/lib/iscsi/nodes/* 2>/dev/null
 /pace/iscsiwatchdog.sh 2>/dev/null
 pcs resource update clusterip nic="$enpdev" ip=$clusterip cidr_netmask=24 2>/dev/null
 if [ $? -ne 0 ];
 then
 pcs resource create clusterip ocf:heartbeat:IPaddr2 nic="$enpdev" ip=$clusterip cidr_netmask=24 op monitor on-fail=restart 2>/dev/null
 fi
 pcs resource enable clusterip 2>/dev/null
 pcs resource debug-start clusterip 2>/dev/null
 ETCDCTL_API=3 ./etcdput.py leader$myhost $myip
 ETCDCTL_API=3 ./etcdput.py clusterip $clusterip
 ETCDCTL_API=3 ./etcddel.py known --prefix
else
 cat /pacedata/runningetcdnodes.txt | grep $myhost &>/dev/null
 if [ $? -ne 0 ];
 then
  ETCDCTL_API=3 ./etcdget.py clusterip  > /pacedata/clusterip
  /sbin/pcs resource delete --force clusterip && /sbin/ip addr del $clusterip/24 dev $enpdev 2>/dev/null
 ETCDCTL_API=3 ./etccluster.py 'local'
 chmod +r /etc/etcd/etcd.conf.yml
 systemctl daemon-reload
 systemctl stop etcd 2>/dev/null
 systemctl start etcd
#  pcs resource disable clusterip
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
 pcs resource create IPinit ocf:heartbeat:IPaddr2 nic="$ccnic" ip="10.11.11.254" cidr_netmask=24 op monitor on-fail=restart 2>/dev/null
 pcs resource debug-start IPinit 2>/dev/null
 rm -rf /TopStor/key/adminfixed.gpg && cp /TopStor/factory/factoryadmin /TopStor/key/adminfixed.gpg
 zpool export -a 2>/dev/null
 echo $freshcluster | grep 1
 if [ $? -eq 0 ];
 then 
#  sh iscsirefresh.sh
#  sh listingtargets.sh
  zpool import -a 2>/dev/null
  ETCDCTL_API=3 ./putzpool.py 2>/dev/null
 fi
 touch /var/www/html/des20/Data/Getstatspid
fi
#zpool export -a
rm -rf /pacedata/startzfs

