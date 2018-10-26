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
 echo 1 > /sys/block/$l/device/delete 2>/dev/null
done
echo disks="${disks[@]}" >> /root/hostlosttmp
echo "${disks[@]}" | awk '{print $2}'  | while read l;
do
 echo checking disk $l >> /root/hostlosttmp
 ETCDCTL_API=3 /pace/changeop.py $myhost scsi-$l 
done
echo udpating database >> /root/hostlosttmp
ETCDCTL_API=3 /pace/etcddel.py hosts/$thehost  --prefix
ETCDCTL_API=3 /pace/etcddel.py cannot  --prefix
ETCDCTL_API=3 /pace/etcddel.py oldhosts/$thehost  --prefix
ETCDCTL_API=3 /pace/putzpool.py 
