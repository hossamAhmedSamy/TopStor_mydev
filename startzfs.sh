cd /pace
iscsimapping='/pacedata/iscsimapping';
runningpools='/pacedata/pools/runningpools';
myhost=`hostname -s`
hostnam=`cat /TopStordata/hostname`
poollist='/pacedata/pools/'${myhost}'poollist';
lastreboot=`uptime -s`
seclastreboot=`date --date="$lastreboot" +%s`
secrunning=`cat $runningpools | grep runningpools | awk '{print $2}'`
 ./addtargetdisks.sh
lsblk -Sn | grep LIO &>/dev/null
if [ $? -ne 0 ]; then
sleep 12
fi
 ./initdisks.sh 1
 zpool export -a
if [ -z $secrunning ]; then
 echo hithere: $lastreboot : $seclastreboot
 secdiff=222;
else
 secdiff=$((seclastreboot-secrunning));
fi
if [ $secdiff -ne 0 ]; then
 echo runningpools $seclastreboot > $runningpools
 ./keysend.sh &>/dev/null
 pcs resource create IPinit ocf:heartbeat:IPaddr ip="10.11.11.254" cidr_netmask=24
 zpool export -a
 sh iscsirefresh.sh
 sh listingtargets.sh
 touch /var/www/html/des20/Data/Getstatspid
fi
