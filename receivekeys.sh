#!/bin/sh
echo $@ > /root/receivekeys
partner=`echo $@ | awk '{print $1}'`
partnerip=`echo $@ | awk '{print $2}'`
clusterip=`echo $@ | awk '{print $3}'`
port=`echo $@ | awk '{print $4}'`
ptype=`echo $@ | awk '{print $5}'`
ppass=`echo $@ | awk '{print $6}'`
keys=`echo $@ | awk '{print $7}'`
./etcdget.py Partner $clusterip | grep $ppass | grep $port 
if [ $? -eq 0 ];
then
 echo it is ok >> /root/receivekeys
fi
exit
cd /TopStordata/
mkdir ${partner}_keys 2>/dev/null
cd ${partner}_keys 
rm -rf * 2>/dev/null
ssh-keygen -f $partner -N "" 1>/dev/null
cat ${partner}.pub
