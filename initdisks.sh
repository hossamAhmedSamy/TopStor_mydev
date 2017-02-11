#!/bin/sh 
cd /pace
#### typeis : 1 for mirror... 0 for capacity stripe  ######
typeis=`echo $@ | awk '{print $1}'`
iscsimapping='/pacedata/iscsimapping';
targethosts='/pacedata/iscsitargets';
myhost=`hostname -s`
#runningpools='/pacedata/pools/runningpools';
nhosts=`cat $targethosts | wc -l`
if [ $nhosts -le 1 ]; then
 /sbin/zpool import -a
fi
/sbin/zpool status > /pacedata/zpoolstatus
/sbin/zpool import >>/pacedata/zpoolstatus
runningpools='/pacedata/zpoolstatus';
declare -a idledisk=();
declare -a hostdisk=();
declare -a runninghosts=(`cat $iscsimapping | grep -v notconnected | awk '{print $1}'`);
while read -r  hostline ; do
 host=`echo $hostline | grep -v notconnected | awk '{print $1}'`;
 if [ ! -z "$host" ]; then
  ls -l /dev/disk/by-path/ | grep "$host" &>/dev/null;
  if [ $? -eq 0 ]; then
   devformatted=`echo $hostline | awk '{print $2}'`;
   newdiskid=`echo $hostline | awk '{print $3}'`;
   echo newdiskid=$newdiskid
   cat $runningpools | grep "$newdiskid" &>/dev/null
   if [ $? -ne 0 ]; then 
    echo here $newdisk
    echo $host | grep $myhost &>/dev/null
    if [ $? -eq 0 ]; then
     hostdisk=("${hostdisk[@]}" "$host,$newdiskid");
    else
     echo idledisk=$idledisk
     idledisk=("${idledisk[@]}" "$host,$newdiskid");
    fi
   fi
  fi
 fi
done < $iscsimapping

for localdisk in "${hostdisk[@]}"; do
 nextpool=`zpool list  | wc -l`
 echo idledisk=${#idledisk[@]} localdisk=$localdisk 
 if [ ${#idledisk[@]} -eq 0 ]; then
   disk2=`echo ${localdisk} | awk -F',' '{print $2}'`
 echo nextpool=$nextpool disk2=$disk2
   /sbin/zpool labelclear /dev/disk/by-id/${disk2};
   rm -rf /p${nextpool} &>/dev/null
   if [ $nextpool -gt 1 ]; then
    if [ $typeis -eq 1 ]; then
     olddisk=`cat $runningpools | grep "$myhost" | grep p1 | awk '{print $12}' | grep scsi`
     echo olddisk=$olddisk
   	/sbin/zpool attach -f  p1 $olddisk ${disk2} ;
    else
   	/sbin/zpool create -o ashift=12 -o autoexpand=on -o autoreplace=on -f p${nextpool} ${disk2} ;
    fi
   else
   	/sbin/zpool create -o ashift=12 -o autoexpand=on -o autoreplace=on -f p${nextpool} ${disk2} ;
   /sbin/zfs set compression=lz4 p${nextpool}
   /sbin/zfs set atime=off p${nextpool}
   /sbin/zfs set xattr=sa p${nextpool}
   /sbin/zfs set redundant_metadata=most p${nextpool}
   /sbin/zfs set dedup=on p${nextpool}
   echo /sbin/zpool create p${nextpool} /dev/disk/by-id/scsi-${disk2} ;
  fi
 else
  x=$((${#idledisk[@]}-1));
  if [ $x -ge 0 ]; then
   disk1=`echo ${idledisk[$x]} | awk -F',' '{print $2}'`
   disk2=`echo ${localdisk} | awk -F',' '{print $2}'`
   /sbin/zpool labelclear /dev/disk/by-id/${disk1};
   /sbin/zpool labelclear /dev/disk/by-id/${disk2};
   rm -rf /p${nextpool} &>/dev/null
   /sbin/zpool create -o ashift=12 -o autoexpand=on -o autoreplace=on -f p${nextpool} mirror ${disk1} ${disk2} ;
   /sbin/zfs set compression=lz4 p${nextpool}
   /sbin/zfs set atime=off p${nextpool}
   /sbin/zfs set xattr=sa p${nextpool}
   /sbin/zfs set redundant_metadata=most p${nextpool}
   /sbin/zfs set dedup=on p${nextpool}
   echo /sbin/zpool create p${nextpool} mirror /dev/disk/by-id/scsi-${disk1} /dev/disk/by-id/scsi-${disk2} ;
   if [ $? -eq 0 ]; then 
    unset idledisk[$x];
   fi
  fi
 fi
done
