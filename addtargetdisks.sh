cd /pace
myhost=`hostname`;
declare -a iscsitargets=(`cat /pacedata/iscsitargets | awk '{print $2}' `);
declare -a disks=(`lsblk -nS | grep -v sr0 | grep -v sda | grep -v LIO | awk '{print $1}'`)
mappedhosts=`targetcli ls /iscsi | grep Mapped`;
targets=`targetcli ls backstores/block | grep -v deactivated |  grep dev | awk -F'[' '{print $2}' | awk '{print $1}'`
tpgs=(`targetcli ls /iscsi | grep iqn | grep TPG | awk -F'iqn' '{print $2}' | awk '{print $1}'`)
declare -a newdisks=();
targetcli ls iscsi/ | grep ".$myhost:t1" &>/dev/null
if [ $? -ne 0 ]; then
 targetcli iscsi/ create iqn.2016-03.com.${myhost}:t1 &>/dev/null
fi
i=0;
for devdisk in "${disks[@]}"; do
 echo $targets | grep $devdisk &>/dev/null
 if [ $? -ne 0 ]; then
  newdisks[$i]=$devdisk
  i=$((i+1)) 
 fi
done
for devdisk in "${newdisks[@]}"; do
 /sbin/zpool labelclear /dev/$devdisk;
 targetcli backstores/block create $devdisk /dev/$devdisk
 for iqn in "${tpgs[@]}"; do
  targetcli iscsi/iqn${iqn}/tpg1/luns/ create /backstores/block/$devdisk   
 done
done;

for target in "${iscsitargets[@]}"; do
 echo $mappedhosts | grep $target &>/dev/null
 if [ $? -ne 0 ]; then
  targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/acls/ create iqn.1994-05.com.redhat:$target
 fi
done
targetcli saveconfig
