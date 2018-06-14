#!/usr/bin/sh
logging='/var/www/html/des20/Data/currentinfo3.log'
glog='/var/www/html/des20/Data/TopStorglobal.log'
fromhost=` echo $@ | awk '{print $1}'`;
msg=` echo $@ | awk '{print $2}'`;
msgtype=` echo $@ | awk '{print $3}'`;
msguser=` echo $@ | awk '{print $4}'`;
datenow=`date +%m/%d/%Y`; timenow=`date +%T`;
logcode=$msg'@'$datenow'@'$timenow'@'$fromhost
x=5; code=$msg'@@'; 
while [ $x -le $# ]; do
 logcode=$logcode'@'`echo $@ | awk -v xx=$x '{print $xx}'`;
 code=$code'@'`echo $@ | awk -v xx=$x '{print $xx}'`;
 x=$((x+1));
done
echo code=$code
echo logcode=$logcode
echo $logcode > ${logging}2
dt=${datenow}'T'${timenow}; dtn=`date +%s -d $dt`;
echo $datenow $timenow $fromhost $msgtype $msguser $code $dtn>> $glog
