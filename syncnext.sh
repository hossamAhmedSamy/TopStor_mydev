#!/bin/sh
export ETCDCTL_API=3
cd /TopStor/
theone=` echo $@ | awk '{print $1}'`;
thetwo=` echo $@ | awk '{print $2}'`;
myip=`/sbin/pcs resource show CC | grep Attrib | awk -F'ip=' '{print $2}' | awk '{print $1}'`
./logqueue.py syncnext running system
./etcdsyncnext.py $myip $theone $thetwo 2>/dev/null
