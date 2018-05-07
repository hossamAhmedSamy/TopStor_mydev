cd /pace
iscsimapping='/pacedata/iscsimapping';
iscsitargets='/pacedata/iscsitargets';
declare -a iscsitargets=(`ETCDCTL_API=3 ./iscsiclients.py`);
systemctl status target
if [ $? -ne 0 ];
then
 systemctl start target
fi

/sbin/iscsiadm -m session --rescan &>/dev/null
needrescan=0;
myhost=`hostname -s`
for hostline in "${iscsitargets[@]}"
do
 echo $myhost | grep $hostline
 if [ $? -eq 0 ]; then
  host='127.0.0.1'
 else
  host=` ETCDCTL_API=3 ./etcdgetip.py $hostline`
 fi
 echo hihi
 ping -c 1 -W 1 $host &>/dev/null
 if [ $? -eq 0 ]; then
  needrescan=1;
  hostpath=`ls /var/lib/iscsi/nodes/ | grep "$host"`;
  echo hi cat $iscsimapping  echo $host  grep notconnected 
  cat $iscsimapping |  grep "$host" | grep notconnected &>/dev/null
  if [ $? -eq 0 ]; then
   echo herehihi
   #rm -rf /var/lib/iscsi/nodes/send_targets/$host* &>/dev/null
   hostiqn=`/sbin/iscsiadm -m discovery --portal $host --type sendtargets | awk '{print $2}'`
   /sbin/iscsiadm -m node --targetname $hostiqn --portal $host -u
   /sbin/iscsiadm -m node --targetname $hostiqn --portal $host -l
  fi
  cat $iscsimapping | grep "$host" &>/dev/null
  if [ $? -ne 0 ]; then
   echo new $host
   hostiqn=`/sbin/iscsiadm -m discovery --portal $host --type sendtargets | awk '{print $2}'`
   /sbin/iscsiadm -m node --targetname $hostiqn --portal $host -l
  fi
 else
  echo deleteing $host
  #rm -rf /var/lib/iscsi/nodes/iqn.2016-03.com.${host}:t1 
  #rm -rf /var/lib/iscsi/nodes/${host}* &>/dev/null
 fi
done
if [ $needrescan -eq 1 ]; then
# /sbin/iscsiadm -m session --rescan &>/dev/null
 sleep 1; 
fi
sleep 2;
