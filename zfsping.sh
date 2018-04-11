#!/usr/bin/sh
cd /pace
touch /tmp/zfsping
if [ -f /pacedata/startzfs ];
then
 echo here??
 exit
fi
iscsimapping='/pacedata/iscsimapping';
sumfile='/pacedata/sumfile';
runningpools='/pacedata/pools/runningpools';
myip=`pcs resource show CC | grep Attribute | awk '{print $2}' | awk -F'=' '{print $2 }'`
myhost=`hostname -s`
freshcluster=0
systemctl status etcd &>/dev/null
if [ $? -eq 0 ];
then
 freshcluster=1
 leader='"'`ETCDCTL_API=3 ./etcdget.py leader --prefix`'"'
 echo $leader | grep '""'
 if [ $? -eq 0 ]; 
 then
  ETCDCTL_API=3 ./runningetcdnodes.py $myip
  ETCDCTL_API=3 ./etcdput.py leader$myhost $myip
 fi
 echo $leader | grep $myip
 if [ $? -ne 0 ];
 then
   systemctl stop etcd
 fi
 ETCDCTL_API=3 ./addknown.py
 ETCDCTL_API=3 ./allconfirmed.py
 ETCDCTL_API=3 ./broadcastlog.py
 ETCDCTL_API=3 ./receivelog.py
else
 leader=`ETCDCTL_API=3 ./etcdget.py leader --prefix 2>&1`
 echo $leader | grep Error  &>/dev/null
 if [ $? -eq 0 ];
 then
  clusterip=`cat /pacedata/clusterip`
  ./etccluster.py
  systemctl daemon-reload;
  systemctl start etcd;
  ETCDCTL_API=3 ./etcdput.py clusterip $clusterip
#  pcs resource update clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24 &>/dev/null
#  if [ $? -ne 0 ];
#  then 
  pcs resource create clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24;
#  fi
#  pcs resource enable clusterip
  ETCDCTL_API=3 ./runningetcdnodes.py $myip
  ETCDCTL_API=3 ./etcdput.py leader$myhost $myip
  freshcluster=1
 else 
  echo checking leader
  ETCDCTL_API=3 ./etcdget.py clusterip > /pacedata/clusterip 
  known=`ETCDCTL_API=3 ./etcdget.py known --prefix 2>&1`
  echo $known | grep $myhost  &>/dev/null
  if [ $? -ne 0 ];
  then
   ETCDCTL_API=3 ./etcdput.py possible$myhost $myip
  else
   ETCDCTL_API=3 ./changeetcd.py
   ETCDCTL_API=3 ./receivelog.py
   ETCDCTL_API=3 ./broadcastlog.py
  fi
 fi 
fi
 
 
hostnam=`cat /TopStordata/hostname`
poollist='/pacedata/pools/'${myhost}'poollist';
cachestate=0;
cd /pacedata/pools/
allpools=`cat /pacedata/pools/$(ls /pacedata/pools/ | grep poollist)`
if [ ! -f ${iscsimapping} ];
then 
  echo here
 exit
fi
echo ${iscsimapping} ${iscsimapping}new;
cp ${iscsimapping} ${iscsimapping}new;
declare -a pools=(`/sbin/zpool list -H | awk '{print $1}'`)
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
 systemctl restart target
else
 targetcli ls &>/dev/null
 if [ $? -ne 0 ];
 then
  systemctl restart target
  targetcli saveconfig
 fi
 lsblk -Sn | md5sum --check $sumfile
 if [ $? -ne 0 ];
 then
  lsblk -Sn | md5sum > $sumfile
  echo hereherehere
  ./addtargetdisks.sh
 fi
fi
echo $freshcluster | grep 1
if [ $? -ne 0 ];
then
 echo not leader
 sh iscsirefresh.sh   &>/dev/null &
 sh listingtargets.sh  &>/dev/null
 ./addtargetdisks.sh
fi
ids=`lsblk -Sn -o serial`
echo $freshcluster | grep 1
if [ $? -ne 0 ];
then
 for pool in "${pools[@]}"; do
  spares=(`/sbin/zpool status $pool | grep scsi | grep -v OFFLINE | awk '{print $1}'`)  
  for spare in "${spares[@]}"; do
   echo $ids | grep ${spare:8} &>/dev/null
   if [ $? -ne 0 ]; then
    diskid=`python3.6 diskinfo.py /pacedata/disklist.txt $spare`
    /TopStor/logmsg.sh Diwa4 warning system $diskid 
    zpool remove $pool $spare;
    if [ $? -eq 0 ]; then
     /TopStor/logmsg.sh Disu4 info system $diskid 
     cachestate=1
    else 
    /TopStor/logmsg.sh Dist5 info system $diskid 
     zpool offline $pool $spare
     echo $spare >/pacedata/Offlinedisks
    /TopStor/logmsg.sh Disu5 info system $diskid 
    fi
   fi  
  done 
 done
fi
echo $freshcluster | grep 1
if [ $? -ne 0 ];
then
 echo here here
 exit
fi
 sh iscsirefresh.sh   &>/dev/null &
 sh listingtargets.sh  &>/dev/null
 sleep 1
runninghosts=`cat $iscsimapping | grep -v notconnected | awk '{print $1}'`
for pool in "${pools[@]}"; do
 singledisk=`/sbin/zpool list -Hv $pool | wc -l`
 zpool=`/sbin/zpool status $pool`
 if [ $singledisk -gt 3 ]; then
  echo "${zpool[@]}" | grep -E "FAULT|OFFLI" &>/dev/null
  if [ $? -eq 0 ];
  then
   /TopStor/GetDisklist a
   faildisk=`echo "${zpool[@]}" | grep -E "FAULT|OFFLI" | awk '{print $1}'`
   diskidf=`python3.6 diskinfo.py /pacedata/disklist.txt $faildisk`
   cat /pacedata/Offlinedisks | grep $faildisk
   if [ $? -ne 0 ]; then
    /TopStor/logmsg.sh Difa1 error system $diskidf 
    echo $faildisk > /pacedata/Offlinedisks
    echo hi
   fi
   sparedisk=`echo "${zpool[@]}" | grep "AVAIL" | awk '{print $1}' | head -1`
   if [ ! -z $sparedisk ]; then
   diskids=`python3.6 diskinfo.py /pacedata/disklist.txt $sparedisk`
    /TopStor/logmsg.sh Dist2 info system $diskidf $diskids  
    /sbin/zpool replace $pool $faildisk $sparedisk
    /TopStor/logmsg.sh Disu2 info system $diskidf $diskidf  
    /TopStor/logmsg.sh Dist3 info system $diskf
    /sbin/zpool detach $pool $faildisk &>/dev/null;
    /TopStor/logmsg.sh Disu3 info system $diskidf
    echo hi > /pacedata/Offlinedisks
    #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
    cachestate=1;
   fi
  fi
  /sbin/zpool status $pool | grep "was /dev" &>/dev/null
  if [ $? -eq 0 ]; then
   faildisk=`/sbin/zpool status $pool | grep "was /dev" | awk -F'-id/' '{print $2}' | awk -F'-part' '{print $1}'`;
   /sbin/zpool detach $pool $faildisk &>/dev/null;
   #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
   cachestate=1;
  fi 
  /sbin/zpool status $pool | grep "was /dev/s" ;
  if [ $? -eq 0 ]; then
   faildisk=`/sbin/zpool status $pool | grep "was /dev/s" | awk -F'was ' '{print $2}'`;
   /sbin/zpool detach $pool $faildisk &>/dev/null;
   #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool ;
   cachestate=1;
  fi 
  /sbin/zpool status $pool | grep UNAVAIL &>/dev/null
  if [ $? -eq 0 ]; then
   faildisk=`/sbin/zpool status $pool | grep UNAVAIL | awk '{print $1}'`;
   /sbin/zpool detach $pool $faildisk &>/dev/null;
   #/sbin/zpool set cachefile=/pacedata/pools/${pool}.cache $pool;
   cachestate=1;
  fi 
 fi
done
while read -r  hostline ; do
 host=`echo $hostline | awk '{print $1}'`
 echo $hostline | grep "notconnected" &>/dev/null
 if [ $? -eq 0 ]; then
  hostdiskid=`echo $host | awk '{print $3}'`
  for pool2 in "${pools[@]}"; do
   /sbin/zpool list -Hv $pool2 | grep "$hostdiskid" &>/dev/null
   if [ $? -eq 0 ]; then 
    /sbin/zpool offline $pool2 "$hostdiskid" &>/dev/null;
    #/sbin/zpool set cachefile=/pacedata/pools/${pool2}.cache $pool2;
   cachestate=1;
   fi
  done
  cat ${iscsimapping}new | grep -w "$host" | grep "notconnected" &>/dev/null
  if [ $? -ne 0 ]; then 
#   echo disconnecting $host disks
   declare -a hostdiskids=(`cat ${iscsimapping}new | grep -w "$host" | awk '{print $3}'`);
   for hostdiskid in "${hostdiskids[@]}"; do
    for pool2 in "${pools[@]}"; do
     /sbin/zpool list -Hv $pool2 | grep "$hostdiskid" &>/dev/null
     if [ $? -eq 0 ]; then 
      /sbin/zpool offline $pool2 "$hostdiskid" &>/dev/null;
     # /sbin/zpool set cachefile=/pacedata/pools/${pool2}.cache $pool2;
      cachestate=1;
     fi
    done
   done;
  fi
 fi
done < ${iscsimapping}
echo $freshcluster | grep 1
if [ $? -eq 0 ];
then
 /sbin/zpool import -a
 systemctl start nfs
 chgrp apache /var/www/html/des20/Data/*
 chmod g+r /var/www/html/des20/Data/*
fi
