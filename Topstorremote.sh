#!/usr/local/bin/zsh
cd /TopStor
partners='/TopStordata/partners.txt'
#rm /tmp/msgremotefile 2>/dev/null
#rm /tmp/msgrack 2>/dev/null
#mkfifo -m 600 /tmp/msgremotefile 2>/dev/null
#mkfifo -m 600 /tmp/msgrack 2>/dev/null
echo $$ > /var/run/topstorremote.pid
ClearExit() {
	echo got a signal > /TopStor/txt/sigstatusremote.txt
	rm /tmp/msgremotefile;
        rm /tmp/msgrack;
	rm /var/run/topstorremote.pid
	exit 0;
}
trap ClearExit HUP
#./ProxySVC.sh &
myhost=`hostname -s `
myip=`/sbin/pcs resource show $CC | grep Attrib | awk -F'ip=' '{print $2}' | awk '{print $1}'`
ETCDCTL_API=3 /bin/python3.6 topstorrecvreq.py $myip 
echo it is dead >/TopStor/txt/statusremote.txt
