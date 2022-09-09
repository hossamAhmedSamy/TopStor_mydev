#!/bin/sh
isnew=`echo $@ | awk '{print $1}'`

echo $isnew | grep new
if [ $? -eq 0 ];
then
 snapshot=`echo $@ | awk '{print $2}'`
 poolvol=`echo $@ | awk '{print $3}'`
 nodeloc=`echo $@ | awk '{print $4}' | sed 's/\%\%/ /g' `
 echo zfs send -DvPc $snapshot \| $nodeloc zfs recv -F $poolvol
 left='send -DvPc '$snapshot
 #zfs send -DvPc $snapshot | $nodeloc zfs recv -F $poolvol
else
 #cmd = './sendzfs.sh old '+myvol+' '+snapshot+' '+poolvol+' '+nodeloc
 myvolsnap=`echo $@ | awk '{print $2}'`
 snapshot=`echo $@ | awk '{print $3}'`
 poolvol=`echo $@ | awk '{print $4}'`
 nodeloc=`echo $@ | awk '{print $5}' | sed 's/\%\%/ /g' `
 echo zfs send -DvPc -i  $myvolsnap $snapshot \| $nodeloc zfs recv -F $poolvol
 left='-DvPc -i '${myvolsnap}' '$snapshot
 #zfs send -DvPc -i $myvolsnap $snapshot | $nodeloc zfs recv -F $poolvol
fi
right=' '${nodeloc}' zfs recv -F '$poolvol
zfs send $left | $right
if [ $? -eq 0 ]
then
 echo result_Successresult_
else
 echo result_failresult_
fi
