#!/bin/sh
export ETCDCTL_API=3
vol=`echo $@ | awk '{print $1}'`
echo $vol > /root/nfsumount
cp /etc/exports 
rm -rf /TopStordata/exportip.${vol}*
echo '# init' > /etc/exports
cat /TopStordata/exportip.* > /etc/exports
exportfs -r
