#!/bin/sh
cd /TopStor
partners='/TopStordata/partners.txt'
echo $$ > /var/run/servicewatchdog.pid
ClearExit() {
	echo got a signal > /TopStor/txt/sigstatusremote_service.txt
	rm /var/run/servicewatchdog.pid
	exit 0;
}
trap ClearExit HUP
myhost=`hostname -s `
#sleep 120
while true;
do
systemctl status httpd 
if [ $? -ne 0 ];
then
 systemctl start httpd
fi
sleep 1
systemctl status topstorremote 
if [ $? -ne 0 ];
then
 systemctl start topstorremote 
fi
sleep 1
systemctl status topstorremoteack 
if [ $? -ne 0 ];
then
 systemctl start topstorremoteack
fi
sleep 2
/usr/bin/chronyc -a makestep
done

echo it is dead >/TopStor/txt/statusremote.txt
