#!/bin/sh
export ETCDCTL_API=3
cd /TopStor/
theone=` echo $@ | awk '{print $1}'`;
thetwo=` echo $@ | awk '{print $2}'`;
myip=`/sbin/pcs resource show CC | grep Attributes | awk '{print $2}' | awk -F'=' '{print $2}'`
./etcdsyncnext.py $myip $theone $thetwo 2>/dev/null
