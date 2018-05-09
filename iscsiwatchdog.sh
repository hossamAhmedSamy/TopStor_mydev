#!/bin/sh
systemctl status etcd &>/dev/null
if [ $? -eq 0 ];
then
 systemctl restart target &>/dev/null
 systemctl restart iscsi &>/dev/null
 sh /pace/iscsirefresh.sh
 sh /pace/listingtargets.sh
 sh /pace/addtargetdisks.sh
fi
