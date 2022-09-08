#!/bin/sh
isnew=`echo $@ | awk '{print $1}'`

echo $isnew | grep new
if [ $? -eq 0 ];
then
 snapshot=`echo $@ | awk '{print $2}'`
 poolvol=`echo $@ | awk '{print $3}'`
 nodeloc=`echo $@ | awk '{print $4}' | sed 's/\%\%/ /g' `
 echo zfs send -DvPc $snapshot \| $nodeloc zfs recv -F $poolvol
 zfs send -DvPc $snapshot | $nodeloc zfs recv -F $poolvol
else
 #cmd = './sendzfs.sh old '+myvol+' '+snapshot+' '+poolvol+' '+nodeloc
 myvolsnap=`echo $@ | awk '{print $2}'`
 snapshot=`echo $@ | awk '{print $3}'`
 poolvol=`echo $@ | awk '{print $4}'`
 nodeloc=`echo $@ | awk '{print $5}' | sed 's/\%\%/ /g' `
 echo zfs send -DvPc -i  $myvolsnap $snapshot \| $nodeloc zfs recv -F $poolvol
 zfs send -DvPc -i $myvolsnap $snapshot | $nodeloc zfs recv -F $poolvol
fi

