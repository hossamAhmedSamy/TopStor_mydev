#!/bin/sh
systemctl status etcd 
if [ $? -eq 0 ];
then
 systemctl restart target
 systemctl restart iscsi
 sh /pace/iscsirefresh.sh
 sh /pace/listingtargets.sh
 sh /pace/addtargetdisks.sh
fi
