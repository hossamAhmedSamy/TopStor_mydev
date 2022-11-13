#!/bin/sh
glog='/TopStordata/TopStorglobal.log'
echo $@ > /root/logmsg2tmp
dt=` echo $@ | awk '{print $1}'`;
tm=` echo $@ | awk '{print $2}'`;
fromhost=` echo $@ | awk '{print $3}'`;
msg=` echo $@ | awk '{print $4}'`;
msgtype=` echo $@ | awk '{print $5}'`;
msguser=` echo $@ | awk '{print $6}'`;
#datenow=`date +%m/%d/%Y`; timenow=`date +%T`;
logcode=$msg'@'$dt'@'$tm'@'$fromhost
x=7; code=$msg'@@'; 
while [ $x -le $# ]; do
 logcode=$logcode'@'`echo $@ | awk -v xx=$x '{print $xx}'`;
 code=$code'@'`echo $@ | awk -v xx=$x '{print $xx}'`;
 x=$((x+1));
done
echo code=$code
echo logcode=$logcode
#dt=${datenow}'T'${timenow}; 
dtn=`date +%s `;
echo $dt $tm $fromhost $msgtype $msguser $code $dtn>> $glog
