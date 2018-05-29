#!/usr/local/bin/zsh
cd /TopStor
rm /tmp/msgrack 2>/dev/null
mkfifo -m 600 /tmp/msgrack 2>/dev/null
echo $$ > /var/run/topstorremoteack.pid
ClearExit() {
        echo got a signal > /TopStor/txt/sigstatusremoteack.txt
        rm /tmp/msgrack;
        rm /var/run/topstorremoteack.pid
         exit 0;
}
trap ClearExit HUP
#./ProxySVC.sh &
myip=`pcs resource show CC | grep Attrib | awk '{print $2}' | awk -F'=' '{print $2}'`
/bin/python3.6 topstorrecvreply.py $myip
