#!/bin/sh
systemctl status etcd 
if [ $? -eq 0 ];
then
 sh /pace/iscsirefresh.sh
 sh /pace/listingtargets.sh
 sh /pace/addtargetdisks.sh
fi
