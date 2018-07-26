#!/usr/bin/sh
cd /pace
export ETCDCTL_API=3
echo $$ > /var/run/zfsping.pid
failddisks=''
isknown=0
isprimary=0
primtostd=4
date=`date`
enpdev='enp0s8'
echo $date >> /root/zfspingstart
systemctl restart target
cd /pace
rm -rf /pacedata/addiscsitargets 2>/dev/null
rm -rf /pacedata/startzfsping 2>/dev/null
while [ ! -f /pacedata/startzfsping ];
do
 sleep 1;
 echo cannot run now > /root/zfspingtmp
done
echo startzfs run >> /root/zfspingtmp
/pace/startzfs.sh
#sleep 5
date=`date `
echo starting in $date >> /root/zfspingtmp
while true;
do
 sleep 5
 needlocal=0
 myip=`pcs resource show CC | grep Attribute | awk '{print $2}' | awk -F'=' '{print $2 }'`
 myhost=`hostname -s`
 runningcluster=0
 echo check if I primary etcd >> /root/zfspingtmp
 netstat -ant | grep 2379 | grep LISTEN &>/dev/null
 if [ $? -eq 0 ]; 
 then
  echo I am primary etcd >> /root/zfspingtmp
  if [[ $isprimary -le 10 ]];
  then
   isprimary=$((isprimary+1))
  fi
  if [[ $primtostd -le 10 ]];
  then
   primtostd=$((primtostd+1))
  fi
  if [ $primtostd -eq 3 ];
  then
   /TopStor/logmsg.py Partsu05 info system $myhost
   primtostd=$((primtostd+1))
  fi
  if [ $isprimary -eq 3 ];
  then
   echo for $isprimary sending info Partsu03 booted with ip >> /root/zfspingtmp
   /TopStor/logmsg.py Partsu03 info system $myhost $myip
   /pace/etcdput.py ready/$myhost ok
   /pace/putzpool.py
   /TopStor/zpooltoimport.py all 
   sleep 3
   touch /pacedata/addiscsitargets 
  fi
  runningcluster=1
  leaderall=` ./etcdget.py leader --prefix 2>/dev/null`
  if [[ -z $leaderall ]]; 
  then
   echo no leader although I am primary node >> /root/zfspingtmp
   ./runningetcdnodes.py $myip 2>/dev/null
   ./etcddel.py leader --prefix 2>/dev/null
   ./etcdput.py leader/$myhost $myip 2>/dev/null
  fi
  echo adding known from list of possbiles >> /root/zfspingtmp
  ./addknown.py 2>/dev/null
 else
  echo I am not a primary etcd.. heartbeating leader >> /root/zfspingtmp
  leaderall=` ./etcdget.py leader --prefix 2>&1`
  echo $leaderall | grep Error  &>/dev/null
  if [ $? -eq 0 ];
  then
   echo leader is dead.. stopping local etcd >> /root/zfspingtmp
   ./etcdgetlocal.py $myip known --prefix | wc -l | grep 1
   if [ $? -eq 0 ];
   then
    /TopStor/logmsg.py Partst05 info system $myhost
    primtostd=0;
   fi
   systemctl stop etcd 2>/dev/null
   clusterip=`cat /pacedata/clusterip`
   echo starting primary etcd with clsuterip=$clusterip >> /root/zfspingtmp
   ./etccluster.py 'new' $myip 2>/dev/null
   chmod +r /etc/etcd/etcd.conf.yml
   systemctl daemon-reload 2>/dev/null
   systemctl start etcd 2>/dev/null
   ./etcdput.py clusterip $clusterip 2>/dev/null
   pcs resource create clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24 2>/dev/null
   systemctl restart smb 2>/dev/null
   echo adding me as a leader >> /root/zfspingtmp
   ./runningetcdnodes.py $myip 2>/dev/null
   ./etcddel.py leader 2>/dev/null
   ./etcdput.py leader/$myhost $myip 2>/dev/null
   echo importing all pools >> /root/zfspingtmp
   #/sbin/zpool import -am &>/dev/null
   echo running putzpool and nfs >> /root/zfspingtmp
   ./putzpool.py 2>/dev/null
   systemctl start nfs 2>/dev/null
   chgrp apache /var/www/html/des20/Data/* 2>/dev/null
   chmod g+r /var/www/html/des20/Data/* 2>/dev/null
   runningcluster=1
  else 
   echo I am not primary.. checking if I am local etcd>> /root/zfspingtmp
   netstat -ant | grep 2378 | grep $myip | grep LISTEN &>/dev/null
   if [ $? -ne 0 ];
   then
    echo I need to be local etcd .. no etcd is running>> /root/zfspingtmp
    needlocal=1
   else
    echo local etcd is already running>> /root/zfspingtmp
    needlocal=2
   fi
   echo checking if I am known host >> /root/zfspingtmp
   known=` ./etcdget.py known --prefix 2>/dev/null`
   echo $known | grep $myhost  &>/dev/null
   if [ $? -ne 0 ];
   then
    echo I am not a known adding me as possible >> /root/zfspingtmp
    ./etcdput.py possible$myhost $myip 2>/dev/null
   else
    echo I am known so running all needed etcd task:boradcast, log..etc >> /root/zfspingtmp
    if [[ $isknown -eq 0 ]];
    then
     echo running sendhost.py $leaderip 'user' 'recvreq' $myhost >>/root/tmp2
     leaderall=` ./etcdget.py leader --prefix `
     leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
     leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
     /pace/sendhost.py $leaderip 'user' 'recvreq' $myhost
     sleep 1
     /pace/sendhost.py $leaderip 'cifs' 'recvreq' $myhost
     /pace/sendhost.py $leaderip 'logall' 'recvreq' $myhost
     isknown=$((isknown+1))
    fi
    if [[ $isknown -le 10 ]];
    then
     isknown=$((isknown+1))
    fi
    if [[ $isknown -eq 3 ]];
    then
     /TopStor/logmsg.py Partsu04 info system $myhost $myip
     /pace/etcdput.py ready/$myhost ok
     sleep 3
     touch /pacedata/addiscsitargets 
    fi
    echo finish running tasks task:boradcast, log..etc >> /root/zfspingtmp
   fi
  fi 
 fi
 /pace/putzpool.py
 echo checking if I need to run local etcd >> /root/zfspingtmp
 if [[ $needlocal -eq 1 ]];
 then
  echo start the local etcd >> /root/zfspingtmp
  ./etccluster.py 'local' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload
  systemctl stop etcd 2>/dev/null
  systemctl start etcd 2>/dev/null
  leaderall=` ./etcdget.py leader --prefix `
  leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
  leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
  ./etcdsync.py $myip primary primary 2>/dev/null
  ./etcddellocal.py $myip known --prefix 2>/dev/null
  ./etcddellocal.py $myip localrun --prefix 2>/dev/null
  ./etcddellocal.py $myip run --prefix 2>/dev/null
  ./etcdsync.py $myip known known 2>/dev/null
  ./etcdsync.py $myip localrun localrun 2>/dev/null
  ./etcdsync.py $myip leader known 2>/dev/null
#   ./etcddellocal.py $myip known/$myhost --prefix 2>/dev/null
  echo done and exit >> /root/zfspingtmp
  continue 
 fi
 if [[ $needlocal -eq  2 ]];
 then
  echo I am already local etcd running iscsirefresh on $myip $myhost  >> /root/zfspingtmp
  /pace/iscsiwatchdog.sh $myip $myhost $leader
 fi
 echo checking if still in the start initcron is still running  >> /root/zfspingtmp
 if [ -f /pacedata/forzfsping ];
 then
  echo Yes. so I have to exit >> /root/zfspingtmp
  continue
 fi
 echo No. so checking  I am primary >> /root/zfspingtmp
 if [[ $runningcluster -eq 1 ]];
 then
  echo Yes I am primary so will check for known hosts >> /root/zfspingtmp
  ./addknown.py 2>/dev/null
  ./selectimport.py $myhost
 fi 
 /pace/iscsiwatchdog.sh 2>/dev/null 
 /pace/putzpool.py 2>/dev/null
  echo Collecting a change in system occured >> /root/zfspingtmp
 #/pace/changeop.py hosts/$myhost/current d
 /pace/changeop.py $myhost
 /pace/selectspare.py $myhost
done
