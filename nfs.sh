#!/bin/sh
export ETCDCTL_API=3
ipaddr=`echo $@ | awk '{print $1}'`
ipsubnet=`echo $@ | awk '{print $2}'`
nmcli conn mod cmynode +ipv4.addresses ${ipaddr}/$ipsubnet
nmcli conn up cmynode
echo '# init' > /etc/exports
cat /TopStordata/exportip.* > /etc/exports
exportfs -r
