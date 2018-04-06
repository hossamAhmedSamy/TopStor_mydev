#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
declare -a targets=(`cat /pacedata/iscsitargets | awk '{print $2}'`);
#sleep 15
#node=`echo $@ | awk '{print $1}'`
myhost=`hostname -s`
#myadd=`host $myhost | awk '{print $NF}'`
myadd=`ip a | grep dynamic | awk '{print $2}' | awk -F/ '{print $1}'`
echo $myadd
echo $myadd | grep -E 'DOM|found'
if [ $? -ne 0 ]; then
 echo 127.0.0.1 localhost > /etc/hosts
 echo $myadd $myhost >> /etc/hosts
fi
myhostCC=`cat /TopStordata/hostname`
myaddCC=`/sbin/pcs resource show CC | grep Attrib | awk '{print $2}' | awk -F'=' '{print $2}'`
grep $myhostCC /etc/hosts &>/dev/null
if [ $? -ne 0 ]; then
 grep $myaddCC /etc/hosts &>/dev/null
 if [ $? -ne 0 ]; then
 echo $myaddCC $myhostCC >> /etc/hosts
 else
  sed -i "/$myaddCC/c$myaddCC $myhostCC" /etc/hosts
 fi
else
 sed -i "/$myhostCC/c$myaddCC $myhostCC" /etc/hosts
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
securessh=$(expect -c "
 set timeout 10
 spawn ssh-copy-id -i /root/.ssh/id_rsa.pub root@$myhost 
 expect \"*\?\"
 send \"yes\r\"
 expect \"*assword:\"
 send \"Abdoadmin\r\"
 expect eof
 ")
