#!/bin/sh
echo $@ > /root/targetcreatevol
cd /TopStor

owner=`/TopStor/etcdgetlocal.py clusternode`
pool=`echo $@ | awk '{print $1}' | awk -F'/' '{print $1}'`
name=`echo $@ | awk '{print $1}' | awk -F'/' '{print $2}'`
ipaddress=`echo $@ | awk '{print $2}'`
Subnet=`echo $@ | awk '{print $3}'`
size=`echo $@ | awk '{print $4}'`
typep=`echo $@ | awk '{print $5}'`
groups=`echo $@ | awk '{print $6}'`
oldsnap=`echo $@ | awk '{print $7}'`
newvol=`./etcdgetlocal.py vol $name | grep $pool | awk -F'/' '{print $6}'`

leaderip=` ./etcdgetlocal.py leaderip `
echo $newvol | grep $name 
if [ $? -eq 0 ];
then
 volinfo=`./etcdgetlocal.py vol $newvol`
 zfs unmount -f $pool/${newvol}
 #latestsnap=`/TopStor/getlatestsnap.py $newvol | awk -F'result_' '{print $2}'`
 echo zfs rollback $pool/$newvol@$oldsnap
 echo 'noold' | grep $oldsnap
 if [ $? -eq 0 ];
 then
  zfs list -t snapshot -o name | grep ^${pool}/${newvol}@  | tac | xargs -n 1 zfs destroy -r 
 else
  zfs rollback -r $pool/$newvol@$oldsnap
 fi
 oldnew='old'
else 
 echo ./createmyvol.py $owner $pool $name $ipaddress $Subnet $size $typep $groups > /root/targetcreatevol
 ./createmyvol.py $owner $pool $name $ipaddress $Subnet $size $typep $groups
 oldnew='new'
 latestsnap=''
 zfs destroy -f $pool/${newvol}
fi
newvol=`./etcdgetlocal.py vol $name | grep $pool | awk -F'/' '{print $6}'`
echo $newvol | grep $name 
if [ $? -eq 0 ];
then
 volinfo=`./etcdgetlocal.py vol $newvol`
 volleft=` echo $volinfo | awk -F"'," '{print $1}' | awk -F"'" '{print $2}'`
 volright=` echo $volinfo | awk -F"'," '{print $2}' | awk -F"'" '{print $2}'`
 volleft=`echo $volleft | sed 's/active/replica/g'`
 zfs set status:mount=disabled $pool/$newvol 
 echo ./etcdputlocal.py $volleft $volright
 ./etcdput.py $leaderip $volleft $volright
 stamp=`date +%s`
 leader=`./etcdgetlocal.py leader `
 ETCDCTL_API=3 /pace/etcdput.py $leaderip sync/volumes/${pool}_$newvol/request volumes_$stamp
 ETCDCTL_API=3 /pace/etcdput.py $leaderip sync/volumes/${pool}_$newvol/request/$leader volumes_$stamp
 docker rm -f `docker ps | grep $ipaddress | awk '{print $1}'` 2>/dev/null
 echo result_${oldnew}vol/@${oldnew}result_$pool/${newvol}result_${latestsnap}result_
else
 echo result_problem/@newresult_
 
fi 
