#!/bin/sh
if [ "$#" -eq 0 ];
then
 islocal=0
else
 islocal=1
 myip=`echo $@ | awk '{print $1}'`
 myhost=`echo $@ | awk '{print $2}'`
fi

systemctl status etcd &>/dev/null
if [ $? -eq 0 ];
then
# systemctl restart target &>/dev/null
# systemctl restart iscsi &>/dev/null
 sh /pace/iscsirefresh.sh
 sh /pace/listingtargets.sh
 sh /pace/addtargetdisks.sh
 if [ $islocal -eq 0 ];
 then
  ETCDCTL_API=3 /pace/putzpool.py 
 else
  echo $myip $myhost $islocal
  ETCDCTL_API=3 /pace/putzpoollocal.py $myip $myhost
 fi
fi
