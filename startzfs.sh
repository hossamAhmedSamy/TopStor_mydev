#!/bin/sh
cd /pace
export ETCDCTL_API=3
echo starting startzfs > /root/tmp2
iscsimapping='/pacedata/iscsimapping';
runningpools='/pacedata/pools/runningpools';
clusterip='10.11.11.230'
enpdev='enp0s8'
myhost=`hostname -s`
/sbin/rabbitmqctl add_user rabbmezo HIHIHI 2>/dev/null
/sbin/rabbitmqctl set_permissions -p / rabbmezo ".*" ".*" ".*" 2>/dev/null
/sbin/rabbitmqctl set_user_tags rabbmezo administrator
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
/sbin/ip addr del $clusterip/24 dev $enpdev 2>/dev/null
/sbin/pcs resource delete --force clusterip 
echo finish identify clusterip >> /root/tmp2
systemctl status etcd &>/dev/null
if [ $? -ne 0 ];
then
  /sbin/pcs resource delete --force clusterip 2>/dev/null
fi
 echo starting nodesearch>>/root/tmp2
 result=` ./nodesearch.py $myip 2>/dev/null`
 echo finish nodesearch>>/root/tmp2
freshcluster=0
echo $result | grep nothing 
if [ $? -eq 0 ];
then
 echo no node is found so making me as primary>>/root/tmp2
 rm -rf /pacedata/running*
 freshcluster=1
  ./etccluster.py 'new' $myip 2>/dev/null
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
 datenow=`date +%m/%d/%Y`; timenow=`date +%T`;
  /TopStor/logmsg2.sh $datenow $timenow $myhost Partst03 info system $myhost $myip
  ./runningetcdnodes.py $myip 2>/dev/null
  ./etcddel.py known --prefix 2>/dev/null 
  ./etcddel.py possbile --prefix 2>/dev/null 
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
 systemctl start smb
 echo startedclusterip >>/root/tmp2
  ./etcddel.py leader --prefix 2>/dev/null
  ./etcdput.py leader/$myhost $myip 2>/dev/null
  ./etcdput.py primary/name $myhost 2>/dev/null
  ./etcdput.py primary/address $myip 2>/dev/null
  ./etcdput.py clusterip $clusterip 2>/dev/null
  ./etcddel.py known --prefix 2>/dev/null
  ./etcddel.py possible --prefix 2>/dev/null
  ./etcddel.py localrun --prefix 2>/dev/null
 systemctl start topstorremote
 systemctl start topstorremoteack
 echo deleted knowns and added leader >>/root/tmp2
else
 echo found other host as primary.. checking if it shares same host name>>/root/tmp2
 cat /pacedata/runningetcdnodes.txt | grep $myhost &>/dev/null
 if [ $? -ne 0 ];
 then
  leaderall=` ./etcdget.py leader --prefix `
  leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
  leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
   /TopStor/logmsg.py Partst04 info system $myhost $myip
  #msg="{'req': 'msg', 'reply': ['/TopStor/logmsg.py','Partst04','info','system','$myhost','$myip']}"
  #/pace/sendhost.py $leaderip "$msg" 'recvreply' $myhost
 echo getting clusterip from another leader >>/root/tmp2
   ./etcdget.py clusterip 2>/dev/null > /pacedata/clusterip
  /sbin/ip addr del $clusterip/24 dev $enpdev 2>/dev/null
  /sbin/pcs resource delete --force clusterip 
  /sbin/ip addr del $clusterip/24 dev $enpdev 2>/dev/null
  echo starting etcd as local >>/root/tmp2
   ./etccluster.py 'local' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml 2>/dev/null
  systemctl daemon-reload 2>/dev/null
  systemctl stop etcd 2>/dev/null
  systemctl start etcd 2>/dev/null
   ./etcdputlocal.py $myip 'local/'$myhost $myip
  echo sync leader with local database >>/root/tmp2
   ./etcdsync.py $myip primary primary 2>/dev/null
   ./etcddellocal.py $myip known --prefix 2>/dev/null
   ./etcddellocal.py $myip localrun --prefix 2>/dev/null
   ./etcddellocal.py $myip run --prefix 2>/dev/null
   ./etcdsync.py $myip known known 2>/dev/null
   ./etcdsync.py $myip localrun localrun 2>/dev/null
   ./etcdsync.py $myip leader known 2>/dev/null
   ./etcddel.py known/$myhost --prefix 2>/dev/null
  /sbin/rabbitmqctl add_user rabb_$leader YousefNadody 2>/dev/null
  /sbin/rabbitmqctl set_permissions -p / rabb_$leader ".*" ".*" ".*" 2>/dev/null
#  /sbin/rabbitmqctl set_user_tags rabb_ administrator
   ./etcddellocal.py $myip users --prefix 2>/dev/null
   ./etcdsync.py $myip run/$leader/user users 2>/dev/null
  systemctl start topstorremote
  systemctl start topstorremoteack
  echo etcd started as local >>/root/tmp2
  rm -rf /var/lib/iscsi/nodes/* 2>/dev/null
  echo starting iscsiwaatchdog >>/root/tmp2
  /pace/iscsiwatchdog.sh $myip $myhost $leader 2>/dev/null
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
   ./putzpool.py 2>/dev/null
  echo ran putzpool >>/root/tmp2
 fi
 touch /var/www/html/des20/Data/Getstatspid
fi
#zpool export -a
sleep 2
rm -rf /pacedata/forzfsping 2>/dev/null
