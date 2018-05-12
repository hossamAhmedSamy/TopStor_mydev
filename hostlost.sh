#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
thehost=`echo $@ | awk '{print $1}'`
#declare -a disks=(`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`);
declare -a disks=`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`;
echo "${disks[@]}"
echo "${disks[@]}" > /root/losthost
echo "${disks[@]}" | awk '{print $1}' | awk -F'/' '{print $NF}' | while read l;
do
 echo 1 > /sys/block/$l/device/delete
done
ETCDCTL_API=3 /pace/etcddel.py run $thehost 
ETCDCTL_API=3 /pace/etcddel.py run disk 
ETCDCTL_API=3 /pace/putzpool.py 

exit
