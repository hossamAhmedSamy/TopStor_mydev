#!/usr/bin/sh
fnloop () {
cd /TopStor
/TopStor/iscsiwatchdog.sh $1 $2 $3
}


rabbitip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
initial=0
while true;
do
 fnloop $rabbitip $myhost $initial
 initial=1
 sleep 1 
done

