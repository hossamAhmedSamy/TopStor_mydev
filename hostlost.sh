#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
myhost=`hostname -s `
thehost=`echo $@ | awk '{print $1}'`
#declare -a disks=(`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`);
declare -a disks=`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`;
echo "${disks[@]}"
echo "${disks[@]}" > /root/losthost
echo "${disks[@]}" | awk '{print $1}' | awk -F'/' '{print $NF}' | while read l;
do
 echo 1 > /sys/block/$l/device/delete
done
zpool=`ETCDCTL_API=3 /pace/etcdget.py run --prefix | grep $myhost | grep disk | grep -v free` 
pool=`ETCDCTL_API=3 /pace/etcdget.py run --prefix | grep $myhost | grep pool | grep name | awk -F'name' '{print $2}' | cut -c 5- | rev | cut -c 3- | rev` 
echo pool=$pool >/root/hostlosttmp
echo zpool="${zpool[@]}" >> /root/hostlosttmp
echo disks="$disks[@]}" >> /root/hostlosttmp
echo "${disks[@]}" | awk '{print $2}'  | while read l;
do
 echo checking disk $l >> /root/hostlosttmp
 echo "${zpool[@]}" | grep $l
 if [ $? -eq 0 ];
 then
   echo offlining disk $l in pool $pool >> /root/hostlosttmp
  /sbin/zpool offline  $pool scsi-$l
 fi
done
echo udpating database >> /root/hostlosttmp
ETCDCTL_API=3 /pace/etcddel.py run $thehost 
ETCDCTL_API=3 /pace/etcddel.py run disk 
ETCDCTL_API=3 /pace/putzpool.py 

exit
