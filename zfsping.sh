#!/usr/bin/sh
cd /pace
echo $$ > /var/run/zfsping.pid
isknown=0
isprimary=0
primtostd=4
date=`date`
echo $date >> /root/zfspingstart
export ETCDCTL_API=3
systemctl restart target
cd /pace
rm -rf /pacedata/startzfsping 2>/dev/null
while [ ! -f /pacedata/startzfsping ];
do
 sleep 1;
 echo cannot run now > /root/zfspingtmp
done
echo startzfs run >> /root/zfspingtmp
/pace/startzfs.sh
sleep 5
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
 echo $primtostd | grep 3
 if [ $? -eq 0 ];
 then
  /TopStor/logmsg.sh Partsu05 info system $myhost
  primtostd=$((primtostd+1))
 fi
 echo $isprimary | grep 3
 if [ $? -eq 0 ];
 then
  /TopStor/logmsg.sh Partsu03 info system $myhost $myip
  isprimary=$((isprimary+1))
 fi
 runningcluster=1
# leader='"'`ETCDCTL_API=3 ./etcdget.py leader --prefix 2>/dev/null`'"'
 leader=`ETCDCTL_API=3 ./etcdget.py leader --prefix 2>/dev/null`
 if [[ -z $leader ]]; 
 then
  echo no leader although I am primary node >> /root/zfspingtmp
  ETCDCTL_API=3 ./runningetcdnodes.py $myip 2>/dev/null
  ETCDCTL_API=3 ./etcddel.py leader 2>/dev/null
  ETCDCTL_API=3 ./etcdput.py leader/$myhost $myip 2>/dev/null
 fi
 echo adding known from list of possbiles >> /root/zfspingtmp
 ETCDCTL_API=3 ./addknown.py 2>/dev/null
# echo checking confirmed >> /root/zfspingtmp
# ETCDCTL_API=3 ./allconfirmed.py 2>/dev/null
# echo broadcasting log >> /root/zfspingtmp
# ETCDCTL_API=3 ./broadcastlog.py 2>/dev/null
# echo receiving log >> /root/zfspingtmp
# ETCDCTL_API=3 ./receivelog.py 2>/dev/null
 echo after checking logs and broadcasts..etc >> /root/zfspingtmp
else
 echo I am not a primary etcd.. heartbeating leader >> /root/zfspingtmp
 leader=`ETCDCTL_API=3 ./etcdget.py leader --prefix 2>&1`
 echo $leader | grep Error  &>/dev/null
 if [ $? -eq 0 ];
 then
  echo leader is dead.. stopping local etcd >> /root/zfspingtmp
  ETCDCTL_API=3 ./etcdgetlocal.py $myip known --prefix | wc -l | grep 1
  if [ $? -eq 0 ];
  then
   /TopStor/logmsg.sh Partst05 info system $myhost
   primtostd=0;
  fi
  systemctl stop etcd 2>/dev/null
  clusterip=`cat /pacedata/clusterip`
  echo starting primary etcd with clsuterip=$clusterip >> /root/zfspingtmp
  ETCDCTL_API=3 ./etccluster.py 'new' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload 2>/dev/null
  systemctl start etcd 2>/dev/null
  ETCDCTL_API=3 ./etcdput.py clusterip $clusterip 2>/dev/null
  pcs resource create clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24 2>/dev/null
  echo adding me as a leader >> /root/zfspingtmp
  ETCDCTL_API=3 ./runningetcdnodes.py $myip 2>/dev/null
  ETCDCTL_API=3 ./etcddel.py leader 2>/dev/null
  ETCDCTL_API=3 ./etcdput.py leader/$myhost $myip 2>/dev/null
  echo importing all pools >> /root/zfspingtmp
  /sbin/zpool import -a &>/dev/null
  echo running putzpool and nfs >> /root/zfspingtmp
  ETCDCTL_API=3 ./putzpool.py 2>/dev/null
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
#  ETCDCTL_API=3 ./etcdget.py clusterip 2>/dev/null > /pacedata/clusterip
  echo checking if I am known host >> /root/zfspingtmp
  known=`ETCDCTL_API=3 ./etcdget.py known --prefix 2>/dev/null`
  echo $known | grep $myhost  &>/dev/null
  if [ $? -ne 0 ];
  then
   echo I am not a known adding me as possible >> /root/zfspingtmp
   ETCDCTL_API=3 ./etcdput.py possible$myhost $myip 2>/dev/null
   isknown=0
  else
   echo I am known so running all needed etcd task:boradcast, log..etc >> /root/zfspingtmp
#   ETCDCTL_API=3 ./changeetcd.py 2>/dev/null
#   ETCDCTL_API=3 ./receivelog.py 2>/dev/null
#   ETCDCTL_API=3 ./broadcastlog.py 2>/dev/null
   echo $isknown | grep 0 
   if [ $? -eq 0 ];
   then
    echo running sendhost.py $leaderip 'user' 'recvreq' $myhost >>/root/tmp2
    leaderall=`ETCDCTL_API=3 ./etcdget.py leader --prefix `
    leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
    leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
    /pace/sendhost.py $leaderip 'user' 'recvreq' $myhost
    sleep 1
    /pace/sendhost.py $leaderip 'cifs' 'recvreq' $myhost
    ETCDCTL_API=3 /pace/etcddel.py md --prefix
    isknown=$((isknown+1))
   fi
   if [[ $isknown -le 10 ]];
   then
    isknown=$((isknown+1))
   fi
   echo $isknown | grep 3
   if [ $? -eq 0 ];
   then
    ETCDCTL_API=3 /pace/etcddel.py md --prefix
    /TopStor/logmsg.sh Partsu04 info system $myhost $myip
    msg="{'req': 'msg', 'reply': ['/TopStor/logmsg.sh','Partsu04','info','system','$myhost','$myip']}"
    /pace/sendhost.py $leaderip "$msg" 'recvreply' $myhost
   fi
   echo finish running tasks task:boradcast, log..etc >> /root/zfspingtmp
  fi
 fi 
fi
echo checking if I need to run local etcd >> /root/zfspingtmp
echo $needlocal | grep 1 &>/dev/null
if [ $? -eq 0 ];
then
  echo start the local etcd >> /root/zfspingtmp
  ETCDCTL_API=3 ./etccluster.py 'local' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload
  systemctl stop etcd 2>/dev/null
  systemctl start etcd 2>/dev/null
  ETCDCTL_API=3 ./etcdsync.py $myip primary primary 2>/dev/null
  ETCDCTL_API=3 ./etcddellocal.py $myip known --prefix 2>/dev/null
  ETCDCTL_API=3 ./etcddellocal.py $myip localrun --prefix 2>/dev/null
  ETCDCTL_API=3 ./etcddellocal.py $myip run --prefix 2>/dev/null
  ETCDCTL_API=3 ./etcdsync.py $myip known known 2>/dev/null
  ETCDCTL_API=3 ./etcdsync.py $myip localrun localrun 2>/dev/null
  ETCDCTL_API=3 ./etcdsync.py $myip leader known 2>/dev/null
#  ETCDCTL_API=3 ./etcddellocal.py $myip known/$myhost --prefix 2>/dev/null
  echo done and exit >> /root/zfspingtmp
  continue 
fi
echo $needlocal | grep 2 &>/dev/null
if [ $? -eq 0 ];
then
  echo I am already local etcd running iscsirefresh on $myip $myhost  >> /root/zfspingtmp
 /pace/iscsiwatchdog.sh $myip $myhost
  echo .. I am exiting now\(temporary\)  >> /root/zfspingtmp
 continue
fi
echo checking if still in the start initcron is still running  >> /root/zfspingtmp
if [ -f /pacedata/forzfsping ];
then
echo Yes. so I have to exit >> /root/zfspingtmp
 continue
fi
 echo No. so checking  I am primary >> /root/zfspingtmp
echo $runningcluster | grep 1 &>/dev/null
if [ $? -eq 0 ];
then
echo Yes I am a primary so will collect the scsi config for etcd  >> /root/zfspingtmp
 /pace/iscsiwatchdog.sh 2>/dev/null 
 lsscsi=`lsscsi -i --size | md5sum | awk '{print $1}'`
 lsscsiold=`ETCDCTL_API=3 /pace/etcdget.py checks/$myhost/lsscsi `
 echo $lsscsi | grep $lsscsiold
 if [ $? -eq 0 ];
 then
  echo collecting the zpool status too as long the scsi config stabilized >> /root/zfspingtmp
  zpool=`/sbin/zpool status 2>/dev/null`
  if [[ -z $zpool ]];
   then
    zpool='0'
    echo no pools are found >> /root/zfspingtmp
  fi
  echo old zpool and new zpool status compare >> /root/zfspingtmp
  zpool1=`echo $zpool | md5sum | awk '{print $1}'`
  zpool1old=`ETCDCTL_API=3 /pace/etcdget.py checks/$myhost/zpool 2>/dev/null`
  if [[ -z $zpool1old ]];
  then
   echo no pools are registered before>> /root/zfspingtmp
   zpool1old='0'
  fi
  echo $zpool1 | grep $zpool1old &>/dev/null
  if [ $? -eq 0 ];
  then 
   echo no new change either in scsi nor in a zpool>> /root/zfspingtmp
   echo $zpool | grep -E "FAIL|OFFL|was " &>/dev/null
   if [ $? -ne 0 ];
   then
    echo no new change either in scsi nor in a zpool..exiting>> /root/zfspingtmp
    continue
   fi
    echo no new changes either in scsi nor in a zpool. but zpool degraded>> /root/zfspingtmp
   
  else
   echo collecting new change in pool>> /root/zfspingtmp
   ETCDCTL_API=3 /pace/etcdput.py checks/$myhost/zpool $zpool1
  fi
 else 
   echo collecting new change in scsi>> /root/zfspingtmp
  ETCDCTL_API=3 /pace/etcdput.py checks/$myhost/lsscsi $lsscsi 
 fi
fi
hostnam=`cat /TopStordata/hostname`
declare -a pools=(`/sbin/zpool list -H 2>/dev/null  | awk '{print $1}'`)
declare -a idledisk=();
declare -a hostdisk=();
declare -a alldevdisk=();
cd /pace
echo checking if a disk is faulty >> /root/zfspingtmp
fdisk -l 2>&1 | grep "cannot open"
if [ $? -eq 0 ];
then
 echo a disk is found faulty >> /root/zfspingtmp
 faileddisk=`fdisk -l 2>&1 | grep "cannot open" | awk '{print $4}' | awk -F':' '{print $1}' | awk -F'/' '{print $3}'`
 echo "offline" > /sys/block/$faileddisk/device/state
 echo "1" > /sys/block/$faileddisk/device/delete
 echo removing the disk from system  and restarting target>> /root/zfspingtmp
 sleep 2
 systemctl restart target 2>/dev/null
else
 echo no faulty disk  checking if the target is running ok>> /root/zfspingtmp
 targetcli ls &>/dev/null
 if [ $? -ne 0 ];
 then
 echo target is not running good so restarting and saving configuration>> /root/zfspingtmp
  systemctl restart target 2>/dev/null
  targetcli saveconfig 2>/dev/null
 fi
fi
if [ ! -z $pools ];
then
 echo going through pool health>> /root/zfspingtmp
 ids=`lsblk -Sn -o serial`
 for pool in "${pools[@]}"; do
 echo checking if a fualty disk is part of a pool>> /root/zfspingtmp
 spares=(`/sbin/zpool status $pool 2>/dev/null | grep scsi | grep -v OFFLINE | grep -v ONLINE | awk '{print $1}'`)  
  for spare in "${spares[@]}"; do
   echo disk $spare is faulty >> /root/zfspingtmp
   echo $ids | grep ${spare:8} &>/dev/null
   if [ $? -ne 0 ]; then
    diskid=`python3.6 diskinfo.py /pacedata/disklist.txt $spare`
    /TopStor/logmsg.sh Diwa4 warning system $spare $pool
    /sbin/zpool remove $pool $spare 2>/dev/null;
    ETCDCTL_API=3 /pace/putzpool.py 2>/dev/null
    if [ $? -eq 0 ]; then
     /TopStor/logmsg.sh Disu4 info system $spare 
     cachestate=1
    else 
     /TopStor/logmsg.sh Dist5 info system $spare
     /sbin/zpool offline $pool $spare 2>/dev/null
     /TopStor/logmsg.sh Disu5 info system $spare 
    fi
   fi
  done 
 done
 for pool in "${pools[@]}"; do
  echo checking if a offline disk in the pool>> /root/zfspingtmp
  singledisk=`/sbin/zpool list -Hv $pool 2>/dev/null | wc -l`
  zpool=`/sbin/zpool status $pool 2>/dev/null`
  if [ $singledisk -gt 3 ]; then
   echo "${zpool[@]}" | grep -E "FAULT|OFFLI" &>/dev/null
   if [ $? -eq 0 ];
   then
    echo found FAULT/OFFLINE disk in the pool>> /root/zfspingtmp
    faildisk=`echo "${zpool[@]}" | grep -E "FAULT|OFFLI" | awk '{print $1}'`
    diskpath=`ETCDCTL_API=3 /pace/diskinfo.py run getkey $faildisk `
    diskidf=`echo $diskpath | awk -F'/' '{print $(NF-1)}'`
    ETCDCTL_API=3 /pace/diskinfo.py run getkey $diskpath | awk -F'/' '{print $(NF-1)}'
    /TopStor/logmsg.sh Difa1 error system $diskidf $hostnam
    echo checking spare disk in the pool>> /root/zfspingtmp
    sparedisk=`echo "${zpool[@]}" | grep "AVAIL" | awk '{print $1}' | head -1 2>/dev/null`
    if [ ! -z $sparedisk  ]; then
      diskids=`ETCDCTL_API=3 /pace/diskinfo.py run getkey $sparedisk | awk -F'/' '{print $(NF-1)}'`
     echo diskids=$diskids
     /TopStor/logmsg.sh Dist2 info system $diskidf $diskids $hostnam
     echo /sbin/zpool offline $pool $faildisk 2>/dev//null
     /sbin/zpool offline $pool $faildisk 2>/dev/null
     echo replacing offline/faulty with spare in the pool>> /root/zfspingtmp
     echo /sbin/zpool replace $pool $faildisk $sparedisk $hostnam 2>/dev/null
     /sbin/zpool replace $pool $faildisk $sparedisk 2>/dev/null
     ETCDCTL_API=3 /pace/putzpool.py 2>/dev/null
     /TopStor/logmsg.sh Disu2 info system $diskidf $diskidf $hostnam
     /TopStor/logmsg.sh Dist3 info system $diskidf $hostnam
     echo detaching OFFLINE disk with spare in the pool>> /root/zfspingtmp
     /sbin/zpool detach $pool $faildisk &>/dev/null
     /sbin/zpool remove $pool $faildisk &>/dev/null
     /TopStor/logmsg.sh Disu3 info system $diskidf $hostnam
    else
     echo no spare disk >> /root/zfspingtmp
     echo detaching OFFLINE disk without spare in the pool>> /root/zfspingtmp
     /sbin/zpool detach $pool $faildisk &>/dev/null
     /sbin/zpool remove $pool $faildisk &>/dev/null
     ETCDCTL_API=3 /pace/putzpool.py 2>/dev/null
     /TopStor/logmsg.sh Disu3 info system $diskidf $hostnam
    fi
    ETCDCTL_API=3 /pace/putzpool.py run/$myhost --prefix 2>/dev/null
    diskstatus=`echo $diskpath | awk -F'/' '{OFS=FS;$NF=""; print}' `'status'
    diskfs=`ETCDCTL_API=3 /pace/diskinfo.py run getvalue $diskstatus `
    echo $diskfs | grep ONLINE
    if [ $? -eq 0 ];
    then
     ETCDCTL_API=3 ./putzpool.py 2>/dev/null
    fi
   fi
   /sbin/zpool status $pool 2>/dev/null| grep "was /dev" &>/dev/null
   if [ $? -eq 0 ]; then
    faildisk=`/sbin/zpool status $pool 2>/dev/null | grep "was /dev" | awk -F'-id/' '{print $2}' | awk -F'-part' '{print $1}'`;
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    /sbin/zpool remove $pool $faildisk &>/dev/null;
    ETCDCTL_API=3 /pace/putzpool.py 2>/dev/null
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
    cachestate=1;
   fi 
   /sbin/zpool status $pool 2>/dev/null| grep "was /dev/s" ;
   if [ $? -eq 0 ]; then
    faildisk=`/sbin/zpool status $pool 2>/dev/null| grep "was /dev/s" | awk -F'was ' '{print $2}'`;
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    /sbin/zpool remove $pool $faildisk &>/dev/null;
    ETCDCTL_API=3 /pace/putzpool.py 2>/dev/null
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool ;
    cachestate=1;
   fi 
   /sbin/zpool status $pool 2>/dev/null| grep UNAVAIL &>/dev/null
   if [ $? -eq 0 ]; then
    faildisk=`/sbin/zpool status $pool 2>/dev/null| grep UNAVAIL | awk '{print $1}'`;
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    /sbin/zpool remove $pool $faildisk &>/dev/null;
    ETCDCTL_API=3 /pace/putzpool.py 2>/dev/null
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
    cachestate=1;
   fi 
  fi
 done
 echo after long operations due to a faulty disk is inside a pool>> /root/zfspingtmp
fi
done
