#!/bin/sh
cd /TopStor
export ETCDCTL_API=3
enpdev='enp0s8'
leaderip=`echo $@ | awk '{print $1}'`
pool=`echo $@ | awk '{print $2}'`
vol=`echo $@ | awk '{print $3}'`
ipaddr=`echo $@ | awk '{print $4}'`
ipsubnet=`echo $@ | awk '{print $5}'`
portalport=`echo $@ | awk '{print $6}'`
targetiqn=`echo $@ | awk '{print $7}'`
chapuser=`echo $@ | awk '{print $8}'`
chappas=`echo $@ | awk '{print $9}'`
vtype='iscsi'
myhost=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternode`
	myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
	leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
	echo $leader | grep $myhost
	if [ $? -ne 0 ];
	then
 		etcd=$myhostip
	else
 		etcd=$leaderip
 	fi

echo $@ > /root/iscsiparam
allvols=`./etcdget.py $etcd volumes --prefix`
replivols=`echo $allvols | grep $vol`
echo $replivols | grep active
if [ $? -ne 0 ];
then
 exit
fi

rightip=`/pace/etcdget.py $etcd ipaddr/$myhost $vtype-$ipaddr | grep -v $vol`
otherip=`/pace/etcdget.py $etcd ipaddr $vtype-$ipaddr | grep -v $myhost | wc -c`
othervtype=`/pace/etcdget.py $etcd ipaddr $ipaddr | grep -v $vtype | wc -c` 
if [ $otherip -ge 5 ];
then 
 echo another host is holding the ip
 echo otherip=$otherip
 exit
fi
if [ $othervtype -ge 5 ];
then 
 echo the ip is used by another protocol 
 /TopStor/logmsg.py ISCSIwa01 warning $userreq $ipaddr 
 exit
fi
resname=$vtype'-'$ipaddr
if [[ $rightip == '' ]];
then
 echo nothing found
 rightip=''
 rightvols=$vol
else
 echo found other vols
rightvols=`/pace/etcdget.py $etcd ipaddr/$myhost/$ipaddr/$ipsubnet | sed "s/$resname\///g"`'/'$vol
fi
 /pace/etcdput.py $leaderip ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols
 #/pace/broadcasttolocal.py ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols 
echo continue
echo /pace/addzfsvolumeastarget.sh $pool ${vol} $ipaddr $portalport $targetiqn $chapuser $chappas
 for i in $(echo $targetiqn | sed "s/,/ /g")
 do
#pdhcp2524812990 pool1is_250024055 10.11.11.11 3263 iqn.1991-05.com.microsoft:desktop-jckvhk3 MoatazNegm MezoAdmin
  /pace/addzfsvolumeastarget.sh $pool $vol $ipaddr $portalport $i $chapuser $chappas 

    # call your procedure/other scripts here below
 done
#/pace/addzfsvolumeastarget.sh $pool ${vol} $ipaddr $portalport $targetiqn $chapuser $chappas
