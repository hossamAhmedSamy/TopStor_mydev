#!/bin/sh
export ETCDCTL_API=3
echo hihihi > /root/etctocronlocal
myip=`/sbin/pcs resource show CC | grep Attributes | awk -F'ip=' '{print $2}' | awk '{print $1}'`
/TopStor/etctocron.py all
/pace/etcdsync.py $myip Snapperiod Snapperiod 2>/dev/null

