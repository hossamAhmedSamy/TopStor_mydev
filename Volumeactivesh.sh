#!/bin/sh
export ETCDCTL_API=3
cd /TopStor/
echo $@ > /root/volumeactivesh
pDG=`echo $@ | awk '{print $1}'`;
name=`echo $@ | awk '{print $2}'`;
prot=`echo $@ | awk '{print $3}'`;
active=`echo $@ | awk '{print $4}'`;
ipaddr=` echo $@ | awk '{print $5}'`;
userreq=` echo $@ | awk '{print $6}'`;
privilege=$prot;
contrun=`./privthis.sh $privilege $userreq`;
if [[ $contrun == 'true' ]]
then
 docker exec etcdclient /TopStor/logqueue.py `basename "$0"` running $userreq
 echo prot=$prot, $active
 echo $prot | grep CIFS
 if [ $? -eq 0 ]
 then
  echo $active | grep disabled
  if [ $? -eq 0 ]
  then
   sed -i 's/active/disabled/g' /$pDG/smb.$name
   dockerps=`docker ps | grep $ipaddr | awk '{print $1}'`
   docker rm -f $dockerps 2>/dev/null
  
   zfs set status:mount=disabled $pDG/$name
   zfs unmount -f $pDG/$name
  else
   sed -i 's/disabled/active/g' /$pDG/smb.$name*
   zfs mount $pDG/$name
   zfs set status:mount=active $pDG/$name
   ./VolumeCheck.py
  fi
 fi
fi
 docker exec etcdclient /TopStor/logqueue.py `basename "$0"` stop $userreq
