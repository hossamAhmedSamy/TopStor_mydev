#!/bin/sh
if [[ "$#" -eq 0 ]];
then
 islocal=0
else
 islocal=1
 myip=`echo $@ | awk '{print $1}'`
 myhost=`echo $@ | awk '{print $2}'`
 leader=`echo $@ | awk '{print $3}'`
fi

systemctl status etcd &>/dev/null
if [ $? -eq 0 ];
then
# systemctl restart target &>/dev/null
# systemctl restart iscsi &>/dev/null
 echo start >> /root/iscsiwatch
 sh /pace/iscsirefresh.sh
 sh /pace/listingtargets.sh
 if [ -f /pacedata/addiscsitargets ];
 then
  echo updating iscsitargets >> /root/iscsiwatch
  sh /pace/addtargetdisks.sh
 else
  echo cannot add new iscsi targets at the moment >> /root/iscsiwatch
 fi
 if [[ $islocal -eq 0 ]];
 then
  echo putzpool to leader >> /root/zfspingtmp
  echo putzpool to leader hi="$#" >> /root/iscsiwatch
  ETCDCTL_API=3 /pace/putzpool.py icsiwatchversion
 else
  echo putzpool local $myip $myhost $islocal >> /root/zfspingtmp
  echo putzpool local $myip $myhost $islocal >> /root/iscsiwatch
  ETCDCTL_API=3 /pace/putzpoollocal.py $myip $myhosti $leader
 fi
fi
