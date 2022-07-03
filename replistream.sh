#!/bin/sh
echo $@ > /root/replistream
partner=`echo $@ | awk '{print $1}'`
snapshot=`echo $@ | awk '{print $2}'`
nodeip=`echo $@ | awk '{print $3}'`
poolvol=`echo $@ | awk '{print $4}'`
partnerinfo=`./etcdget.py Partner/$partner`
pport=`echo $partnerinfo | awk -F'/' '{print $3}'`
phrase=`echo $partnerinfo | awk -F'/' '{print $NF}'`
clusterip=`./etcdget.py namespace/mgmtip | awk -F'/' '{print $1}'`
isopen=`./checkpartner.sh $partner Receiver $nodeip $pport $clusterip $phrase old`
nodeloc='ssh -oBatchmode=yes -i /TopStordata/'${nodeip}'_keys/'${nodeip}' -p '$pport' '${nodeip}
myvol=`echo $snapshot | awk -F'@' '{print $1}'`
volinfo=` ./etcdget.py vol $myvol`
volip=`echo $volinfo | awk -F'/' '{print $12}'`
volsubnet=` echo $volinfo | awk -F'/' '{print $13}' | awk -F"'" '{print $1}'` 
voltype=`echo $volinfo | awk -F'/' '{print $2}'`
groups=`echo $volinfo | awk -F'/' '{print $9}'`
quota=`zfs get quota $myvol -H | awk '{print $3}'`
result=`$nodeloc /TopStor/targetcreatevol.sh $poolvol $volip $volsubnet $quota $voltype $groups`
echo result = $result
echo $result | grep 'problem/@problem'
if [ $? -eq 0 ];
then
 echo result_cannot create volume result_ 
 exit
fi
poolvol=`echo $result | awk -F'result_' '{print $3}'`
#snapshot=`echo $snapshot | awk -F'@' '{print $1}'`
echo $result | grep 'newvol/@new'
if [ $? -eq 0 ];
then
 echo $result
 zfs send -DvPc $snapshot | $nodeloc zfs recv -F $poolvol 
 result=$?
else
 echo $result
 lastsnap=`echo $result | awk -F'result_' '{print $4}' | sed 's/ //g'`
 zfs send -DvPc -i $myvol@$lastsnap $snapshot | $nodeloc zfs recv -F $poolvol 
 result=$?
 echo 'zfs send -DvPc -i '$myvol'@'$lastsnap $snapshot' | '$nodeloc' zfs recv -F '$poolvol 
fi
#zfs send -Lc $snapshot | $nodeloc zfs recv -F $poolvol 
if [ $result -eq 0 ];
then
 props=`zfs get all $snapshot | awk '{print $2"="$3}' | grep ':' | grep -v receiver | tr '\n' ','`
 $nodeloc /TopStor/targetsetprop.sh $poolvol $clusterip ${props:0:-1}
fi
echo result_${result}result_
