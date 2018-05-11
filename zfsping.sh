#!/usr/bin/sh
export ETCDCTL_API=3
cd /pace
if [ -f /pacedata/forzfsping ];
then
 touch /pacedata/forstartzfs
 exit
fi
needlocal=0
myip=`pcs resource show CC | grep Attribute | awk '{print $2}' | awk -F'=' '{print $2 }'`
myhost=`hostname -s`
runningcluster=0
netstat -ant | grep 2379 | grep $myip | grep LISTEN &>/dev/null
if [ $? -eq 0 ]; 
then
 runningcluster=1
 leader='"'`ETCDCTL_API=3 ./etcdget.py leader --prefix 2>/dev/null`'"'
 echo $leader | grep '""'
 if [ $? -eq 0 ]; 
 then
  ETCDCTL_API=3 ./runningetcdnodes.py $myip 2>/dev/null
  ETCDCTL_API=3 ./etcdput.py leader$myhost $myip 2>/dev/null
 fi
 echo $leader | grep $myip
 if [ $? -ne 0 ];
 then
  systemctl stop etcd 2>/dev/null
  needlocal=1
 fi
 ETCDCTL_API=3 ./addknown.py 2>/dev/null
 ETCDCTL_API=3 ./allconfirmed.py 2>/dev/null
 ETCDCTL_API=3 ./broadcastlog.py 2>/dev/null
 ETCDCTL_API=3 ./receivelog.py 2>/dev/null
else
 leader=`ETCDCTL_API=3 ./etcdget.py leader --prefix 2>&1`
 echo $leader | grep Error  &>/dev/null
 if [ $? -eq 0 ];
 then
   systemctl stop etcd 2>/dev/null
  clusterip=`cat /pacedata/clusterip`
  ETCDCTL_API=3 ./etccluster.py 'new' 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload 2>/dev/null
  systemctl start etcd 2>/dev/null
  ETCDCTL_API=3 ./etcdput.py clusterip $clusterip 2>/dev/null
  pcs resource create clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24 2>/dev/null
  ETCDCTL_API=3 ./runningetcdnodes.py $myip 2>/dev/null
  ETCDCTL_API=3 ./etcdput.py leader$myhost $myip 2>/dev/null
  /sbin/zpool import -a &>/dev/null
  ETCDCTL_API=3 ./putzpool.py 2>/dev/null
  systemctl start nfs 2>/dev/null
  chgrp apache /var/www/html/des20/Data/* 2>/dev/null
  chmod g+r /var/www/html/des20/Data/* 2>/dev/null
  runningcluster=1
 else 
  netstat -ant | grep 2378 | grep $myip | grep LISTEN &>/dev/null
  if [ $? -ne 0 ];
  then
   needlocal=1
  else
   needlocal=2
  fi
  echo checking leader
  echo $needlocal
  ETCDCTL_API=3 ./etcdget.py clusterip 2>/dev/null > /pacedata/clusterip
  known=`ETCDCTL_API=3 ./etcdget.py known --prefix 2>/dev/null`
  echo $known | grep $myhost  &>/dev/null
  if [ $? -ne 0 ];
  then
   ETCDCTL_API=3 ./etcdput.py possible$myhost $myip 2>/dev/null
  else
   echo I am possible
   ETCDCTL_API=3 ./changeetcd.py 2>/dev/null
   ETCDCTL_API=3 ./receivelog.py 2>/dev/null
   ETCDCTL_API=3 ./broadcastlog.py 2>/dev/null
  fi
 fi 
fi
echo $needlocal | grep 1 &>/dev/null
if [ $? -eq 0 ];
then
  ETCDCTL_API=3 ./etccluster.py 'local' 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload
  systemctl stop etcd 2>/dev/null
  systemctl start etcd 2>/dev/null
  exit
fi
echo $needlocal | grep 2 &>/dev/null
if [ $? -eq 0 ];
then
 exit
fi
if [ -f /pacedata/forzfsping ];
then
 exit
fi
echo $runningcluster | grep 1 &>/dev/null
if [ $? -eq 0 ];
then
 lsscsi=`lsscsi -i --size | md5sum | awk '{print $1}'`
 lsscsiold=`ETCDCTL_API=3 /pace/etcdget.py checks/$myhost/lsscsi `
 echo $lsscsi | grep $lsscsiold
 if [ $? -eq 0 ];
 then
  zpool=`zpool status 2>/dev/null`
  if [ -z $zpool ];
   then zpool='0'
  fi
  zpool1=`echo $zpool | md5sum | awk '{print $1}'`
  zpool1old=`ETCDCTL_API=3 /pace/etcdget.py checks/$myhost/zpool 2>/dev/null`
  if [ -z $zpool1old ];
  then
   zpool1old='0'
  fi
  echo $zpool1 | grep $zpool1old &>/dev/null
  if [ $? -eq 0 ];
  then 
   echo lsscsi no change
   exit
  else
   ETCDCTL_API=3 /pace/etcdput.py checks/$myhost/zpool $zpool1
  fi
 else 
  ETCDCTL_API=3 /pace/etcdput.py checks/$myhost/lsscsi $lsscsi 
 fi
fi
hostnam=`cat /TopStordata/hostname`
declare -a pools=(`/sbin/zpool list -H 2>/dev/null  | awk '{print $1}'`)
declare -a idledisk=();
declare -a hostdisk=();
declare -a alldevdisk=();
cd /pace
fdisk -l 2>&1 | grep "cannot open"
if [ $? -eq 0 ];
then
 faileddisk=`fdisk -l 2>&1 | grep "cannot open" | awk '{print $4}' | awk -F':' '{print $1}' | awk -F'/' '{print $3}'`
 echo "offline" > /sys/block/$faileddisk/device/state
 echo "1" > /sys/block/$faileddisk/device/delete
 sleep 2
 systemctl restart target 2>/dev/null
else
 targetcli ls &>/dev/null
 if [ $? -ne 0 ];
 then
  systemctl restart target 2>/dev/null
  targetcli saveconfig 2>/dev/null
 fi
fi
ids=`lsblk -Sn -o serial`
if [ ! -z $pools ];
then
 for pool in "${pools[@]}"; do
 spares=(`/sbin/zpool status $pool 2>/dev/null | grep scsi | grep -v OFFLINE | awk '{print $1}'`)  
  for spare in "${spares[@]}"; do
   echo $ids | grep ${spare:8} &>/dev/null
   if [ $? -ne 0 ]; then
    diskid=`python3.6 diskinfo.py /pacedata/disklist.txt $spare`
    /TopStor/logmsg.sh Diwa4 warning system $diskid $hostnam
    zpool remove $pool $spare 2>/dev/null;
    if [ $? -eq 0 ]; then
     /TopStor/logmsg.sh Disu4 info system $diskid $hostnam 
     cachestate=1
    else 
     /TopStor/logmsg.sh Dist5 info system $diskid  $hostnam
     zpool offline $pool $spare 2>/dev/null
     /TopStor/logmsg.sh Disu5 info system $diskid $hostnam 
    fi
   fi
  done 
 done
 for pool in "${pools[@]}"; do
  singledisk=`/sbin/zpool list -Hv $pool 2>/dev/null | wc -l`
  zpool=`/sbin/zpool status $pool 2>/dev/null`
  if [ $singledisk -gt 3 ]; then
   echo "${zpool[@]}" | grep -E "FAULT|OFFLI" &>/dev/null
   if [ $? -eq 0 ];
   then
    ETCDCTL_API=3 /pace/etcddel.py run/$myhost --prefix
    ETCDCTL_API=3 /pace/putzpool.py run/$myhost --prefix 2>/dev/null
    faildisk=`echo "${zpool[@]}" | grep -E "FAULT|OFFLI" | awk '{print $1}'`
    diskpath=`ETCDCTL_API=3 /pace/diskinfo.py run getkey $faildisk `
    echo $diskpath
    echo faildisk=$faildisk
    diskidf=`echo $diskpath | awk -F'/' '{print $(NF-1)}'`
    echo diskidf=$diskidf
    ETCDCTL_API=3 /pace/diskinfo.py run getkey $diskpath | awk -F'/' '{print $(NF-1)}'
    /TopStor/logmsg.sh Difa1 error system $diskidf $hostnam
    sparedisk=`echo "${zpool[@]}" | grep "AVAIL" | awk '{print $1}' | head -1`
    echo sparedisk=$sparedisk
    sparedisk=`echo "${zpool[@]}" | grep "AVAIL" | awk '{print $1}' | head -1`
    if [ ! -z $sparedisk ]; then
      diskids=`ETCDCTL_API=3 /pace/diskinfo.py run getkey $sparedisk | awk -F'/' '{print $(NF-1)}'`
     echo diskids=$diskids
     /TopStor/logmsg.sh Dist2 info system $diskidf $diskids $hostnam
     echo /sbin/zpool offline $pool $faildisk 2>/dev//null
     /sbin/zpool offline $pool $faildisk 2>/dev/null
     echo /sbin/zpool replace $pool $faildisk $sparedisk $hostnam 2>/dev/null
     /sbin/zpool replace $pool $faildisk $sparedisk 2>/dev/null
     echo is repalced ?
     /TopStor/logmsg.sh Disu2 info system $diskidf $diskidf $hostnam
     /TopStor/logmsg.sh Dist3 info system $diskidf $hostnam
     /sbin/zpool detach $pool $faildisk &>/dev/null
     /TopStor/logmsg.sh Disu3 info system $diskidf $hostnam
     ETCDCTL_API=3 /pace/etcddel.py run/$myhost --prefix
     ETCDCTL_API=3 /pace/putzpool.py run/$myhost --prefix 2>/dev/null
    fi
    diskstatus=`echo $diskpath | awk -F'/' '{OFS=FS;$NF=""; print}' `'status'
    diskfs=`ETCDCTL_API=3 /pace/diskinfo.py run getvalue $diskstatus `
    echo $diskfs | grep ONLINE
    if [ $? -eq 0 ];
    then
     ETCDCTL_API=3 ./etcddel.py run/myhost --prefix
     ETCDCTL_API=3 ./putzpool.py 2>/dev/null
    fi
   fi
   /sbin/zpool status $pool 2>/dev/null| grep "was /dev" &>/dev/null
   if [ $? -eq 0 ]; then
    faildisk=`/sbin/zpool status $pool 2>/dev/null | grep "was /dev" | awk -F'-id/' '{print $2}' | awk -F'-part' '{print $1}'`;
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
    cachestate=1;
   fi 
   /sbin/zpool status $pool 2>/dev/null| grep "was /dev/s" ;
   if [ $? -eq 0 ]; then
    faildisk=`/sbin/zpool status $pool 2>/dev/null| grep "was /dev/s" | awk -F'was ' '{print $2}'`;
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool ;
    cachestate=1;
   fi 
   /sbin/zpool status $pool 2>/dev/null| grep UNAVAIL &>/dev/null
   if [ $? -eq 0 ]; then
    faildisk=`/sbin/zpool status $pool 2>/dev/null| grep UNAVAIL | awk '{print $1}'`;
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
    cachestate=1;
   fi 
  fi
 done
 ETCDCTL_API=3 /pace/etcddel.py run/$myhost --prefix
 ETCDCTL_API=3 /pace/putzpool.py run/$myhost --prefix 2>/dev/null
 zpool1=`zpool status 2>/dev/null | md5sum | awk '{print $1}'`
 ETCDCTL_API=3 /pace/etcdput.py checks/$myhost/zpool $zpool1 
 lsscsi=`lsscsi -i --size | md5sum | awk '{print $1}'`
 ETCDCTL_API=3 /pace/etcdput.py checks/$myhost/lsscsi $lsscsi 
fi
