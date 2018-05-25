#!/bin/sh
cd /pace
echo starting startzfs > /root/tmp2
iscsimapping='/pacedata/iscsimapping';
runningpools='/pacedata/pools/runningpools';
clusterip='10.11.11.230'
enpdev='enp0s8'
myhost=`hostname -s`
myip=`/sbin/pcs resource show CC | grep Attributes | awk '{print $2}' | awk -F'=' '{print $2}'`
 ccnic=`/sbin/pcs resource show CC | grep nic\= | awk -F'nic=' '{print $2}' | awk '{print $1}'`
/sbin/pcs resource delete --force clusterip 2>/dev/null
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
echo finish identify clusterip >> /root/tmp2
systemctl status etcd &>/dev/null
if [ $? -ne 0 ];
then
  /sbin/pcs resource delete --force clusterip 2>/dev/null
fi
 echo starting nodesearch>>/root/tmp2
 result=`ETCDCTL_API=3 ./nodesearch.py $myip 2>/dev/null`
 echo finish nodesearch>>/root/tmp2
freshcluster=0
echo $result | grep nothing 
if [ $? -eq 0 ];
then
 echo no node is found so making me as primary>>/root/tmp2
 rm -rf /pacedata/running*
 freshcluster=1
 ETCDCTL_API=3 ./etccluster.py 'new' $myip 2>/dev/null
 chmod +r /etc/etcd/etcd.conf.yml 2>/dev/null
 echo starginetcd >>/root/tmp2
 systemctl daemon-reload 2>/dev/null
 systemctl start etcd 2>/dev/null
 while [ $? -ne 0 ];
 do
  sleep 1
  systemctl daemon-reload 2>/dev/null
  sleep 1
  systemctl start etcd 2>/dev/null
  echo starting etcd=$?
 done
 echo started etcd as primary>>/root/tmp2
 ETCDCTL_API=3 ./runningetcdnodes.py $myip 2>/dev/null
 ETCDCTL_API=3 ./etcddel.py known --prefix 2>/dev/null 
 ETCDCTL_API=3 ./etcddel.py possbile --prefix 2>/dev/null 
 rm -rf /var/lib/iscsi/nodes/* 2>/dev/null
 echo startiscsiwatchdog >>/root/tmp2
 /pace/iscsiwatchdog.sh 2>/dev/null
 echo started iscsiwatchdog >>/root/tmp2
 /sbin/pcs resource update clusterip nic="$enpdev" ip=$clusterip cidr_netmask=24 2>/dev/null
 if [ $? -ne 0 ];
 then
 echo creating clusterip >>/root/tmp2
  /sbin/pcs resource create clusterip ocf:heartbeat:IPaddr2 nic="$enpdev" ip=$clusterip cidr_netmask=24 op monitor on-fail=restart 2>/dev/null
 fi
 echo createdclusterip >>/root/tmp2
 /sbin/pcs resource enable clusterip 2>/dev/null
 /sbin/pcs resource debug-start clusterip 2>/dev/null
 echo startedclusterip >>/root/tmp2
 ETCDCTL_API=3 ./etcdput.py leader/$myhost $myip 2>/dev/null
 ETCDCTL_API=3 ./etcdput.py primary/name $myhost 2>/dev/null
 ETCDCTL_API=3 ./etcdput.py primary/address $myip 2>/dev/null
 ETCDCTL_API=3 ./etcdput.py clusterip $clusterip 2>/dev/null
 ETCDCTL_API=3 ./etcddel.py known --prefix 2>/dev/null
 ETCDCTL_API=3 ./etcddel.py possible --prefix 2>/dev/null
 ETCDCTL_API=3 ./etcddel.py localrun --prefix 2>/dev/null
 echo deleted knowns and added leader >>/root/tmp2
else
 echo found other host as primary.. checking if it shares same host name>>/root/tmp2
 cat /pacedata/runningetcdnodes.txt | grep $myhost &>/dev/null
 if [ $? -ne 0 ];
 then
 echo getting clusterip from another leader >>/root/tmp2
  ETCDCTL_API=3 ./etcdget.py clusterip 2>/dev/null > /pacedata/clusterip
  /sbin/pcs resource delete --force clusterip && /sbin/ip addr del $clusterip/24 dev $enpdev 2>/dev/null
  echo starting etcd as local >>/root/tmp2
  ETCDCTL_API=3 ./etccluster.py 'local' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml 2>/dev/null
  systemctl daemon-reload 2>/dev/null
  systemctl stop etcd 2>/dev/null
  systemctl start etcd 2>/dev/null
  ETCDCTL_API=3 ./etcdputlocal.py $myip 'local/'$myhost $myip
  echo sync leader with local database >>/root/tmp2
  ETCDCTL_API=3 ./etcdsync.py $myip primary 2>/dev/null
  ETCDCTL_API=3 ./etcddellocal.py $myip known --prefix 2>/dev/null
  ETCDCTL_API=3 ./etcddellocal.py $myip localrun --prefix 2>/dev/null
  ETCDCTL_API=3 ./etcddellocal.py $myip run --prefix 2>/dev/null
  ETCDCTL_API=3 ./etcdsync.py $myip known 2>/dev/null
  ETCDCTL_API=3 ./etcdsync.py $myip localrun 2>/dev/null
  echo etcd started as local >>/root/tmp2
  rm -rf /var/lib/iscsi/nodes/* 2>/dev/null
  echo starting iscsiwaatchdog >>/root/tmp2
  /pace/iscsiwatchdog.sh $myip $myhost 2>/dev/null
  echo started iscsiwaatchdog >>/root/tmp2
#  pcs resource disable clusterip
 fi
fi

echo starting disk LIO check >>/root/tmp2
myhost=`hostname -s`
hostnam=`cat /TopStordata/hostname`
poollist='/pacedata/pools/'${myhost}'poollist';
lastreboot=`uptime -s`
seclastreboot=`date --date="$lastreboot" +%s`
secrunning=`cat $runningpools | grep runningpools | awk '{print $2}'`
# ./addtargetdisks.sh
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
echo starting keysend >>/root/tmp2
 ./keysend.sh &>/dev/null
# pcs resource create IPinit ocf:heartbeat:IPaddr2 nic="$ccnic" ip="10.11.11.254" cidr_netmask=24 op monitor on-fail=restart 2>/dev/null
# pcs resource debug-start IPinit 2>/dev/null
 rm -rf /TopStor/key/adminfixed.gpg && cp /TopStor/factory/factoryadmin /TopStor/key/adminfixed.gpg
 zpool export -a 2>/dev/null
echo i all zpool exported >>/root/tmp2
 echo $freshcluster | grep 1
 if [ $? -eq 0 ];
 then 
#  sh iscsirefresh.sh
#  sh listingtargets.sh
  echo freshcluster=$freshcluster so zpool importing >>/root/tmp2
  zpool import -a 2>/dev/null
  ETCDCTL_API=3 ./putzpool.py 2>/dev/null
  echo ran putzpool >>/root/tmp2
 fi
 touch /var/www/html/des20/Data/Getstatspid
fi
#zpool export -a
sleep 10
rm -rf /pacedata/forzfsping 2>/dev/null
