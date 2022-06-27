#!/bin/sh
partner=`echo $@ | awk '{print $1}'`
port=`echo $@ | awk '{print $2}'`
isnew=`echo $@ | awk '{print $3}'`
count=0
nodeloc='ssh -i /TopStordata/'${partner}'_keys/'${partner}' -p '$port' '${partner}
result='closed'
echo $isnew | grep 'new' >/dev/null
if [ $? -eq 0 ];
then
 strict='-o StrictHostKeyChecking=no' 
 known=`cat /root/.ssh/known_hosts | grep -v $partner`
 echo -e "$known" > /root/.ssh/known_hosts
 clusterip=`echo $@ | awk '{print $3}'`
else
 strict=''
fi
while [ $count -le 10 ];
do
 ssh -oBatchmode=yes -i /TopStordata/${partner}_keys/${partner} -p $port $strict ${partner} ls  >/dev/null 2>/dev/null
 if [ $? -eq 0 ];
 then
  result='open'
  echo $isnew | grep 'new' >/dev/null
  if [ $? -eq 0 ];
  then
   noden=`$nodeloc /usr/bin/hostname` 
   nodei=`$nodeloc /TopStor/etcdget.py ready/$noden` 
   /TopStor/etcdput.py Prtnrcluster/${partner}/$nodei $noden 
   ssh -oBatchmode=yes -i /TopStordata/${partner}_keys/${partner} -p $port $strict ${nodei} ls  >/dev/null 2>/dev/null
  fi
  count=11
 else
  count=$((count +1))
  sleep 1
 fi
done
echo $result 
