#!/bin/sh
echo $@ > /root/checkpartnertemp
partner=`echo $@ | awk '{print $1}'`
replitype=`echo $@ | awk '{print $2}'`
partnerip=`echo $@ | awk '{print $3}'`
port=`echo $@ | awk '{print $4}'`
clusterip=`echo $@ | awk '{print $5}'`
phrase=`echo $@ | awk '{print $6}'`
isnew=`echo $@ | awk '{print $7}'`
count=0
nodeloc='ssh -oBatchmode=yes -i /TopStordata/'${partnerip}'_keys/'${partnerip}' -p '$port' '${partnerip}
result='closed'
myip=`/sbin/pcs resource show CC | grep Attrib | awk -F'ip=' '{print $2}' | awk '{print $1}'`
myhost=`hostname`
/TopStor/etcdget.py Partnernode/${partner}_$replitype $partnerip | grep $myip
if [ $? -ne 0 ];
then
 isnew='new'
 echo partner is new to myhost
fi
if [ ! -f /TopStordata/${partnerip}_keys/${partnerip}  ];
then
 isnew='new'
 echo keys are not found so makeing new ones
fi

ssh -oBatchmode=yes -i /TopStordata/${partnerip}_keys/${partnerip} -p $port ${partnerip} ls  >/dev/null 2>/dev/null
if [ $? -ne 0 ];
then
 isnew='new'
 echo partner is not connecting
fi

echo $isnew | grep 'new' >/dev/null
if [ $? -eq 0 ];
then
 /TopStor/pumpkeys.py $partnerip $replitype $port $phrase
 strict='-o StrictHostKeyChecking=no' 
 known=`cat /root/.ssh/known_hosts | grep -v $partnerip`
 echo -e "$known" > /root/.ssh/known_hosts
 clusterip=`echo $@ | awk '{print $3}'`
else
 strict=''
fi
while [ $count -le 10 ];
do
 echo ssh -oBatchmode=yes -i /TopStordata/${partnerip}_keys/${partnerip} -p $port $strict ${partnerip} ls 
 ssh -oBatchmode=yes -i /TopStordata/${partnerip}_keys/${partnerip} -p $port $strict ${partnerip} ls  >/dev/null 2>/dev/null
 if [ $? -eq 0 ];
 then
  result='open'
  echo $isnew | grep 'new' >/dev/null
  if [ $? -eq 0 ];
  then
   noden=`$nodeloc /usr/bin/hostname` 
   nodei=`$nodeloc /TopStor/etcdget.py ready/$noden` 
#   /TopStor/pumpkeys.py $nodei $replitype $port $phrase
   echo nodei=$nodei
   sleep 2
   echo $nodei | grep $partnerip
   if [ $? -ne 0 ];
   then
    stamp=`date +%s` 
    known=`cat /root/.ssh/known_hosts | grep -v $partnerip`
    echo -e "$known" > /root/.ssh/known_hosts
    ssh -oBatchmode=yes -i /TopStordata/${nodei}_keys/${nodei} -p $port $strict ${nodei} ls  >/dev/null 2>/dev/null
   fi
   /TopStor/etcdput.py Partnernode/${partner}_$replitype/$nodei/$myip $noden 
   #/TopStor/etcdput.py sync/Partnernode/$nodei/$myip $stamp
   leader=`./etcdget.py leader --prefix`
   echo $leader | grep $myip
   if [ $? -ne 0 ];
   then
    /TopStor/etcdputlocal.py $myip Partnernode/${partner}_$replitype/$nodei/$myip $noden 
   fi
  fi
  count=11
 else
  count=$((count +1))
  sleep 1
 fi
done
echo $result 
