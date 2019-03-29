#!/bin/sh
echo $@ > /root/qtmp
glog='/var/www/html/des20/Data/TopStorqueue.log'
dt=` echo $@ | awk '{print $1}'`;
tm=` echo $@ | awk '{print $2}'`;
fromhost=` echo $@ | awk '{print $3}'`;
msg=` echo $@ | awk '{print $4}'`;
msgtype=` echo $@ | awk '{print $5}'`;
msguser=` echo $@ | awk '{print $6}'`;
logcode=$msg'@'$dt'@'$tm'@'$fromhost
x=7; code=$msg'@@'; 
while [ $x -le $# ]; do
 logcode=$logcode'@'`echo $@ | awk -v xx=$x '{print $xx}'`;
 code=$code'@'`echo $@ | awk -v xx=$x '{print $xx}'`;
 x=$((x+1));
done
echo code=$code
echo logcode=$logcode
dtn=`date +%s -d ${dt}'T'$tm`;
echo $dt $tm $fromhost $msgtype $msguser $code $dtn>> $glog
