#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
declare -a targets=(`cat /pacedata/iscsitargets | awk '{print $2}'`);
#node=`echo $@ | awk '{print $1}'`
myhost=`hostname -s`
myadd=`host $myhost | awk '{print $NF}'`
echo $myadd | grep -E 'DOM|found'
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
myhostCC=`cat /TopStordata/hostname`
myaddCC=`/sbin/pcs resource show CC | grep Attrib | awk '{print $2}' | awk -F'=' '{print $2}'`
grep $myhostCC /etc/hosts &>/dev/null
if [ $? -ne 0 ]; then
 echo $myaddCC $myhostCC >> /etc/hosts
else
 oldaddCC=`cat /etc/hosts | grep "$myhostCC" | awk '{print $1}'`
 sed -i "s/$oldadd/$myaddCC/g" /etc/hosts
fi
if [ ! -f /root/.ssh/id_rsa ] ;then 
 ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -P "";
fi
securessh=$(expect -c "
 set timeout 10
 spawn ssh-copy-id -i /root/.ssh/id_rsa.pub root@$myhostCC 
 expect \"*\?\"
 send \"yes\r\"
 expect \"*assword:\"
 send \"Abdoadmin\r\"
 expect eof
 ")
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
