#!/bin/sh
echo $@ > /root/replitargetget
cd /TopStor
partner=`echo $@ | awk '{print $1}'`
volume=`echo $@ | awk '{print $2}'`
volsize=`echo $@ | awk '{print $3}'`
snapshot=`echo $@ | awk '{print $4}'`
partnerinfo=`./etcdget.py Partner/$partner`
replitype=`echo $partnerinfo | awk -F'/' '{print $2}'`
pport=`echo $partnerinfo | awk -F'/' '{print $3}'`
clusterip=`./etcdget.py namespace/mgmtip | awk -F'/' '{print $1}'`
phrase=`echo $partnerinfo | awk -F'/' '{print $NF}'`
isnew='old'
isopen='closed'
echo pport=$pport
echo ./etcdget.py Partnernode/$partner --prefix
partnersinfo=`./etcdget.py Partnernode/$partner --prefix`
echo partnersinfo=$partnersinfo
echo "$partnersinfo" | while read node 
do
 echo node=$node
 echo isopen=$isopen
 echo $isopen | grep open
 if [ $? -eq 0 ];
 then
  break
 fi
 partnerip=`echo $node | awk -F'/' '{print $3}'`
 echo partnerip=$partnerip
 isopen=`./checkpartner.sh $partner $replitype $partnerip $pport $clusterip $phrase $isnew`
 echo isnew=$isopen 
 echo $isopen | grep open
 if [ $? -ne 0 ];
 then
  continue
 fi
 echo $partnerip $pport
 nodeloc='ssh -oBatchmode=yes -i /TopStordata/'${partnerip}'_keys/'${partnerip}' -p '$pport' '${partnerip}
 echo nodeloc /TopStor/repliSelection.py $volume $volsize $snapshot
 xx=`$nodeloc /TopStor/repliSelection.py $volume $volsize $snapshot`
 echo $xx | awk -F'result_' '{print $2}'
done


