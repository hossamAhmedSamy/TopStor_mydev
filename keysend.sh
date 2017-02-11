#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
declare -a targets=(`cat /pacedata/iscsitargets | awk '{print $2}'`);
#node=`echo $@ | awk '{print $1}'`
myhost=`hostname -s`
myadd=`host $myhost | awk '{print $NF}'`
echo $myadd | grep DOM
if [ $? -ne 0 ]; then
 grep $myhost /etc/hosts &>/dev/null
 if [ $? -ne 0 ]; then
  echo $myadd | grep DOM
  echo $myadd $myhost >> /etc/hosts
 else
  oldadd=`cat /etc/hosts | grep "$myhost" | awk '{print $1}'`
  sed -i "s/$oldadd/$myadd/g" /etc/hosts
 fi
fi
if [ ! -f /root/.ssh/id_rsa ] ;then 
 ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -P "";
fi
for node in "${targets[@]}"; do
securessh=$(expect -c "
 set timeout 10
 spawn ssh-copy-id -i /root/.ssh/id_rsa.pub root@$node 
 expect \"*\?\"
send \"yes\r\"
expect \"*assword:\"
send \"Abdoadmin\r\"
expect eof
")
done
