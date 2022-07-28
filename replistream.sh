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
$nodeloc /TopStor/targetcreatevol.sh $poolvol $volip $volsubnet $voltype $groups






 






zfs send -DvP $snapshot | $nodeloc zfs recv $poolvol 
if [ $? -eq 0 ];
then
 props=`zfs get all $snapshot | awk '{print $2"="$3}' | grep ':' | grep -v receiver | tr '\n' ','`
 $nodeloc /TopStor/targetsetprop.sh $poolvol $clusterip ${props:0:-1}
fi
echo result_$?result_
