cd /pace
iscsimapping='/pacedata/iscsimapping';
iscsitargets='/pacedata/iscsitargets';
declare -a iscsitargets=(`ETCDCTL_API=3 ./iscsiclients.py`);
systemctl status iscsid &>/dev/null
if [ $? -ne 0 ];
then
 systemctl start iscsid 
fi
systemctl status target &>/dev/null
if [ $? -ne 0 ];
then
 systemctl start target
fi
systemctl status iscsi &>/dev/null
if [ $? -ne 0 ];
then
 systemctl start iscsi 
fi

echo /sbin/iscsiadm -m session --rescan
/sbin/iscsiadm -m session --rescan &>/dev/null
needrescan=0;
myhost=`hostname -s`
for hostline in "${iscsitargets[@]}"
do
 echo $myhost | grep $hostline
 host=` ETCDCTL_API=3 ./etcdgetip.py $hostline`
 echo hihi
 ping -c 1 -W 1 $host &>/dev/null
 if [ $? -eq 0 ]; then
  needrescan=1;
#  hostpath=`ls /var/lib/iscsi/nodes/ | grep "$host"`;
#  echo hi cat $iscsimapping  echo $host  grep notconnected 
#  cat $iscsimapping |  grep "$host" | grep notconnected &>/dev/null
#  if [ $? -eq 0 ]; then
#   echo herehihi
#   #rm -rf /var/lib/iscsi/nodes/send_targets/$host* &>/dev/null
   echo /sbin/iscsiadm -m discovery --portal $host --type sendtargets 
   hostiqn=`/sbin/iscsiadm -m discovery --portal $host --type sendtargets | awk '{print $2}'`
   if [ $? -ne 0 ];
   then
    ff=`ls /var/lib/iscsi/nodes/* | awk '{print $NF}' | grep $myhost` 
    rm -rf /var/lib/iscsi/nodes/$ff 
    hostiqn=`/sbin/iscsiadm -m discovery --portal $host --type sendtargets | awk '{print $2}'`
   fi
   echo /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host --login
   /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host --login
 fi
done
