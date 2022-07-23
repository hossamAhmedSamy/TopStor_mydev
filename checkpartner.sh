#!/bin/sh
echo $@ > /root/checkpartnertemp
partner=`echo $@ | awk '{print $1}'`
partnerip=`echo $@ | awk '{print $2}'`
port=`echo $@ | awk '{print $3}'`
isnew=`echo $@ | awk '{print $4}'`
count=0
nodeloc='ssh -i /TopStordata/'${partnerip}'_keys/'${partnerip}' -p '$port' '${partnerip}
result='closed'
myip=`/sbin/pcs resource show CC | grep Attrib | awk -F'ip=' '{print $2}' | awk '{print $1}'`
/TopStor/etcdget.py nodereceiver/${partner} $partnerip | grep $myip
if [ $? -ne 0 ];
then
 isnew='new'
fi
echo $isnew | grep 'new' >/dev/null
if [ $? -eq 0 ];
then
 strict='-o StrictHostKeyChecking=no' 
 known=`cat /root/.ssh/known_hosts | grep -v $partnerip`
 echo -e "$known" > /root/.ssh/known_hosts
 clusterip=`echo $@ | awk '{print $3}'`
else
 strict=''
fi
while [ $count -le 10 ];
do
 ssh -oBatchmode=yes -i /TopStordata/${partnerip}_keys/${partnerip} -p $port $strict ${partnerip} ls  >/dev/null 2>/dev/null
 if [ $? -eq 0 ];
 then
  result='open'
  echo $isnew | grep 'new' >/dev/null
  if [ $? -eq 0 ];
  then
   noden=`$nodeloc /usr/bin/hostname` 
   nodei=`$nodeloc /TopStor/etcdget.py ready/$noden` 
   echo nodei=$nodei
   echo $nodei | grep $partnerip
   if [ $? -ne 0 ];
   then
    stamp=`date +%s` 
    known=`cat /root/.ssh/known_hosts | grep -v $partnerip`
    echo -e "$known" > /root/.ssh/known_hosts
    /TopStor/preparekeys.sh $nodei 
    ssh -oBatchmode=yes -i /TopStordata/${nodei}_keys/${nodei} -p $port $strict ${nodei} ls  >/dev/null 2>/dev/null
   fi
   /TopStor/etcdput.py Partnernode/${partner}/$nodei/$myip $noden 
   /TopStor/etcdput.py sync/Partnernode/$nodei/$myip $stamp
  fi
  count=11
 else
  count=$((count +1))
  sleep 1
 fi
done
echo $result 
